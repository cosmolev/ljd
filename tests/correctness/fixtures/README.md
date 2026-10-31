# Authored LuaJIT correctness fixtures (#174, #182, #183)

`fixtures.json` identifies 256 genuine chunks: 42 authored programs × debug/stripped ×
three matching compiler/VM profiles, plus the four exact issue attachments. Each entry
records source/input SHA-256, compiler revision, dump version, header flags and GC64
layout. Issue attachments preserve their exact bytes; their original compiler binary
hash was not supplied. Newly generated fixtures record that hash too. No header is edited.

The eight common controls are copied from the repository's portable Lua compatibility
sources. The focused controls split swaps, call/return/table adjustment, varargs, anonymous
calls, repeat-loop state, captured variables and signed/unsigned cdata boundaries.
The eleven `loop-*.lua` programs add loop-carried writes, accumulator and snapshot
updates, exits, zero iterations, nesting, recursive reentry and name-collision checks.
The four `repeat-break-*.lua` programs cover branch reconnection after extracting
the until condition, including side effects, short-circuiting and nested breaks.
The ten `upvalues-*.lua` programs cover descriptor binding, mutable siblings,
snapshots and call order, capture chains, recursion, UCLO/register reuse, loop
lifetimes, break/return edges, shadowing, multiple results and parent returns.
These sources are authored tests, so only their originals and recovered derivatives may
be executed by the harness. Public/user programs are never behavioral test inputs.

`expectations.json` is a reviewed outcome map, including failures. The independent
source/bytecode oracle must agree before an engine result is classified. Every engine
runs twice; recovered bytes and outcome classifications must agree. Diagnostics retain
raw paths/addresses; their normalized copies support comparison. The previous engine's
stripped table totals can vary with hash iteration because it loses an accumulator
write. The loop-state repair fixes that accumulator, but the table-read snapshot
defect remains a behavior mismatch. The repeat/break follow-up repairs the combined
loop fixture and all 24 new variants; they must pass behavior checks. All 60 new
upvalue variants must also pass. The remaining 18 method/table/short-circuit
mismatches remain explicit; no engine or syntax failure is relabeled a pass.

Run `tests/correctness/verify.py` as documented in [the test guide](../README.md).
`--generate` rebuilds all compiler-generated chunks in place while preserving exact
issue attachments. Use a copy when reviewing a compiler change. `--record` prepares a
candidate outcome map for manual review; it still fails on lost behavior passes.
