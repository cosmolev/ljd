"""Compile authored boundary probes and compare their original/recovered behavior."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from verify import environment, run

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tools', type=Path, required=True)
parser.add_argument('--baseline', type=Path, required=True)
parser.add_argument('--candidate', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
config = json.loads(args.tools.read_text())
rows = []
for profile, tool in config['oracles'].items():
    vm = tool['runtime']
    assert hashlib.sha256(Path(vm).read_bytes()).hexdigest() == config['files'][vm]
    for source in sorted(Path(__file__).with_name('fixtures').joinpath('sources').glob('remaining-*.lua')):
        for debug in (True, False):
            name = profile + '-' + source.stem[len('remaining-'):] + ('-debug' if debug else '-stripped')
            directory = args.output / name
            directory.mkdir(parents=True, exist_ok=True)
            chunk = directory / 'input.luac'
            compilation = run([vm, '-bg' if debug else '-bs', source, chunk], directory, 'compile', environment(vm))
            assert compilation['exit'] == 0 and not compilation['timeout']
            original = run([vm, source], directory, 'source', environment(vm))
            bytecode = run([vm, chunk], directory, 'bytecode', environment(vm))
            assert original == bytecode and original['exit'] == 0 and not original['timeout']
            row = {'id': name, 'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                   'inputSha256': hashlib.sha256(chunk.read_bytes()).hexdigest(), 'original': original}
            for label, engine in [('baseline', args.baseline), ('candidate', args.candidate)]:
                recovered = directory / label / 'recovered.lua'
                recovery = run([sys.executable, engine, '-f', chunk], recovered.parent, 'recover')
                recovered.write_text(recovery['stdout'])
                actual = (run([vm, recovered], recovered.parent, 'behavior', environment(vm), timeout=1)
                          if recovery['exit'] == 0 else recovery)
                row[label] = {'pass': actual == original, 'actual': actual}
            rows.append(row)
            print(name, row['baseline']['pass'], '->', row['candidate']['pass'], flush=True)
(args.output / 'results.json').write_text(json.dumps(rows, indent=2) + '\n')
