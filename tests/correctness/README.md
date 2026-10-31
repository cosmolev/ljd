# Authored LuaJIT correctness checks

These 106 cases qualify the scoped fixes from
[cosmolev/decompiler#174](https://github.com/cosmolev/decompiler/issues/174).
All inputs are authored programs. No recovered public/user program is executed.
The four exact issue attachments are retained alongside 17 programs compiled with
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

Qualified baseline → fork: 21 → 63 behavior passes, 45 → 33 behavior mismatches,
37 → 3 syntax failures, 3 → 7 timeouts. Every previous behavior pass is preserved.
Four additional timeouts expose an existing loop-state defect after anonymous-call
syntax becomes valid. Two incorrect stripped-table results vary with hash iteration
order; both observations are retained and remain failures.

The fixes preserve integer cdata bits/signedness, single-result call/vararg adjustment,
straight-line named-local swap snapshots, and anonymous-call syntax. Remaining
loop-carried register writes and stripped upvalue binding are separately tracked in
[#182](https://github.com/cosmolev/decompiler/issues/182) and
[#183](https://github.com/cosmolev/decompiler/issues/183).
Other table, method, short-circuit and stripped-vararg limitations remain in the matrix.
Passing this finite suite does not establish universal LuaJIT recovery.

`compilers.json` and `upstream.json` pin source revisions and archive hashes;
`fixtures/fixtures.json` pins the authored source and bytecode bytes, layouts and
compiler identity. `--generate` rebuilds generated fixtures while preserving exact
issue attachments. `--record` prepares a candidate expectation map for manual review
and still rejects lost behavior passes.
