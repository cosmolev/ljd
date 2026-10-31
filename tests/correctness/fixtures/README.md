# Authored LuaJIT correctness fixtures (#174)

`fixtures.json` identifies 106 genuine chunks: 17 authored programs × debug/stripped ×
three matching compiler/VM profiles, plus the four exact issue attachments. Each entry
records source/input SHA-256, compiler revision, dump version, header flags and GC64
layout. Issue attachments preserve their exact bytes; their original compiler binary
hash was not supplied. Newly generated fixtures record that hash too. No header is edited.

The eight common controls are copied from the repository's portable Lua compatibility
sources. The focused controls split swaps, call/return/table adjustment, varargs, anonymous
calls, repeat-loop state, captured variables and signed/unsigned cdata boundaries.
These sources are authored tests, so only their originals and recovered derivatives may
be executed by the harness. Public/user programs are never behavioral test inputs.

`expectations.json` is a reviewed outcome map, including failures. The independent
source/bytecode oracle must agree before an engine result is classified. Every engine
runs twice; recovered bytes and outcome classifications must agree. Diagnostics retain
raw paths/addresses; their normalized copies support comparison. The stripped tables
control can produce different incorrect totals because it loses an accumulator write
and observes hash iteration order. Both observations are retained, never called passes.

Run `tests/correctness/verify.py` as documented in [the test guide](../README.md).
`--generate` rebuilds all compiler-generated chunks in place while preserving exact
issue attachments. Use a copy when reviewing a compiler change. `--record` prepares a
candidate outcome map for manual review; it still fails on lost behavior passes.
