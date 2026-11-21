#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2026 Gilad Shrem <shrem173@gmail.com>.
"""Migrate documents using the published 2024 modified theorem modules to Plus.

Requires Python 3.10+ and LyX 2.5.1-2.5.3. Tested with LyX 2.5.3 only.
Preview with --dry-run. Copies are the default; --in-place requires an exact
backup. Personal changes to the 2024 modules or settings are outside scope.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import gzip
import os
from pathlib import Path
import re
import subprocess
import sys
import zlib

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lyx_installation import (Cancelled, LyXInstallation, converter_env,
                              find_lyx25, select_user_dir, running_lyx, lyx_running)
from lyx_migration_structure import (MigrationError, Plan, prepare_labels, header_view,
                                     field, field_span, apply_edits)
from lyx_tool_io import write_new, save_in_place, describe_error, ask_yes_no as _ask_yes_no

VERSION = '2.0.0'
LAST_PRE_25_FORMAT = 620
MODULE_MAP = {
    'theorems-ams-new': 'theorem-ams-plus',
    'theorems-ams-extended-new': 'theorem-ams-extended-plus',
    'theorems-starred-new': 'theorem-starred-plus',
    'theorems-sec-new': 'theorem-sec-plus',
}
UNKNOWN_LEGACY = re.compile(r'theorems?-(?:.+-)?(?:new|modified)\Z')
# LaTeX environments that Plus defines; a personal \newtheorem with one of
# these names in the Local Layout or Preamble clashes with the modules.
PLUS_ENVIRONMENTS = frozenset('''acknowledgement answer assumption auxclaim ax claim conclusion condition
    conjecture cor counterexample criterion defn example examples fact lem lyxalgorithm notation notes
    observation problem prop question rem reminder sol summary thm xca'''.split())
PERSONAL_THEOREM = re.compile(r'\\newtheorem\*?\s*\{([A-Za-z]+)(\*?)\}')


def personal_theorem_clashes(header: str) -> list[str]:
    """Names from \\newtheorem in the Local Layout or Preamble that Plus also defines."""
    found = []
    for block in re.findall(r'(?s)\\begin_(?:local_layout|preamble)\r?\n(.*?)\\end_(?:local_layout|preamble)', header):
        for name, star in PERSONAL_THEOREM.findall(block):
            if name in PLUS_ENVIRONMENTS and name+star not in found:
                found.append(name+star)
    return found
_VERBOSE = False
_INTERACTIVE = False
_OUTPUT_GROUP = None
_COLORS = {'CHANGED': '94', 'WARNING': '93', 'SAVED': '92', 'ERROR': '1;91',
           'PREVIEW': '96', 'OUTPUT': '96', 'BACKUP': '96', 'INFO': '95'}


class OutputExists(MigrationError):
    """The chosen copy of the selected document already exists."""
    def __init__(self, path: Path):
        super().__init__(f'{path} already exists; existing files are never overwritten. '
                         'Choose a different name with --output.')
        self.path = path


def _color_enabled(stream) -> bool:
    """Use console colors only when the output stream supports them."""
    try:
        if not stream.isatty() or 'NO_COLOR' in os.environ or os.environ.get('TERM') == 'dumb':
            return False
        if os.name != 'nt':
            return True
        import ctypes
        import msvcrt
        handle = ctypes.c_void_p(msvcrt.get_osfhandle(stream.fileno()))
        mode = ctypes.c_ulong()
        kernel = ctypes.windll.kernel32
        if not kernel.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(mode.value & 4 or kernel.SetConsoleMode(handle, mode.value | 4))
    except (AttributeError, ImportError, OSError, ValueError):
        return False


def _separate(group: str, *, file=None) -> None:
    global _OUTPUT_GROUP
    if _OUTPUT_GROUP is not None and _OUTPUT_GROUP != group:
        print(file=sys.stdout if file is None else file, flush=True)
    _OUTPUT_GROUP = group


def _message(kind: str, text: str, *, file=None, group: str = 'status') -> None:
    stream = sys.stdout if file is None else file
    _separate(group, file=stream)
    label = f'{kind:<7}'
    if _color_enabled(stream):
        label = f'\033[{_COLORS[kind]}m{label}\033[0m'
    print(label+'  '+text, file=stream)


def _detail(*args, **kwargs) -> None:
    if _VERBOSE:
        _separate('status', file=kwargs.get('file'))
        print(*args, **kwargs)


def _reason(exc: BaseException) -> str:
    return describe_error(exc) if isinstance(exc, OSError) else str(exc)


def ask_yes_no(question: str, *, default: bool = False) -> bool:
    """Ask a yes/no question; Enter returns the default."""
    _separate('questions')
    color = _color_enabled(sys.stdout)
    try:
        return _ask_yes_no(('\033[1;96m' if color else '')+'? '+question, default=default)
    finally:
        if color:
            print('\033[0m', end='', flush=True)


def _show_changes(records: dict, payloads: dict, outputs: dict, *, preview: bool = False) -> None:
    kind = 'PREVIEW' if preview else 'CHANGED'
    titles = {'theorems-ams-new': 'AMS', 'theorems-ams-extended-new': 'Extended',
              'theorems-starred-new': 'Unnumbered', 'theorems-sec-new': 'Section numbering'}
    for path in payloads:
        record = records[path]
        report = record.report
        prefix = path.name+': ' if len(payloads) > 1 else ''
        before, after = document_format(record.original), document_format(payloads[path])
        if before != after:
            _message(kind, prefix+f'File format: {before} -> {after}')
        if report['module_replacements']:
            names = ', '.join(titles.get(old, old) for old, _ in report['module_replacements'])
            _message(kind, prefix+'Modules: '+names+' -> Plus')
        layouts = [f'{old} -> {new}: {report[key]}' for old, new, key in (
            ('Diagnosis', 'Observation', 'diagnosis_converted'),
            ('Diagnosis*', 'Observation*', 'diagnosis_star_converted')) if report[key]]
        if layouts:
            _message(kind, prefix+'; '.join(layouts))
        changes = []
        if len(report['labels']) == 1:
            old, new = next(iter(report['labels'].items()))
            changes.append(f'Label: {old} -> {new}')
        elif report['labels']:
            changes.append(f"Labels updated: {len(report['labels'])}")
        if report['references_updated']:
            changes.append(f"References updated: {report['references_updated']}")
        if report['separators_added']:
            changes.append(f"Separators added: {report['separators_added']}")
        child_links = sum(child in outputs and outputs[child] != child for child, _ in record.children)
        if child_links:
            changes.append(f'Child links updated: {child_links}')
        if changes:
            _message(kind, prefix+'; '.join(changes))


def _show_saved(outputs: dict, payloads: dict, reused: set) -> None:
    for path in payloads:
        if path in reused:
            _message('INFO', 'Using the existing identical copy: '+str(outputs[path]))
        else:
            _message('SAVED', str(outputs[path]))
    _message('INFO', 'Next: open the saved file in LyX 2.5 and check the PDF export.', group='next')


def unpack(raw: bytes) -> bytes:
    try:
        return gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
    except (OSError, EOFError, zlib.error) as exc:
        raise MigrationError('Invalid gzip document: '+str(exc)) from exc


def repack(original: bytes, plain: bytes) -> bytes:
    if plain == unpack(original):
        return original
    return gzip.compress(plain, mtime=0) if original.startswith(b'\x1f\x8b') else plain


def document_format(raw: bytes) -> int:
    prefix = unpack(raw).split(b'\\begin_header', 1)[0]
    matches = re.findall(rb'(?m)^\\lyxformat[ \t]+(\d+)[ \t]*\r?$', prefix)
    if len(matches) != 1:
        raise MigrationError('Expected one numeric LyX format declaration.')
    return int(matches[0])


def prepare_document(raw: bytes, *, inherited_modules=()) -> tuple[Plan, dict]:
    """Plan the module and layout renames for one document, with exact offsets."""
    text = unpack(raw).decode('utf-8')
    if not text.lstrip('\ufeff').startswith('#LyX '):
        raise MigrationError('The input is not a LyX document.')
    document_format(raw)
    header, split = header_view(text)
    for token in ('begin_document', 'begin_header', 'end_header'):
        if len(re.findall(r'(?m)^\\'+token+r'[ \t]*\r?$', header)) != 1:
            raise MigrationError('Missing or repeated '+token+'.')
    if not (header.index('\\begin_document') < header.index('\\begin_header') < header.index('\\end_header')):
        raise MigrationError('Invalid header order.')
    body = text[split:]
    for token in ('begin_body', 'end_body', 'end_document'):
        if len(re.findall(r'(?m)^\\'+token+r'[ \t]*\r?$', body)) != 1:
            raise MigrationError('Missing or repeated '+token+'.')
    if not re.search(r'\\end_body[ \t]*\r?\n\s*\\end_document[ \t]*\s*\Z', body):
        raise MigrationError('Unexpected text after the LyX body.')
    blocks = list(re.finditer(r'(?ms)^\\begin_modules[ \t]*\r?\n(.*?)^\\end_modules[ \t]*\r?$', header))
    starts = re.findall(r'(?m)^\\begin_modules[ \t]*\r?$', header)
    ends = re.findall(r'(?m)^\\end_modules[ \t]*\r?$', header)
    if len(starts) != len(ends) or len(blocks) != len(starts) or len(blocks) > 1:
        raise MigrationError('Malformed or repeated modules block.')
    before, after, replacements = [], [], []
    if blocks:
        block = blocks[0]
        entries = []
        for line in block[1].splitlines(keepends=True):
            name = line.strip()
            if not name or name.startswith('#'):
                entries.append((line, None))
                continue
            if re.search(r'\s', name) or name in before:
                raise MigrationError('Invalid or duplicate module: '+name)
            if UNKNOWN_LEGACY.fullmatch(name) and name not in MODULE_MAP:
                raise MigrationError('Unsupported module: '+name+' (see manual 4.4). Nothing was changed.')
            before.append(name)
            entries.append((line, name))
        rewritten = []
        for line, name in entries:
            if name is not None:
                target = MODULE_MAP.get(name, name)
                if target != name:
                    replacements.append((name, target))
                    if target in before:
                        continue
                    line = line.replace(name, target, 1)
                after.append(target)
            rewritten.append(line)
        text = apply_edits(text, [(block.start(1), block.end(1), ''.join(rewritten))])
    plan = Plan(text, before, after, inherited_modules=inherited_modules)
    report = dict(gzip=raw.startswith(b'\x1f\x8b'), module_replacements=replacements,
                  modules_before=before, modules_after=after,
                  diagnosis_converted=plan.counts['Diagnosis'], diagnosis_star_converted=plan.counts['Diagnosis*'],
                  separators_added=plan.separator_count)
    return plan, report


def finish_document(raw: bytes, plan: Plan, report: dict, mapping: dict) -> tuple[bytes, dict]:
    payload = repack(raw, plan.finish(mapping).encode('utf-8'))
    report.update(changed=payload != raw, labels=dict(plan.label_map), references_updated=plan.reference_count,
                  warnings=list(plan.warnings))
    return payload, report


def migrate_bytes(raw: bytes, *, inherited_modules=()) -> tuple[bytes, dict]:
    plan, report = prepare_document(raw, inherited_modules=inherited_modules)
    return finish_document(raw, plan, report, prepare_labels([plan]))


def upgrade_format(source: Path, original: bytes, install: LyXInstallation) -> bytes:
    current = document_format(original)
    if current > install.target_format:
        raise MigrationError('The document is newer than the selected LyX; format downgrade is not supported.')
    if current == install.target_format:
        return original
    if source.read_bytes() != original:
        raise MigrationError('Source changed before format conversion.')
    _detail(f'Official document conversion: {current} -> {install.target_format}. This may normalize document structure.')
    result = subprocess.run([str(install.python), '-B', str(install.converter), '--to', str(install.target_format),
                             '--systemlyxdir', str(install.resources), str(source)],
                            capture_output=True, env=converter_env(), timeout=120)
    diagnostics = result.stderr.decode('utf-8', errors='replace').strip()
    if diagnostics:
        _message('WARNING', diagnostics)
    if result.returncode or not result.stdout or document_format(result.stdout) != install.target_format:
        raise MigrationError('Official document conversion failed; no migrated file was saved.')
    if source.read_bytes() != original:
        raise MigrationError('Source changed during official format conversion.')
    return repack(original, unpack(result.stdout))


def linked_files(plan: Plan, source: Path) -> list[tuple[Path, tuple[int, int]]]:
    linked = []
    for node in plan.nodes:
        if node.kind != 'inset' or node.name != 'CommandInset include':
            continue
        inset = plan.text[node.content:node.end]
        if not re.search(r'(?m)^LatexCommand[ \t]+(?:input|include)[ \t]*\r?$', inset):
            continue
        name = field(plan.text, node, 'filename')
        if name is None:
            raise MigrationError('Child Document is missing its filename.')
        if name[1].lower().endswith('.lyx'):
            linked.append(((source.parent/name[1]).resolve(), field_span(node, name)))
    return linked


def master_field(plan: Plan):
    return re.search(r'(?m)^\\master[ \t]+"?([^"\r\n]+?)"?[ \t]*\r?$', plan.header)


@dataclass
class Document:
    path: Path
    original: bytes
    working: bytes
    plan: Plan
    report: dict
    children: list
    inherited: frozenset


def plan_project(source: Path, *, output=None, in_place=False, with_children=False,
                 upgrade_installation=None, check_outputs=True, quiet=False):
    """Read and validate the complete selected set before any file write.

    Returns (records, outputs, payloads, reused). Only documents that change,
    or that must point to a changed child, get an output; an identical existing
    copy of a child is reused instead of being written again.
    """
    source = source.resolve(strict=True)
    records, visiting = {}, set()

    def load(path, inherited=frozenset(), parent=None):
        _detail('Checking: '+str(path))
        if path in visiting:
            raise MigrationError('Child Document cycle: '+str(path))
        if path in records:
            if records[path].inherited != inherited:
                raise MigrationError('Shared Child Document has different inherited 2024 modules: '+str(path))
            return
        if parent is not None and not path.is_file():
            raise MigrationError(f'Child document not found: {path} (included from {parent.name}). Nothing was changed.')
        visiting.add(path)
        try:
            original = path.read_bytes()
            prepare_document(original)
            working = upgrade_format(path, original, upgrade_installation) if upgrade_installation else original
            plan, report = prepare_document(working, inherited_modules=inherited)
            children = linked_files(plan, path)
            records[path] = Document(path, original, working, plan, report, children, inherited)
            for old, new in report['module_replacements']:
                _detail(f'  Module: {old} -> {new}')
            _detail(f"  Layouts: Diagnosis {plan.counts['Diagnosis']}; Diagnosis* {plan.counts['Diagnosis*']}")
            if with_children:
                effective = inherited | frozenset(report['modules_before']) & MODULE_MAP.keys()
                for child, _ in children:
                    load(child, frozenset(effective), path)
        except MigrationError:
            raise
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            raise MigrationError(f'Cannot read {path.name}: {_reason(exc)}') from exc
        finally:
            visiting.remove(path)

    load(source)
    try:
        mapping = prepare_labels([r.plan for r in records.values()])
    except MigrationError as exc:
        label = getattr(exc, 'label', None)
        where = next((p.name for p, r in records.items() if label and label in r.plan.text), None)
        raise MigrationError('Cannot convert '+(where or 'the labels')+': '+str(exc)) from exc
    root = records[source]
    if not with_children and root.children and (mapping or root.report['module_replacements'] or root.plan.layout_map):
        raise MigrationError('Changing the master modules can also affect its Child Documents. '
                             'Run again with --with-children so they are converted together.')
    content = {}
    for path, record in records.items():
        master = master_field(record.plan)
        if master and (mapping or record.report['module_replacements'] or record.plan.layout_map) \
                and (path.parent/master[1]).resolve() not in records:
            raise MigrationError('This is a child document. Convert its master document instead'
                                 + ('' if _INTERACTIVE else ' (with --with-children)')
                                 + ': '+str((path.parent/master[1]).resolve()))
        try:
            content[path] = finish_document(record.working, record.plan, record.report, mapping)
        except (OSError, ValueError) as exc:
            raise MigrationError(f'Cannot convert {path.name}: {_reason(exc)}') from exc
    # A document is written when it changes, or when it includes a written child.
    written = {path for path, (payload, _) in content.items() if payload != records[path].original}
    grew = True
    while grew:
        grew = False
        for path, record in records.items():
            if path not in written and any(child in written for child, _ in record.children):
                written.add(path)
                grew = True
    if not written:
        return records, {}, {}, set()
    written.add(source)
    if in_place and written != {source}:
        raise MigrationError('Child documents also change, so the result is saved as copies. '
                             'Replacing the original works only for a single document.')
    outputs = {path: path.with_name(path.stem+'.plus'+path.suffix) for path in written}
    outputs[source] = source if in_place else (output or outputs[source]).resolve()
    if outputs[source].parent != source.parent:
        raise MigrationError('Save the copy in the same folder as the original, with a new name. '
                             'Images, the Preamble and child documents are linked relative to that folder.')
    if not in_place and any(path in records for path in outputs.values()):
        raise MigrationError('The output name is the name of an input document. Choose a new name.')
    if len(set(outputs.values())) != len(outputs):
        raise MigrationError('Two documents would have the same output path.')
    payloads = {}
    for path in sorted(written, key=lambda p: p != source):
        record = records[path]
        payload, report = content[path]
        try:
            if with_children:
                updated, _ = prepare_document(payload)
                edits = [(a, b, os.path.relpath(outputs[child], outputs[path].parent).replace('\\', '/'))
                         for child, (a, b) in linked_files(updated, path) if child in outputs]
                master = master_field(updated)
                if master and (parent := (path.parent/master[1]).resolve()) in outputs:
                    edits.append((master.start(1), master.end(1), os.path.relpath(outputs[parent], outputs[path].parent).replace('\\', '/')))
                payload = repack(payload, apply_edits(updated.text, edits).encode('utf-8'))
            report['changed'] = payload != record.original
            if migrate_bytes(payload)[0] != payload:
                raise MigrationError('Output failed repeat-migration verification.')
        except (OSError, ValueError) as exc:
            raise MigrationError(f'Cannot convert {path.name}: {_reason(exc)}') from exc
        payloads[path] = payload
        _detail('\nDocument: '+str(path))
        for old, new in report['labels'].items():
            _detail(f'  Label and references: {old} -> {new}')
        _detail(f"  References updated: {report['references_updated']}; separators added: {report['separators_added']}")
        clashes = personal_theorem_clashes(record.plan.text.split('\\end_header', 1)[0])
        if clashes:
            report['warnings'].append('The Local Layout or Preamble defines '+', '.join(clashes)
                                      + ' with \\newtheorem, and Plus defines the same environments. This can add '
                                      'an extra first page or LaTeX errors; remove or rename these personal definitions.')
        for warning in ([] if quiet else report['warnings']):
            _message('WARNING', (path.name+': ' if len(written) > 1 else '')+warning)
        _detail('  '+('Replace after exact backup: ' if in_place else 'New copy: ')+str(outputs[path]))
    reused = set()
    if check_outputs:
        # Detect save conflicts before anything is written.
        for path, destination in outputs.items():
            if not destination.parent.is_dir():
                raise MigrationError('Output folder does not exist: '+str(destination.parent))
            if in_place:
                if destination.with_name(destination.name+'.bak').exists():
                    raise MigrationError('A backup already exists: '+str(destination)+'.bak. '
                                         'Move it elsewhere, or save a new copy instead. Nothing was changed.')
            elif destination.exists():
                if path != source and destination.read_bytes() == payloads[path]:
                    reused.add(path)
                elif path == source:
                    raise OutputExists(destination)
                else:
                    raise MigrationError('A different copy of a child document already exists: '+str(destination)
                                         +'. Move the earlier .plus.lyx copies elsewhere and run again. Nothing was changed.')
    return records, outputs, payloads, reused


def save_project(records: dict, outputs: dict, payloads: dict, reused: set, *, in_place=False) -> None:
    def check_sources():
        for path, record in records.items():
            if path.read_bytes() != record.original:
                raise MigrationError('Source changed during migration: '+str(path))
    check_sources()
    if in_place:
        path = next(iter(payloads))
        _message('BACKUP', str(save_in_place(path, records[path].original, payloads[path])))
        return
    created = []
    try:
        for path, payload in payloads.items():
            if path in reused:
                continue
            write_new(outputs[path], payload)
            created.append((outputs[path], payload))
        check_sources()
    except BaseException:
        for destination, payload in created:
            if destination.is_file() and destination.read_bytes() == payload:
                destination.unlink()
        raise


def _file_dialog(save: bool, initial: Path | None = None) -> Path | None | bool:
    """Windows Open/Save dialog. Returns False when no dialog can be shown."""
    if os.name != 'nt' or not sys.stdin.isatty():
        return False
    try:
        import ctypes
        from ctypes import wintypes as w

        class OPENFILENAMEW(ctypes.Structure):
            _fields_ = [('lStructSize', w.DWORD), ('hwndOwner', w.HWND), ('hInstance', w.HINSTANCE),
                        ('lpstrFilter', w.LPCWSTR), ('lpstrCustomFilter', w.LPWSTR), ('nMaxCustFilter', w.DWORD),
                        ('nFilterIndex', w.DWORD), ('lpstrFile', w.LPWSTR), ('nMaxFile', w.DWORD),
                        ('lpstrFileTitle', w.LPWSTR), ('nMaxFileTitle', w.DWORD), ('lpstrInitialDir', w.LPCWSTR),
                        ('lpstrTitle', w.LPCWSTR), ('Flags', w.DWORD), ('nFileOffset', w.WORD),
                        ('nFileExtension', w.WORD), ('lpstrDefExt', w.LPCWSTR), ('lCustData', w.LPARAM),
                        ('lpfnHook', w.LPVOID), ('lpTemplateName', w.LPCWSTR), ('pvReserved', w.LPVOID),
                        ('dwReserved', w.DWORD), ('FlagsEx', w.DWORD)]

        dialogs = ctypes.WinDLL('comdlg32')
        filters = ctypes.create_unicode_buffer('LyX documents (*.lyx)\0*.lyx\0All files (*.*)\0*.*\0\0')
        name = ctypes.create_unicode_buffer(initial.name if save and initial else '', 4096)
        folder = ctypes.create_unicode_buffer(str(initial.parent) if initial else '')
        title = ctypes.create_unicode_buffer('Save the converted LyX document' if save else 'Select a LyX document')
        ofn = OPENFILENAMEW()
        ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
        ofn.hwndOwner = ctypes.windll.kernel32.GetConsoleWindow()
        ofn.lpstrFilter = ctypes.cast(filters, w.LPCWSTR)
        ofn.nFilterIndex = 1
        ofn.lpstrFile = ctypes.cast(name, w.LPWSTR)
        ofn.nMaxFile = len(name)
        ofn.lpstrInitialDir = ctypes.cast(folder, w.LPCWSTR) if initial else None
        ofn.lpstrTitle = ctypes.cast(title, w.LPCWSTR)
        ofn.lpstrDefExt = 'lyx'
        # PATHMUSTEXIST | HIDEREADONLY | NOCHANGEDIR | EXPLORER | DONTADDTORECENT (+ FILEMUSTEXIST to open)
        ofn.Flags = 0x800 | 0x4 | 0x8 | 0x80000 | 0x02000000 | (0 if save else 0x1000)
        call = dialogs.GetSaveFileNameW if save else dialogs.GetOpenFileNameW
        if call(ctypes.byref(ofn)):
            return Path(name.value)
        return False if dialogs.CommDlgExtendedError() else None
    except (AttributeError, OSError, ValueError):
        return False


def choose_input() -> Path | None:
    chosen = _file_dialog(save=False)
    if chosen is not False:
        return chosen
    while True:
        answer = input('LyX file to convert (full path; you can drag the file into this window; Enter = cancel): ').strip().strip('"')
        if not answer:
            return None
        path = Path(answer)
        if not path.is_absolute():
            print('Enter the full path, for example C:\\Users\\me\\Documents\\notes.lyx.')
        elif not path.is_file():
            print('File not found: '+str(path))
        else:
            return path


def choose_output(source: Path) -> Path | None:
    suggested = source.with_name(source.stem+'.plus'+source.suffix)
    while True:
        chosen = _file_dialog(save=True, initial=suggested)
        if chosen is False:
            answer = input(f'Name of the new copy (Enter = {suggested.name}): ').strip().strip('"')
            chosen = Path(answer) if answer else suggested
        if chosen is None:
            return None
        if not chosen.is_absolute():
            chosen = source.parent/chosen
        if not chosen.suffix:
            chosen = chosen.with_suffix('.lyx')
        chosen = chosen.resolve()
        if chosen.parent != source.parent.resolve():
            print('Save the copy in the same folder as the original ('+str(source.parent)+').')
        elif chosen == source.resolve():
            print('Choose a new name; the original is replaced only with the backup option.')
        elif chosen.exists():
            print(chosen.name+' already exists. Choose a different name.')
        else:
            return chosen


def _open_folder(path: Path) -> None:
    try:
        if os.name == 'nt':
            os.startfile(str(path))
        else:
            subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', str(path)])
    except OSError as exc:
        _message('WARNING', f'Saved; the folder could not be opened: {exc}')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?', type=Path, help='The LyX document to convert (a dialog opens if omitted)')
    parser.add_argument('--lyx-dir', type=Path, help='LyX installation directory')
    parser.add_argument('--user-dir', type=Path, help='LyX user directory; read-only in this tool')
    parser.add_argument('--non-interactive', action='store_true', help='No questions, dialogs or folder opening')
    parser.add_argument('--verbose', action='store_true', help='Show installation details and the full migration plan')
    parser.add_argument('--dry-run', action='store_true', help='Print the plan and detect problems without writing files')
    parser.add_argument('--upgrade-to-2.5', dest='upgrade_to_25', action='store_true', help='Optional official document format conversion')
    parser.add_argument('--with-children', action='store_true', help='Also convert included Child Documents (automatic when interactive)')
    saves = parser.add_mutually_exclusive_group()
    saves.add_argument('--output', type=Path, help='New filename in the original directory; existing files are never overwritten')
    saves.add_argument('--in-place', action='store_true', help='Replace a single original after an exact .bak backup')
    args = parser.parse_args(argv)
    global _VERBOSE, _INTERACTIVE, _OUTPUT_GROUP
    _VERBOSE, _INTERACTIVE, _OUTPUT_GROUP = args.verbose, not args.non_interactive, None
    interactive = _INTERACTIVE
    print(f'Theorems (AMS) Plus {VERSION}: convert documents from the 2024 package')
    saved = None
    try:
        if not interactive and args.input is None:
            raise MigrationError('--non-interactive requires an input file.')
        processes = running_lyx()
        install = find_lyx25(args.lyx_dir, interactive=interactive, processes=processes)
        profile = select_user_dir(install, args.user_dir, interactive=interactive, processes=processes)
        source = args.input or choose_input()
        if source is None:
            raise Cancelled()
        source = source.resolve(strict=True)
        for text in ('LyX version: '+install.version, 'Installation: '+str(install.root),
                     'User directory: '+str(profile), 'File: '+str(source)):
            _message('INFO', text, group='info')
        if install.version != '2.5.3':
            _message('WARNING', 'Tested only with LyX 2.5.3; the selected version is '+install.version+'.', group='info')
        raw = source.read_bytes()
        children = dict.fromkeys(path for path, _ in linked_files(prepare_document(raw)[0], source))
        with_children = args.with_children or (interactive and bool(children))
        if children:
            _message('INFO', f'Child documents: {len(children)}'
                     + ('; converted together when needed.' if with_children else '.'), group='info')
        upgrade = install if args.upgrade_to_25 else None
        # One planning pass up front, so problems appear before any question.
        records, outputs, payloads, _ = plan_project(source, output=args.output, in_place=args.in_place,
                                                     with_children=with_children,
                                                     upgrade_installation=upgrade, check_outputs=False)
        if not payloads:
            _message('INFO', 'No conversion needed. Nothing was written.')
            return 0
        required = {new for r in records.values() for _, new in r.report['module_replacements']}
        for name in sorted(required):
            if not any((folder/'layouts'/(name+'.module')).is_file() for folder in (profile, install.resources)):
                _message('WARNING', 'Install '+name+'.module in the selected profile before opening the converted document.')
        previewed = False
        if args.dry_run:
            _show_changes(records, payloads, outputs, preview=True)
            for path in payloads:
                _message('OUTPUT', str(outputs[path]))
            try:
                plan_project(source, output=args.output, in_place=args.in_place, with_children=with_children,
                             upgrade_installation=upgrade, quiet=True)
            except MigrationError as exc:
                _message('WARNING', 'When saving: '+str(exc))
            _message('PREVIEW', 'Preview only. Nothing was saved; compilation was not checked.')
            return 0
        if interactive and ask_yes_no('Preview without saving?'):
            _show_changes(records, payloads, outputs, preview=True)
            previewed = True
            if not ask_yes_no('Save now?'):
                _message('INFO', 'Nothing was saved.')
                return 0
        if lyx_running(processes):
            _message('WARNING', 'LyX is running. Close it before saving: an open document may be saved over the converted file.')
            if interactive and not ask_yes_no('Continue anyway?'):
                raise Cancelled()
        in_place, output = args.in_place, args.output
        if interactive and not in_place and output is None and set(payloads) == {source}:
            in_place = ask_yes_no('Replace original and create a .bak backup?')
        while True:
            if interactive and not in_place and output is None:
                output = choose_output(source)
                if output is None:
                    raise Cancelled()
            try:
                records, outputs, payloads, reused = plan_project(
                    source, output=output, in_place=in_place, with_children=with_children,
                    upgrade_installation=upgrade, quiet=True)
                break
            except OutputExists as exc:
                if not interactive:
                    raise
                print(exc.path.name+' already exists. Choose a different name.')
                output = None
        save_project(records, outputs, payloads, reused, in_place=in_place)
        saved = outputs[source]
        if not previewed:
            _show_changes(records, payloads, outputs)
        _show_saved(outputs, payloads, reused)
        if interactive and ask_yes_no('Open output folder?', default=True):
            _open_folder(saved.parent)
        return 0
    except Cancelled:
        _message('INFO', 'Cancelled. Nothing was changed.')
        return 1
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        _message('ERROR', _reason(exc), file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt) as exc:
        print()
        if saved is None:
            _message('INFO', 'Cancelled. Nothing was changed.')
            return 130 if isinstance(exc, KeyboardInterrupt) else 1
        return 0


if __name__ == '__main__':
    status = main()
    if not os.environ.get('LYX_PLUS_LAUNCHER') and '--non-interactive' not in sys.argv:
        try:
            input('\nPress Enter to close...')
        except (EOFError, KeyboardInterrupt):
            pass
    raise SystemExit(status)
