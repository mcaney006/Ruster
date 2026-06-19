#!/usr/bin/env python3
"""
RUSTER capability adapter — minimal, dumb transport bridge.

PERMITTED non-Malbolge component (see project rules: "A minimal runtime
capability adapter"). It contains NO business logic. Specifically it does NOT
route, authenticate, authorize, validate (beyond a transport byte cap),
render HTML, make session decisions, run application queries, or make
password/case-management decisions. It only:

  * converts an inbound HTTP request into a byte stream,
  * writes that byte stream to a Malbolge process's stdin,
  * returns the Malbolge process's stdout as the HTTP response body.

The Malbolge program is chosen by environment, not by the adapter inspecting
the request:

  RUSTER_INTERP   path to an unmodified Malbolge interpreter
                  (default: runtime/interpreter/malbolge)
  RUSTER_PROGRAM  path to a .mu program (default: src/echo_four_bytes.mu)
  RUSTER_PORT     listen port (default: 8080)
  RUSTER_MAXBODY  transport byte cap (default: 1048576)
  RUSTER_MODE     "body"  -> write the raw request body to stdin (demo: lets the
                            hand-written echo primitive round-trip end-to-end)
                  "frame" -> write the canonical REQUEST frame of PROTOCOL.md §1
                            (the contract a complete application would consume)

This file is deliberately tiny and generic. All meaning lives on the Malbolge
side; here there is only framing.
"""
import os, sys, subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

INTERP  = os.environ.get("RUSTER_INTERP",  "runtime/interpreter/malbolge")
PROGRAM = os.environ.get("RUSTER_PROGRAM", "src/echo_four_bytes.mu")
PORT    = int(os.environ.get("RUSTER_PORT", "8080"))
MAXBODY = int(os.environ.get("RUSTER_MAXBODY", str(1024 * 1024)))
MODE    = os.environ.get("RUSTER_MODE", "body")
TIMEOUT = float(os.environ.get("RUSTER_TIMEOUT", "10"))


def canonical_frame(method, path, query, headers, body):
    """Build the PROTOCOL.md §1 REQUEST frame as raw bytes (no interpretation)."""
    def lp(b):  # length-prefixed: "<len>\n<bytes>"
        if isinstance(b, str):
            b = b.encode("utf-8", "surrogateescape")
        return str(len(b)).encode() + b"\n" + b
    out = bytearray(b"REQUEST\n")
    out += lp(method); out += lp(path); out += lp(query)
    out += str(len(headers)).encode() + b"\n"
    for k, v in headers:
        out += lp(k.lower()); out += lp(v)
    out += lp(body)
    out += b"END_REQUEST\n"
    return bytes(out)


def run_malbolge(stdin_bytes):
    """Spawn the interpreter on the configured program; pipe bytes through."""
    proc = subprocess.run(
        [INTERP, PROGRAM],
        input=stdin_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=TIMEOUT,
    )
    return proc.stdout


class Handler(BaseHTTPRequestHandler):
    server_version = "ruster-adapter/0"

    def _handle(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > MAXBODY:
            self.send_response(413); self.end_headers()
            self.wfile.write(b"payload too large\n"); return
        body = self.rfile.read(length) if length else b""
        if MODE == "frame":
            stdin_bytes = canonical_frame(
                self.command, self.path.split("?", 1)[0],
                (self.path.split("?", 1)[1] if "?" in self.path else ""),
                list(self.headers.items()), body)
        else:
            stdin_bytes = body
        try:
            out = run_malbolge(stdin_bytes)
        except subprocess.TimeoutExpired:
            self.send_response(504); self.end_headers()
            self.wfile.write(b"malbolge process timed out\n"); return
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    do_GET = _handle
    do_POST = _handle
    do_PUT = _handle

    def log_message(self, *a):  # quiet
        pass


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    sys.stderr.write(
        f"ruster-adapter listening on 127.0.0.1:{PORT} "
        f"interp={INTERP} program={PROGRAM} mode={MODE}\n")
    sys.stderr.flush()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
