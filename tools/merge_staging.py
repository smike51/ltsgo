"""Merge agent chunks in kb/staging/<book>/<chunk>/ into one base.

Usage: python -I -X utf8 tools/merge_staging.py [repo_root]
- entities from all books -> kb/staging/_shared/entities.jsonl, deduplicated by wikidata, then by key;
  key renames are applied to every reference (stops, links, mentions, facts, quotes).
- other tables -> kb/staging/<book>/merged/<table>.jsonl
- research/media-<short>.jsonl -> merged/media.jsonl; research/places-<short>.jsonl -> merged/places.jsonl
- checks: every quote with passage_seq is a substring of that passage body; dangling keys.
Writes kb/staging/REPORT.md. Nothing here changes statuses — they stay proposals.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "kb", "staging")
BOOKS = {"karamzin-letters": "karamzin", "goncharov-pallada": "goncharov"}
TABLES = ["stops", "entity_links", "mentions", "facts", "quotes", "sources"]
REF_FIELDS = {"stops": ["place_key"], "entity_links": ["from_key", "to_key"], "mentions": ["entity_key"],
              "facts": ["entity_key"], "quotes": [], "sources": []}
STATUS_RANK = {"verified_source": 4, "verified_wiki": 3, "disputed": 2, "book_only": 1, "unverified": 0}


def read_jsonl(path, problems):
    rows = []
    if not os.path.exists(path):
        return rows
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            problems.append(f"bad json {os.path.relpath(path, ROOT)}:{n}: {e}")
    return rows


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def merge_entity(a, b):
    """keep the better-status row, fill empty fields from the other, union names_then and meta"""
    if STATUS_RANK.get(b.get("status"), 0) > STATUS_RANK.get(a.get("status"), 0):
        a, b = b, a
    out = dict(a)
    for k, v in b.items():
        if out.get(k) in (None, "", [], {}):
            out[k] = v
    seen, names = set(), []
    for n in (a.get("names_then") or []) + (b.get("names_then") or []):
        t = json.dumps(n, ensure_ascii=False, sort_keys=True)
        if t not in seen:
            seen.add(t)
            names.append(n)
    out["names_then"] = names
    out["meta"] = {**(b.get("meta") or {}), **(a.get("meta") or {})}
    by = {x for x in (str(a.get("created_by", "")), str(b.get("created_by", ""))) if x}
    out["created_by"] = ", ".join(sorted(by))
    return out


def main():
    problems = []
    all_entities, per_book = [], {}
    for book in BOOKS:
        bdir = os.path.join(ST, book)
        chunks = sorted(d for d in os.listdir(bdir) if os.path.isdir(os.path.join(bdir, d)) and d != "merged") \
            if os.path.isdir(bdir) else []
        tabs = defaultdict(list)
        for ch in chunks:
            for e in read_jsonl(os.path.join(bdir, ch, "entities.jsonl"), problems):
                e.setdefault("meta", {})["chunk"] = f"{book}/{ch}"
                all_entities.append(e)
            for t in TABLES:
                for r in read_jsonl(os.path.join(bdir, ch, f"{t}.jsonl"), problems):
                    r["_chunk"] = ch
                    tabs[t].append(r)
        per_book[book] = (chunks, tabs)

    # dedupe entities: wikidata first, then key
    rename, by_wd, by_key = {}, {}, {}
    kind_fix = {"organization": "organisation", "object": "artwork"}  # schema enum
    for e in all_entities:
        if e.get("kind") in kind_fix:
            e.setdefault("meta", {})["kind_was"] = e["kind"]
            e["kind"] = kind_fix[e["kind"]]
        k, wd = e.get("key"), (e.get("wikidata") or "").strip() or None
        if not k:
            problems.append(f"entity without key: {norm(json.dumps(e, ensure_ascii=False))[:120]}")
            continue
        target = by_wd.get(wd) if wd else None
        if target is None and k in by_key:
            target = by_key[k]
            if wd and by_key[k].get("wikidata") and by_key[k]["wikidata"] != wd:
                problems.append(f"key clash {k}: {by_key[k]['wikidata']} vs {wd} — kept apart as {k}--{wd}")
                e["key"] = f"{k}--{wd}"
                rename[(e["meta"]["chunk"], k)] = e["key"]
                target = None
        if target is None:
            by_key[e["key"]] = e
            if wd:
                by_wd[wd] = e
            continue
        merged = merge_entity(target, e)
        canon = target["key"]
        merged["key"] = canon
        if k != canon:
            rename[(e["meta"]["chunk"], k)] = canon
        by_key[canon] = merged
        for w, ent in list(by_wd.items()):
            if ent is target:
                by_wd[w] = merged
        if wd:
            by_wd[wd] = merged
    entities = sorted(by_key.values(), key=lambda e: (e.get("kind", ""), e["key"]))
    for e in entities:
        e.get("meta", {}).pop("chunk", None)
    keys = {e["key"] for e in entities}
    write_jsonl(os.path.join(ST, "_shared", "entities.jsonl"), entities)

    report = ["# Сводка базы (kb/staging)", "", f"Сущностей всего: **{len(entities)}** — " +
              ", ".join(f"{k}: {v}" for k, v in Counter(e.get("kind") for e in entities).most_common()),
              f"С Wikidata: {sum(1 for e in entities if e.get('wikidata'))}; статусы: " +
              ", ".join(f"{k}: {v}" for k, v in Counter(e.get("status") for e in entities).most_common()), ""]

    for book, short in BOOKS.items():
        chunks, tabs = per_book[book]
        passages = {}
        p = os.path.join(ROOT, "texts", book, "passages.jsonl")
        for r in read_jsonl(p, problems):
            passages[r["seq"]] = norm(r["body"])
        out_dir = os.path.join(ST, book, "merged")
        bad_quotes, dangling = 0, Counter()
        for t in TABLES:
            rows = []
            for r in tabs[t]:
                ch = r.pop("_chunk")
                for f in REF_FIELDS[t]:
                    if r.get(f):
                        r[f] = rename.get((f"{book}/{ch}", r[f]), r[f])
                        if r[f] not in keys:
                            dangling[f"{t}.{f}"] += 1
                if t == "quotes":
                    r["entity_keys"] = [rename.get((f"{book}/{ch}", k), k) for k in r.get("entity_keys") or []]
                qtext = r.get("text") if t == "quotes" else r.get("quote")
                seq = r.get("passage_seq") or r.get("passage_from")
                if t in ("quotes", "facts", "entity_links") and qtext and seq and not r.get("source_url"):
                    ok = norm(qtext) in passages.get(seq, "")
                    r["quote_ok"] = ok
                    bad_quotes += 0 if ok else 1
                rows.append(r)
            if t == "stops":
                rows.sort(key=lambda r: (r.get("passage_from") or 0, r.get("seq_hint") or 0))
            if t == "sources":
                rows = list({r.get("url"): r for r in rows}.values())
            write_jsonl(os.path.join(out_dir, f"{t}.jsonl"), rows)
            tabs[t] = rows
        extra = {}
        for kind in ("media", "places"):
            src = os.path.join(ROOT, "research", f"{kind}-{short}.jsonl")
            rows = read_jsonl(src, problems)
            if rows:
                write_jsonl(os.path.join(out_dir, f"{kind}.jsonl"), rows)
            extra[kind] = rows
        lic = Counter((r.get("licence") or "НЕТ") for r in extra["media"])
        report += [f"## {book}", f"куски: {', '.join(chunks) or '—'}",
                   "", "| таблица | строк |", "|---|---|"]
        report += [f"| {t} | {len(tabs[t])} |" for t in TABLES]
        report += [f"| media (research) | {len(extra['media'])} |", f"| places (research) | {len(extra['places'])} |", ""]
        report.append(f"Цитаты не найдены в тексте: **{bad_quotes}**" + (" (поле quote_ok=false)" if bad_quotes else ""))
        if dangling:
            report.append("Ссылки на несуществующие ключи: " + ", ".join(f"{k}: {v}" for k, v in dangling.items()))
        if extra["media"]:
            report.append("Лицензии медиа: " + ", ".join(f"{k}: {v}" for k, v in lic.most_common()))
        report.append("")
    if problems:
        report += ["## Проблемы", ""] + [f"- {p}" for p in problems[:200]]
    open(os.path.join(ST, "REPORT.md"), "w", encoding="utf-8", newline="\n").write("\n".join(report) + "\n")
    print("\n".join(report[:6]))
    print(f"problems: {len(problems)}; report: kb/staging/REPORT.md")


if __name__ == "__main__":
    main()
