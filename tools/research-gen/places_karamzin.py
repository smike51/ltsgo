import json, os
OUT = r"C:/Users/admin/OneDrive/dev/ltsgo/research"
BOOK = "Карамзин, «Письма русского путешественника», passages.jsonl"

def S(title, url, quote=""):
    return {"title": title, "url": url, "quote": quote}

def bk(seq):
    return S(f"{BOOK}, seq {seq}", "texts/karamzin-letters/passages.jsonl")

WP = lambda lang, t: f"https://{lang}.wikipedia.org/wiki/{t}"

E = []
def add(city, name, kind, seq, quote, status, person=None, address_then=None, address_now=None,
        lat=None, lon=None, wikidata=None, survives="unknown", now_what=None, sources=None, notes=None):
    E.append(dict(book="karamzin-letters", city=city, name_then=name, kind=kind, person=person,
                  passage_seq=seq, book_quote=quote, address_then=address_then, address_now=address_now,
                  lat=lat, lon=lon, wikidata=wikidata, survives=survives, now_what=now_what,
                  status=status, sources=[bk(seq)] + (sources or []), notes=notes))

# ---------- Riga
add("Рига", "Hotel de Petersbourg (Гостиница «Санкт-Петербург»)", "hotel", 4,
    "остановился в \"Hotel de Petersbourg\"", "verified_source",
    address_then="против Рижского замка (Замковая площадь)", address_now="Pils laukums, Рига (номер дома не установлен)",
    survives="survives", now_what="здание сохранилось, не гостиница",
    sources=[S("Historic Riga hotels", "https://rigasights.com/historic-riga-hotels",
               "in a two-story building opposite the castle")],
    notes="Открыта в 1763; в 1874 надстроена; работала до 1940. Дата письма — 31 мая 1789 (юлианский)." )
# ---------- Königsberg
add("Кёнигсберг", "Дом Иммануила Канта", "house", 9, "Домик у него маленький, и внутри приборов немного.",
    "verified_source", person="Иммануил Кант",
    address_then="Prinzessinstraße (с 1924 — Kantstraße), купл. в конце 1783",
    address_now="Калининград, район бывшей Принцессинштрассе у Королевского замка (точно не привязано)",
    survives="lost", now_what="снесён в 1893 под расширение магазина Лидтке; квартал застроен после войны",
    sources=[S("S. Naragon, Kant's House", "https://users.manchester.edu/FacStaff/SSNaragon/Kant/Helps/Life/KantHouse.html", "")],
    notes="Номер дома в источниках расходится (№3 / 87-88) — уточнить по Kuhrke «Kants Wohnhaus» (1917). Координаты не ставлю (примерно 54.706, 20.512 — не проверено).")
add("Кёнигсберг", "Кафедральный собор", "church", 9, "Здешняя кафедральная церковь огромна.", "verified_wiki",
    address_now="остров Канта (Кнайпхоф), Калининград", survives="rebuilt",
    now_what="восстановлен после войны; музей, у стены — могила Канта",
    sources=[S("Wikipedia: Königsberg Cathedral", WP("en", "Königsberg_Cathedral"))],
    notes="Идентификация однозначна; Wikidata/координаты дозаполнить при загрузке.")
# ---------- Berlin / Potsdam
add("Берлин", "Квартира Карамзина на Брюдерштрассе", "lodging", 15,
    "живущим в той же улице, где я живу, то есть в Bruderstrasse", "book_only",
    address_then="Brüderstraße (дом не назван)", address_now="Brüderstraße, Berlin-Mitte",
    notes="Только улица; дом неизвестен.")
add("Берлин", "Дом Николаи (Nicolaihaus)", "house", 15, "живущим в той же улице, где я живу, то есть в Bruderstrasse",
    "verified_wiki", person="Фридрих Николаи", address_then="Brüderstraße 13", address_now="Brüderstraße 13, 10178 Berlin",
    lat=52.514073, lon=13.402926, wikidata="Q1655145", survives="survives", now_what="памятник архитектуры, барочная лестница эпохи Николаи",
    sources=[S("Wikipedia: Nicolaihaus", WP("de", "Nicolaihaus"),
               "Das barocke Treppenhaus stammt noch aus den Zeiten Friedrich Nicolais")],
    notes="Николаи купил дом в 1787, жил до 1811. Цитата книги — о той же улице, где жил Карамзин.")
add("Берлин", "Дом Рамлера", "house", 18, "Ныне был я у старика Рамлера, немецкого Горация.", "book_only",
    person="Карл Вильгельм Рамлер", notes="Адрес Рамлера в 1789 не установлен.")
add("Берлин", "Дом К. Ф. Морица", "house", 19, "\"Карл Филипп Мориц, живет в ***\"", "book_only",
    person="Карл Филипп Мориц", notes="Адрес скрыт самим автором.")
add("Берлин", "Тиргартен (кофейные дома)", "landmark", 14, None, "unverified",
    notes="Кофейни в Тиргартене упомянуты в письме 14; точной цитаты и названий нет — проверить.")
add("Потсдам", "Русская церковь", "church", 17, "В Потсдаме есть русская церковь под надзиранием старого русского солдата",
    "unverified", notes="Вероятно, домовая церковь при русских певчих/гренадерах; к Александровской (1829) отношения не имеет. Место не установлено.")
# ---------- Dresden
add("Дрезден", "Трактир на почтовом дворе", "inn", 22, "Я остановился в трактире на почтовом дворе", "book_only",
    notes="Название и адрес не установлены.")
add("Дрезден", "Картинная галерея", "landmark", 22, "пошел я в славную картинную галерею, которая почитается одною из первых в Европе",
    "verified_wiki", address_then="Stallhof (Johanneum), Neumarkt", address_now="галерея с 1855 в Цвингере (Gemäldegalerie Alte Meister)",
    survives="rebuilt", now_what="здание Иоганнеума — Музей транспорта; собрание — в Цвингере",
    sources=[S("Wikipedia: Gemäldegalerie Alte Meister", WP("de", "Gemäldegalerie_Alte_Meister"))],
    notes="В 1789 галерея помещалась в Иоганнеуме — сверить точнее.")
# ---------- Leipzig
add("Лейпциг", "Трактир Мемеля", "inn", 25, "Я остановился в трактире у Мемеля, против почтового двора.", "book_only",
    address_then="против почтового двора", notes="Мемель — фамилия хозяина (дальше «г. Мемель испугался»). Письмо «Лейпциг, июля 14» (юлианский).")
add("Лейпциг", "Трактир «Голубой ангел»", "inn", 27, "в трактир \"Голубого ангела\"", "unverified",
    address_then="Petersstraße (?)", address_now="на месте — Petershof (1927–29), Petersstraße",
    survives="lost", now_what="торговый дом Petershof",
    sources=[S("Leipzig Travel: Petershof", "https://www.leipzig.travel/en/then/petershof-petersstrasse", "")],
    notes="Трактир «Zum (blauen) Engel» на месте Петерсхофа (Бёттгер показывал там фарфор в 1710); источники расходятся в названии, номер дома не найден.")
add("Лейпциг", "Сад Платнера за городом", "house", 26, "Он живет за городом, в саду.", "book_only", person="Эрнст Платнер",
    notes="Место сада не установлено.")
add("Штёттериц (под Лейпцигом)", "Дом Вейсе", "house", 28, "\"Там, на правой стороне, большой дом с садом!\"", "disputed",
    person="Кристиан Феликс Вейсе",
    address_now="Leipzig-Stötteritz, господский дом «Unterer Teil» (?)",
    sources=[S("Wikipedia: Christian Felix Weiße", WP("en", "Christian_Felix_Weiße"))],
    notes="Версия 1: Штёттериц (усадьба Вейсе). Версия 2: в 1789 Вейсе ещё не владел имением (купил в 1790) — жил в деревне иначе. Сохранность дома — по слабому источнику (Komoot).")
# ---------- Weimar
add("Веймар", "Гостиница «Слон» (Elephant)", "inn", 30, "я велел постиллиону везти себя в трактир \"Слона\".", "verified_wiki",
    address_then="Markt", address_now="Markt 19, 99423 Weimar", lat=50.97889, lon=11.33028, wikidata="Q203756",
    survives="rebuilt", now_what="Hotel Elephant (новое здание 1938, арх. Гислер)",
    sources=[S("Wikipedia: Hotel Elephant", WP("de", "Hotel_Elephant"), "mussten 1937 dem geplanten Neubau weichen")],
    notes="Основана 1696; старое здание снесено 1937.")
add("Веймар", "Дом Виланда", "house", 30, "Наемный слуга немедленно был отправлен мною к Виланду", "unverified", person="Кристоф Мартин Виланд",
    address_now="Marienstraße 1 (?)", notes="Адрес 1789 не подтверждён; один путеводитель даёт «Wielands Wohnung» Marienstraße 1 без дат.")
add("Веймар", "Дом Гердера (пасторский дом)", "house", 31, "Гердер принял меня с такою же кроткою ласкою, как и вчера", "unverified",
    person="Иоганн Готфрид Гердер", address_now="Herderplatz 8 (Herderhaus) — предположительно",
    notes="Гердер как генерал-суперинтендант жил в пасторском доме у Городской церкви; адрес не сверен.")
add("Веймар", "Егерский дом — дом, где жил Гёте", "house", 31, "идучи мимо того дома, где живет Гете", "verified_wiki",
    person="Иоганн Вольфганг Гёте", address_then="Jägerhaus, Marienstraße", address_now="Marienstraße 5/7, Weimar",
    lat=50.976325, lon=11.328788, survives="rebuilt", now_what="Баухаус-университет; повреждён в войну, восстановлен с изменениями",
    sources=[S("Wikipedia: Jägerhaus (Weimar)", WP("de", "Jägerhaus_(Weimar)"), "wohnte hier von 1789 bis 1792 zusammen mit Christiane Vulpius")],
    notes="Находка: летом 1789 Гёте жил не на Фрауэнплане, а в Егерском доме.")
# ---------- Erfurt / Gotha / Frankfurt
add("Эрфурт", "Трактир без названия", "inn", 33, "остановился в трактире (которого имени, право, не знаю)", "book_only")
add("Гота", "Трактир «Колокольчик»", "inn", 34, "остановился в трактире \"Колокольчика\"", "book_only",
    notes="Нем. «Zur Glocke» (?) — не найден.")
add("Франкфурт-на-Майне", "Трактир «Звезда»", "inn", 35, "остановился в трактире \"Звезды\"", "book_only",
    notes="Нем. «Zum Stern» (?) — не найден.")
# ---------- Basel
add("Базель", "Трактир «Аист» (Zum Storchen)", "inn", 42, "остановились мы с ним в одном трактире, под вывескою \"Аиста\"",
    "verified_source", address_then="Stadthausgasse 25 / Fischmarkt", address_now="Fischmarkt 10 (офисное здание «Storchen»)",
    survives="lost", now_what="офисное здание «Storchen»",
    sources=[S("Staatsarchiv Basel-Stadt: Gasthof zum Storchen, Stadthausgasse 25 (~1870)", "https://dls.staatsarchiv.bs.ch/records/388802", "Gasthof zum Storchen")],
    notes="Старое здание, по всей видимости, заменено; сохранность не подтверждена.")
add("Базель", "Кафедральный собор (Мюнстер)", "church", 42, "Монументы Эразма и супруги императора Рудольфа I были для меня примечательнее других.",
    "verified_wiki", address_now="Münsterplatz, Basel", survives="survives", now_what="собор, могила Эразма",
    sources=[S("Wikipedia: Basler Münster", WP("de", "Basler_Münster"))])
# ---------- Zurich
add("Цюрих", "Трактир «Ворон» (Gasthof zum Raben)", "inn", 45, "В трактире под вывескою \"Ворона\" отвели нам большую светлую комнату",
    "unverified", address_then="у Шиффленде, у выхода Лиммата из озера", address_now="Schifflände (точный адрес не установлен)",
    survives="unknown", now_what=None,
    sources=[S("Helveticarchives GS-GRAF-ANSI-ZH-1023 (1820–28)", "https://www.helveticarchives.ch", "Gasthof zum Raben [später Bellevue] / J. Wirz Besitzer")],
    notes="Позже «Bellevue»; положение у озера совпадает с книгой (Лиммат под окнами).")
add("Цюрих", "Дом Лафатера (пасторат Св. Петра)", "house", 45, "Пришедши в одиннадцать часов к Лафатеру", "verified_source",
    person="Иоганн Каспар Лафатер", address_then="у церкви Св. Петра", address_now="St. Peterhofstatt 6, Zürich",
    survives="survives", now_what="Лафатерхаус / Sammlung Lavater",
    sources=[S("HMdb marker 67118", "https://www.hmdb.org/m.asp?m=67118", ""),
             S("zuerich.com: Lavaterhaus", "https://www.zuerich.com", "")],
    notes="Маркер: жил здесь 1784–1801 как диакон/пастор Св. Петра.")
# ---------- Schaffhausen
add("Шафхаузен", "Трактир «Корона» (Krone)", "inn", 47, "Мы пришли прямо в трактир \"Венца\"", "unverified",
    address_now="Kirchhofplatz 7, Schaffhausen (Hotel Kronenhof) — предположительно", survives="unknown", now_what="Hotel Kronenhof",
    sources=[S("Staatsarchiv Schaffhausen: план «Gasthof zur Krone und Kronenhof»", "https://klio.sh.ch/api/records/0bde7d80100f49f8a6fae397aae328cf/export", "")],
    notes="Тождество «Венца» 1789 и нынешнего Kronenhof не доказано.")
add("Нойхаузен (у Шафхаузена)", "Рейнский водопад", "landmark", 47, "услышали мы шум Рейна, удвоили шаги свои, пришли на край высокого берега и увидели водопад.",
    "verified_wiki", survives="survives", now_what="природный памятник",
    sources=[S("Wikipedia: Rheinfall", WP("de", "Rheinfall"))])
# ---------- Bern / Thun
add("Берн", "Трактир «Корона» (Krone)", "inn", 54, "комнату в трактире \"Венца\": так много здесь приезжих!", "unverified",
    address_now="Gerechtigkeitsgasse (номер не подтверждён)",
    sources=[S("KGS-Inventar kgs_00754", "https://data.geo.admin.ch/ch.babs.kulturgueter/PDF/kgs_00754_gsk-d.pdf", "")],
    notes="Инвентарь называет гостиницу (постр. 1578–82), где в 1779 останавливались Гёте и Карл Август; улица в выдержке не названа.")
add("Берн (окрестности)", "Загородный дом коллекционера Шпренгли", "house", 62, "Домик у него прекрасный, за городом, на высоком месте", "book_only",
    person="Шпренгли (коллекционер)")
add("Тун", "Трактир «Фрейгоф» (Freienhof)", "inn", 55, "остановился я в трактире \"Фрейгофе\"", "verified_source",
    address_now="Freienhofgasse 3, Thun", survives="unknown", now_what="Hotel Aare Thun (бывш. Freienhof)",
    sources=[S("MySwitzerland: Hotel Freienhof/Aare Thun", "https://www.myswitzerland.com", "")],
    notes="Место и имя подтверждены; история здания XVIII в. не проверена.")
# ---------- Lausanne / Vevey
add("Лозанна", "Трактир «Олень» (Cerf)", "inn", 64, None, "unverified",
    sources=[S("Livre Beau Rivage Palace (цит. путеводитель Joanne 1841)", "https://brp.ch/brochure/livrebeaurivage/files/basic-html/page38.html", "the lion d'or, the couronne, the cerf, the aigle")],
    notes="Lion d'Or и Couronne были заняты. «Cerf» существовал (1841), адрес не найден. Цитату книги дозаполнить.")
add("Лозанна", "Café littéraire", "cafe", 64, "был я в \"Cafe litteraire\"", "book_only")
add("Веве", "Трактир (без названия)", "inn", 64, None, "book_only")
# ---------- Geneva area
add("Женева", "Наёмная комната", "lodging", 65, "нанял себе большую, светлую, изрядно прибранную комнату в доме", "book_only",
    notes="Улица не названа; друг жил на той же улице (seq 66).")
add("Женева", "Театр (опера)", "theatre", 66, "бываю на женевских вечеринках и в опере.", "unverified",
    notes="Театр Нёв (1783) у ворот Нёв — вероятно; не сверено.")
add("Женева", "Трактир «Золотые весы»", "inn", 70, "ужинать в трактире \"Золотых весов\"", "book_only", notes="«Balance d'or» (?) не найдена.")
add("Ферне", "Замок Вольтера", "house", 65, "Бывший Вольтеров замок построен на возвышенном месте", "verified_wiki", person="Вольтер (ум. 1778)",
    address_now="1 allée du Château, Ferney-Voltaire", lat=46.2575, lon=6.10361, wikidata="Q2969210",
    survives="survives", now_what="музей (государство с 1999, CMN)",
    sources=[S("Wikipedia: Château de Voltaire", WP("fr", "Château_de_Voltaire"))], notes="Обедал в трактире Ферне (не назван).")
add("Жанту", "Сельский дом Шарля Бонне", "house", 71, "постучался я у дверей сельского его домика", "verified_source", person="Шарль Бонне",
    address_now="Rue du Village 20, 1294 Genthod", survives="survives", now_what="частное владение, памятник",
    sources=[S("Canton de Genève, recensement patrimoine 2011-26120", "https://ge.ch/geodata/SIPATRIMOINE/SI-EVI-OPS/EVI/edition/objets/2011-26120.htm", "")],
    notes="Построен 1728–30 (арх. Малле); Бонне жил с 1766, умер там в 1793. Также в книге: «живет верстах в четырех от Женевы, в деревне Жанту».")
add("Ивердон", "Трактир (без названия)", "inn", 73, None, "book_only")
add("Бьенское озеро", "Остров Св. Петра (дом Руссо)", "landmark", 73, "Недавно был я на острове св. Петра", "verified_wiki",
    survives="survives", now_what="бывший монастырь — отель, комната Руссо",
    sources=[S("Wikipedia: St. Petersinsel", WP("de", "St._Petersinsel"))])
# ---------- Lyon
add("Лион", "Hôtel de Milan", "hotel", 78, "остановились мы в \"Hotel de Milan\"", "verified_source",
    address_then="place des Terreaux", address_now="8 place des Terreaux, Lyon", survives="survives", now_what="жилой дом (гостиница закрыта 1905)",
    sources=[S("Inventaire Auvergne-Rhône-Alpes IA69004579", "https://patrimoine.auvergnerhonealpes.fr", "Hôtel de voyageurs dit Hôtel de Milan, actuellement immeuble"),
             S("Guichet du savoir 139612", "https://www.guichetdusavoir.org/question/voir/139612", "")],
    notes="Здание XVII–нач. XVIII в., надстроено 1717.")
add("Лион", "Театр", "theatre", 78, "Проехав мимо театра, огромного здания", "unverified",
    notes="Театр Суффло (1756) на месте нынешней Опера де Лион — вероятно; не сверено.")
# ---------- Paris
add("Париж", "Квартира у Hôtel Britannique, ул. Генего", "lodging", 81, "остановились мы подле \"Hotel Britannique\". Там, в третьем этаже", "book_only",
    address_then="rue Guénégaud", address_now="rue Guénégaud, Paris 6e (дом не установлен)",
    notes="seq 87: «Люксанбур недалеко от улицы Генего, в которой живу»; соседом был Лагарп. Здание не опознано.")
add("Париж", "Пале-Рояль (сад, кафе)", "landmark", 81, "Мы пришли в Пале-Рояль, огромное здание, которое принадлежит герцогу Орлеанскому", "verified_wiki",
    survives="survives", now_what="Государственный совет, сад", sources=[S("Wikipedia: Palais-Royal", WP("fr", "Palais-Royal"))],
    notes="Кафе де Фуа, дю Каво, де Валуа, де Шартр — seq 81/87/93; отдельно не привязаны.")
add("Париж", "Салон госпожи Гло*", "salon", 83, "Нынешний день обедал я у господина Гло*", "book_only", notes="Лицо не раскрыто.")
add("Париж", "Опера (Глюк, «Орфей»)", "theatre", 86, None, "unverified",
    notes="В 1790 — зал Порт-Сен-Мартен; не сверено.")
add("Париж", "Академия надписей (Лувр)", "other", 88, "в Академии надписей и словесности имел счастие узнать Бартелеми-Платона", "verified_wiki",
    address_then="Лувр", now_what="Академия — в Институте Франции", sources=[S("Wikipedia: Académie des inscriptions", WP("fr", "Académie_des_inscriptions_et_belles-lettres"))])
add("Париж", "Дом инвалидов", "landmark", 94, "Лудовик XIV построил самый великолепнейший в Европе Инвалидный дом", "verified_wiki", survives="survives",
    sources=[S("Wikipedia: Hôtel des Invalides", WP("fr", "Hôtel_des_Invalides"))])
add("Париж", "Сорбоннская церковь", "church", 98, "В Сорбонскую церковь ходят все удивляться искусству ваятеля Жирардона.", "verified_wiki", survives="survives",
    now_what="часовня Сорбонны, гробница Ришелье", sources=[S("Wikipedia: Chapelle de la Sorbonne", WP("fr", "Chapelle_de_la_Sorbonne"))])
add("Париж", "Аббатство Св. Женевьевы", "church", 98, "В аббатстве св. Женевьевы хранится прах Декартов", "verified_wiki", survives="rebuilt",
    now_what="церковь снесена 1807; от аббатства — лицей Генриха IV, башня Хлодвига", sources=[S("Wikipedia: Abbaye Sainte-Geneviève", WP("fr", "Abbaye_Sainte-Geneviève_de_Paris"))])
add("Версаль", "Версальский дворец и сад, Трианон", "landmark", 100, "в сравнении с Версальским!", "verified_wiki", survives="survives",
    sources=[S("Wikipedia: Château de Versailles", WP("fr", "Château_de_Versailles"))])
add("Сен-Дени", "Аббатство Сен-Дени", "church", 102, "То есть я был в аббатстве", "verified_wiki", survives="survives",
    now_what="базилика (усыпальницы разорены в 1793)", sources=[S("Wikipedia: Basilique Saint-Denis", WP("fr", "Basilique_Saint-Denis"))])
add("Эрменонвиль", "Парк и гробница Руссо", "landmark", 106, "Верст 30 от Парижа до Эрменонвиля", "verified_wiki", survives="survives",
    now_what="Parc Jean-Jacques Rousseau (прах Руссо в Пантеоне с 1794)", sources=[S("Wikipedia: Parc Jean-Jacques-Rousseau", WP("fr", "Parc_Jean-Jacques-Rousseau"))])
add("Париж", "Национальное собрание (Манеж)", "other", 108, None, "unverified",
    notes="В 1790 — зал Манежа у Тюильри (снесён); точную цитату дозаполнить.")
# ---------- Calais / Dover
add("Кале", "Отель Дессеня (Hôtel d'Angleterre)", "hotel", 110, "Я тотчас пошел к Дессеню (которого дом есть самый лучший в городе)", "verified_source",
    person="Пьер Кийак «Дессен»", survives="lost", now_what="на месте — муниципальный коллеж (1911)",
    sources=[S("Victorian Web: Johannot, Dessein", "http://www.victorianweb.org/art/illustration/johannot/47.html", ""),
             S("The Spectator, 7 Oct 1911", "http://archive.spectator.co.uk/article/7th-october-1911/27/calais", "")],
    notes="Тот же отель, что у Стерна в «Сентиментальном путешествии». Письмо датировано «Го-Бюиссон» — сверить.")
add("Дувр", "Дувр (замок)", "landmark", 113, "Мы в Дувре, и я в Англии", "unverified", notes="Посещение замка — проверить по тексту письма.")
# ---------- London
add("Лондон", "Французский трактир", "inn", 115, "мне отвели уголок в одном французском трактире", "book_only")
add("Лондон", "Квартира на Оксфорд-стрит у Кавендиш-сквер", "lodging", 117,
    "нашел я в Оксфордской улице, близ Cavendish Square, прекрасные три комнаты за полгинею в неделю", "book_only",
    address_now="Oxford Street у Cavendish Square, London W1 (дом не установлен)",
    notes="Дом не опознан; см. A. G. Cross «By the Banks of the Thames» (1980, ©).")
add("Лондон", "Вестминстерское аббатство (оратория «Мессия»)", "church", 116, "успел слышать в Вестминстерском аббатстве Генделеву ораторию \"Мессию\"", "verified_wiki",
    survives="survives", sources=[S("Wikipedia: Westminster Abbey", WP("en", "Westminster_Abbey"))])
add("Лондон", "Бедлам (Бетлемская больница)", "other", 118, "\"Это Бедлам!\" -- скажете вы и не ошибетесь.", "verified_wiki",
    address_then="Moorfields", survives="lost", now_what="здание в Мурфилдс снесено (1815); больница переехала",
    sources=[S("Wikipedia: Bethlem Royal Hospital", WP("en", "Bethlem_Royal_Hospital"))])
add("Лондон", "Собор Св. Павла", "church", 120, "Здешняя церковь св. Павла почти столько же славна, как римская св. Петра", "verified_wiki",
    survives="survives", sources=[S("Wikipedia: St Paul's Cathedral", WP("en", "St_Paul's_Cathedral"))])
add("Виндзор", "Виндзорский парк", "landmark", 121, "в пять часов, своротив немного с большой дороги, вступили в Виндзорский парк", "verified_wiki",
    survives="survives", sources=[S("Wikipedia: Windsor Great Park", WP("en", "Windsor_Great_Park"))])
add("Лондон", "Воксхолл-гарденс", "landmark", 123, "я описываю вам славный английский Воксал", "verified_wiki",
    survives="lost", now_what="закрыт 1859; Spring Gardens (парк)", sources=[S("Wikipedia: Vauxhall Gardens", WP("en", "Vauxhall_Gardens"))])
add("Лондон", "Ранела (Ranelagh Gardens, ротонда)", "landmark", 126, "вошли в большую круглую залу, прекрасно о", "verified_wiki",
    survives="lost", now_what="ротонда снесена 1805; сады Королевского госпиталя в Челси", sources=[S("Wikipedia: Ranelagh Gardens", WP("en", "Ranelagh_Gardens"))])
add("Лондон", "Вестминстер-холл (процесс Гастингса)", "landmark", 130, "Славная Вестминстерская зала (Westminster-hall) построена еще в XI веке", "verified_wiki",
    survives="survives", sources=[S("Wikipedia: Westminster Hall", WP("en", "Westminster_Hall"))])
add("Ричмонд", "Загородный дом знакомого", "house", 117, None, "book_only", notes="Ночевал у знакомого; лицо и дом не установлены.")

# fix truncated quote
for e in E:
    if e["passage_seq"] == 126:
        e["book_quote"] = "в десятом часу вошли в большую круглую залу"
    q = e["book_quote"]
    if q: assert len(q.split()) <= 25, q

os.makedirs(OUT, exist_ok=True)
with open(f"{OUT}/places-karamzin.jsonl", "w", encoding="utf-8") as f:
    for e in E: f.write(json.dumps(e, ensure_ascii=False) + "\n")

MARK = {"verified_source": "✅", "verified_wiki": "✅", "book_only": "📖", "unverified": "❓", "disputed": "⚖️"}
from collections import Counter, OrderedDict
c = Counter(e["status"] for e in E)
L = ["# Карамзин — адреса: где жил и где бывал (1789–1790)", "",
     f"Всего мест: {len(E)}. " + ", ".join(f"{k}: {v}" for k, v in c.most_common()) + ".",
     "Даты в книге — по юлианскому календарю. ✅ подтверждено источником / Википедией · 📖 только книга · ❓ не проверено · ⚖️ спорно.",
     "Машинная версия: `places-karamzin.jsonl`.", ""]
groups = OrderedDict()
for e in E: groups.setdefault(e["city"], []).append(e)
for city, es in groups.items():
    L += [f"## {city}", "", "| | место | тип | письмо | цитата | адрес сейчас | сохранность / что сейчас |", "|---|---|---|---|---|---|---|"]
    for e in es:
        nm = e["name_then"] + (f" ({e['person']})" if e["person"] else "")
        q = f"«{e['book_quote']}»" if e["book_quote"] else "—"
        now = ((e["survives"] or "") + ("; " + e["now_what"] if e["now_what"] else "")).strip("; ")
        L.append(f"| {MARK[e['status']]} | {nm} | {e['kind']} | {e['passage_seq']} | {q} | {e['address_now'] or '—'} | {now or '—'} |")
    L.append("")
L += ["## Пробелы", "",
      "- Не найдены трактиры: Гота «Колокольчик», Франкфурт «Звезда», Эрфурт (без имени), Дрезден (почтовый двор), Лейпциг «у Мемеля», Женева «Золотые весы», Лондон (французский трактир), Ивердон, Веве.",
      "- Только улица, без дома: Берлин Brüderstraße, Париж rue Guénégaud (Hôtel Britannique не опознан), Лондон Oxford Street у Cavendish Square.",
      "- Нужна сверка: Цюрих «Ворон» (точный адрес у Шиффленде), Берн и Шафхаузен «Корона» (тождество с нынешними), Лозанна «Олень», Лейпциг «Голубой ангел» (название/номер), дома Виланда и Гердера, дом Вейсе (1789 — до покупки имения), номер дома Канта и его координаты.",
      "- Нет цитаты книги: Лозанна «Олень», Веве, Ивердон, Ричмонд, Опера (Париж), Нац. собрание, Тиргартен — дозаполнить из passages.jsonl.",
      "- Для знаменитых мест (соборы, дворцы, сады) Wikidata и координаты не ставились — дозаполнить загрузчиком из Wikidata.",
      "- Лондонские театры (Хеймаркет, Итальянская опера), Royal Exchange, Тауэр, Твикенхем, Шантийи, Марли, Нотр-Дам, Отель-Дьё и парижские театры (Théâtre-Français, Italiens, Monsieur, Variétés) — упомянуты в книге, в каталог пока не внесены.",
      ]
open(f"{OUT}/places-karamzin.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(E), dict(c))
