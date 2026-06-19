# Feasibility: what handwritten Malbolge Unshackled can and cannot do

This is the honest engineering record for RUSTER. It states precisely which
parts of the requested application are achievable as **handwritten,
generator-free** Malbolge Unshackled, demonstrates the boundary with running
code, and explains *why* the boundary sits where it does. It exists so that no
claim in this repository is taken on faith.

## TL;DR

* **Achievable by hand, and shipped here:** strictly linear (loop-free) programs
  over the input/output/halt primitives — read a byte, write a byte, halt, and
  any fixed-length unrolling thereof. These are real Malbolge Unshackled, run on
  two independent reference interpreters, and are covered by passing tests.
* **Not achievable by hand, and therefore *not* shipped (not faked):** anything
  requiring a backward branch — loops, parsing, conditionals over request
  content, state folding, HTML generation, hashing dispatch. That is the entire
  web application. No working handwritten Malbolge implementing it exists, here
  or anywhere.

The repository contains **zero** placeholder/stub `.mu` files standing in for
the application. Producing files that *look* like `router.mu`/`auth.mu` but do
not implement routing/auth would violate both the project's own rules ("no
mocked behavior, no placeholder functions, no TODO implementations") and basic
honesty. They are intentionally absent, and this document explains why.

## The mechanism that makes hand-authoring fail

A Malbolge step does three things to the cell under the code pointer `c`:

1. **Decode by position:** `op = XLAT1[(m[c] - 33 + c) mod 94]`. The same byte
   means different instructions at different addresses.
2. **Execute** one of eight operations (`i j * p < / v o`).
3. **Self-modify:** `m[c] ← XLAT2[m[c] - 33]`, then `c++`, `d++`.

Steps (1) and (3) are individually survivable. The killer is their
**interaction under a backward jump**. For a strictly linear program every cell
is executed at most once, so step (3) is never *observed* — the encryption
happens after the cell has done its job and is never read again. Placement
reduces to one independent equation per cell:

```
byte(c) = ((wanted_index - c) mod 94) + 33
```

a closed form with no search (see `tools/verify-encoding.py`, and the
`src/*.semantics.md` companions). That is exactly the regime of the shipped
programs.

The moment control flow returns to an already-executed cell `k` (which every
loop, and therefore every parser, scanner, and renderer requires), the
interpreter reads the **XLAT2-encrypted** value of `m[k]`, not the byte you
typed. The instruction executed on the second visit is a function of:

* the original byte,
* how many times the cell has already executed (each visit re-encrypts),
* the data-pointer trajectory that may have *also* written `m[k]` via `*`/`p`,
* and, **in Malbolge Unshackled specifically**, nondeterministically chosen
  high trits (Ørjan Johansen's reference uses `randomIO`/`randomRIO`; the
  language is defined so a correct program must work for *every* choice).

The independent per-cell equations collapse into one large, coupled,
history-dependent, partially nondeterministic constraint system. Solving it is
the well-known reason that:

* the first Malbolge "Hello, World!" (1998–2000) was **found by search**, not
  written;
* every non-trivial Malbolge / Malbolge Unshackled program in existence is the
  output of a **generator** (Lou Scheffer's cryptanalysis tooling; Matthias
  Lutter's LMAO / HeLL / LMFAO assembler chain for Unshackled);
* no human-authored Malbolge program performs even general input-dependent
  branching by hand.

RUSTER's rules forbid every one of those generation methods (LMFAO/LAL,
normalized Malbolge, transpilers, code generators, search/beam/genetic/constraint
synthesis, automatically generated instruction sequences). Forbidding the only
known production method for looping Malbolge, while also requiring a functioning
looping program (a web server), is internally contradictory: the constraints
cannot be jointly satisfied. This document chooses to satisfy the *language and
honesty* constraints exactly, and to report the application gap rather than fake
it.

## The boundary, demonstrated

| Capability | Needs a backward jump? | Hand-authorable? | Shipped & tested? |
|---|:--:|:--:|:--:|
| Halt | no | yes | `src/halt.mu` ✅ |
| Emit accumulator, halt | no | yes | `src/print_nul.mu` ✅ |
| Read 1 byte, echo, halt | no | yes | `src/echo_one_byte.mu` ✅ |
| Read N bytes, echo, halt (fixed N) | no | yes (unroll) | `src/echo_four_bytes.mu` ✅ |
| Echo an *unbounded* stream | **yes** (loop) | no | — |
| Parse the REQUEST frame | **yes** | no | — |
| Compare credentials / branch | **yes** | no | — |
| Fold the event log into state | **yes** | no | — |
| Render/escape HTML | **yes** | no | — |

The first four rows are proven by `tests/run-tests` (12 passing assertions
across two reference interpreters) and `tools/verify-direct-execution`. The
remaining rows are not implemented and are not represented by stub files.

## What a *functioning* RUSTER would actually require

Every real-world "Malbolge program" of this size is emitted by an assembler such
as Matthias Lutter's LMFAO for Unshackled (you write HeLL/assembly; the tool
produces the self-consistent encrypted Malbolge). That toolchain is precisely
what this project forbids. So a genuinely functioning, feature-complete RUSTER
has exactly two honest routes, both of which require relaxing one stated
constraint:

1. **Keep "raw handwritten Malbolge", drop "functioning web app".** That is this
   repository: a validated toolchain plus the maximal hand-authorable Malbolge
   Unshackled primitives, with the gap documented. (Chosen.)
2. **Keep "functioning web app", drop "no generators".** Implement the
   application in HeLL/assembly and assemble it to Malbolge Unshackled with
   LMFAO — real Malbolge bytes, but machine-generated, which rules 10 and the
   "no code generators / no generated Malbolge output" clause prohibit.

A third route — "implement the app in a permitted language behind the adapter"
— would produce a working product but is *not* Malbolge and would contradict
"do not silently replace Malbolge Unshackled with another language", so it is
not done here without an explicit decision to change scope.

This file is the proof obligation discharged: the claims are bounded, the
working parts run, and the non-working parts are neither hidden nor faked.
