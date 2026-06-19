# `print_nul.mu` — language-semantics companion

**Program bytes (exactly 2):** `c P` → `0x63 0x50`
**Behaviour:** write one `0x00` byte (the initial accumulator value), then halt.
**Validated on:** standard `malbolge` and Unshackled `unshackled` interpreters.

## Decode

`op = XLAT1[(m[c] - 33 + c) mod 94]`:

| pos `c` | byte | `(byte-33+c) mod 94` | `XLAT1` | instruction |
|---:|---:|---:|:--:|:--|
| 0 | `0x63` = 99 | `(99-33+0) mod 94 = 66` | `<` | OUT (emit `a mod 256`) |
| 1 | `0x50` = 80 | `(80-33+1) mod 94 = 48` | `v` | HALT |

The accumulator `a` is `0` at program start and is never modified, so `OUT`
emits a single `0x00` byte; `HALT` stops. This is the minimal demonstration of
the **output** primitive in isolation (no input), and the minimal program that
also runs under the Unshackled loader's ≥ 2-cell requirement.

## Position-dependence / self-modification

Linear, two cells, each executed once. Cell 0's XLAT2 re-encryption happens
after it emits and is never revisited; cell 1 halts. Both bytes were placed by
the closed-form inverse `byte = ((index - pos) mod 94) + 33` with `index = 66`
(OUT) at pos 0 and `index = 48` (HALT) at pos 1. No coupling, no search. See
`src/echo_one_byte.semantics.md` §3 and `docs/FEASIBILITY.md`.
