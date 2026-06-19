# `halt.mu` — language-semantics companion

**Program bytes (exactly 1):** `Q` → `0x51`
**Behaviour:** halt immediately, producing no output.
**Validated on:** `runtime/interpreter/malbolge` (standard Malbolge).
*(The Unshackled reference loader rejects sources shorter than 2 cells by
design, so this 1-cell program is scoped standard-only in `tests/cases.tsv`;
`print_nul.mu` is the 2-cell program that also halts under Unshackled.)*

## Decode

The interpreter computes `op = XLAT1[(m[c] - 33 + c) mod 94]` for the single
cell at `c = 0`:

```
(0x51 - 33 + 0) mod 94 = (81) mod 94 = 81 ... wait, compute carefully:
0x51 = 81;  81 - 33 + 0 = 48;  48 mod 94 = 48;  XLAT1[48] = 'v' = HALT.
```

So the very first instruction is HALT and the program stops. `a = c = d = 0`
throughout; nothing is read, written, rotated, or jumped.

## Position-dependence / self-modification

There is exactly one instruction and it is executed exactly once. The
post-execution XLAT2 encryption of the cell is never observed because the
program has already halted. With a single linear cell there is no backward
jump and therefore no coupling between the cell's stored byte and any later
decode — the byte was placed by directly inverting the decode equation
`byte = ((48 - 0) mod 94) + 33 = 81 = 'Q'`. See `docs/FEASIBILITY.md` for why
this triviality does not extend to branching/looping programs.
