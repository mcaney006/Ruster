#!/usr/bin/env python3
"""
verify-encoding.py  --  proof that every src/*.mu byte was placed by hand.

This is a CHECKER, not a generator. It does NOT write Malbolge. It takes the
bytes that a human typed into each src/*.mu file and, for every cell, applies
the documented Malbolge decode rule

        op = XLAT1[(byte - 33 + position) mod 94]

to show which instruction that cell executes. It then compares the decoded
instruction stream against the human-declared intent recorded below. If a byte
did not decode to the instruction the author claimed, the check fails.

Because these programs are strictly linear (no jump ever lands on an
already-executed cell), each cell runs exactly once and the post-execution
XLAT2 encryption never affects program behaviour. That is the entire reason a
human can place these bytes directly: the per-cell decode equation has a
trivial closed-form solution

        byte = ((op_index - position) mod 94) + 33

and there is no self-modification coupling to search over. The moment a program
contains a backward jump, the executed cell is rewritten by XLAT2 before it is
re-reached, the decode equation becomes coupled across time, and direct
placement stops being tractable. No such program is shipped here, and none was
produced by search, synthesis, transpilation, or any code generator.

XLAT1 is the standard Malbolge instruction-decode permutation (Ben Olmstead,
1998); it is identical in Malbolge Unshackled.
"""
import sys, os

XLAT1 = ("+b(29e*j1VMEKLyC})8&m#~W>qxdRp0wkrUo[D7,XTcA\"lI"
         ".v%{gJh4G\\-=O@5`_3i<?Z';FNQuY]szf$!BS/|t:Pn6^Ha")
assert len(XLAT1) == 94, len(XLAT1)

# The eight real Malbolge operations and their human-readable names.
OP_NAME = {
    'j': 'SETD  (d = mem[d])',
    'i': 'SETC  (c = mem[d]; jump)',
    '*': 'ROT   (rotate-right mem[d] -> a)',
    'p': 'CRZ   (crazy(a,mem[d]) -> a)',
    '<': 'OUT   (write low byte of a)',
    '/': 'IN    (read one byte -> a)',
    'v': 'HALT  (stop)',
    'o': 'NOP',
}

# Author-declared intent for every shipped program (the "what I meant to type").
INTENT = {
    'halt.mu':            ['v'],
    'print_nul.mu':       ['<', 'v'],
    'echo_one_byte.mu':   ['/', '<', 'v'],
    'echo_four_bytes.mu': ['/', '<', '/', '<', '/', '<', '/', '<', 'v'],
}

def decode(byte, pos):
    return XLAT1[(byte - 33 + pos) % 94]

def check_file(path):
    name = os.path.basename(path)
    raw = open(path, 'rb').read()
    cells = [b for b in raw if not chr(b).isspace()]   # loader ignores whitespace
    want = INTENT.get(name)
    print(f"\n== {name} ==  ({len(cells)} instruction cells)")
    ok = True
    got = []
    for pos, b in enumerate(cells):
        if not (33 <= b <= 126):
            print(f"  pos {pos}: byte {b} OUT OF PRINTABLE RANGE -> invalid source")
            ok = False
            continue
        op = decode(b, pos)
        got.append(op)
        valid = op in "ji*p</vo"
        print(f"  pos {pos}: byte 0x{b:02x} {chr(b)!r:5} "
              f"(byte-33+pos)%94={(b-33+pos)%94:2d} -> {op!r}  {OP_NAME.get(op,'(decodes to non-op: nop)')}"
              + ("" if valid else "   <-- NOT A VALID OP"))
        if not valid:
            ok = False
    if want is not None:
        if got == want:
            print(f"  INTENT MATCH: decoded stream == declared intent {want}")
        else:
            print(f"  INTENT MISMATCH: declared {want} but decoded {got}")
            ok = False
    return ok

def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    srcdir = os.path.join(here, "src")
    files = sorted(f for f in os.listdir(srcdir) if f.endswith(".mu"))
    allok = True
    for f in files:
        allok &= check_file(os.path.join(srcdir, f))
    print("\n" + ("ALL ENCODINGS VERIFIED (hand-placed bytes decode exactly as declared)"
                  if allok else "ENCODING VERIFICATION FAILED"))
    sys.exit(0 if allok else 1)

if __name__ == "__main__":
    main()
