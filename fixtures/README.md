# Deterministic fixtures

These are byte-exact inputs and expected outputs for the hand-written Malbolge
Unshackled programs in `src/`. They are deterministic: the linear primitives
have no nondeterminism (they never use the `*`/`p` ops whose high trits the
Unshackled spec leaves nondeterministic), so output is a pure function of input.

The canonical case table that the harness reads is `tests/cases.tsv`; the files
here mirror a subset as standalone byte fixtures for manual inspection:

| fixture | input bytes | program | expected output bytes |
|---|---|---|---|
| `echo_one_Z`    | `5a` (`Z`)            | `src/echo_one_byte.mu`   | `5a` |
| `echo_four_ABCD`| `41 42 43 44` (`ABCD`)| `src/echo_four_bytes.mu`| `41 42 43 44` |
| `print_nul`     | (none)               | `src/print_nul.mu`       | `00` |

Reproduce any row, e.g.:

```bash
printf 'ABCD' | runtime/interpreter/unshackled src/echo_four_bytes.mu | od -An -tx1
# -> 41 42 43 44
```
