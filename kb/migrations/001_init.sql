-- LTSGO knowledge base, stage 1 (2026-11-08). See ../../ARCHITECTURE.md.
-- Pattern: onpoint-casa/kb/migrations/001_init.sql (facts with source + verbatim quote, review, history).
-- Writes go through ltsgo-kb only. Agents and models write change_proposals; a person approves.
--
-- Shape:
--   books ─ book_texts ─ passages            (the text itself, split into letters/chapters/paragraphs)
--   books ─ journeys ─ stops ─ entities      (the route: who went where and when)
--   entities (person|place|building|event|artwork|organisation|vessel)  ─ entity_links
--   mentions  (passage ↔ entity)   quotes (curated passages)   facts (everything else, with layer then|now|go)
--   media     (then/now pictures, maps, later AI video/audio)  offers (hotels, tours, tickets — monetisation)

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------- sources (same as onpoint) ----------
CREATE TABLE sources (
  id            serial PRIMARY KEY,
  url           text NOT NULL UNIQUE,
  title         text,
  publisher     text,                     -- 'Wikidata', 'ru.wikipedia', 'Wikisource', 'Gallica', 'museum site'
  tier          text NOT NULL DEFAULT 'secondary'
                CHECK (tier IN ('primary','scholarly','official','wiki','secondary','snippet','dataset')),
  lang          text,
  licence       text,                     -- 'PD', 'CC BY-SA 4.0', ...
  monitor       text NOT NULL DEFAULT 'none' CHECK (monitor IN ('none','hash','rss','api','dataset')),
  check_every   interval,
  last_fetched  timestamptz,
  last_hash     text,
  last_status   int,
  blocked_since timestamptz,
  notes         text
);

CREATE TABLE source_snapshots (
  id           bigserial PRIMARY KEY,
  source_id    int NOT NULL REFERENCES sources(id),
  fetched_at   timestamptz NOT NULL DEFAULT now(),
  http_status  int,
  hash         text,
  text_excerpt text
);

-- ---------- books and their texts ----------
CREATE TABLE books (
  id            serial PRIMARY KEY,
  key           text NOT NULL UNIQUE,     -- 'karamzin-letters', 'polo-devisement', 'verne-80-days'
  title         jsonb NOT NULL,           -- {"ru": "...", "en": "...", "orig": "..."}
  author_id     int,                      -- -> entities(id), set after entities exist
  orig_lang     text NOT NULL,
  written_from  int, written_to int,      -- years
  published     int,
  kind          text NOT NULL DEFAULT 'real' CHECK (kind IN ('real','fictional','mixed')),
  rights        jsonb NOT NULL DEFAULT '{}', -- {"orig":"PD","ru":"PD|own|©","en":"PD|own|©","checked":"2026-11-08","note":"..."}
  wave          int,                      -- 1 = MVP wave; null = catalogue only
  status        text NOT NULL DEFAULT 'catalogue'
                CHECK (status IN ('catalogue','text','extracting','review','published')),
  meta          jsonb NOT NULL DEFAULT '{}'
);

CREATE TABLE book_texts (                 -- one edition or translation of a book
  id            serial PRIMARY KEY,
  book_id       int NOT NULL REFERENCES books(id),
  lang          text NOT NULL,
  edition       text NOT NULL,            -- 'orig-1797', 'tr-minaev-1902', 'ltsgo-2026'
  translator    text,
  licence       text NOT NULL,            -- 'PD' | 'own' | '©-quotes-only'
  ai_translated boolean NOT NULL DEFAULT false,
  source_id     int REFERENCES sources(id),
  UNIQUE (book_id, edition)
);

CREATE TABLE passages (                   -- the text split into addressable pieces
  id            bigserial PRIMARY KEY,
  text_id       int NOT NULL REFERENCES book_texts(id),
  seq           int NOT NULL,             -- order inside the text
  part          text,                     -- 'letter 12', 'ch. 3', 'book II ch. 41'
  heading       text,                     -- e.g. 'Кёнигсберг, июня 19, 1789'
  date_in_text  text,                     -- as written
  body          text NOT NULL,
  aligned_to    bigint REFERENCES passages(id), -- the same piece in the original (for translations)
  search        tsvector,
  UNIQUE (text_id, seq)
);
CREATE INDEX passages_search ON passages USING gin (search);
CREATE INDEX passages_body_trgm ON passages USING gin (body gin_trgm_ops);

-- ---------- entities: people, places, buildings, events, artworks ----------
CREATE TABLE entities (
  id            serial PRIMARY KEY,
  kind          text NOT NULL CHECK (kind IN
                ('person','place','building','event','artwork','organisation','vessel','route_segment')),
  key           text NOT NULL UNIQUE,     -- 'kant', 'koenigsberg', 'hotel-de-bretagne-paris', 'storming-bastille'
  wikidata      text UNIQUE,              -- 'Q9312'
  name          jsonb NOT NULL,           -- {"ru": "...", "en": "..."}
  names_then    jsonb NOT NULL DEFAULT '[]', -- historic names: [{"name":"Кёнигсберг","lang":"ru","until":1946}]
  parent_id     int REFERENCES entities(id),   -- building -> city, city -> country
  lat           double precision,         -- places/buildings; PostGIS later if nearby search needs it
  lon           double precision,
  geo_precision text CHECK (geo_precision IN ('exact','street','district','city','region','approx')),
  born          text, died text,          -- persons: as text, may be approximate ('ок. 1254')
  starts        text, ends text,          -- events
  preservation  text CHECK (preservation IN ('intact','rebuilt','altered','ruin','lost','unknown')),
  status        text NOT NULL DEFAULT 'unverified'
                CHECK (status IN ('verified_source','verified_wiki','book_only','unverified','disputed','obsolete')),
  meta          jsonb NOT NULL DEFAULT '{}',
  created_by    text NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX entities_kind ON entities (kind);
CREATE INDEX entities_name_trgm ON entities USING gin ((name::text) gin_trgm_ops);
ALTER TABLE books ADD CONSTRAINT books_author FOREIGN KEY (author_id) REFERENCES entities(id);

CREATE TABLE entity_links (               -- 'met', 'stayed_at', 'saw', 'located_in', 'took_part', 'portrait_of'
  id            bigserial PRIMARY KEY,
  from_id       int NOT NULL REFERENCES entities(id),
  to_id         int NOT NULL REFERENCES entities(id),
  kind          text NOT NULL,
  book_id       int REFERENCES books(id), -- null = general fact, not tied to a book
  passage_id    bigint REFERENCES passages(id),
  during        text,
  status        text NOT NULL DEFAULT 'unverified'
                CHECK (status IN ('verified_source','verified_wiki','book_only','unverified','disputed','obsolete')),
  note          text
);

-- ---------- the route ----------
CREATE TABLE journeys (
  id            serial PRIMARY KEY,
  book_id       int NOT NULL REFERENCES books(id),
  traveller_id  int REFERENCES entities(id),  -- Karamzin; Phileas Fogg (fictional person); Nellie Bly
  key           text NOT NULL UNIQUE,     -- 'karamzin-1789', 'fogg-1872', 'bly-1889'
  title         jsonb NOT NULL,
  kind          text NOT NULL DEFAULT 'real' CHECK (kind IN ('real','fictional','reconstructed')),
  starts        date, ends date,
  calendar      text NOT NULL DEFAULT 'gregorian' CHECK (calendar IN ('gregorian','julian')),
  colour        text,                     -- map line colour
  meta          jsonb NOT NULL DEFAULT '{}'
);

CREATE TABLE stops (
  id            serial PRIMARY KEY,
  journey_id    int NOT NULL REFERENCES journeys(id),
  seq           int NOT NULL,
  place_id      int NOT NULL REFERENCES entities(id),
  arrived       date, departed date,      -- in journeys.calendar
  date_precision text NOT NULL DEFAULT 'day' CHECK (date_precision IN ('day','month','year','unknown')),
  date_in_text  text,                     -- as the book says
  transport_in  text,                     -- how he got here: 'post-chaise', 'ship', 'on foot', 'rail'
  passage_from  bigint REFERENCES passages(id),
  passage_to    bigint REFERENCES passages(id),
  kind          text NOT NULL DEFAULT 'stay' CHECK (kind IN ('stay','pass','mention_only')),
  status        text NOT NULL DEFAULT 'unverified'
                CHECK (status IN ('verified_source','verified_wiki','book_only','unverified','disputed','obsolete')),
  note          text,                     -- e.g. 'in reality K. was here later than the letter says'
  UNIQUE (journey_id, seq)
);

-- ---------- text ↔ entities ----------
CREATE TABLE mentions (
  id            bigserial PRIMARY KEY,
  passage_id    bigint NOT NULL REFERENCES passages(id),
  entity_id     int NOT NULL REFERENCES entities(id),
  surface       text NOT NULL,            -- the words used in the text
  char_from     int, char_to int,
  status        text NOT NULL DEFAULT 'unverified'
                CHECK (status IN ('verified_source','verified_wiki','book_only','unverified','disputed','obsolete'))
);
CREATE INDEX mentions_entity ON mentions (entity_id);

CREATE TABLE quotes (                     -- curated, shown on the site
  id            bigserial PRIMARY KEY,
  passage_id    bigint NOT NULL REFERENCES passages(id),
  text          text NOT NULL,            -- must be a substring of passages.body (checked by code)
  stop_id       int REFERENCES stops(id),
  entity_ids    int[] NOT NULL DEFAULT '{}',
  tags          text[] NOT NULL DEFAULT '{}', -- 'humour','culture-clash','food','tolerance'
  state         text NOT NULL DEFAULT 'proposed' CHECK (state IN ('proposed','approved','rejected'))
);

-- ---------- facts (everything else) ----------
CREATE TABLE fact_classes (
  name         text PRIMARY KEY,
  check_every  interval,                  -- null = never re-checked (history does not change)
  needs_review boolean NOT NULL DEFAULT true,
  note         text
);
INSERT INTO fact_classes VALUES
  ('history',      NULL,       true,  'what happened then: biography, events, the building in 1790'),
  ('identity',     '365 days', false, 'Wikidata id, coordinates, names — re-synced from Wikidata'),
  ('preservation', '365 days', true,  'what is left of the place today'),
  ('visit',        '90 days',  true,  'opening hours, tickets, closed for restoration'),
  ('transport',    '180 days', true,  'how to get there today'),
  ('rights',       '365 days', true,  'copyright of texts, translations, pictures'),
  ('trivia',       NULL,       true,  'interesting facts of the time and place');

CREATE TABLE facts (
  id             bigserial PRIMARY KEY,
  entity_id      int REFERENCES entities(id),
  stop_id        int REFERENCES stops(id),
  book_id        int REFERENCES books(id),
  key            text NOT NULL,           -- 'bio.short', 'built', 'famous_for', 'now.what_is_here', 'visit.hours'
  layer          text NOT NULL CHECK (layer IN ('then','now','go')),
  lang           text NOT NULL DEFAULT 'ru',
  value          jsonb NOT NULL,
  fact_class     text NOT NULL REFERENCES fact_classes(name),
  status         text NOT NULL
                 CHECK (status IN ('verified_source','verified_wiki','book_only','unverified','disputed','obsolete')),
  checked_at     date,
  check_every    interval,
  source_id      int REFERENCES sources(id),
  passage_id     bigint REFERENCES passages(id), -- when the fact rests on the book itself
  quote          text,                    -- verbatim sentence the value rests on
  note           text,
  version        int NOT NULL DEFAULT 1,
  reviewed_by    text,
  reviewed_at    timestamptz,
  created_by     text NOT NULL,           -- 'import:wikidata' | 'agent:<name>' | 'editor:<name>'
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now(),
  search         tsvector,
  CHECK (entity_id IS NOT NULL OR stop_id IS NOT NULL OR book_id IS NOT NULL)
);
CREATE UNIQUE INDEX facts_live ON facts
  (coalesce(entity_id,0), coalesce(stop_id,0), coalesce(book_id,0), key, lang) WHERE status <> 'obsolete';
CREATE INDEX facts_search ON facts USING gin (search);

CREATE VIEW facts_due AS
SELECT f.*, coalesce(f.check_every, c.check_every) AS every,
       coalesce(f.checked_at, f.created_at::date) + coalesce(f.check_every, c.check_every) AS due
FROM facts f JOIN fact_classes c ON c.name = f.fact_class
WHERE f.status <> 'obsolete' AND coalesce(f.check_every, c.check_every) IS NOT NULL;

CREATE TABLE fact_history (
  id          bigserial PRIMARY KEY,
  fact_id     bigint NOT NULL REFERENCES facts(id),
  version     int NOT NULL,
  value       jsonb,
  status      text,
  changed_at  timestamptz NOT NULL DEFAULT now(),
  changed_by  text NOT NULL,
  reason      text,
  snapshot_id bigint REFERENCES source_snapshots(id)
);

-- ---------- media ----------
CREATE TABLE media (
  id            bigserial PRIMARY KEY,
  kind          text NOT NULL CHECK (kind IN
                ('engraving','painting','drawing','photo','map','portrait','manuscript','video','audio','model3d')),
  era           text NOT NULL CHECK (era IN ('then','now','reconstruction')),
  entity_id     int REFERENCES entities(id),
  stop_id       int REFERENCES stops(id),
  title         jsonb NOT NULL DEFAULT '{}',
  creator       text,
  year          text,
  url           text NOT NULL,            -- original page (Commons, Gallica, museum)
  file_url      text,                     -- direct file
  storage_key   text,                     -- our copy
  licence       text NOT NULL,            -- 'PD', 'CC BY-SA 4.0', 'partner', ...
  attribution   text,
  source_id     int REFERENCES sources(id),
  derived_from  bigint REFERENCES media(id), -- an animated / colourised version of another picture
  ai_generated  boolean NOT NULL DEFAULT false,
  ai_tool       text,                     -- model / service, when ai_generated
  viewpoint     jsonb,                    -- {"lat":..,"lon":..,"bearing":..} for then/now pairs
  state         text NOT NULL DEFAULT 'proposed' CHECK (state IN ('proposed','approved','rejected')),
  created_by    text NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now()
);

-- ---------- offers (monetisation) ----------
CREATE TABLE offers (
  id            bigserial PRIMARY KEY,
  kind          text NOT NULL CHECK (kind IN ('hotel','tour','excursion','ticket','transport','guide','premium')),
  entity_id     int REFERENCES entities(id),
  stop_id       int REFERENCES stops(id),
  journey_id    int REFERENCES journeys(id), -- a whole-route tour
  partner       text NOT NULL,            -- 'booking', 'getyourguide', 'tripster', 'own'
  title         jsonb NOT NULL,
  url           text NOT NULL,            -- affiliate link
  price_from    numeric, currency text,
  langs         text[] NOT NULL DEFAULT '{}',
  active        boolean NOT NULL DEFAULT true,
  checked_at    date,
  meta          jsonb NOT NULL DEFAULT '{}'
);

-- ---------- review, alerts, agents (same as onpoint) ----------
CREATE TABLE change_proposals (
  id          bigserial PRIMARY KEY,
  target      text NOT NULL CHECK (target IN
              ('fact','entity','entity_link','stop','mention','quote','media','offer','book')),
  target_id   bigint,                       -- null = a new row
  proposed    jsonb NOT NULL,               -- the row as it should be, plus {quote, source_url}
  diff        jsonb,
  snapshot_id bigint REFERENCES source_snapshots(id),
  quote_ok    boolean,                      -- set by code: the quote was found in the source text
  agent       text NOT NULL,
  confidence  numeric,
  state       text NOT NULL DEFAULT 'open' CHECK (state IN ('open','approved','rejected','applied')),
  decided_by  text,
  decided_at  timestamptz,
  decision_note text,
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX proposals_open ON change_proposals (target, state) WHERE state = 'open';

CREATE TABLE alerts (
  id         bigserial PRIMARY KEY,
  kind       text NOT NULL,
  ref        jsonb NOT NULL,
  severity   text NOT NULL DEFAULT 'info' CHECK (severity IN ('info','warn','crit')),
  created_at timestamptz NOT NULL DEFAULT now(),
  closed_at  timestamptz
);

CREATE TABLE agent_runs (
  id           bigserial PRIMARY KEY,
  agent        text NOT NULL,
  book_id      int REFERENCES books(id),
  started_at   timestamptz NOT NULL DEFAULT now(),
  finished_at  timestamptz,
  items        int DEFAULT 0,
  model_calls  int DEFAULT 0,
  search_calls int DEFAULT 0,
  ok           boolean,
  error        text
);

CREATE TABLE locks (
  name   text PRIMARY KEY,
  holder text NOT NULL,
  until  timestamptz NOT NULL
);

-- semantic search over passages and facts (bge-m3 = 1024 dims, via the GPU gateway)
CREATE TABLE embeddings (
  ref_kind  text NOT NULL CHECK (ref_kind IN ('passage','fact','entity')),
  ref_id    bigint NOT NULL,
  model     text NOT NULL,
  embedding vector(1024) NOT NULL,
  PRIMARY KEY (ref_kind, ref_id)
);
