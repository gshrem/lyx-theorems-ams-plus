#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2026 Gilad Shrem <shrem173@gmail.com>.
"""Preview or merge the package translations and missing LyX defaults.

Close LyX before applying. Preview is the default. Existing unrelated entries
and custom translations are preserved; --replace-conflicts is explicit opt-in.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
# Support the isolated Python runtime bundled with LyX for Windows.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lyx_installation import (Cancelled, find_lyx25, select_user_dir, print_target,
                              running_lyx, lyx_running)
from lyx_tool_io import write_new, save_in_place, ask_yes_no, describe_error

VERSION = '2.0.0'
BLOCK = re.compile(r'(?m)^[ \t]*\ufeff?[ \t]*Translation[ \t]+([^\s]+)[ \t]*(?:#[^\r\n]*)?\r?\n(.*?)^[ \t]*End[ \t]*(?:#[^\r\n]*)?(?:\r?\n|$)', re.S)
ENTRY = re.compile(r'(?m)^([ \t]*)"([^"\r\n]+)"([ \t]+)"((?:\\.|[^"\\\r\n])*)"([ \t]*(?:#[^\r\n]*)?)(\r?\n|$)')

def parse_blocks(text: str) -> dict[str, re.Match]:
    if '\ufeff' in text[1:]:
        raise ValueError('A UTF-8 BOM is only supported at the start of the file.')
    blocks = {}
    position = 0
    for match in BLOCK.finditer(text):
        comments_only(text[position:match.start()], 'outside Translation blocks')
        if match[1] in blocks:
            raise ValueError('Duplicate Translation block: '+match[1])
        entries(match[2])
        blocks[match[1]] = match
        position = match.end()
    comments_only(text[position:], 'outside Translation blocks')
    if not blocks:
        raise ValueError('No Translation blocks found; refusing to rewrite this file.')
    return blocks

def comments_only(text: str, location: str) -> None:
    for line in text.splitlines():
        if line.strip() and not line.lstrip('\ufeff \t').startswith('#'):
            raise ValueError('Unrecognized or incomplete translation syntax '+location+': '+line[:120])


def entries(body: str) -> dict[str, re.Match]:
    found = {}
    position = 0
    for match in ENTRY.finditer(body):
        comments_only(body[position:match.start()], 'inside a Translation block')
        if match[2] in found:
            raise ValueError('Duplicate translation key: '+match[2])
        found[match[2]] = match
        position = match.end()
    comments_only(body[position:], 'inside a Translation block')
    return found

def merge_bytes(original: bytes, stock: bytes, mapping: dict, *, replace_conflicts=False, fresh=False,
                remove_diagnosis=False) -> tuple[bytes, list[dict]]:
    """Fill missing defaults and merge package entries without losing user values."""
    text, base = original.decode('utf-8'), stock.decode('utf-8')
    blocks, base_blocks = parse_blocks(text), parse_blocks(base)
    newline = '\r\n' if '\r\n' in text else '\n'
    edits, report = [], []
    for language in dict.fromkeys([*blocks, *base_blocks, *mapping]):
        translations = mapping.get(language, {})
        block = blocks.get(language)
        body = block[2] if block else ''
        old = entries(body)
        defaults = entries(base_blocks[language][2]) if language in base_blocks else {}
        body_edits, additions = [], []
        for key, value in translations.items():
            if any(ch in key+value for ch in ('"', '\r', '\n', '\\')):
                raise ValueError('Unsupported characters in package translation: '+key)
        desired = {key: match[4] for key, match in defaults.items()}
        desired.update(translations)
        if remove_diagnosis and language == 'he':
            desired.pop('Diagnosis', None)
            if 'Diagnosis' in old:
                match = old['Diagnosis']
                # Retain any user comment on the removed entry.
                comment = match[5].strip()
                body_edits.append((match.start(), match.end(), comment+newline if comment else ''))
                report.append(dict(language='he', key='Diagnosis', old=match[4], new=None, action='remove-legacy'))
        for key, value in sorted(desired.items()):
            # Existing non-package entries are always retained, including
            # translations customized against an older LyX installation.
            if key not in translations and key in old:
                continue
            current = old[key][4] if key in old else None
            if current == value:
                continue
            # Equality with a stock default does not establish user intent.
            action = 'add' if current is None or fresh else ('replace-existing' if replace_conflicts else 'keep-existing')
            if key not in translations:
                action = 'add-stock'
            report.append(dict(language=language,key=key,old=current,new=value,action=action))
            if action == 'keep-existing':
                continue
            if key in old:
                match = old[key]
                body_edits.append((match.start(4),match.end(4),value))
            else:
                additions.append(f'\t"{key}" "{value}"{newline}')
        for start,end,value in sorted(body_edits,reverse=True):
            body=body[:start]+value+body[end:]
        if additions:
            if body and not body.endswith(('\n','\r')):
                body+=newline
            body+=''.join(additions)
        if block:
            edits.append((block.start(2),block.end(2),body))
        elif body:
            edits.append((len(text),len(text),newline+f'Translation {language}'+newline+body+'End'+newline))
    for start,end,value in sorted(edits,reverse=True):
        text=text[:start]+value+text[end:]
    parse_blocks(text)
    return text.encode('utf-8'),report

def summarize(report: list[dict], mapping: dict, *, verbose: bool) -> None:
    """Counts by default; every entry with --verbose."""
    package = [r for r in report if r['action'] in ('add', 'replace-existing') and r['key'] in mapping.get(r['language'], {})]
    kept = [r for r in report if r['action'] == 'keep-existing']
    stock = [r for r in report if r['action'] == 'add-stock']
    removed = [r for r in report if r['action'] == 'remove-legacy']
    replaced = [r for r in package if r['action'] == 'replace-existing']
    print(f'  Package translations to add or update: {len(package)}'
          + (f' (replacing {len(replaced)} of your values)' if replaced else ''))
    if kept:
        print(f'  Your values kept instead of the package values: {len(kept)}')
    if stock:
        print(f'  LyX default translations missing from your file: {len(stock)}')
    if removed:
        print('  The legacy Hebrew Diagnosis entry is removed.')
    if verbose:
        for row in report:
            old = '(none)' if row['old'] is None else '"'+row['old']+'"'
            new = '(removed)' if row['new'] is None else '"'+row['new']+'"'
            print(f"    {row['action']}: {row['language']}: {row['key']}: {old} -> {new}")
    elif report:
        print('  Run with --verbose to list every entry.')


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user-dir',type=Path,help='LyX user directory, if automatic selection is ambiguous')
    parser.add_argument('--lyx-dir',type=Path,help='LyX 2.5 installation directory, if it is not found automatically')
    parser.add_argument('--verbose',action='store_true',help='List every planned entry')
    action=parser.add_mutually_exclusive_group()
    action.add_argument('--apply',action='store_true',help='Write the reviewed merge; default is preview only')
    action.add_argument('--dry-run',action='store_true',help='Preview only (also the default)')
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--non-interactive',action='store_true',help='No questions; keep Diagnosis unless --remove-diagnosis is given')
    mode.add_argument('--interactive',action='store_true',help='Ask about replacement, legacy translation removal and saving (used when the CMD file is double-clicked)')
    legacy=parser.add_mutually_exclusive_group()
    legacy.add_argument('--remove-diagnosis',dest='remove_diagnosis',action='store_true',default=None,
                        help='Remove only the Hebrew Diagnosis entry; not needed for migrated Plus documents')
    legacy.add_argument('--keep-diagnosis',dest='remove_diagnosis',action='store_false',
                        help='Keep the legacy Hebrew Diagnosis entry (default)')
    parser.add_argument('--replace-conflicts',action='store_true',default=None,help='Explicitly replace existing package translation keys, including values equal to LyX defaults')
    args=parser.parse_args(argv)
    interactive=args.interactive
    saving_started=False
    print(f'Theorems (AMS) Plus {VERSION}: Hebrew translations for LyX')
    try:
        processes=running_lyx()
        install=find_lyx25(args.lyx_dir,interactive=not args.non_interactive,processes=processes,require_converter=False)
        profile=select_user_dir(install,args.user_dir,interactive=not args.non_interactive,processes=processes)
        print_target(install,profile)
        target=profile/'layouttranslations'
        stock=(install.resources/'layouttranslations').read_bytes()
        existed=target.exists()
        original=target.read_bytes() if existed else stock
        package_file=Path(__file__).resolve().parent.parent/'translations'/'theorems-plus.json'
        try:
            mapping=json.loads(package_file.read_text(encoding='utf-8'))['translations']
        except (OSError,ValueError,KeyError,TypeError) as exc:
            raise ValueError('The package translations file is missing or damaged: '+str(package_file)
                             +'. Keep the translations folder next to the tools folder.') from exc
        replace=args.replace_conflicts
        if interactive and replace is None:
            _,initial=merge_bytes(original,stock,mapping,fresh=not existed)
            conflicts=[row for row in initial if row['action']=='keep-existing']
            if conflicts:
                print('Your file has translations that differ from the package:')
                for row in conflicts:
                    print(f"  {row['language']}: {row['key']}: yours \"{row['old']}\", package \"{row['new']}\"")
                print('Y uses the package values instead of these; N keeps yours.')
                replace=ask_yes_no('Replace existing package translations?')
        blocks=parse_blocks(original.decode('utf-8'))
        hebrew=entries(blocks['he'][2]) if 'he' in blocks else {}
        remove=args.remove_diagnosis
        if remove is None and 'Diagnosis' in hebrew and interactive:
            print('Existing Hebrew Diagnosis translation: '+hebrew['Diagnosis'][4])
            print('Removing it may change headings in old, unconverted documents. Plus uses Observation instead.')
            remove=ask_yes_no('Remove this legacy Hebrew Diagnosis entry?')
        payload,report=merge_bytes(original,stock,mapping,replace_conflicts=bool(replace),fresh=not existed,
                                  remove_diagnosis=bool(remove))
        if payload==original and existed:
            print('Already up to date. Nothing was changed.')
            return 0
        print('Planned changes'+(' (a new file is created):' if not existed else ':'))
        summarize(report,mapping,verbose=args.verbose)
        backup=target.with_name(target.name+'.bak')
        if existed and backup.exists():
            print('Note: '+str(backup)+' already exists. Move it elsewhere before saving; it is never overwritten.')
        apply=args.apply
        if interactive and not args.dry_run and not apply:
            if lyx_running(processes):
                print('LyX is running. Translations are loaded only when LyX starts; restart it after saving.')
            print('Target: '+str(target.resolve()))
            apply=ask_yes_no('Apply the changes shown above?')
        elif apply and lyx_running(processes):
            print('LyX is running. Restart it after saving to load the translations.')
        if not apply:
            print('Nothing was saved.' if interactive else 'Preview only. Nothing was saved. Run again with --apply to save.')
            return 0
        if existed and backup.exists():
            raise ValueError('A backup already exists: '+str(backup)+'. Move it elsewhere and run the tool again. Nothing was changed.')
        saving_started=True
        if existed:
            backup=save_in_place(target,original,payload)
            print('Backup of your previous file: '+str(backup))
        else:
            write_new(target,payload)
        print('Saved and verified: '+str(target))
        print('Restart LyX to load the translations.')
        return 0
    except Cancelled:
        print('Cancelled. Nothing was changed.')
        return 1
    except (OSError,ValueError) as exc:
        text=describe_error(exc) if isinstance(exc,OSError) else str(exc)
        print('Error: '+text,file=sys.stderr)
        return 1
    except (EOFError,KeyboardInterrupt) as exc:
        print()
        if saving_started:
            print('Cancelled while saving. Check the target and its .bak backup before trying again: '+str(target))
        else:
            print('Cancelled. Nothing was changed.')
        return 130 if isinstance(exc,KeyboardInterrupt) else 1

if __name__=='__main__':
    raise SystemExit(main())
