# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2026 Gilad Shrem <shrem173@gmail.com>.
"""Exact, in-memory edits for the published 2024 theorem layouts."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import re


class MigrationError(ValueError):
    """Migration cannot proceed without an ambiguous or incomplete edit."""


def header_view(text: str) -> tuple[str, int]:
    """Mask Preamble and Local Layout without changing character offsets."""
    lines, offset, protected = [], 0, None
    for line in text.splitlines(keepends=True):
        token = line.strip()
        if protected is None and token == '\\begin_body':
            return ''.join(lines), offset
        if protected is None and token in {'\\begin_preamble', '\\begin_local_layout'}:
            protected = token.replace('begin_', 'end_', 1)
        if protected is not None:
            lines.append(re.sub(r'[^\r\n]', ' ', line))
            if token == protected:
                protected = None
        else:
            lines.append(line)
        offset += len(line)
    raise MigrationError('Missing LyX body or unclosed Preamble / Local Layout.')


@dataclass
class Node:
    kind: str
    name: str
    start: int
    content: int
    end: int
    parent: Node | None


def nodes(text: str) -> list[Node]:
    found, stack = [], []
    token = re.compile(r'(?m)^\\(begin|end)_(layout|inset|deeper)(?:[ \t]+([^\r\n]*))?[ \t]*\r?$')
    for match in token.finditer(text):
        direction, kind, name = match.groups()
        if direction == 'begin':
            node = Node(kind, (name or '').strip(), match.start(), match.end(), 0, stack[-1] if stack else None)
            found.append(node)
            stack.append(node)
        else:
            if not stack or stack[-1].kind != kind:
                raise MigrationError('Unbalanced LyX structure at '+match[0])
            stack.pop().end = match.end()
    if stack:
        raise MigrationError('Unclosed LyX '+stack[-1].kind)
    return found


def apply_edits(text: str, edits: list[tuple[int, int, str]]) -> str:
    limit = len(text)
    for start, end, value in sorted(edits, reverse=True):
        if start < 0 or end > limit or start > end:
            raise MigrationError('Overlapping or invalid migration edits.')
        text = text[:start]+value+text[end:]
        limit = start
    return text


def field(text: str, node: Node, key: str) -> re.Match | None:
    return re.search(r'(?m)^'+re.escape(key)+r'[ \t]+"([^"\r\n]*)"[ \t]*\r?$', text[node.content:node.end])


def field_span(node: Node, match: re.Match) -> tuple[int, int]:
    return node.content+match.start(1), node.content+match.end(1)


def commented(region: str, position: int) -> bool:
    """Recognize an unescaped TeX percent, including LyX's ERT backslash."""
    line_start = region.rfind('\n', 0, position)+1
    line = region[line_start:position]
    if region[:line_start].rstrip('\r\n').endswith('\\backslash'):
        line = '\\'+line
    return re.search(r'(?<!\\)(?:\\\\)*%', line) is not None


REF_COMMAND = re.compile(
    r'(?:\\backslash\r?\n|\\)(label|ref|pageref|eqref|vref|Vref|vpageref|autoref|Autoref|nameref|prettyref|'
    r'cref|Cref|cpageref|Cpageref|crefrange|Crefrange|cpagerefrange|Cpagerefrange|'
    r'zcref|zCref|zcpageref|zCpageref|zref|zpageref)\*?'
    r'(?:\[[^\]\r\n]*\])?\s*\{([^{}\r\n]*)\}(?:\s*\{([^{}\r\n]*)\})?'
)


class Plan:
    def __init__(self, text: str, before: list[str], after: list[str], *, inherited_modules=()):
        self.text = text
        self.header, self.body_start = header_view(text)
        self.nodes = nodes(text[self.body_start:])
        for node in self.nodes:
            node.start += self.body_start
            node.content += self.body_start
            node.end += self.body_start
        self.edits, self.warnings, self.labels = [], [], []
        self.counts = {'Diagnosis': 0, 'Diagnosis*': 0}
        self.separator_count = self.reference_count = 0
        self.label_map = {}
        modules = set(before) | set(inherited_modules)
        layout_map = {}
        if modules & {'theorems-ams-new', 'theorems-starred-new'}:
            layout_map['Diagnosis*'] = 'Observation*'
        if 'theorems-ams-new' in modules:
            layout_map['Diagnosis'] = 'Observation'
        present = {n.name for n in self.nodes if n.kind == 'layout'}
        self.layout_map = {old: new for old, new in layout_map.items() if old in present}
        if (present & {'Diagnosis', 'Diagnosis*'}) - self.layout_map.keys():
            self.warnings.append('Diagnosis without its published 2024 defining module was retained.')
        if present & {'Note', 'Note*'} and modules & {'theorems-ams-extended-new'}:
            self.warnings.append('Note / Note* is not part of the published 2024 modules or Plus. It was not converted; check its defining module or Local Layout.')
        previous_by_parent = {}
        for node in (n for n in self.nodes if n.kind == 'layout'):
            previous = previous_by_parent.get(id(node.parent))
            new = self.layout_map.get(node.name, node.name)
            if previous and previous.name != node.name and self.layout_map.get(previous.name, previous.name) == new:
                newline = '\r\n' if '\r\n' in text else '\n'
                separator = newline.join(['\\begin_layout Standard', '\\begin_inset Separator plain',
                                          '\\end_inset', '', '\\end_layout', ''])
                self.edits.append((node.start, node.start, separator))
                self.separator_count += 1
            previous_by_parent[id(node.parent)] = node
            if node.name in self.layout_map:
                match = re.match(r'\\begin_layout[ \t]+([^\r\n]*?)[ \t]*\r?$', text[node.start:node.content])
                self.edits.append((node.start+match.start(1), node.start+match.end(1), new))
                self.counts[node.name] += 1
        self.tex_regions = []
        for node in self.nodes:
            if node.kind != 'inset':
                continue
            owner = node.parent.name if node.parent and node.parent.kind == 'layout' else ''
            if node.name == 'CommandInset label':
                value = field(text, node, 'name')
                if value is None:
                    raise MigrationError('Malformed LyX label.')
                self.labels.append((value[1], field_span(node, value), self.layout_map.get(owner)))
            elif node.name == 'ERT' or node.name.startswith('Formula'):
                start = node.start+len('\\begin_inset Formula') if node.name.startswith('Formula') else node.content
                target = self.layout_map.get(owner) if node.name == 'ERT' else None
                self.tex_regions.append((start, node.end, target))
        for start, end, target in self.tex_regions:
            region = text[start:end]
            for match in REF_COMMAND.finditer(region):
                if match[1] == 'label' and not commented(region, match.start()):
                    self.labels.append((match[2], (start+match.start(2), start+match.end(2)), target))

    def choose_labels(self, occupied: set[str]):
        for label, span, target in self.labels:
            if not target:
                continue
            if not label.startswith('diag:'):
                self.warnings.append('Custom label retained: '+label+'. Check any custom reference formatting.')
                continue
            suffix = label[5:]
            if not suffix or any(c in label for c in '{},\\\r\n'):
                error = MigrationError('The label "'+label+'" contains a brace, comma or backslash, '
                                       'so it cannot be renamed safely. Rename it in LyX (right-click the '
                                       'label, or Insert > Label) and run the tool again. Nothing was changed.')
                error.label = label
                raise error
            candidate = base = 'obs:'+suffix
            number = 2
            while candidate in occupied:
                candidate = base+'-plus-'+str(number)
                number += 1
            occupied.add(candidate)
            self.label_map[label] = candidate

    @staticmethod
    def replace_list(value: str, mapping: dict[str, str]) -> str:
        if value in mapping:
            return mapping[value]
        def replace(match):
            token = match[0]
            if token in mapping:
                return mapping[token]
            return token.replace(token.strip(), mapping.get(token.strip(), token.strip()))
        return re.sub(r'[^,]+', replace, value)

    def finish(self, mapping: dict[str, str]) -> str:
        edits, recognized = list(self.edits), []
        for label, span, target in self.labels:
            if label in self.label_map:
                edits.append((*span, self.label_map[label]))
            recognized.append(span)
        for node in self.nodes:
            if node.kind == 'inset' and node.name == 'CommandInset ref':
                value = field(self.text, node, 'reference')
                if value is None:
                    raise MigrationError('Malformed LyX reference.')
                replacement = self.replace_list(value[1], mapping)
                if replacement != value[1]:
                    edits.append((*field_span(node, value), replacement))
                    self.reference_count += 1
        settings = self.text[:self.body_start]
        for match in REF_COMMAND.finditer(settings):
            groups = (2, 3) if match[1].lower().endswith('range') else (2,)
            if not commented(settings, match.start()) and any(match[group] is not None and self.replace_list(match[group], mapping) != match[group] for group in groups):
                raise MigrationError('A renamed label is used in Preamble / Local Layout. Review that reference manually; settings were not changed.')
        for start, end, target in self.tex_regions:
            region = self.text[start:end]
            for match in REF_COMMAND.finditer(region):
                if match[1] == 'label' or commented(region, match.start()):
                    continue
                groups = (2, 3) if match[1].lower().endswith('range') else (2,)
                for group in groups:
                    if match[group] is None:
                        continue
                    span = start+match.start(group), start+match.end(group)
                    recognized.append(span)
                    replacement = self.replace_list(match[group], mapping)
                    if replacement != match[group]:
                        edits.append((*span, replacement))
                        self.reference_count += 1
            for old in mapping:
                for match in re.finditer(r'(?<![\w:.-])'+re.escape(old)+r'(?![\w:.-])', region):
                    position = start+match.start()
                    if not commented(region, match.start()) and not any(a <= position < b for a, b in recognized):
                        raise MigrationError('Unrecognized TeX use of '+old+'. Review this reference manually; nothing was saved.')
        result = apply_edits(self.text, edits)
        nodes(result[header_view(result)[1]:])
        return result


def prepare_labels(plans: list[Plan]) -> dict[str, str]:
    labels = Counter(label for plan in plans for label, _, _ in plan.labels)
    if any(plan.layout_map for plan in plans):
        duplicate = next((label for label, count in labels.items() if count > 1), None)
        if duplicate is not None:
            raise MigrationError('Duplicate label makes reference ownership ambiguous: '+duplicate)
    occupied, result = set(labels), {}
    for plan in plans:
        plan.choose_labels(occupied)
        result.update(plan.label_map)
    return result
