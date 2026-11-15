# kb/staging — база до сервера

Сервера `ltsgo-kb` ещё нет, поэтому база собирается здесь: JSONL-файлы по таблицам схемы
`kb/migrations/001_init.sql`. Связи — по строковым ключам (`key`), а не по id. Всё здесь —
**предложения** (правило 2): статусы ставит человек, при загрузке в Postgres каждая строка
становится `change_proposals`.

## Папки
`kb/staging/<book>/<chunk>/` — результат одного агента (например `karamzin-letters/p001-076/`).
После всех агентов `tools/merge_staging.py` сводит куски в `kb/staging/<book>/merged/`
и общий `kb/staging/_shared/entities.jsonl` (люди и места общие для всех книг).

## Файлы и поля (одна строка = один объект)
- `entities.jsonl` — `{key, kind, wikidata, name:{ru,en}, names_then:[{name,lang,until}], parent_key,
  lat, lon, geo_precision, born, died, starts, ends, preservation, status, meta, created_by}`
  - `kind`: person | place | building | event | artwork | organisation | vessel
  - `key`: латиница, kebab-case, однозначно: `kant`, `koenigsberg`, `hotel-de-bretagne-paris`, `frigate-pallada`.
    Если есть Wikidata — `wikidata` обязателен (по нему сливаются дубли между кусками).
  - `status`: verified_wiki (сверено с Wikidata/Википедией) | book_only | unverified | disputed
- `stops.jsonl` — `{journey_key, seq_hint, place_key, arrived, departed, calendar, date_precision,
  date_in_text, transport_in, passage_from, passage_to, kind (stay|pass|mention_only), status, note}`
  - `passage_*` = `seq` из `texts/<book>/passages.jsonl`; даты ISO в календаре путешествия.
- `entity_links.jsonl` — `{from_key, to_key, kind (met|stayed_at|saw|visited|located_in|took_part|
  portrait_of|host_of|travelled_with), passage_seq, during, status, quote, note}`
- `mentions.jsonl` — `{passage_seq, entity_key, surface}` — как назван в тексте.
- `facts.jsonl` — `{entity_key | stop_ref | book_key, key, layer (then|now|go), lang, value,
  fact_class (history|identity|preservation|visit|transport|trivia), status, source_url,
  source_title, passage_seq, quote, note, created_by}`
  - факт без `quote` (дословно из книги или источника) не пишем; для книги — `passage_seq` + цитата
    из `body`; для источника под охраной — цитата ≤ 15 слов.
- `quotes.jsonl` — `{passage_seq, text, stop_ref, entity_keys:[], tags:[]}` — яркие места для сайта;
  `text` — точная подстрока `body` (проверит код), 1–3 предложения.
- `sources.jsonl` — `{url, title, publisher, tier (primary|secondary), lang, licence}`.

Медиа и адреса собираются отдельно: `research/media-*.jsonl`, `research/places-*.jsonl` —
merge переносит их в `media.jsonl` и `entities`/`entity_links`.

## Путешествия (journeys)
- `karamzin-1789` — Карамзин, юлианский календарь, май 1789 – июль 1790.
- `goncharov-1852` — Гончаров на «Палладе» и сушей через Сибирь, юлианский, окт. 1852 – февр. 1855.
- Другие участники («Паллада»: Путятин, Посьет, Унковский, Гошкевич, Можайский…) — люди (`person`),
  связи `travelled_with`; свои journeys — позже, если понадобятся.
