# `echo_one_byte.mu` — language-semantics companion

**Program bytes (exactly 3):** `u b O`  →  `0x75 0x62 0x4f`
**Behaviour:** read one byte from stdin, write it to stdout, halt.
**Validated on:** `runtime/interpreter/malbolge` (standard) and
`runtime/interpreter/unshackled` (Ørjan Johansen Unshackled reference).

---

## 1. The decode rule

At each step a Malbolge interpreter looks at the code cell under the code
pointer `c`, takes its current value `m[c]`, and computes

```
op = XLAT1[(m[c] - 33 + c) mod 94]
```

where `XLAT1` is the fixed 94-character decode permutation. Only eight results
are real instructions (`i j * p < / v o`); everything else is a no-op. The
operation therefore depends on **both** the byte value **and** the absolute
position `c`. The relevant rows of `XLAT1` for this program are:

| `XLAT1` index | character | instruction |
|---:|:--:|:--|
| 48 | `v` | HALT |
| 66 | `<` | OUT (write low 8 bits of accumulator `a`) |
| 84 | `/` | IN  (read one byte into `a`; EOF → 59048) |

## 2. Cell-by-cell derivation

Each cell is placed by inverting the decode equation. To make position `c`
execute operation with `XLAT1` index `k`, choose

```
byte = ((k - c) mod 94) + 33      # always lands in printable ASCII 33..126
```

| pos `c` | wanted op | index `k` | `((k-c) mod 94)+33` | byte | char |
|---:|:--:|---:|---:|---:|:--:|
| 0 | IN  `/` | 84 | 84+33 = 117 | `0x75` | `u` |
| 1 | OUT `<` | 66 | 65+33 =  98 | `0x62` | `b` |
| 2 | HALT`v` | 48 | 46+33 =  79 | `0x4f` | `O` |

Check (forward direction, exactly what the interpreter computes):
`(117-33+0)%94 = 84 → '/'`, `(98-33+1)%94 = 66 → '<'`, `(79-33+2)%94 = 48 → 'v'`. ✓
`tools/verify-encoding.py` performs this check mechanically.

## 3. Why position-dependence and self-modification do **not** break this program

After a cell executes, the interpreter **encrypts it in place**:
`m[c] ← XLAT2[m[c] - 33]`, then advances `c` and `d`. So the byte you wrote is
*not* the byte that sits there after the instruction runs. In general that is
catastrophic for hand-authoring, because a later jump back to that cell would
read the *encrypted* value and decode a *different* instruction.

This program is **strictly linear**: `c` only ever advances `0 → 1 → 2`, and
then `v` halts. **No cell is ever visited twice.** Therefore:

* the XLAT2 encryption of cell 0 happens *after* cell 0 has already done its
  job and is never observed again;
* likewise for cells 1 and 2;
* there is no backward jump, so there is no coupling between a cell's
  pre-execution value and any later decode.

That is the whole reason a human can place these three bytes directly: the
constraint system degenerates to three **independent** one-variable modular
equations (section 2), each with the trivial closed-form solution above. There
is nothing to search.

The accumulator path is equally simple. `a` starts at 0; `IN` overwrites it
with the input byte; `OUT` emits `a mod 256`; `HALT` stops. The data pointer
`d` advances `0 → 1 → 2` but is never read by `IN`/`OUT`/`HALT`, so the
memory cells it passes over are irrelevant.

## 4. Standard vs. Unshackled

The three instructions used here (`IN`, `OUT`, `HALT`) and the decode rule are
**identical** in standard Malbolge and in Malbolge Unshackled. The places where
Unshackled differs — unbounded ternary word width, the rotate (`*`) width-growth
rule, the "crazy" (`p`) operation, and the nondeterministic high trits — are
**never exercised** by this program. That is why the byte-for-byte identical
file produces identical output on both reference interpreters (see
`tests/run-tests`). The Unshackled loader additionally requires ≥ 2 source
cells, which this 3-cell program satisfies.

## 5. Where this stops scaling

Add a loop (a backward `i`/`j` jump) and cell *k* is re-entered *after* having
been rewritten by XLAT2. Its decode now depends on its own execution history,
the data-pointer trajectory, and — in Unshackled — nondeterministic trits. The
independent per-cell equations of section 2 become one large coupled,
history-dependent, partly nondeterministic system. That coupling is exactly why
every non-trivial Malbolge program in existence was produced by an automated
generator, and why none is shipped in `src/`. See `docs/FEASIBILITY.md`.
