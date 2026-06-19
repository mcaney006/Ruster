# RUSTER byte-level protocol

This document specifies the canonical byte stream exchanged between the runtime
capability adapter and the Malbolge process, plus the on-disk event-store
record format. It is a **specification**; the implementation-status of each
section against the current `src/` tree is stated explicitly in
`docs/FEASIBILITY.md` and summarised in `README.md`. Nothing in this file is
claimed to be implemented in handwritten Malbolge unless `README.md` says so.

The design goal of the protocol is that the adapter stays *dumb*: it performs no
routing, auth, validation, rendering, or persistence policy. It only frames
bytes. Every decision lives on the Malbolge side.

All integers are unsigned ASCII-decimal unless stated otherwise, each on its own
line terminated by a single `\n` (0x0A). "Length" always counts bytes of the
payload that follows, so the reader never needs to scan for a delimiter inside
binary data.

## 1. Request frame (adapter → Malbolge, on stdin)

```
REQUEST\n
<METHOD_LENGTH>\n
<METHOD bytes>
<PATH_LENGTH>\n
<PATH bytes>
<QUERY_LENGTH>\n
<QUERY bytes>
<HEADER_COUNT>\n
( <NAME_LENGTH>\n <NAME bytes> <VALUE_LENGTH>\n <VALUE bytes> ) * HEADER_COUNT
<BODY_LENGTH>\n
<BODY bytes>
END_REQUEST\n
```

* `METHOD` is the raw HTTP method (`GET`, `POST`, …).
* `PATH` is the percent-encoded path exactly as received (decoding is the
  Malbolge side's job — see `encoding` responsibilities).
* `QUERY` is the raw query string without the leading `?`.
* Header names are lower-cased by the adapter only as a byte transform
  (no semantic interpretation).
* `BODY_LENGTH` is authoritative; the adapter never forwards more than the
  configured maximum (`MAX_BODY`, default 1 MiB) and emits a truncated frame the
  Malbolge side must reject.

## 2. Response frame (Malbolge → adapter, on stdout)

```
STATUS <code>\n
( HEADER <NAME_LENGTH> <NAME> <VALUE_LENGTH> <VALUE>\n ) *
BODY <LENGTH>\n
<body bytes>
END_RESPONSE\n
```

* `<code>` is a 3-digit HTTP status.
* Header tokens are length-prefixed so values may contain spaces.
* The adapter copies these verbatim into a real HTTP response; it does not add,
  remove, or reorder semantic headers (it may add only hop-by-hop framing such
  as `Content-Length` recomputed from `BODY LENGTH`).

## 3. Persistence capability (opaque, adapter ↔ store)

The adapter exposes four opaque operations over the same length-prefixed
convention. It treats every blob as **uninterpreted bytes** — it does not parse
event types or fields.

```
PUT  <KEY_LEN>\n <KEY> <VAL_LEN>\n <VAL>      -> OK\n | ERR\n
GET  <KEY_LEN>\n <KEY>                        -> VAL <LEN>\n <bytes> | NONE\n
APPEND <STREAM_LEN>\n <STREAM> <VAL_LEN>\n <VAL> -> SEQ <n>\n
SCAN <STREAM_LEN>\n <STREAM> <FROM_SEQ>\n     -> ( REC <LEN>\n <bytes> )* END\n
```

`APPEND`/`SCAN` implement the append-only event log; `SEQ` is a monotonically
increasing per-stream sequence number. The store guarantees durability and
ordering only; all meaning is imposed by the Malbolge replay logic.

## 4. Crypto & entropy capability (opaque)

```
HASH <LEN>\n <input>            -> DIGEST <LEN>\n <bytes>
VERIFY <LEN>\n <input> <LEN>\n <digest> -> YES\n | NO\n
RANDOM <n>\n                    -> RAND <n>\n <bytes>
TIME                           -> TIME <unix_seconds>\n
```

These are generic primitives. Password policy, token shape, session lifetime,
and CSRF semantics are **not** encoded here — they belong to the Malbolge side.

## 5. Event-store record format (Malbolge-defined)

Each `APPEND`ed blob is a length-prefixed binary record the Malbolge program
serialises and deserialises itself:

```
MAGIC   : 4 bytes  "RST1"
TYPE    : 1 byte   (see table)
SEQ     : 8 bytes  big-endian
TS      : 8 bytes  big-endian unix seconds (from TIME capability)
PAYLOAD_LEN : 4 bytes big-endian
PAYLOAD : PAYLOAD_LEN bytes (type-specific, length-prefixed fields)
CRC32   : 4 bytes big-endian over MAGIC..PAYLOAD
```

Event `TYPE` codes:

| code | event |
|---:|:--|
| 0x01 | USER_REGISTERED |
| 0x02 | SESSION_CREATED |
| 0x03 | SESSION_REVOKED |
| 0x10 | CASE_CREATED |
| 0x11 | CASE_UPDATED |
| 0x12 | CASE_DELETED |
| 0x20 | EVIDENCE_ADDED |
| 0x30 | ENTITY_ADDED |
| 0x31 | RELATIONSHIP_ADDED |
| 0x40 | AUDIT_EVENT_RECORDED |

State is reconstructed by `SCAN`ning a stream from sequence 0, verifying each
record's CRC, rejecting malformed/short records, and folding valid events into
the in-memory projection. Authorization is checked **before** any mutating event
is `APPEND`ed.

## 6. Implemented vs specified

The byte-stream **transport primitives** of §1–§2 (read a length-prefixed field
from stdin; write a length-prefixed field to stdout; halt) are the operations
demonstrated by the handwritten programs in `src/` and exercised by
`tests/run-tests`. The higher-level framing, the event-store fold (§5), and the
capability semantics (§3–§4) are specified here but, per `docs/FEASIBILITY.md`,
are **not** implementable as handwritten, generator-free Malbolge and are not
present as working code. They are documented so the boundary is unambiguous.
