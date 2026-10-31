# Authored LuaJIT correctness checks

These 256 cases qualify the scoped fixes from
[cosmolev/decompiler#174](https://github.com/cosmolev/decompiler/issues/174) and
the loop-state repair for [#182](https://github.com/cosmolev/decompiler/issues/182),
and upvalue binding for [#183](https://github.com/cosmolev/decompiler/issues/183).
All inputs are authored programs. No recovered public/user program is executed.
The four exact issue attachments are retained alongside 42 programs compiled with
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
and call evaluation order. The #182 qualification retained `loop-break.lua` as a
separate failure in repeat/break reconstruction. That failure is repaired by the
follow-up below.

Liveness is computed to a fixed point on the original bytecode CFG, before the
loop swapper relocates numeric/iterator warps into initialization blocks. A second
backward pass protects the actual reaching definitions at loop entries/exits;
loop-generated indices are excluded, and unrelated reuse of the same register is
not protected. Straight-line snapshots are also kept when moving their expression
would cross a write to a dependency. Surviving registers receive collision-free
function-local storage after the existing AST transformations.

The earlier cdata, arity, swap and anonymous-call fixes remain covered. Stripped
upvalue binding is repaired by the #183 follow-up below.
The table-control accumulator now survives, but its table-read snapshots still do
not; the overall control remains a mismatch. Method and short-circuit limitations
also remain in the matrix. The stripped vararg control now passes with bound captures.
Passing this finite suite does not establish universal LuaJIT recovery.

## Repeat/break reconstruction

The previous fork revision `bb2955b2f5c75564876288ecf32f7afe3ced5828` fails even this
standalone program, with or without debug information:

```lua
local n = 0
repeat
  n = n + 1
  if n == 3 then break end
until n > 5
print(n)
```

The branch which skips `break` targets the first until-condition block. The loop
reconstructor extracts that condition as an expression but left the branch pointing
outside the body, triggering `assert warp.false_target in body`. The repair adds
an empty body exit and redirects that branch to it before removing the condition
blocks. Normal execution reaches the until test; `break` exits without evaluating
it. The assertion remains enabled. The adjacent NoOp cleanup now tests the contained
node rather than its list.

The four new `repeat-break-*.lua` programs cover the minimal failure, exit through
either break or until, condition side effects, AND/OR short-circuit evaluation, and
nested loops. Together with the original combined while/repeat/for fixture, these
are 30 debug/stripped and layout variants. Every variant now passes in the matching
VM; source and original bytecode observations agree first.

Linux x86_64 / deployed Python 3.10.20: 130 → 160 behavior passes across 196 cases,
30 → zero engine failures, no lost passes and no timeouts. The existing 33 behavior
mismatches and three syntax failures remain unchanged. On the previous 172 cases
alone, passes increase from 130 to 136. macOS Python 3.12.13: 88 → 108 passes across
132 executable cases, with the same preservation checks and 64 non-GC64 dump2 cases
explicitly unsupported on that platform. Both trials agree on recovered bytes and
outcome classifications.

`compilers.json` and `upstream.json` pin source revisions and archive hashes;
`fixtures/fixtures.json` pins the authored source and bytecode bytes, layouts and
compiler identity. `--generate` rebuilds generated fixtures while preserving exact
issue attachments. `--record` prepares a candidate expectation map for manual review
and still rejects lost behavior passes.

## Upvalue binding (#183)

The baseline for this follow-up is `15a3ee146ea866c874025d7b17eeb268df12b472`.
The issue's exact stripped input is the existing `luajit-2.1-gc64-upvalue-stripped`
fixture, SHA-256 `8d590a3962223187b08500a27a3bd972161da4834c4ab94e752628387762aa87`.
Its original and recovered programs now both print `7`, rather than recovery
reading an unbound global `uv0` and printing nil.

The new `ast/upvalues.py` pass resolves each child descriptor to either a parent
register (`0x8000`, with optional immutable flag `0x4000`) or a parent upvalue.
Private local cells model shared storage. Closure factories capture the cell
identity at FNEW; UCLO replaces the parent's cell while retaining the register
value. Existing closures keep their old cell, so sibling mutation, capture chains,
recursive closures, register reuse and loop iterations retain their lifetimes.
Names are reserved across the complete tree, including debug and global names.

FNEW's reaching writes and reads/writes while captures are open are protected
before temporary elimination. Ordinary reused temporaries remain eligible for
substitution. Call and table-field motion cannot cross retained snapshots or other
calls. Immutable reads may still form immediate short-circuit expressions. The
late debug-name heuristic cannot relabel a retained temporary as a later local.
Parameters and loop indices keep native declarations, with explicit cell copies.
Simultaneous assignments and return arity remain intact. There is no output-text
replacement, global-name fallback or disabled structural assertion.

The ten `upvalues-*.lua` sources add 60 genuine debug/stripped variants across all
three layouts: mutable sibling captures, parameters, call snapshots/order, nested
inheritance, direct/mutual recursion, UCLO/register reuse, numeric/iterator/while/
repeat loop captures, conditional break/return exits, shadowing/global collisions,
multiple results/nils and captures surviving multiple parent returns.

Linux x86_64 / deployed Python 3.10.20: **187 → 238 behavior passes** across 256
cases, with all 60 new variants passing and every previous pass preserved. On the
original 196 cases alone, passes improve **160 → 178**. The remaining 18 mismatches
are the existing method, table and short-circuit controls. There are no engine
failures, syntax failures or timeouts. macOS / Python 3.12.13 checks 172 supported
cases: **126 → 160 passes**, 12 existing mismatches; 84 non-GC64 dump2 cases are
explicitly unsupported on that platform. Both recovery trials agree on output
bytes and classifications, after source/bytecode equivalence is verified.

This is behavioral qualification of authored programs, not a claim of universal
recovery. Explicit cells/factories add allocations; debug-library upvalue inspection,
allocation-sensitive behavior and stack-frame identity are not qualified by this suite.
