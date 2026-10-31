#!/usr/bin/env python3
"""Compare pinned ljd engines on authored fixtures only, using matching LuaJIT VMs."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import resource
import signal
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).with_name('fixtures')
PINS = {'luajit-2.0-non-gc64': '592f9e3f549c7f176a9a7a0d70189559305f2eda',
        'luajit-2.1-gc64': '8ca762976ebc85ad9bde3e15f147a7e326e0dd01',
        'luajit-2.1-non-gc64': '8ca762976ebc85ad9bde3e15f147a7e326e0dd01'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def run(command, directory, label, env=None, timeout=5):
    directory.mkdir(parents=True, exist_ok=True)
    def limits():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    with (directory / (label + '.stdout')).open('wb') as out, (directory / (label + '.stderr')).open('wb') as err:
        process = subprocess.Popen(list(map(str, command)), stdout=out, stderr=err, env=env,
                                   start_new_session=True, preexec_fn=limits)
        expired = False
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            expired = True
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    result = dict(exit=process.returncode, timeout=expired,
                  stdout=(directory / (label + '.stdout')).read_text(errors='backslashreplace'),
                  stderr=(directory / (label + '.stderr')).read_text(errors='backslashreplace'))
    save(directory / (label + '.json'), dict(command=list(map(str, command)), **result))
    return result


def environment(vm):
    return dict(os.environ, LUA_PATH=str(Path(vm).parent / '?.lua') + ';;', LC_ALL='C')


def generate(config, fixtures, output):
    catalog = fixtures / 'fixtures.json'
    cases = [c for c in json.loads(catalog.read_text())['cases'] if c['id'].startswith('issue-')] if catalog.exists() else []
    for profile, revision in PINS.items():
        tool = config['oracles'][profile]
        assert tool['revision'] == revision
        vm = tool['runtime']
        assert sha(vm) == config['files'][vm]
        for source in sorted((fixtures / 'sources').glob('*.lua')):
            for debug in (True, False):
                name = profile + '-' + source.stem + ('-debug' if debug else '-stripped')
                chunk = fixtures / 'inputs' / (name + '.luac')
                chunk.parent.mkdir(parents=True, exist_ok=True)
                result = run([vm, '-bg' if debug else '-bs', source, chunk], output / name, 'compile', environment(vm))
                assert result['exit'] == 0 and not result['timeout'], result
                header = chunk.read_bytes()[:5]
                assert header[:3] == b'\x1bLJ' and header[3] == tool['dumpVersion']
                assert bool(header[4] & 8) == (tool['layout'] == 'GC64')
                assert bool(header[4] & 2) == (not debug)
                cases.append(dict(id=name, profile=profile, debug=debug, dumpVersion=header[3],
                    flags=header[4], layout=tool['layout'], compilerRevision=revision,
                    compilerSha256=sha(vm), source=str(source.relative_to(fixtures)),
                    sourceSha256=sha(source), input=str(chunk.relative_to(fixtures)), inputSha256=sha(chunk)))
    save(fixtures / 'fixtures.json', dict(cases=cases))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tools', type=Path, required=True)
    parser.add_argument('--fixtures', type=Path, default=FIXTURES)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--python', default=sys.executable)
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('--record', action='store_true', help='Record a review candidate without applying expectations')
    parser.add_argument('--profile', action='append', choices=list(PINS))
    args = parser.parse_args()
    config = json.loads(args.tools.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    if args.generate:
        generate(config, args.fixtures, args.output / 'generation')
    cases = json.loads((args.fixtures / 'fixtures.json').read_text())['cases']
    profiles = args.profile or list(PINS)
    rows, failures = [], []
    for case in cases:
        if case['profile'] not in profiles:
            rows.append(dict(id=case['id'], status='unsupported-runtime-layout', profile=case['profile']))
            continue
        tool = config['oracles'][case['profile']]
        assert tool['revision'] == PINS[case['profile']]
        vm = tool['runtime']
        assert sha(vm) == config['files'][vm]
        source, chunk = (args.fixtures / case[k] for k in ['source', 'input'])
        assert sha(source) == case['sourceSha256'] and sha(chunk) == case['inputSha256']
        directory = args.output / case['id']
        original = run([vm, source], directory, 'source', environment(vm))
        bytecode = run([vm, chunk], directory, 'bytecode', environment(vm))
        assert original == bytecode and original['exit'] == 0 and not original['timeout'], case['id']
        if 'expectedStdout' in case:
            assert original['stdout'] == case['expectedStdout'], case['id']
        row = dict(id=case['id'], profile=case['profile'], debug=case['debug'], expected=original)
        for label, engine in [('baseline', args.baseline), ('candidate', args.candidate)]:
            observations = []
            for trial in range(2):
                trial_dir = directory / label / str(trial)
                result = run([args.python, engine, '-f', chunk], trial_dir, 'recover', timeout=10)
                recovered = trial_dir / 'recovered.lua'
                recovered.write_bytes((trial_dir / 'recover.stdout').read_bytes())
                status, actual = 'engine-failure', None
                if result['exit'] == 0 and not result['timeout'] and recovered.stat().st_size:
                    syntax = run([vm, '-b', recovered, trial_dir / 'parsed.luac'], trial_dir, 'syntax', environment(vm))
                    status = 'syntax-failure'
                    if syntax['exit'] == 0 and not syntax['timeout']:
                        actual = run([vm, recovered], trial_dir, 'behavior', environment(vm), timeout=1)
                        # Retain raw diagnostics above; normalize only the per-trial path for comparison.
                        actual['stderr'] = actual['stderr'].replace(str(trial_dir), '<trial>')
                        actual['stderr'] = actual['stderr'].replace('/%s/%d/' % (label, trial), '/<trial>/')
                        actual['stderr'] = re.sub(r'(?m)(\[C\]: at )0x[0-9a-f]+', r'\1<address>', actual['stderr'])
                        status = ('timeout' if actual['timeout'] else
                                  'behavior-pass' if actual == original else 'behavior-mismatch')
                observations.append(dict(status=status, recoveredSha256=sha(recovered), actual=actual))
            assert all(observations[0][k] == observations[1][k] for k in ['status', 'recoveredSha256']), (
                'nondeterministic outcome/source', case['id'], label)
            row[label] = dict(observations[0], actualStable=observations[0]['actual'] == observations[1]['actual'],
                              trials=observations)
        if row['baseline']['status'] == 'behavior-pass' and row['candidate']['status'] != 'behavior-pass':
            failures.append(case['id'] + ': lost behavior pass')
        rows.append(row)
        print(case['id'], row['baseline']['status'], '->', row['candidate']['status'], flush=True)
    reviewed = {r['id']: r['candidate']['status'] for r in rows if 'candidate' in r}
    if not args.record:
        expectations = json.loads((args.fixtures / 'expectations.json').read_text())
        for name, outcome in reviewed.items():
            if expectations.get(name) != outcome:
                failures.append(name + ': expected ' + str(expectations.get(name)) + ', got ' + outcome)
        assert set(expectations) == {r['id'] for r in rows}, 'Fixture coverage changed'
    summary = {label: dict(Counter(r[label]['status'] for r in rows if label in r)) for label in ['baseline', 'candidate']}
    save(args.output / 'results.json', dict(platform=platform.platform(), python=subprocess.check_output(
        [args.python, '--version'], text=True).strip(), fixturesSha256=sha(args.fixtures / 'fixtures.json'),
        tools={p: dict(config['oracles'][p], sha256=sha(config['oracles'][p]['runtime'])) for p in profiles},
        engines={label: {str(p.relative_to(engine.parent)): sha(p) for p in sorted(engine.parent.rglob('*.py'))}
                 for label, engine in [('baseline', args.baseline), ('candidate', args.candidate)]},
        summary=summary, cases=rows, failures=failures))
    save(args.output / 'review-candidate.json', reviewed)
    print(json.dumps(dict(summary=summary, failures=failures), indent=2))
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
