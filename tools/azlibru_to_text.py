"""az.lib.ru .shtml (cp1251) -> clean UTF-8 text.

Usage: python -I tools/azlibru_to_text.py <in.shtml> [<in2.shtml> ...] <out.txt>
Takes the body between <!--Section Begins--> and <!--Section Ends-->,
strips tags, decodes entities, keeps one paragraph per line.
"""
import html
import re
import sys


def body(path):
    raw = open(path, "rb").read().decode("cp1251", errors="replace")
    m = re.search(r"<!--Section Begins-->(.*)<!--Section Ends-->", raw, re.S)
    if not m:
        raise SystemExit(f"no Section markers in {path}")
    s = m.group(1)
    s = re.sub(r"(?i)<br\s*/?>|<dd>|</?p[^>]*>|</?h\d[^>]*>|</?div[^>]*>|<li>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in s.splitlines()]
    out, blank = [], False
    for ln in lines:
        if ln:
            out.append(ln)
            blank = False
        elif not blank and out:
            out.append("")
            blank = True
    return "\n".join(out).strip() + "\n"


if __name__ == "__main__":
    *ins, dst = sys.argv[1:]
    text = "\n\n".join(body(p) for p in ins)
    open(dst, "w", encoding="utf-8", newline="\n").write(text)
    print(dst, len(text), "chars")
