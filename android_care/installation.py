"""Curated, offline skill installation and portable release packaging."""
from pathlib import Path
import stat
import zipfile


SKILL_NAME = 'android-device-care'
PROJECT_DIRS = {'codex': '.agents/skills', 'cursor': '.cursor/skills',
                'claude': '.claude/skills', 'antigravity': '.agents/skills'}
USER_DIRS = {**PROJECT_DIRS, 'antigravity': '.gemini/config/skills'}
PUBLIC_FILES = (
    'SKILL.md', 'LICENSE', 'scripts/android_care.py', 'scripts/install_skill.py',
    'android_care/__init__.py', 'android_care/adb.py', 'android_care/cli.py',
    'android_care/analyzer.py', 'android_care/report.py', 'android_care/installation.py',
    'references/onboarding.md', 'references/roadmap.md', 'references/safety-and-evidence.md',
)


def checked_path(path):
    """Check lexical ancestors before resolving anything, including Windows junctions."""
    path = Path(path).expanduser().absolute()
    if '..' in path.parts:
        raise ValueError('Parent traversal (..) is not supported; provide a direct path.')
    for part in (path, *path.parents):
        if part.is_symlink() or getattr(part, 'is_junction', lambda: False)():
            raise ValueError(f'Symlink or junction paths are not supported: {part}')
        try:
            attributes = getattr(part.lstat(), 'st_file_attributes', 0)
        except FileNotFoundError:
            continue
        if attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError(f'Windows reparse-point paths (including junctions) are not supported: {part}')
    return path


def bundle_files(source):
    """Return only the public runtime and reference files; never recurse over the repository."""
    source = checked_path(source)
    result = {}
    for relative in PUBLIC_FILES:
        path = source / relative
        checked_path(path)
        if not path.is_file():
            raise ValueError(f'Missing or non-file bundle entry: {path}')
        result[path.relative_to(source).as_posix()] = path.read_bytes()
    return result


def installation_target(agent, *, project=None, user=False, home=None):
    if (project is not None) == bool(user):
        raise ValueError('Choose exactly one of project or user scope.')
    directories = USER_DIRS if user else PROJECT_DIRS
    if agent not in directories:
        raise ValueError(f'Unsupported agent: {agent}')
    base = (Path.home() if home is None else Path(home)) if user else Path(project)
    return checked_path(base / directories[agent] / SKILL_NAME)


def install(source, target, *, dry_run=False):
    files = bundle_files(source)
    target = checked_path(target)
    if target.exists():
        raise FileExistsError(f'Installation already exists: {target}')
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        checked_path(target)
        target.mkdir()  # Exclusive creation: another installation must never be overwritten.
        for relative, data in files.items():
            path = target / relative
            checked_path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(data)
    return tuple(files)


def package(source, output):
    files = bundle_files(source)
    output = checked_path(output)
    if output.suffix.lower() != '.zip':
        raise ValueError('Choose a .zip output path.')
    output.parent.mkdir(parents=True, exist_ok=True)
    checked_path(output)
    with output.open('xb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for relative, data in files.items():
                entry = zipfile.ZipInfo(f'{SKILL_NAME}/{relative}', date_time=(2020, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, data)
    return tuple(files)
