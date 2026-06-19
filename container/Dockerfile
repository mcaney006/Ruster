# RUSTER container — builds the permitted non-Malbolge components (the two
# unmodified interpreters and the dumb adapter) and runs the demo endpoint.
# No application logic is built here; src/*.mu is executed, never compiled.

FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc ghc libghc-random-dev libghc-mtl-dev \
        python3 ca-certificates curl make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Build interpreters (Malbolge reference in C, Unshackled reference in Haskell).
RUN make interpreters

# Sanity: run the byte-stream primitive tests at build time. Build fails if the
# hand-written Malbolge does not execute correctly.
RUN bash tests/run-tests && bash tools/verify-direct-execution \
    && python3 tools/verify-encoding.py && bash tools/forbidden-language-check

ENV RUSTER_PORT=8080 \
    RUSTER_INTERP=runtime/interpreter/unshackled \
    RUSTER_PROGRAM=src/echo_four_bytes.mu \
    RUSTER_MODE=body

EXPOSE 8080
CMD ["python3", "runtime/capability-adapter/adapter.py"]
