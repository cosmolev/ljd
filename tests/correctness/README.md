# Authored LuaJIT correctness checks

These 172 cases qualify the scoped fixes from
[cosmolev/decompiler#174](https://github.com/cosmolev/decompiler/issues/174) and
the loop-state repair for [#182](https://github.com/cosmolev/decompiler/issues/182).
All inputs are authored programs. No recovered public/user program is executed.
The four exact issue attachments are retained alongside 28 programs compiled with
debug information and stripped, for each of three pinned compiler/VM profiles:
LuaJIT dump1 non-GC64, dump2 GC64 and dump2 non-GC64.

```sh
python3 tests/correctness/tools.py /tmp/ljd-vms
# Extract the checksum-verified archive in upstream.json to /tmp/ljd-baseline.
python3 tests/correctness/verify.py --tools /tmp/ljd-vms/tools.json \
  --baseline /tmp/ljd-baseline/main.py --candidate "$PWD/main.py" \
  --output /tmp/ljd-results
```

Use Linux x86_64 to execute all three layouts. The harness verifies original source
and bytecode observations in the matching VM before checking recovered syntax and
behavior. Every engine runs twice. Output bytes and outcome classifications must
agree; diagnostics retain both observations. Timeouts and children are bounded.
`fixtures/expectations.json` includes reviewed failures, not just successes.

The original 106-case qualification for #174 improved the upstream engine from
21 to 63 behavior passes. The #182 candidate is compared against the previous
`cosmolev` revision `bf7b5de1e5bc62ccdeceb578bbceb9107c379f0c` as well: across all
172 cases, behavior passes increase from 96 to 130, mismatches fall from 51 to 33,
and timeouts fall from 16 to zero. The three syntax failures and six engine failures
remain explicit. Every previous pass is preserved. On the original 106 cases alone,
all seven previous timeouts now pass, bringing the pass count from 63 to 70.

The expanded run uses deployed Linux Python 3.10.20 and all three matching VMs.
macOS Python 3.12.13 independently checks 116 executable cases: 65 to 88 behavior
passes, no lost passes, and 11 to zero timeouts. Its 56 dump2 non-GC64 cases are
explicitly unsupported on that platform. Original source and bytecode agree before
recovery; both recovery trials agree on source bytes and classification.

The eleven new `loop-*.lua` programs cover repeat/while state, numeric and iterator
accumulators, branch updates, early exits, empty loops and values used only after
loop exit, nested loops, recursive calls, global-name collisions, register snapshots
and call evaluation order. `loop-break.lua` retains a separate known failure in
the combination of repeat/break and adjacent loops: both the previous engine and
candidate fail `_fix_loops` with the same assertion for all six variants. It is not
counted as a loop-state success.

Liveness is computed to a fixed point on the original bytecode CFG, before the
loop swapper relocates numeric/iterator warps into initialization blocks. A second
backward pass protects the actual reaching definitions at loop entries/exits;
loop-generated indices are excluded, and unrelated reuse of the same register is
not protected. Straight-line snapshots are also kept when moving their expression
would cross a write to a dependency. Surviving registers receive collision-free
function-local storage after the existing AST transformations.

The earlier cdata, arity, swap and anonymous-call fixes remain covered. Stripped
upvalue binding remains tracked in [#183](https://github.com/cosmolev/decompiler/issues/183).
The table-control accumulator now survives, but its table-read snapshots still do
not; the overall control remains a mismatch. Method, short-circuit, stripped-vararg
and combined repeat/break limitations also remain in the matrix.
Passing this finite suite does not establish universal LuaJIT recovery.

`compilers.json` and `upstream.json` pin source revisions and archive hashes;
`fixtures/fixtures.json` pins the authored source and bytecode bytes, layouts and
compiler identity. `--generate` rebuilds generated fixtures while preserving exact
issue attachments. `--record` prepares a candidate expectation map for manual review
and still rejects lost behavior passes.
