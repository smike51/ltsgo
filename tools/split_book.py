"""Split a clean book text into passages (letters / chapters) for kb.passages.

Usage: python -I tools/split_book.py <profile> <full.txt> <out_dir>
  profile: karamzin-letters | goncharov-pallada
Writes <out_dir>/text.txt (author text only, editorial apparatus cut off)
and <out_dir>/passages.jsonl  {seq, part, heading, date_in_text, body}.
Heading detection is heuristic — the result is a draft for human review.
"""
import json
import re
import sys

MONTH = r"(январ|феврал|март|апрел|ма[яй]|июн|июл|август|сентябр|октябр|ноябр|декабр)"
TIME = r"(час\w* (утра|вечера|ночи|пополудни)|полночь|ночью|дорогою)"


def karamzin(lines):
    # cut the 1964 editorial commentary (© — not ours to publish)
    end = next(i for i, l in enumerate(lines) if l.strip() == "КОММЕНТАРИИ")
    lines = lines[:end]
    paras = [p for p in lines if p.strip()]
    out, cur = [], None

    def is_heading(i):
        p = paras[i].strip()
        if len(p) > 60 or "\n" in p or re.search(r"[,;:!?]$", p):
            return False
        prev = paras[i - 1].strip() if i else ""
        nxt = paras[i + 1].strip() if i + 1 < len(paras) else ""
        prose_around = len(nxt) > 120 and (len(prev) > 120 or i < 12)
        if re.search(MONTH, p, re.I) or re.search(TIME, p, re.I):
            return prose_around or bool(re.search(r"17[89]\d", p))
        # bare place name: "Базель", "Корчма", "Долина Гасли"
        if re.fullmatch(r"[А-ЯЁ][а-яё.-]+( [А-ЯЁа-яё.-]+){0,3}\.?", p) and p not in ("Вольтер",):
            return prose_around
        return False

    preface = []
    for i, p in enumerate(paras):
        if i < 3:  # title lines
            continue
        if is_heading(i) and p.strip() != "1793":
            cur = {"part": None, "heading": p.strip(), "body": []}
            out.append(cur)
        elif cur is None:
            preface.append(p)
        else:
            cur["body"].append(p)
    pre = [x for x in preface if not x.startswith(("Воспроизводится", "Оригинал на"))]
    passages = [{"part": "Предисловие ко 2-му изданию", "heading": "Предисловие", "body": pre}] + out
    for ps in passages:
        m = re.search(r"\d.*", ps["heading"])
        ps["date_in_text"] = ps["heading"] if re.search(MONTH + "|" + TIME + r"|17[89]\d", ps["heading"], re.I) else None
    text = "\n\n".join(paras[3:])
    text = re.sub(r"^Воспроизводится.*\n\n|^Оригинал на.*\n\n", "", text, flags=re.M)
    return passages, text


def goncharov(lines):
    txt = "\n".join(lines)
    # drop the editor's "Впервые опубликовано" blocks (they sit between volumes and at the end)
    txt = re.sub(r"Впервые опубликовано:.*?(?=\n\nИ\. ?А\. Гончаров|\Z)", "", txt, flags=re.S)
    paras = [p.strip() for p in txt.split("\n") if p.strip()]
    passages, cur, vol = [], None, "Том I"
    for p in paras:
        if p in ("Том I", "Том II"):
            vol = p
            continue
        if re.fullmatch(r"[IVX]+\. [А-ЯЁ\"«» ,.\-–—]+", p) or re.fullmatch(r"ЧЕРЕЗ ДВАДЦАТЬ ЛЕТ\*?", p) \
                or p.startswith("Предисловие автора"):
            cur = {"part": vol, "heading": p.rstrip("*"), "date_in_text": None, "body": []}
            passages.append(cur)
        elif cur is not None and p not in ("И.А. Гончаров", "И. А. Гончаров", 'Фрегат "Паллада"',
                                           "Очерки путешествия в двух томах"):
            cur["body"].append(p)
    return passages, txt.strip() + "\n"


if __name__ == "__main__":
    profile, src, out_dir = sys.argv[1:]
    lines = open(src, encoding="utf-8").read().splitlines()
    passages, text = {"karamzin-letters": karamzin, "goncharov-pallada": goncharov}[profile](lines)
    open(f"{out_dir}/text.txt", "w", encoding="utf-8", newline="\n").write(text)
    with open(f"{out_dir}/passages.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for seq, ps in enumerate(passages, 1):
            body = "\n\n".join(ps["body"])
            f.write(json.dumps({"seq": seq, "part": ps["part"], "heading": ps["heading"],
                                "date_in_text": ps["date_in_text"], "chars": len(body), "body": body},
                               ensure_ascii=False) + "\n")
    print(profile, len(passages), "passages,", len(text), "chars")
