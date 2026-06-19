# `echo_four_bytes.mu` — language-semantics companion

**Program bytes (exactly 9):** `u b s ` q ^ o \ I`
→ `0x75 0x62 0x73 0x60 0x71 0x5e 0x6f 0x5c 0x49`
**Behaviour:** read 4 bytes from stdin and echo each immediately, then halt.
**Validated on:** standard `malbolge` and Unshackled `unshackled` interpreters.

This is `echo_one_byte` **unrolled four times** — a worked example showing that
*fixed-length, loop-free* programs of arbitrary length remain hand-authorable,
because unrolling never reuses a cell. The instruction stream is

```
/  <  /  <  /  <  /  <  v        (IN OUT × 4, then HALT)
```

## Cell-by-cell derivation

`byte = ((index - pos) mod 94) + 33`, with `IN`=index 84, `OUT`=index 66,
`HALT`=index 48:

| pos | op | index | byte | char |
|---:|:--:|---:|---:|:--:|
| 0 | `/` | 84 | 117 | `u` |
| 1 | `<` | 66 |  98 | `b` |
| 2 | `/` | 84 | 115 | `s` |
| 3 | `<` | 66 |  96 | `` ` `` |
| 4 | `/` | 84 | 113 | `q` |
| 5 | `<` | 66 |  94 | `^` |
| 6 | `/` | 84 | 111 | `o` |
| 7 | `<` | 66 |  92 | `\` |
| 8 | `v` | 48 |  73 | `I` |

Notice the same op recurs at different positions with **different bytes**
(`/` is `u,s,q,o` at positions 0,2,4,6; `<` is `b,`,^,\` at 1,3,5,7). That is
the position-dependence of the language made concrete: identical instructions
need different source bytes depending on where they sit. `tools/verify-encoding.py`
checks every row.

## Position-dependence / self-modification

Still strictly linear: `c` advances `0…8` and halts; **no cell is revisited**,
so XLAT2 re-encryption is never observed and the nine placement equations stay
independent (one per cell). Input handling: each `IN` overwrites `a` with the
next stdin byte; if stdin is exhausted, `IN` yields 59048 and `OUT` emits
`59048 mod 256 = 168` (`0xa8`) — visible in `tools/verify-direct-execution`,
which supplies only one input byte. With four input bytes (`tests/run-tests`)
the output is the four input bytes verbatim.

The hard wall is unchanged: introduce a backward jump to echo an *unbounded*
stream and the re-entered cell decodes against its XLAT2-encrypted value, which
is the coupled, history-dependent (and in Unshackled, nondeterministic) regime
that no human authors by hand. See `docs/FEASIBILITY.md`.
