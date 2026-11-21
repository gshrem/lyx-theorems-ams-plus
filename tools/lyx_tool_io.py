# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2026 Gilad Shrem <shrem173@gmail.com>.
"""Verified file writes, questions and error texts shared by both tools."""
from pathlib import Path
import errno
import os
import sys
import tempfile

LOCKED = 'it is read-only or open in another program (for example LyX)'


def describe_error(exc: BaseException) -> str:
    """Turn a Windows/Python error into a short explanation for the user."""
    name = getattr(exc, 'filename', None)
    where = str(name) if name else ''
    if isinstance(exc, UnicodeDecodeError):
        return 'The file is not UTF-8 text, so it is not a valid LyX 2.x file.'
    if isinstance(exc, PermissionError):
        return f'Cannot access {where}: {LOCKED}.' if where else f'Access denied: {LOCKED}.'
    if isinstance(exc, FileNotFoundError):
        if where and len(where) >= 260:
            return ('The path is longer than Windows allows (260 characters). '
                    'Move the document to a folder with a shorter path: '+where)
        return 'File or folder not found: '+where if where else 'File or folder not found.'
    if isinstance(exc, OSError) and exc.errno == errno.ENOSPC:
        return 'The disk is full; nothing was changed.'
    if isinstance(exc, OSError) and exc.strerror:
        return f'{exc.strerror}: {where}' if where else exc.strerror
    return str(exc)


def write_new(path: Path, payload: bytes) -> None:
    """Create exclusively. Never overwrite an existing output or backup."""
    identity = None
    try:
        with path.open('xb') as stream:
            stat = os.fstat(stream.fileno())
            identity = (stat.st_dev, stat.st_ino)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if path.read_bytes() != payload:
            raise ValueError('Saved file verification failed: '+str(path))
    except BaseException:
        if identity is not None:
            try:
                stat = path.stat()
                if (stat.st_dev, stat.st_ino) == identity:
                    path.unlink()
            except FileNotFoundError:
                pass
            except OSError as exc:
                print(f'Could not remove incomplete output {path}: {exc}', file=sys.stderr)
        raise


def check_replaceable(source: Path) -> None:
    """Fail before any backup when the file or its folder cannot be written."""
    try:
        with source.open('r+b'):
            pass
    except OSError as exc:
        raise ValueError(f'Cannot replace {source}: {LOCKED}. Nothing was changed.') from exc
    if not os.access(source.parent, os.W_OK):
        raise ValueError(f'No permission to write in {source.parent}. Nothing was changed.')


def save_in_place(source: Path, original: bytes, payload: bytes) -> Path:
    """Back up the exact original, then replace only an unchanged source."""
    if source.read_bytes() != original:
        raise ValueError('The source changed; refusing to replace it: '+str(source))
    check_replaceable(source)
    backup = source.with_name(source.name+'.bak')
    write_new(backup, original)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', dir=source.parent,
                                         prefix='.lyx-plus-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if temporary.read_bytes() != payload:
            raise ValueError('Temporary output verification failed.')
        if source.read_bytes() != original:
            raise ValueError('The source changed before replacement: '+str(source))
        os.replace(temporary, source)
        temporary = None
    except BaseException as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        # The original is untouched, so the new backup is only a redundant copy.
        try:
            if source.read_bytes() == original and backup.read_bytes() == original:
                backup.unlink()
        except OSError:
            pass
        if isinstance(exc, OSError):
            raise ValueError(f'Cannot replace {source}: {LOCKED}. Nothing was changed.') from exc
        raise
    if source.read_bytes() != payload:
        raise ValueError('Saved source verification failed; exact backup: '+str(backup))
    return backup


def ask_yes_no(question: str, *, default: bool = False) -> bool:
    choices = 'Y/n' if default else 'y/N'
    while True:
        answer = input(f'{question} [{choices}]: ').strip().lower()
        if not answer:
            return default
        # With a Hebrew keyboard layout the Y and N keys type ט and מ.
        if answer in {'y', 'yes', 'ט', 'כן', 'n', 'no', 'מ', 'לא'}:
            return answer in {'y', 'yes', 'ט', 'כן'}
        print('Enter Y or N, or press Enter for the capitalized default.')
