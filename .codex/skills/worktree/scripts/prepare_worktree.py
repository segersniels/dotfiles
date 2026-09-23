#!/usr/bin/env python3
"""Copy ignored local configuration and optionally clone compatible Node dependencies."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args]).decode().rstrip('\n')


def tracked(root):
    return set(filter(None, git(root, 'ls-files', '-z').split('\0')))


def ignored(root, relative):
    result = subprocess.run(['git', '-C', str(root), 'check-ignore', '-q', '--', relative])
    if result.returncode not in (0, 1):
        raise RuntimeError('Could not check ignore rules')
    return result.returncode == 0


def inside(path, root):
    return path == root or root in path.parents


def clone(source, target):
    if sys.platform == 'darwin':
        command = ['/bin/cp', '-cRp', str(source), str(target)]
    elif sys.platform.startswith('linux'):
        command = ['cp', '-a', '--reflink=always', '--', str(source), str(target)]
    else:
        raise RuntimeError('Dependency cloning requires macOS or Linux')
    subprocess.run(command, check=True)


def dependency_links(directory, source, target):
    links = []
    for parent, dirs, files in os.walk(directory, followlinks=False):
        for name in dirs + files:
            path = Path(parent) / name
            if not path.is_symlink():
                continue
            resolved = path.resolve()
            if not inside(resolved, source):
                raise RuntimeError(f'Dependency link leaves source worktree: {path}')
            if os.path.isabs(os.readlink(path)):
                destination = target / path.relative_to(source)
                replacement = target / resolved.relative_to(source)
                links.append((destination, os.path.relpath(replacement, destination.parent)))
    return links


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--target', required=True, type=Path)
    parser.add_argument('--copy-deps', action='store_true', help='Clone node_modules when dependency inputs match')
    args = parser.parse_args()
    source, target = args.source.resolve(), args.target.resolve()
    if inside(target, source) or inside(source, target):
        raise RuntimeError('Use separate, non-nested source and target worktrees')
    for root in (source, target):
        if Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root:
            raise RuntimeError(f'Expected a worktree root: {root}')
    if Path(git(source, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve() != Path(git(target, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve():
        raise RuntimeError('Source and target must belong to the same Git repository')
    if git(target, 'status', '--porcelain', '--untracked-files=normal'):
        raise RuntimeError('Target must be clean before preparation')

    source_files, target_files = tracked(source), tracked(target)
    directories = {Path('.')}
    for name in source_files:
        directories.update(Path(name).parents)
    report = {'source': str(source), 'target': str(target), 'env_copied': [], 'dependencies_cloned': [], 'skipped': []}
    for directory in sorted(directories):
        folder = source / directory
        if not folder.is_dir() or not inside(folder.resolve(), source):
            continue
        for path in sorted(folder.glob('.env*')):
            if path.name != '.env' and not path.name.startswith('.env.'):
                continue
            relative = str(path.relative_to(source))
            destination = target / relative
            if path.is_symlink() or not path.is_file() or relative in source_files:
                continue
            if not ignored(source, relative) or relative in target_files or not ignored(target, relative):
                report['skipped'].append({'path': relative, 'reason': 'environment file must be ignored in both worktrees'})
                continue
            if destination.exists() or destination.is_symlink():
                report['skipped'].append({'path': relative, 'reason': 'already exists'})
                continue
            if not inside(destination.parent.resolve(), target):
                raise RuntimeError(f'Destination parent leaves target worktree: {relative}')
            destination.parent.mkdir(parents=True, exist_ok=True)
            with path.open('rb') as src, destination.open('xb') as dst:
                os.chmod(destination, 0o600)
                shutil.copyfileobj(src, dst)
            report['env_copied'].append(relative)

    if args.copy_deps:
        inputs = {'package.json', 'package-lock.json', 'npm-shrinkwrap.json', 'yarn.lock', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', 'bun.lock', 'bun.lockb', '.npmrc', '.yarnrc.yml', '.nvmrc', '.node-version', '.tool-versions'}
        names = source_files | target_files
        config_paths = {name for name in names if Path(name).name in inputs or 'patches' in Path(name).parts}
        # Include ignored local package-manager configuration in the compatibility check.
        for directory in directories:
            config_paths.update(str(directory / name) for name in inputs if (source / directory / name).is_file() or (target / directory / name).is_file())
        matches = bool(config_paths) and all(
            (source / name).is_file() and (target / name).is_file()
            and (source / name).read_bytes() == (target / name).read_bytes()
            for name in config_paths
        )
        if not matches:
            report['skipped'].append({'path': 'node_modules', 'reason': 'dependency inputs differ or are missing; install with the project package manager'})
        else:
            package_dirs = {Path('.')} | {Path(name).parent for name in names if Path(name).name == 'package.json'}
            for directory in sorted(package_dirs):
                relative = str(directory / 'node_modules')
                origin, destination = source / relative, target / relative
                if not origin.is_dir() or origin.is_symlink():
                    continue
                if destination.exists() or destination.is_symlink():
                    report['skipped'].append({'path': relative, 'reason': 'already exists'})
                    continue
                if not ignored(source, relative + '/') or not ignored(target, relative + '/') or any(name.startswith(relative + '/') for name in names):
                    raise RuntimeError(f'Dependencies must be ignored and untracked: {relative}')
                if not inside(origin.resolve(), source) or not inside(destination.parent.resolve(), target):
                    raise RuntimeError(f'Dependency path leaves its worktree: {relative}')
                links = dependency_links(origin, source, target)
                destination.parent.mkdir(parents=True, exist_ok=True)
                clone(origin, destination)
                for path, replacement in links:
                    path.unlink()
                    path.symlink_to(replacement)
                report['dependencies_cloned'].append(relative)
    if git(target, 'status', '--porcelain', '--untracked-files=normal'):
        raise RuntimeError('Preparation left visible Git changes; inspect the target')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Preparation failed: {error}. Inspect the target; partial copies are retained.', file=sys.stderr)
        sys.exit(1)
