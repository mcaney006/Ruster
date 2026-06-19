# RUSTER

Intelligence case-management — built around **handwritten, generator-free
Malbolge Unshackled**, with a validated toolchain and an honest, demonstrated
boundary between what such code can and cannot do.

This README does not oversell. Read [§ Headline truth](#headline-truth) first.

---

## Headline truth

The brief asked for a full multi-user web application written almost entirely in
**raw, handwritten Malbolge Unshackled**, with **no** code generators,
assemblers (LMFAO/LAL), normalized Malbolge, transpilers, or search/beam/genetic/
constraint synthesis — and simultaneously a **functioning, tested** product.

Those two requirements cannot both be satisfied, and not because of effort. In
Malbolge every code cell is decoded by its **position** and **rewrites itself
after it executes**. For *linear* code (no backward jump) that self-modification
is never observed, so a human can place bytes directly by inverting one equation
per cell. The instant control flow loops back to an already-executed cell — which
*every* parser, comparison, state fold, and HTML renderer needs — the cell now
decodes against its **encrypted** value, coupled across time, the data-pointer
trajectory, and (in Unshackled) **nondeterministic** high trits. That coupled
system is why the first Malbolge "Hello, World!" was *found by search*, and why
every non-trivial Malbolge program in existence is **generator output** — exactly
what the rules forbid. Full reasoning, with a capability table, is in
[`docs/FEASIBILITY.md`](docs/FEASIBILITY.md).

So this repository does the honest maximum:

* It **validates** the documented Malbolge Unshackled interpreter against the
  language spec, and builds a second independent reference interpreter.
* It ships the **complete set of byte-stream primitives that are genuinely
  hand-authorable** in raw Malbolge Unshackled — read a byte, write a byte,
  halt, and fixed-length unrollings — each **executed on two reference
  interpreters** and covered by passing tests.
* It puts a **live Malbolge Unshackled process in a real HTTP request path**
  through a deliberately dumb capability adapter, and tests it end to end.
* It **refuses to fake the rest.** There are **no** stub `router.mu`/`auth.mu`
  files pretending to implement logic they do not. The application gap is
  documented, not hidden. (The project's own rules forbid "mocked behavior",
  "placeholder functions", and "TODO implementations" — honoring them means the
  unbuildable files are absent.)

Everything claimed below actually runs. See the verbatim transcript in
[§ Test output](#test-output).

## What is real here

| Thing | Status |
|---|---|
| Standard Malbolge reference interpreter (Olmstead), compiled | ✅ `runtime/interpreter/malbolge` |
| Malbolge **Unshackled** reference interpreter (Ørjan Johansen), compiled | ✅ `runtime/interpreter/unshackled` |
| Interpreter validated against spec via a known program | ✅ reference cat echoes input |
| Hand-written `halt` (`src/halt.mu`) | ✅ runs, exit 0 |
| Hand-written `print_nul` (`src/print_nul.mu`) | ✅ emits `00` on both engines |
| Hand-written `echo_one_byte` (`src/echo_one_byte.mu`) | ✅ read→write→halt, both engines |
| Hand-written `echo_four_bytes` (`src/echo_four_bytes.mu`) | ✅ fixed-length unroll, both engines |
| Dumb capability adapter (framing only) | ✅ `runtime/capability-adapter/adapter.py` |
| Real HTTP endpoint backed by a **live** Malbolge process | ✅ `tests/integration` |
| Byte-level protocol spec | ✅ `runtime/PROTOCOL.md` |
| Per-file language-semantics companions | ✅ `src/*.semantics.md` |
| Encoding proof (no generated code) | ✅ `tools/verify-encoding.py` |
| Forbidden-language build gate | ✅ `tools/forbidden-language-check` |
| Responsive static CSS | ✅ `static/application.css` |
| nginx + Docker packaging | ✅ `container/`, `docker-compose.yml` |

## What is specified but NOT implemented (and why it is absent, not faked)

Registration, password verification, sessions, CSRF, case/evidence/entity CRUD,
search, pagination, the audit-log fold, server-rendered HTML and escaping — every
feature that requires a **loop or a content-dependent branch** in Malbolge — is
specified in `runtime/PROTOCOL.md` and analysed in `docs/FEASIBILITY.md`, but is
**not** present as working Malbolge, because no human can hand-author looping
Malbolge without the forbidden generators. No placeholder files stand in for it.

The two honest ways to get a *functioning* feature-complete RUSTER, each of which
requires relaxing exactly one stated constraint, are spelled out at the end of
[`docs/FEASIBILITY.md`](docs/FEASIBILITY.md). Pick one and the scope can move
accordingly — but it is a scope decision, not something to paper over.

## Repository layout

```
.
├── README.md                  ← you are here
├── LICENSE                    ← MIT (interpreters: public domain, see PROVENANCE)
├── Makefile                   ← build / test / verify entry points
├── docker-compose.yml
├── container/
│   ├── Dockerfile             ← builds interpreters + adapter, runs tests at build
│   └── nginx.conf             ← unmodified reverse proxy
├── runtime/
│   ├── interpreter/
│   │   ├── malbolge.c         ← standard reference (Olmstead), unmodified semantics
│   │   ├── Unshackled.hs      ← Unshackled reference (Johansen), verbatim
│   │   └── PROVENANCE.md
│   ├── capability-adapter/
│   │   └── adapter.py         ← dumb HTTP↔stdin/stdout framing, NO business logic
│   └── PROTOCOL.md            ← byte-level request/response + event-store spec
├── src/                       ← APPLICATION BYTES — raw Malbolge only
│   ├── halt.mu                + halt.semantics.md
│   ├── print_nul.mu           + print_nul.semantics.md
│   ├── echo_one_byte.mu       + echo_one_byte.semantics.md
│   └── echo_four_bytes.mu     + echo_four_bytes.semantics.md
├── static/application.css
├── fixtures/                  ← test inputs (see tests/cases.tsv)
├── tests/
│   ├── cases.tsv              ← data-driven primitive cases
│   ├── run-tests              ← runs every .mu on both engines, diffs output
│   └── integration            ← real HTTP endpoint + live Malbolge process
├── tools/
│   ├── verify-direct-execution ← proves each .mu is directly interpreter-runnable
│   ├── verify-encoding.py      ← proves each byte was hand-placed (no generation)
│   ├── forbidden-language-check← fails build on conventional-language app code
│   └── make-manifest           ← writes MANIFEST.sha256
└── docs/
    └── FEASIBILITY.md         ← the boundary, proven
```

## Build & run (exact commands)

Prerequisites: `gcc`, `make`, `python3`; for the Unshackled engine also `ghc`
with the `random` and `mtl` packages (`apt-get install -y ghc libghc-random-dev
libghc-mtl-dev`). If `ghc` is absent the build skips the Unshackled binary and
the standard engine still covers the linear primitives identically.

```bash
# 1. Build both reference interpreters
make interpreters

# 2. Run the byte-stream primitive tests on real interpreters
make test                 # -> PASS=12 FAIL=0

# 3. Prove direct execution, hand-encoding, and the forbidden-language gate
make verify

# 4. End-to-end: real HTTP endpoint with a live Malbolge process in the path
bash tests/integration

# 5. Or the whole thing in containers (nginx -> adapter -> Malbolge)
docker compose up --build
curl --data-binary 'ABCD' http://127.0.0.1:8088/case      # -> ABCD

# 6. Regenerate the source hash manifest
make manifest
```

## Test output

Verbatim from this repository (`make test`, `make verify`, `tests/integration`):

```
### tests/run-tests
NAME             PROGRAM                    ENGINE      RESULT  DETAIL
----------------------------------------------------------------------------------------
halt             src/halt.mu                standard    PASS    stdout=<empty>
print_nul        src/print_nul.mu           standard    PASS    stdout=00
print_nul        src/print_nul.mu           unshackled  PASS    stdout=00
echo_one_Z       src/echo_one_byte.mu       standard    PASS    stdout=5a
echo_one_Z       src/echo_one_byte.mu       unshackled  PASS    stdout=5a
echo_one_7       src/echo_one_byte.mu       standard    PASS    stdout=37
echo_one_7       src/echo_one_byte.mu       unshackled  PASS    stdout=37
echo_one_ff      src/echo_one_byte.mu       standard    PASS    stdout=ff
echo_four_ABCD   src/echo_four_bytes.mu     standard    PASS    stdout=41424344
echo_four_ABCD   src/echo_four_bytes.mu     unshackled  PASS    stdout=41424344
echo_four_wxyz   src/echo_four_bytes.mu     standard    PASS    stdout=7778797a
echo_four_wxyz   src/echo_four_bytes.mu     unshackled  PASS    stdout=7778797a

PASS=12 FAIL=0 SKIP=0

### tools/verify-direct-execution
DIRECT EXECUTION VERIFIED: all src/*.mu are accepted and run by the interpreter.

### tools/verify-encoding.py
ALL ENCODINGS VERIFIED (hand-placed bytes decode exactly as declared)

### tools/forbidden-language-check
PASS: application source is raw Malbolge only.

### tests/integration
PASS  POST /case   body='ABCD'  ->  'ABCD'  (via real Malbolge process on runtime/interpreter/unshackled)
PASS  POST /login  body='wxyz'  ->  'wxyz'  (via real Malbolge process on runtime/interpreter/unshackled)
PASS  POST /x      body='1234'  ->  '1234'  (via real Malbolge process on runtime/interpreter/unshackled)
INTEGRATION PASS: HTTP endpoint served responses produced by a live Malbolge Unshackled process.
```

## Proof that no generated Malbolge was used

* Every `src/*.mu` byte is accounted for, cell by cell, by `tools/verify-encoding.py`,
  which shows the decode `XLAT1[(byte-33+pos) mod 94]` and matches it to the
  author-declared instruction stream. The placement rule is the closed form
  `byte = ((index - pos) mod 94) + 33` — direct inversion, no search.
* The programs are **strictly linear**; the companions in `src/*.semantics.md`
  explain per cell why position-dependence and self-modification do not change
  their behaviour.
* The interpreters are third-party references used as an untuned oracle
  (`runtime/interpreter/PROVENANCE.md`); passing tests are evidence the bytes are
  correct Malbolge, not evidence of a bent interpreter.
* `tools/forbidden-language-check` fails the build if any conventional-language
  source appears under `src/`, or if any `.mu` is not valid printable-ASCII
  Malbolge.

## Source manifest

`MANIFEST.sha256` lists the sha256 of every source file. Regenerate and verify:

```bash
make manifest
sha256sum -c MANIFEST.sha256
```

## License

MIT for this repository's own files; the two interpreters are public-domain
third-party references used unmodified in semantics. See `LICENSE` and
`runtime/interpreter/PROVENANCE.md`.
