"""Fetch pinned official sources locally; no environment installation or robot actions.

Default: LIBERO native only. --all restores every reading snapshot; --include-skills
also restores pinned skills. Requires Python 3.12+. Generated files are Git-ignored.
"""
from __future__ import annotations
import argparse
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

STUDY = Path(__file__).resolve().parents[1]
WORK = STUDY / 'work'


def run(*args):
    return subprocess.run(args, check=True, capture_output=True).stdout


def init_source(path, url):
    if path.exists():
        if not (path / '.git').is_dir():
            raise RuntimeError(f'Refusing to replace existing directory: {path}')
        actual = run('git', '-C', str(path), 'remote', 'get-url', 'origin').decode().strip()
        if actual != url:
            raise RuntimeError(f'Unexpected source remote: {actual}')
    else:
        path.mkdir(parents=True)
        run('git', '-C', str(path), 'init')
        run('git', '-C', str(path), 'remote', 'add', 'origin', url)


def ensure_commit(repo, commit):
    if subprocess.run(['git', '-C', str(repo), 'cat-file', '-e', commit + '^{commit}'],
                      capture_output=True).returncode:
        run('git', '-C', str(repo), 'fetch', '--depth=1', 'origin', commit)
    resolved = run('git', '-C', str(repo), 'rev-parse', commit + '^{commit}').decode().strip()
    if resolved != commit:
        raise RuntimeError(f'Commit mismatch: {commit} != {resolved}')


def restore(repo, commit, target):
    marker = target / '.research-source-commit'
    if target.exists():
        if marker.is_file() and marker.read_text().strip() == commit:
            print(f'Already restored: {target.name} {commit[:12]}')
            return
        raise RuntimeError(f'Refusing to replace existing snapshot: {target}')
    ensure_commit(repo, commit)
    data = run('git', '-C', str(repo), 'archive', '--format=tar', commit)
    target.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:') as archive:
        archive.extractall(target, filter='data')
    marker.write_text(commit + '\n')
    print(f'Restored: {target.name} {commit[:12]}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true', help='Restore all branch reading snapshots')
    parser.add_argument('--include-skills', action='store_true')
    args = parser.parse_args()
    if sys.version_info < (3, 12):
        parser.error('Use Python 3.12+ for filtered tar extraction')
    lock = json.loads((STUDY / 'outputs/source-lock.json').read_text())
    source = WORK / 'upstream-rax'
    init_source(source, lock['upstream'])
    commit = next(row['commit'] for row in lock['branches'] if row['branch'] == 'libero-pro/native')
    ensure_commit(source, commit)
    head = subprocess.run(['git', '-C', str(source), 'rev-parse', '--verify', 'HEAD'],
                          capture_output=True, text=True)
    if head.returncode or head.stdout.strip() != commit:
        if run('git', '-C', str(source), 'status', '--porcelain').strip():
            raise RuntimeError('Source checkout has local changes; refusing to change its HEAD')
        run('git', '-C', str(source), 'checkout', '--detach', commit)
    print(f'LIBERO native source: {source}\nPinned commit: {commit}')
    if args.all:
        for row in lock['branches']:
            restore(source, row['commit'], WORK / 'branches' / row['branch'].replace('/', '--'))
    if args.include_skills:
        skills = WORK / 'upstream-skills-lib'
        init_source(skills, 'https://github.com/robot-agent-exploration/skills-lib.git')
        for branch, sha in lock['skills_lib'].items():
            restore(skills, sha, WORK / 'learned-skills' / branch)


if __name__ == '__main__':
    main()
