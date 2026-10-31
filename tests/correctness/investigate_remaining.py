"""Bounded feasibility probes for the remaining authored mismatch families."""
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
fixtures = Path(__file__).with_name('fixtures')
config = json.loads(args.tools.read_text())
rows = []
for case in json.loads((fixtures / 'fixtures.json').read_text())['cases']:
    if Path(case['source']).stem not in ('methods', 'tables', 'shortcircuit'):
        continue
    if case['profile'] not in config['oracles']:
        continue
    vm = config['oracles'][case['profile']]['runtime']
    assert hashlib.sha256(Path(vm).read_bytes()).hexdigest() == config['files'][vm]
    directory = args.output / case['id']
    chunk = fixtures / case['input']
    assert hashlib.sha256(chunk.read_bytes()).hexdigest() == case['inputSha256']
    original = run([vm, chunk], directory, 'original', environment(vm))
    row = {'id': case['id'], 'original': original}
    for label, engine in [('baseline', args.baseline), ('candidate', args.candidate)]:
        recovered = directory / label / 'recovered.lua'
        recovery = run([sys.executable, engine, '-f', chunk], recovered.parent, 'recover')
        recovered.write_text(recovery['stdout'])
        actual = (run([vm, recovered], recovered.parent, 'behavior', environment(vm), timeout=1)
                  if recovery['exit'] == 0 else recovery)
        row[label] = {'pass': actual == original, 'actual': actual}
    rows.append(row)
    print(case['id'], row['baseline']['pass'], '->', row['candidate']['pass'], flush=True)
(args.output / 'results.json').write_text(json.dumps(rows, indent=2) + '\n')
