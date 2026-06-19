# Interpreter provenance

Both interpreters are pre-existing, third-party reference implementations used
unmodified in semantics. They are the "existing, unmodified Malbolge Unshackled
interpreter" permitted by the project rules. They were fetched from public
sources during the build of this repository, not written here.

## `malbolge.c` — standard Malbolge reference (Ben Olmstead, 1998)

* Source: the canonical public-domain reference interpreter (as mirrored by the
  Try It Online project, `https://github.com/TryItOnline/malbolge`).
* Author placed it in the public domain.
* **Only change:** the non-portable `#include <malloc.h>` line was wrapped in a
  platform guard so it compiles on modern Linux/macOS. No interpreter logic,
  table, or arithmetic was altered. Diff is limited to the include block.

## `Unshackled.hs` — Malbolge Unshackled reference (Ørjan Johansen, 2007–)

* Source: `http://oerjan.nvg.org/esoteric/Unshackled.hs`.
* Author placed it in the public domain.
* **No source change.** GHC 9.4 removed the implicit `NondecreasingIndentation`
  rule the program relies on, so it is compiled with the *compiler flag*
  `-XNondecreasingIndentation` (see `Makefile`). The `.hs` bytes are verbatim.

## Why this matters for the project's claims

The interpreters are the *trusted oracle*. RUSTER's Malbolge programs in `src/`
were validated by running them through these unmodified engines (see
`tests/run-tests`). Because the engines are third-party references and were not
tuned to accept our programs, a passing test is genuine evidence the `.mu`
bytes are correct Malbolge — not evidence that an interpreter was bent to fit.

No Malbolge **source** in this repository was generated, assembled, normalized,
transpiled, or search-synthesized. The interpreters are tools; the `src/*.mu`
bytes were hand-placed by inverting the decode equation (see
`tools/verify-encoding.py` and the `src/*.semantics.md` companions).
