#!/usr/bin/env python3
"""Build the three pinned Linux LuaJIT compiler/VM profiles for authored tests."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request
from verify import PINS, save, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=True)
    lock = json.loads((Path(__file__).with_name('compilers.json')).read_text())
    result = dict(oracles={}, files={})
    for profile, revision in PINS.items():
        pin = lock[profile[:10]]
        assert pin['revision'] == revision
        archive = root / (profile + '.tar.gz')
        if not archive.exists():
            with urllib.request.urlopen(pin['url'], timeout=60) as response:
                archive.write_bytes(response.read())
        assert sha(archive) == pin['sha256']
        source = root / profile
        source.mkdir(exist_ok=False)
        # Archive checksum is pinned before passing it to tar.
        subprocess.run(['tar', '-xzf', archive, '-C', source, '--strip-components=1'], check=True)
        stamp = datetime.datetime.fromisoformat(pin['timestamp'].replace('Z', '+00:00'))
        (source / '.relver').write_text(str(int(stamp.timestamp())) + '\n')
        gc64 = profile.endswith('-gc64') and not profile.endswith('-non-gc64')
        subprocess.run(['make', '-j2', 'XCFLAGS=' + ('-DLUAJIT_ENABLE_GC64' if gc64 else '-DLUAJIT_DISABLE_GC64')],
                       cwd=source, check=True)
        vm = source / 'src/luajit'
        result['oracles'][profile] = dict(runtime=str(vm), revision=revision,
            layout='GC64' if gc64 else 'non-GC64', dumpVersion=1 if '2.0' in profile else 2)
        for path in [vm, *sorted((source / 'src/jit').glob('*.lua'))]:
            result['files'][str(path)] = sha(path)
    save(root / 'tools.json', result)


if __name__ == '__main__':
    main()
