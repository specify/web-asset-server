"""Manage institution mappings without changing shared settings or restarting."""
import argparse
import ast
from pathlib import Path
import pprint
import os
from tempfile import NamedTemporaryFile


def update_config(filename, backend, action, entries):
    target = Path(filename)
    source = target.read_text() if target.exists() else ''
    tree = ast.parse(source)
    key = 'COLLECTION_DIRS' if backend == 'local' else 'COLLECTION_S3_PATHS'
    assignments = [n for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == key for t in n.targets)]
    if len(assignments) > 1:
        raise ValueError(f'{key} has multiple assignments; edit it manually')
    node = assignments[0] if assignments else None
    if node and any(other is not node and other.lineno == node.lineno for other in tree.body):
        raise ValueError('Put collection mappings on their own statement line first')
    mapping = ast.literal_eval(node.value) if node else {}
    if mapping is None:
        raise ValueError('Shared local storage is enabled; define COLLECTION_DIRS = {} first')
    if not isinstance(mapping, dict):
        raise ValueError(f'{key} must be a dictionary')
    if action == 'add':
        if backend == 's3':
            from urllib.parse import urlparse
            if len(entries) % 2:
                raise ValueError('S3 add requires collection / s3://bucket/prefix pairs')
            pairs = list(zip(entries[::2], entries[1::2]))
            if any(urlparse(uri).scheme != 's3' or not urlparse(uri).netloc for _, uri in pairs):
                raise ValueError('Invalid S3 URI')
        else:
            pairs = [(name, name) for name in entries]
            if any(Path(name).is_absolute() or '..' in Path(name).parts for name in entries):
                raise ValueError('Use relative collection directory names without ..')
        mapping.update(pairs)
    else:
        for name in entries:
            mapping.pop(name, None)
    replacement = key + ' = ' + pprint.pformat(mapping, sort_dicts=False) + '\n'
    lines = source.splitlines(keepends=True)
    if node:
        lines[node.lineno - 1:node.end_lineno] = [replacement]
        result = ''.join(lines)
    else:
        result = source.rstrip() + '\n\n' + replacement
    ast.parse(result)
    temporary = None
    try:
        with NamedTemporaryFile(mode='w', dir=target.parent, delete=False) as output:
            temporary = output.name
            output.write(result)
        if target.exists():
            import stat
            metadata = target.stat()
            try:
                os.chown(temporary, metadata.st_uid, metadata.st_gid)
            except PermissionError as exc:
                raise ValueError('Cannot preserve configuration ownership; run the helper with sudo') from exc
            os.chmod(temporary, stat.S_IMODE(metadata.st_mode))
        else:
            os.chmod(temporary, 0o600)
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='settings_local.py')
    parser.add_argument('--backend', choices=['local', 's3'], default='local')
    parser.add_argument('action', choices=['add', 'remove'])
    parser.add_argument('entries', nargs='+')
    args = parser.parse_args()
    try:
        update_config(args.config, args.backend, args.action, args.entries)
    except (ValueError, SyntaxError, OSError) as exc:
        parser.error(str(exc))
    print('Configuration updated. Recreate the container to apply it. Assets were not changed.')


if __name__ == '__main__':
    main()
