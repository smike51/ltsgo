# texts/ — тексты книг

Одна папка на книгу (ключ = `books.key`): `raw/` как скачано, `text.txt` чистый UTF-8,
`passages.jsonl` — готово к загрузке в `book_texts` / `passages`, `SOURCE.md` — откуда, издание, права.
Скрипты: `tools/azlibru_to_text.py` (az.lib.ru → текст), `tools/split_book.py` (текст → фрагменты).
Только общественное достояние; комментарии современных изданий — вне `text.txt`.
