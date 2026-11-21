# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2026 Gilad Shrem <shrem173@gmail.com>.
"""Read-only selection of a LyX 2.5 installation and its user directory."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
import ctypes
import json
import re
import subprocess
import sys

sys.dont_write_bytecode = True
SUPPORTED_VERSIONS = {'2.5.1', '2.5.2', '2.5.3'}


class Cancelled(Exception):
    """The user cancelled at a prompt; nothing was written."""

@dataclass(frozen=True)
class LyXInstallation:
    root: Path
    python: Path
    converter: Path
    target_format: int
    version: str = ''
    executable: Path | None = None

    @property
    def resources(self) -> Path:
        return self.converter.parent.parent


@dataclass(frozen=True)
class LyXProcess:
    executable: Path
    user_dir: Path | None
    resources: Path | None


def file_version(path: Path) -> str:
    """Read Windows product metadata without starting LyX or its launcher."""
    if os.name != 'nt' or not path.is_file():
        return ''
    from ctypes import wintypes as w
    api = ctypes.WinDLL('version', use_last_error=True)
    api.GetFileVersionInfoSizeW.argtypes = [w.LPCWSTR, ctypes.POINTER(w.DWORD)]
    api.GetFileVersionInfoSizeW.restype = w.DWORD
    api.GetFileVersionInfoW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID]
    api.VerQueryValueW.argtypes = [w.LPCVOID, w.LPCWSTR, ctypes.POINTER(w.LPVOID), ctypes.POINTER(w.UINT)]
    size = api.GetFileVersionInfoSizeW(str(path), None)
    if not size:
        return ''
    data = ctypes.create_string_buffer(size)
    pointer, length = w.LPVOID(), w.UINT()
    if not api.GetFileVersionInfoW(str(path), 0, size, data) or not api.VerQueryValueW(data, '\\', ctypes.byref(pointer), ctypes.byref(length)):
        return ''
    if length.value < 52:
        return ''
    info = ctypes.cast(pointer, ctypes.POINTER(w.DWORD))
    # VS_FIXEDFILEINFO: product version MS/LS are DWORDs 4 and 5.
    major, minor, patch = info[4] >> 16, info[4] & 0xffff, info[5] >> 16
    return f'{major}.{minor}.{patch}' if major else ''


def registered_versions() -> dict[Path, str]:
    """Use the installer's version when LyX.exe is a launcher without metadata."""
    if os.name != 'nt':
        return {}
    import winreg as reg
    found = {}
    key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
    for hive in (reg.HKEY_CURRENT_USER, reg.HKEY_LOCAL_MACHINE):
        for view in (reg.KEY_WOW64_64KEY, reg.KEY_WOW64_32KEY):
            try:
                with reg.OpenKey(hive, key, 0, reg.KEY_READ | view) as parent:
                    for index in range(reg.QueryInfoKey(parent)[0]):
                        try:
                            with reg.OpenKey(parent, reg.EnumKey(parent, index)) as child:
                                name = reg.QueryValueEx(child, 'DisplayName')[0]
                                if not isinstance(name, str) or not name.startswith('LyX '):
                                    continue
                                root = reg.QueryValueEx(child, 'InstallLocation')[0]
                                version = reg.QueryValueEx(child, 'DisplayVersion')[0]
                                if isinstance(root, str) and root and isinstance(version, str):
                                    found[Path(root).resolve()] = version.strip()
                        except OSError:
                            continue
            except OSError:
                continue
    return found


def command_arguments(command: str) -> list[str]:
    """Parse a Windows process command line with the operating system parser."""
    from ctypes import wintypes as w
    parser = ctypes.windll.shell32.CommandLineToArgvW
    parser.argtypes = [w.LPCWSTR, ctypes.POINTER(ctypes.c_int)]
    parser.restype = ctypes.POINTER(w.LPWSTR)
    count = ctypes.c_int()
    result = parser(command, ctypes.byref(count))
    if not result:
        return []
    try:
        return [result[i] for i in range(count.value)]
    finally:
        free = ctypes.windll.kernel32.LocalFree
        free.argtypes = [w.HLOCAL]
        free.restype = w.HLOCAL
        free(ctypes.cast(result, w.HLOCAL))


def running_lyx() -> list[LyXProcess] | None:
    """None means access was unavailable, not that no LyX process exists."""
    if os.name != 'nt':
        return None
    command = ("[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new(); "
               "$ErrorActionPreference='Stop'; "
               "@(Get-CimInstance Win32_Process -Filter \"Name = 'LyX.exe'\" | "
               "Select-Object ExecutablePath,CommandLine) | ConvertTo-Json -Compress")
    powershell = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    try:
        result = subprocess.run([str(powershell), '-NoProfile', '-NonInteractive', '-Command', command],
                                capture_output=True, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:
            return None
        rows = json.loads(result.stdout.decode('utf-8-sig') or '[]')
        if isinstance(rows, dict):
            rows = [rows]
        found = []
        for row in rows or []:
            if not row.get('ExecutablePath') or not row.get('CommandLine'):
                return None
            args = command_arguments(row['CommandLine'])
            def option(name):
                # LyX uses the last occurrence; launchers may prepend their own.
                positions = [i for i, arg in enumerate(args[:-1]) if arg == name]
                if not positions:
                    return None
                path = Path(args[positions[-1]+1])
                # WMI does not supply the other process's working directory.
                # Resolving a relative option against this tool's CWD is unsafe.
                return path.resolve() if path.is_absolute() else None
            found.append(LyXProcess(Path(row['ExecutablePath']).resolve(), option('-userdir'), option('-sysdir')))
        return found
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def choose_path(title: str, paths: list[Path], *, interactive: bool, flag: str) -> Path:
    paths = list(dict.fromkeys(p.resolve() for p in paths))
    if not interactive:
        choices = '\n'.join('  '+str(p) for p in paths)
        raise ValueError(title+'. Specify '+flag+' "PATH".'+ ('\n'+choices if choices else ''))
    print(title)
    for i, path in enumerate(paths, 1):
        print(f'  {i}. {path}')
    print('Enter a number or a full directory path; 0 cancels.')
    while True:
        answer = input('Directory: ').strip().strip('"')
        if answer == '0':
            raise Cancelled()
        if answer.isdecimal() and 1 <= int(answer) <= len(paths):
            return paths[int(answer)-1]
        if answer and Path(answer).is_absolute() and Path(answer).is_dir():
            return Path(answer).resolve()
        print('Choose a listed number or enter an existing absolute directory path.')

def converter_env() -> dict[str, str]:
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PYTHONUTF8'] = '1'
    return env

def registered_installations(registry=None) -> list[Path]:
    """Read the installer's InstDir25 value in both user scopes and registry views."""
    if registry is None:
        if os.name != 'nt':
            return []
        try:
            import winreg as registry
        except ImportError:
            return []
    candidates=[]
    # Verified in LyX's official Windows installer main.nsh, MultiUser settings
    # and the SoftwareRegistry section. App Paths is a secondary fallback.
    locations=[(r'SOFTWARE\LyX','InstDir25',False),
               (r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\LyX.exe','',True)]
    for key,value_name,executable in locations:
        for hive in (registry.HKEY_CURRENT_USER,registry.HKEY_LOCAL_MACHINE):
            for view in (registry.KEY_WOW64_64KEY,registry.KEY_WOW64_32KEY):
                try:
                    with registry.OpenKey(hive,key,0,registry.KEY_READ|view) as handle:
                        value=registry.QueryValueEx(handle,value_name)[0]
                    if isinstance(value,str) and value.strip():
                        path=Path(os.path.expandvars(value.strip().strip('"')))
                        candidates.append(path.parent.parent if executable else path)
                except OSError:
                    continue
    return list(dict.fromkeys(candidates))

def installation_candidates(explicit: Path | None = None) -> list[Path]:
    if explicit is not None:
        return [explicit.expanduser().resolve()]
    candidates=registered_installations()
    for env_name in ('LOCALAPPDATA','ProgramW6432','ProgramFiles','ProgramFiles(x86)'):
        if value := os.environ.get(env_name):
            prefix=Path(value)/'Programs' if env_name=='LOCALAPPDATA' else Path(value)
            candidates.append(prefix/'LyX 2.5')
    return list(dict.fromkeys(candidates))

def find_lyx25(explicit: Path | None = None, *, interactive=False, processes=None,
               require_converter=True) -> LyXInstallation:
    """Find LyX 2.5. The translation tool only needs its Resources folder."""
    processes = running_lyx() if processes is None else processes
    registered = registered_versions()
    roots = installation_candidates(explicit)
    if explicit is None:
        roots = [p.resources.parent for p in processes or [] if p.resources] + roots
        roots += [p.executable.parent.parent for p in processes or [] if p.executable.parent.name.lower() == 'bin']
    errors, valid = [], []
    for root in dict.fromkeys(p.resolve() for p in roots):
        converter = root / 'Resources' / 'lyx2lyx' / 'lyx2lyx'
        if not converter.is_file():
            continue
        matches = [p for p in processes or [] if p.resources == root/'Resources' or p.executable == root/'bin/LyX.exe']
        executable = matches[0].executable if len(matches) == 1 else root/'bin/LyX.exe'
        if not executable.is_file():
            errors.append(f'{root}: LyX.exe not found')
            continue
        version = file_version(executable) or registered.get(root, '')
        bundled = root / 'Python' / 'python.exe'
        python = bundled if bundled.is_file() else Path(sys.executable)
        if not require_converter:
            if version and not version.startswith('2.5.'):
                errors.append(f'{root}: LyX {version} is not LyX 2.5')
            elif (root/'Resources'/'layouttranslations').is_file():
                valid.append(LyXInstallation(root, python, converter, 0, version, executable))
            continue
        if version not in SUPPORTED_VERSIONS:
            errors.append(f'{root}: unsupported or unverified LyX version ({version or "unknown"})')
            continue
        try:
            result = subprocess.run([str(python), '-B', str(converter), '--list'],
                                    capture_output=True, env=converter_env(), timeout=30)
            # Official lyx2lyx prints --list to stderr (with a success status).
            listing = result.stdout + result.stderr
            versions = re.findall(rb'(?m)^(\d+\.\d+)\s+stable format:\s+(\d+)', listing)
            if result.returncode != 0 or not versions or versions[-1][0] != b'2.5':
                errors.append(f'{root}: converter does not identify itself as the LyX 2.5 series')
                continue
            valid.append(LyXInstallation(root, python, converter, int(versions[-1][1]), version, executable))
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f'{root}: {exc}')
    if len(valid) == 1:
        return valid[0]
    if valid:
        active = [item for item in valid if any(p.resources == item.resources or p.executable == item.executable for p in processes or [])]
        if len(active) == 1:
            return active[0]
        selected = choose_path('Several LyX installations were found; choose the target installation',
                               [item.root for item in valid], interactive=interactive, flag='--lyx-dir')
        return next((item for item in valid if item.root == selected), None) or \
            find_lyx25(selected, processes=processes, require_converter=require_converter)
    suffix = ('\n' + '\n'.join(errors)) if errors else ''
    hint = ('Run the tool from a command window with --lyx-dir "path to LyX 2.5".' if interactive
            else 'Use --lyx-dir "path to LyX 2.5".')
    raise ValueError('No LyX 2.5 installation was found (LyX 2.3 and 2.4 are not supported). '
                     + hint + ' Nothing was changed.' + suffix)


def select_user_dir(installation: LyXInstallation, explicit: Path | None = None, *, interactive=False, processes=None) -> Path:
    """Use the explicit folder, or the only candidate; otherwise ask."""
    if explicit is not None:
        selected = explicit.expanduser().resolve()
    else:
        processes = running_lyx() if processes is None else processes
        active = [p for p in processes or [] if p.resources == installation.resources or p.executable == installation.executable]
        active_dirs = list(dict.fromkeys(p.user_dir for p in active if p.user_dir))
        appdata = Path(os.environ.get('APPDATA', str(Path.home())))
        override = os.environ.get('LYX_USERDIR_25x')
        default = Path(override).expanduser().resolve() if override else appdata/'LyX2.5'
        candidates = active_dirs + ([default] if default.is_dir() else [])
        if not active_dirs:
            candidates += sorted(p for p in appdata.glob('LyX2.5*') if p.is_dir())
        candidates = list(dict.fromkeys(p.resolve() for p in candidates))
        if len(candidates) == 1 and not any(p.user_dir is None for p in active):
            selected = candidates[0]
        else:
            selected = choose_path('Choose the LyX 2.5 user directory shown in Help > About LyX',
                                   candidates, interactive=interactive, flag='--user-dir')
    if not selected.is_dir():
        raise ValueError('The user directory does not exist: '+str(selected)+'. Nothing was changed.')
    return selected.resolve()


def lyx_running(processes) -> bool:
    """True only when a LyX process is known to be running."""
    return bool(processes)


def print_target(installation: LyXInstallation, user_dir: Path) -> None:
    print('LyX version: '+(installation.version or 'unknown'))
    print('Installation: '+str(installation.root))
    print('User directory: '+str(user_dir))
    if installation.version != '2.5.3':
        print('This package was tested with LyX 2.5.3 only.')
