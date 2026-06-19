# RUSTER — build & verification entry points.
#
# The only compiled artifacts are the two *interpreters* (permitted non-Malbolge
# components). The application bytes live in src/*.mu and are executed, never
# compiled.

CC      ?= gcc
CFLAGS  ?= -O2 -Wall
GHC     ?= ghc
GHCFLAGS?= -O0 -XNondecreasingIndentation

STD_SRC := runtime/interpreter/malbolge.c
STD_BIN := runtime/interpreter/malbolge
UNS_SRC := runtime/interpreter/Unshackled.hs
UNS_BIN := runtime/interpreter/unshackled

.PHONY: all interpreters std uns test verify verify-exec verify-encoding manifest forbidden-check clean

all: interpreters test verify

interpreters: std uns

std: $(STD_BIN)
$(STD_BIN): $(STD_SRC)
	$(CC) $(CFLAGS) -o $@ $<

# The Unshackled reference is Haskell; build it if a Haskell toolchain exists,
# otherwise skip gracefully (standard interpreter still covers the linear
# primitives identically).
uns:
	@if command -v $(GHC) >/dev/null 2>&1; then \
	  echo "building Unshackled reference..."; \
	  $(GHC) $(GHCFLAGS) -o $(UNS_BIN) $(UNS_SRC) || echo "ghc build failed (random/mtl missing?)"; \
	else \
	  echo "ghc not found; skipping Unshackled interpreter (standard engine suffices for linear primitives)"; \
	fi

test: std
	@bash tests/run-tests

verify: verify-exec verify-encoding forbidden-check

verify-exec: std
	@bash tools/verify-direct-execution

verify-encoding:
	@python3 tools/verify-encoding.py

# Fails the build if any forbidden-language *application* source is present.
forbidden-check:
	@bash tools/forbidden-language-check

manifest:
	@bash tools/make-manifest > MANIFEST.sha256 && echo "wrote MANIFEST.sha256"

clean:
	rm -f $(STD_BIN) $(UNS_BIN) runtime/interpreter/*.o runtime/interpreter/*.hi
