import json, re, os, sys
ROOT = r'C:\Users\admin\OneDrive\dev\ltsgo'
OUT = os.path.join(ROOT, r'kb\staging\goncharov-pallada\p01-09')
os.makedirs(OUT, exist_ok=True)
CB = 'agent:pallada-p01-09'
J = 'goncharov-1852'
BK = 'goncharov-pallada'
BODY = {}
for l in open(os.path.join(ROOT, r'texts\goncharov-pallada\passages.jsonl'), encoding='utf8'):
    r = json.loads(l); BODY[r['seq']] = r['body']
ERR = []

def chk(seq, q):
    if q not in BODY[seq]:
        ERR.append(f'NOT IN p{seq}: {q[:80]}')
    return q

def S(seq, frag):
    """full sentence of body[seq] containing frag (exact substring)."""
    b = BODY[seq]; i = b.find(frag)
    if i < 0:
        ERR.append(f'FRAG NOT IN p{seq}: {frag[:80]}'); return frag
    def is_end(k):
        c = b[k]
        if c == '\n': return True
        if c in '!?' : return k+1 >= len(b) or b[k+1] in ' \n"»'
        if c == '.':
            if k+1 < len(b) and b[k+1] not in ' \n"»': return False
            # initials like "В.А." / "г."
            if k >= 1 and b[k-1].isupper() and (k < 2 or b[k-2] in ' .\n'): return False
            if b[k-3:k+1] in (' св.', ' г.', ' т.'): return False
            return True
        return False
    s = i
    while s > 0 and not is_end(s-1): s -= 1
    e = i + len(frag)
    if is_end(e-1): return b[s:e].strip().lstrip('"- ').strip()
    while e < len(b) and not is_end(e): e += 1
    if e < len(b) and b[e] != '\n': e += 1
    while e < len(b) and b[e] in '"»': e += 1
    t = b[s:e].strip().lstrip('"- ').strip()
    if len(t) > 420:  # too long: fall back to fragment
        t = frag
    return t

WIKI = {}
for k, v in json.load(open('full.json', encoding='utf8')).items():
    WIKI[k] = v
for k, v in json.load(open('ex_en_6662.json', encoding='utf8')).items():
    WIKI['en:' + k] = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
def wurl(lang, title):
    return f'https://{lang}.wikipedia.org/wiki/' + title.replace(' ', '_')
def wchk(lang, title, q):
    t = WIKI.get(f'{lang}:{title}')
    if t is None: ERR.append(f'WIKI TEXT MISSING {lang}:{title}')
    elif q not in t: ERR.append(f'WIKI QUOTE NOT FOUND {lang}:{title}: {q[:70]}')
    return q

# ---------------- entities ----------------
E = []
def ent(key, kind, wd, ru, en, lat=None, lon=None, gp=None, born=None, died=None, starts=None, ends=None,
        pres=None, status=None, parent=None, then=None, meta=None):
    if status is None: status = 'verified_wiki' if wd else 'book_only'
    E.append(dict(key=key, kind=kind, wikidata=wd, name={'ru': ru, 'en': en},
                  names_then=[{'name': n, 'lang': 'ru', 'until': None} for n in (then or [])],
                  parent_key=parent, lat=lat, lon=lon, geo_precision=gp, born=born, died=died,
                  starts=starts, ends=ends, preservation=pres, status=status, meta=meta or {}, created_by=CB))

P = 'person'
ent('goncharov', P, 'Q189665', 'Иван Александрович Гончаров', 'Ivan Goncharov', born='1812-06-18', died='1891-09-27',
    meta={'role': 'author; secretary to the admiral'})
ent('putyatin', P, 'Q957601', 'Евфимий Васильевич Путятин', 'Yevfimy Putyatin', born='1803-11-20', died='1883-10-28',
    meta={'role': 'vice-admiral, head of the mission', 'book_name': 'адмирал (по имени в книге не назван)'})
ent('posyet', P, 'Q3198773', 'Константин Николаевич Посьет', 'Konstantin Posyet', born='1819-12-21', died='1899-04-26', then=['Посьет'])
ent('unkovsky', P, 'Q2025113', 'Иван Семёнович Унковский', 'Ivan Unkovsky', born='1822-03-29', died='1886-08-11',
    meta={'role': 'commander of the frigate'})
ent('goshkevich', P, 'Q2493535', 'Иосиф Антонович Гошкевич', 'Iosif Goshkevich', born='1814-04-04', died='1875-05-03',
    then=['Осип Антонович Гошкевич'])
ent('avvakum-chestnoy', P, 'Q4055424', 'Аввакум (Честной)', 'Avvakum (Chestnoy)', born='1801-09-18', died='1866-03-10', then=['отец Аввакум'])
ent('voin-rimsky-korsakov', P, 'Q4394687', 'Воин Андреевич Римский-Корсаков', 'Voin Rimsky-Korsakov', born='1822-07-14', died='1871-11-04',
    then=['Воин Андреевич Корсаков', 'В.А. Корсаков'])
ent('ivan-butakov', P, 'Q4100153', 'Иван Иванович Бутаков', 'Ivan Butakov', born='1822-03-10', died='1882-04-30')
ent('schlippenbach', P, 'Q28358711', 'Александр Егорович Шлиппенбах', 'Alexander von Schlippenbach', born='1830-07-13', died='1903-10-01',
    then=['барон Шлипенбах'])
ent('kolokoltsov', P, 'Q4228284', 'Александр Александрович Колокольцов', 'Alexander Kolokoltsov', born='1833-09-15', died='1904-10-01',
    then=['Колокольцев'])
ent('tikhmenev', P, None, 'Пётр Александрович Тихменев', 'Pyotr Tikhmenev', meta={'role': 'officer, mess manager'})
ent('krudener', P, None, 'барон Николай Александрович Криднер (Крюднер)', 'Baron Nikolai Alexandrovich Krüdener', status='verified_source', then=['Криднер', 'барон Крюднер'], meta={'role': 'officer', 'rank': 'лейтенант', 'note': 'гвардейский экипаж, флигель-адъютант великого князя Константина Николаевича; в Wikidata нет; не путать с генералом Николаем Павловичем Криденером (Q2471459)', 'source': 'Гончаров И. А. ПСС, т. 3 (СПб., 2000), примечания к «Фрегату „Паллада“», с. 429', 'source_url': 'http://feb-web.ru/feb/gonchar/texts/gon97/g03/g03-391-.htm', 'source_quote': 'барон Николай Александрович Крюднер (Криднер)'})
ent('boltin', P, None, 'мичман Болтин', 'Midshipman Boltin')
ent('losev', P, None, 'капитан Лосев', 'Captain Losev')
ent('savich', P, None, 'Н.Н. Савич', 'N. N. Savich', meta={'role': 'lieutenant'})
ent('zelenoy', P, None, 'Зеленый (офицер «Паллады»)', 'Zelenoy (officer of the Pallada)', status='unverified',
    meta={'note': 'candidate Q15066993 (А.А. Зеленой, later minister) rejected: ruwiki gives no service on the Pallada'})
ent('l-a-popov', P, None, 'Л.А. Попов', 'L. A. Popov', meta={'role': 'navigating officer'},
    status='unverified')
ent('weyrich', P, None, 'Вейрих', 'Weyrich', meta={'role': 'ship doctor, German'})
ent('faddeev', P, None, 'Фаддеев', 'Faddeev', meta={'role': "the author's orderly (sailor)"})
ent('madeira-consul', P, None, 'русский консул на Мадейре', 'Russian consul at Madeira', meta={'note': 'Portuguese by birth, wine merchant; unnamed'})
ent('commodore-talbot', P, None, 'коммодор Тальбот', 'Commodore Talbot', status='unverified', meta={'note': 'British squadron chief at Simonstown per the book; not identified'})
ent('waterloo-veteran', P, None, 'старик-француз, ветеран Ватерлоо', 'French veteran of Waterloo at Simonstown')
ent('mrs-welch', P, None, 'мистрис Вельч', 'Mrs Welch', meta={'role': "hostess of Welch's hotel, Cape Town"})
ent('caroline', P, None, 'Каролина', 'Caroline', meta={'role': "Welch's hotel"})
ent('richard-malay', P, None, 'малаец Ричард', 'Richard (Malay servant)')
ent('dr-whetherhead', P, None, 'доктор Ведерхед', 'Dr Whetherhead', status='unverified')
ent('vandik', P, None, 'Вандик', 'Vandik (coachman-guide)')
ent('ferstfeld', P, None, 'Ферстфельд', 'Ferstfeld', meta={'role': 'local minister at Stellenbosch'})
ent('andrew-geddes-bain', P, 'Q504836', 'Эндрю Геддес Бейн', 'Andrew Geddes Bain', born='1797-06-11', died='1864-10-20', then=['Бен'])
ent('siyolo', P, None, 'Сейоло (Сийоло)', 'Siyolo', status='unverified', then=['Сейоло'],
    meta={'note': 'Xhosa chief captured in the 8th Frontier War; no Wikidata item found'})
ent('colonel-mackinnon', P, None, 'полковник Меклин', 'Colonel "Meklin"', status='unverified',
    meta={'note': 'possibly Col. George Mackinnon; not verified'})
ent('wellington', P, 'Q131691', 'Артур Уэлсли, герцог Веллингтон', 'Duke of Wellington', born='1769-05-01', died='1852-09-14')
ent('hoo-ah-kay', P, 'Q18658123', 'Ху А Кей (Вампоа)', 'Hoo Ah Kay (Whampoa)', born='1816', died='1880-03-27', then=['Вампоа'])
ent('george-bonham', P, 'Q681359', 'Джордж Бонэм', 'Sir George Bonham', born='1803-09-07', died='1863-10-08', then=['сэр Бонэм'])
ent('nathaniel-savory', P, 'Q11316751', 'Натаниэль Сэвори', 'Nathaniel Savory', born='1794-07-31', died='1874-04-10', then=['Севри', 'Севрэ'])
ent('matthew-c-perry', P, 'Q61855', 'Мэтью Перри', 'Matthew C. Perry', born='1794-04-10', died='1858-03-04')
ent('hk-italian-bishop', P, None, 'итальянский епископ в Гонконге', 'Italian bishop at Hong Kong', status='unverified')

V = 'vessel'
ent('frigate-pallada', V, 'Q2026091', 'фрегат «Паллада»', 'Russian frigate Pallada', starts='1832', ends='1856', pres='lost')
ent('schooner-vostok', V, 'Q11352192', 'шхуна «Восток»', 'Schooner Vostok (1852)', then=['шкуна "Восток"'])
ent('hms-camperdown', V, 'Q5634669', 'HMS Camperdown (бывш. HMS Trafalgar, 1820)', 'HMS Trafalgar (1820), renamed Camperdown', pres='lost', then=['Кемпердоун'])
ent('corvette-olivutsa', V, None, 'корвет «Оливуца»', 'Corvette Olivutsa', status='unverified')
ent('transport-knyaz-menshikov', V, None, 'транспорт «Князь Меньшиков»', 'Transport Knyaz Menshikov', status='unverified',
    meta={'note': 'Russian-American Company transport'})

O = 'organisation'
ent('jardine-matheson', O, 'Q1683452', 'Jardine Matheson', 'Jardine Matheson', then=['Джердин и Маттисон'])

EV = 'event'
ent('wellington-funeral', EV, None, 'Похороны герцога Веллингтона', 'Funeral of the Duke of Wellington', starts='1852-11-18', status='unverified',
    meta={'note': 'date is gregorian, from general knowledge, not quoted; book only mentions the procession'})
ent('eighth-xhosa-war', EV, 'Q20612501', 'Восьмая пограничная война (с коса)', 'Eighth Xhosa War', starts='1850', ends='1853')
ent('equator-crossing-1853', EV, None, 'Пересечение экватора «Палладой»', 'Pallada crosses the equator')
ent('cholera-1852', EV, None, 'Холера на фрегате', 'Cholera on board the Pallada')
ent('typhoon-1853', EV, None, 'Тайфун 8–9 июля 1853', 'Typhoon of 8–9 July 1853')

PL = 'place'
def pl(key, wd, ru, en, lat=None, lon=None, gp=None, **kw):
    ent(key, kw.pop('kind', PL), wd, ru, en, lat, lon, gp, **kw)
pl('kronstadt', 'Q155863', 'Кронштадт', 'Kronstadt', 59.9908, 29.7747, 'city')
pl('saint-petersburg', 'Q656', 'Санкт-Петербург', 'Saint Petersburg', 59.9375, 30.3086, 'city')
pl('gotland', 'Q1027830', 'Готланд', 'Gotland', 57.5, 18.55, 'region')
pl('oresund', 'Q104662', 'Эресунн (Зунд)', 'Øresund', 55.75, 12.75, 'region', then=['Зунд'])
pl('kattegat', 'Q131716', 'Каттегат', 'Kattegat', 56.75, 11.5, 'region')
pl('skagerrak', 'Q1695', 'Скагеррак', 'Skagerrak', 57.75, 9.0, 'region')
pl('dogger-bank', 'Q465816', 'Доггер-банка', 'Dogger Bank', 55.25, 3.5, 'region')
pl('dover', 'Q179224', 'Дувр', 'Dover', 51.1295, 1.3089, 'city')
pl('spithead', 'Q1783560', 'Спитхед', 'Spithead', 50.7514, -1.1367, 'district', then=['Спитгедский рейд'])
pl('isle-of-wight', 'Q9679', 'остров Уайт', 'Isle of Wight', 50.67, -1.27, 'region', then=['остров Байт'])
pl('portsmouth', 'Q72259', 'Портсмут', 'Portsmouth', 50.8058, -1.0872, 'city')
pl('gosport', 'Q936263', 'Госпорт', 'Gosport', 50.7951, -1.1242, 'city', then=['Гос-порт'])
pl('india-arms-gosport', None, 'гостиница India Arms, Госпорт', 'India Arms hotel, Gosport', kind='building', parent='gosport', status='unverified')
pl('london', 'Q84', 'Лондон', 'London', 51.5072, -0.1275, 'city')
pl('st-pauls-cathedral', 'Q173882', 'Собор Святого Павла', "St Paul's Cathedral", 51.5138, -0.0983, 'exact', kind='building', parent='london', pres='intact')
pl('westminster-abbey', 'Q5933', 'Вестминстерское аббатство', 'Westminster Abbey', 51.4994, -0.1274, 'exact', kind='building', parent='london', pres='intact')
pl('british-museum', 'Q6373', 'Британский музей', 'British Museum', 51.5194, -0.1269, 'exact', kind='building', parent='london', then=['Британский музеум'])
pl('london-zoo', 'Q270263', 'Лондонский зоопарк', 'London Zoo', 51.5356, -0.1558, 'exact', parent='london')
pl('thames-tunnel', 'Q1190691', 'Тоннель под Темзой', 'Thames Tunnel', 51.5031, -0.0544, 'exact', kind='building', parent='london')
pl('lizard-point', 'Q1808092', 'мыс Лизард', 'Lizard Point', 49.9661, -5.2019, 'exact', then=['Лизард'])
pl('madeira', 'Q26253', 'Мадейра', 'Madeira', 32.75, -16.95, 'region', then=['Мадера'])
pl('funchal', 'Q25444', 'Фуншал', 'Funchal', 32.65, -16.9167, 'city', parent='madeira', then=['Фунчал'])
pl('cape-verde', 'Q1011', 'Кабо-Верде (острова Зелёного Мыса)', 'Cape Verde', 15.0, -24.0, 'region')
pl('santiago-cape-verde', 'Q108448', 'остров Сантьягу', 'Santiago, Cape Verde', 15.08, -23.62, 'region', parent='cape-verde', then=['С.-Яго', 'Сант-Яго'])
pl('praia', 'Q3751', 'Прая', 'Praia', 14.9177, -23.5092, 'city', parent='santiago-cape-verde', then=['Порто-Прайя'])
pl('cape-of-good-hope', 'Q4092', 'мыс Доброй Надежды', 'Cape of Good Hope', -34.3568, 18.4740, 'exact')
pl('false-bay', 'Q1394912', 'Фолс-Бей', 'False Bay', -34.2, 18.65, 'region', then=['Фальсбэй'])
pl('simons-town', 'Q1013370', 'Саймонстаун', "Simon's Town", -34.1932, 18.4359, 'city', then=['Саймонстоун'])
pl('fountain-hotel-simonstown', None, 'гостиница Fountain hotel, Саймонстаун', 'Fountain Hotel, Simon\'s Town', kind='building', parent='simons-town', status='unverified')
pl('cape-town', 'Q5465', 'Кейптаун', 'Cape Town', -33.9253, 18.4239, 'city', then=['Капштат'])
pl('welchs-hotel', None, 'гостиница Вельч (Welch\'s hotel), Кейптаун', "Welch's hotel, Cape Town", kind='building', parent='cape-town', status='unverified')
pl('table-mountain', 'Q213360', 'Столовая гора', 'Table Mountain', -33.9628, 18.4097, 'approx')
pl('lions-head', 'Q1718867', 'Львиная голова', "Lion's Head", -33.9353, 18.3889, 'approx')
pl('devils-peak', 'Q917040', 'Чёртов пик', "Devil's Peak", -33.9515, 18.4370, 'approx')
pl('companys-garden', 'Q590259', 'Ботанический сад Кейптауна (Company\'s Garden)', "Company's Garden", -33.9270, 18.4170, 'exact', parent='cape-town', status='unverified',
   meta={'note': 'book says «Ботанический сад»; identification with Company\'s Garden is probable'})
pl('wynberg', 'Q667463', 'Винберг', 'Wynberg', -34.0042, 18.4703, 'city', then=['Винберг'])
pl('stellenbosch', 'Q5460', 'Стелленбос', 'Stellenbosch', -33.9367, 18.8614, 'city', then=['Стелленбош'])
pl('elsenburg', None, 'ферма Эльзенбург', 'Elsenburg farm', -33.84, 18.83, 'approx', status='unverified', then=['Эльзенборг'],
   meta={'note': 'candidate Q17088933 (Elsenburg Agricultural Training Institute) not confirmed'})
pl('paarl', 'Q1018144', 'Паарл', 'Paarl', -33.7242, 18.9558, 'city', then=['Паарль'])
pl('wellington-south-africa', 'Q1534385', 'Веллингтон (ЮАР)', 'Wellington, Western Cape', -33.6333, 18.9833, 'city')
pl('bainskloof-pass', 'Q2422542', 'перевал Бейнсклоф', 'Bainskloof Pass', -33.58, 19.10, 'approx', pres='intact')
pl('worcester-south-africa', 'Q1025649', 'Вустер (ЮАР)', 'Worcester, Western Cape', -33.645, 19.4436, 'city', then=['Устер'])
pl('christmas-island', 'Q31063', 'остров Рождества', 'Christmas Island', -10.49, 105.62, 'region')
pl('sunda-strait', 'Q192790', 'Зондский пролив', 'Sunda Strait', -6.0, 105.75, 'region')
pl('java', 'Q3757', 'Ява', 'Java', -7.5, 110.0, 'region')
pl('anjer', 'Q613898', 'Аньер (Анжер)', 'Anyer (Anjer)', -6.0641, 105.9207, 'city', parent='java', then=['Анжер'])
pl('batavia', 'Q1199713', 'Батавия', 'Batavia', -6.13, 106.81, 'city', parent='java')
pl('singapore', 'Q334', 'Сингапур', 'Singapore', 1.29, 103.85, 'city')
pl('hong-kong', 'Q8646', 'Гонконг', 'Hong Kong', 22.28, 114.16, 'city', then=['Гон-Конг', 'Хонкон'])
pl('victoria-hong-kong', 'Q963152', 'Виктория (Гонконг)', 'Victoria, Hong Kong', 22.2833, 114.15, 'district', parent='hong-kong')
pl('guangzhou', 'Q16572', 'Гуанчжоу (Кантон)', 'Guangzhou (Canton)', 23.13, 113.26, 'city', then=['Кантон'])
pl('macau', 'Q14773', 'Макао', 'Macau', 22.19, 113.54, 'city')
pl('south-china-sea', 'Q37660', 'Южно-Китайское море', 'South China Sea', 12.0, 113.0, 'region', then=['Китайское море'])
pl('batan-island', 'Q1437219', 'остров Батан', 'Batan Island', 20.45, 121.97, 'region', then=['Батан'])
pl('bonin-islands', 'Q243634', 'острова Огасавара (Бонин)', 'Bonin Islands', 27.0, 142.2, 'region', then=['Бонин-Сима'])
pl('chichijima', 'Q1072125', 'Титидзима (остров Пиль)', 'Chichijima (Peel Island)', 27.0667, 142.2083, 'region', parent='bonin-islands',
   then=['Пиль', 'порт Ллойд'])
pl('nagasaki', 'Q38234', 'Нагасаки', 'Nagasaki', 32.75, 129.88, 'city')

# ---------------- stops ----------------
ST = []
def stop(seq_hint, place, arr, dep, prec, dit, tr, pf, pt, kind, status, note=None):
    ST.append(dict(journey_key=J, seq_hint=seq_hint, place_key=place, arrived=arr, departed=dep, calendar='julian',
                   date_precision=prec, date_in_text=dit, transport_in=tr, passage_from=pf, passage_to=pt, kind=kind,
                   status=status, note=note))
stop(1, 'kronstadt', None, '1852-10-07', 'day', chk(2, 'Наконец 7 октября фрегат "Паллада" снялся с якоря'), None, 2, 2, 'stay', 'book_only')
stop(2, 'gotland', '1852-10', '1852-10', 'month', chk(2, 'Мы прошли Готланд.'), 'sail', 2, 2, 'pass', 'book_only')
stop(3, 'oresund', '1852-10', '1852-10', 'month', chk(2, 'Мы вошли в Зунд'), 'sail', 2, 2, 'stay', 'book_only',
     'anchored in the Sound; cholera on board, three buried')
stop(4, 'kattegat', '1852-10', '1852-10', 'month', chk(2, 'пустились в Каттегат и Скагеррак, которые пробежали в сутки'), 'sail', 2, 2, 'pass', 'book_only')
stop(5, 'skagerrak', '1852-10', '1852-10', 'month', 'пустились в Каттегат и Скагеррак, которые пробежали в сутки', 'sail', 2, 2, 'pass', 'book_only')
stop(6, 'dogger-bank', '1852-10', '1852-10', 'month', None, 'sail', 2, 2, 'pass', 'book_only')
stop(7, 'spithead', '1852-10-30', None, 'day', chk(2, 'Ночью мы бросили якорь на Спитгедском рейде, между островом Байтом и крепостными стенами Портсмута.'),
     'sail', 2, 2, 'stay', 'unverified', 'arrival date not in the passage; 30 Oct from ru article on the book; other sources give November')
stop(8, 'portsmouth', '1852-10', '1853-01-06', 'day', chk(3, 'С 6 по 18 января 1853'), 'sail', 2, 3, 'stay', 'book_only',
     'frigate docked for repairs, crew moved to HMS Camperdown; departure 6 Jan from vol.I ch.3 heading')
stop(9, 'london', '1852-11', '1852-11', 'month', chk(2, 'Меня выручила из недоумения процессия похорон Веллингтона.'), 'rail', 2, 2, 'stay', 'book_only',
     'side trip from Portsmouth by railway')
stop(10, 'lizard-point', '1853-01-11', '1853-01-11', 'day', chk(2, 'Виден Эддистонский маяк и гладкий, безотрадный утес Лизарда.'), 'sail', 2, 3, 'pass', 'book_only')
stop(11, 'funchal', '1853-01-18', '1853-01-18', 'day', chk(3, '18-го января, восьмой день по выходе из Англии'), 'sail', 3, 3, 'stay', 'book_only')
stop(12, 'praia', '1853-01-25', '1853-01', 'day', chk(4, 'Ровно через неделю после прогулки на Мадере, также в воскресенье'), 'sail', 4, 4, 'stay', 'book_only',
     'date computed: a week after Madeira (18 Jan)')
stop(13, 'simons-town', '1853-03-10', '1853-04-12', 'day', chk(5, 'Наконец 10 марта, часу в шестом вечера'), 'sail', 5, 5, 'stay', 'disputed',
     'book: 10 March; ruwiki (Паллада (фрегат)) says 24 March 1853; departure: «На другой день, 12-го апреля, ушли и мы.»')
stop(14, 'cape-town', '1853-03', '1853-04', 'month', chk(5, "это Welch's hotel"), 'carriage', 5, 5, 'stay', 'book_only')
stop(15, 'stellenbosch', '1853-03', '1853-04', 'month', None, 'carriage', 5, 5, 'stay', 'book_only',
     'inland trip by carts: Stellenbosch, Elsenburg, Paarl, Wellington, Bainskloof, Worcester and back')
stop(16, 'paarl', '1853-03', '1853-04', 'month', None, 'carriage', 5, 5, 'stay', 'book_only')
stop(17, 'wellington-south-africa', '1853-03', '1853-04', 'month', chk(5, 'въехали в Веллингтон'), 'carriage', 5, 5, 'stay', 'book_only')
stop(18, 'bainskloof-pass', '1853-03', '1853-04', 'month', None, 'carriage', 5, 5, 'pass', 'book_only')
stop(19, 'worcester-south-africa', '1853-03', '1853-04', 'month', chk(5, 'поехали дальше, к Устеру'), 'carriage', 5, 5, 'stay', 'book_only')
stop(20, 'christmas-island', '1853-05-13', '1853-05-13', 'day', chk(6, '13-го мая мы прошли в виду необитаемого острова Рождества'), 'sail', 6, 6, 'pass', 'book_only')
stop(21, 'anjer', '1853-05-17', '1853-05-18', 'day', chk(6, 'наконец 17 мая нашего стиля'), 'sail', 6, 6, 'stay', 'book_only',
     '«На другой день утром мы ушли, не видав ни одного европейца, которых всего трое в Анжере.»')
stop(22, 'singapore', '1853-05-24', '1853-06-02', 'day', chk(7, 'Это было 24-го мая, часов в одиннадцать утра'), 'sail', 7, 7, 'stay', 'book_only')
stop(23, 'hong-kong', '1853-06-12', '1853-06-26', 'day', chk(9, 'Мы вышли из Гон-Конга 26 июня'), 'sail', 8, 9, 'stay', 'unverified',
     'arrival not dated in the book; 12 June from ruwiki «12 июня «Паллада» пришла в Гонконг.»')
stop(24, 'batan-island', '1853-07-07', '1853-07-07', 'day', chk(9, '7-го числа вечером мы подошли к главному из островов, Батану'), 'sail', 9, 9, 'pass', 'book_only')
stop(25, 'chichijima', '1853-07', '1853-08-04', 'day', chk(9, 'Наконец 4-го августа, часа в четыре утра'), 'sail', 9, 9, 'stay', 'book_only',
     'Port Lloyd; arrival after the typhoon of 8-9 July, not dated in the book (departure 4 Aug)')
stop(26, 'nagasaki', None, None, 'unknown', None, 'sail', 9, 9, 'mention_only', 'book_only', 'next destination, outside passages 1-9')

# ---------------- links ----------------
LK = []
def link(f, t, kind, seq, q, during=J, status='book_only', note=None):
    LK.append(dict(from_key=f, to_key=t, kind=kind, passage_seq=seq, during=during, status=status,
                   quote=chk(seq, q) if q else None, note=note))
G = 'goncharov'
link(G, 'frigate-pallada', 'travelled_with', 2, 'Наконец 7 октября фрегат "Паллада" снялся с якоря')
link(G, 'krudener', 'travelled_with', 2, 'Барон Криднер в трех шагах от меня насвистывал под шум бури мотив из оперы.')
for k in ('schlippenbach', 'boltin', 'kolokoltsov'):
    link(G, k, 'travelled_with', 2, 'ко мне подошли три офицера: барон Шлипенбах, мичманы Болтин и Колокольцев -- мои будущие спутники и отличные приятели.')
link(G, 'faddeev', 'travelled_with', 2, 'Это был Фаддеев, с которым я уже давно познакомил вас.')
link(G, 'tikhmenev', 'travelled_with', 2, 'распорядителя офицерского стола П.А. Тихменева')
link(G, 'voin-rimsky-korsakov', 'travelled_with', 2, 'Воин Андреевич Корсаков читал ее и дал мне прочесть')
link(G, 'avvakum-chestnoy', 'travelled_with', 2, '"Нет, -- возразил отец Аввакум, -- слышите, вопли!')
link(G, 'losev', 'travelled_with', 3, 'Присутствовавшие -- капитан Лосев, барон Криднер и кто-то еще')
link('unkovsky', G, 'host_of', 3, 'Любезный, гостеприимный хозяин Иван Семенович Унковский')
link(G, 'goshkevich', 'travelled_with', 3, 'О.А. Гошкевич, которого мы звали переводчиком')
link(G, 'ivan-butakov', 'travelled_with', 3, '"А это что? Посмотрите-ка, ведь это наш зеленый лук!" -- сказал Бутаков')
link(G, 'madeira-consul', 'met', 3, 'Консул, родом португалец')
link(G, 'l-a-popov', 'travelled_with', 4, '22 января Л.А. Попов, штурманский офицер, за утренним чаем сказал')
link(G, 'putyatin', 'travelled_with', 4, 'адмирал вышел с книгой и вслух прочел морской устав Петра Великого',
     note='the admiral is never named in the book; identified as Putyatin')
link('frigate-pallada', 'equator-crossing-1853', 'took_part', 4, 'в пять часов фрегат пересек экватор в 18° западной долготы')
link('frigate-pallada', 'cholera-1852', 'took_part', 2, 'На фрегате открылась холера, и мы, дойдя только до Дании, похоронили троих людей')
link(G, 'wellington-funeral', 'saw', 2, 'Меня выручила из недоумения процессия похорон Веллингтона.')
link(G, 'st-pauls-cathedral', 'visited', 2, 'пробрались в самую церковь св. Павла')
link(G, 'british-museum', 'visited', 2, 'пошел вслед за другими в Британский музеум')
link(G, 'westminster-abbey', 'visited', 2, 'наткнулся на великолепное прошедшее: на Вестминстерское аббатство')
link(G, 'london-zoo', 'visited', 2, 'целое утро обозрению зоологического сада')
link(G, 'thames-tunnel', 'visited', 2, 'туннель под Темзой')
link(G, 'hms-camperdown', 'stayed_at', 2, 'Мы мирно жили еще с неделю, по возвращении из Лондона в Портсмут, на "Кемпердоуне", большим обществом.')
link('india-arms-gosport', 'gosport', 'located_in', 2, 'очень хорошая гостиница Indiaarms')
link(G, 'commodore-talbot', 'saw', 5, 'В одном из лучших домов живет начальник эскадры, коммодор Тальбот.')
link(G, 'waterloo-veteran', 'met', 5, 'при Ватерлоо дрался с англичанами, взят ими, завезен сюда')
link(G, 'fountain-hotel-simonstown', 'visited', 5, 'мы зашли в здешнюю гостиницу Fountain hotel')
link(G, 'welchs-hotel', 'stayed_at', 5, "это Welch's hotel")
link('mrs-welch', G, 'host_of', 5, 'мистрис Вельч и Каролина')
link(G, 'caroline', 'met', 5, 'мистрис Вельч и Каролина')
link(G, 'richard-malay', 'met', 5, 'Малаец Ричард')
link(G, 'dr-whetherhead', 'met', 5, 'доктор Ведерхед')
link(G, 'vandik', 'travelled_with', 5, '"Проводник ваш по колонии, -- сказал Вандик, -- меня нанял ваш банкир, с двумя экипажами и с осьмью лошадьми.')
for k in ('krudener', 'zelenoy', 'posyet', 'weyrich', 'goshkevich'):
    link(G, k, 'travelled_with', 5, 'Я ехал с бароном Криднером и Зеленым, в другом "карте" сидели Посьет, Вейрих и Гошкевич.')
link(G, 'ferstfeld', 'met', 5, '"Г. Ферстфельд, местный диктор", -- сказал нам Посьет.')
link(G, 'elsenburg', 'visited', 5, 'Это была голландская ферма Эльзенборг, принадлежащая приятелю доктора.')
link(G, 'andrew-geddes-bain', 'met', 5, 'Мы отдали ему рекомендательное письмо от нашего банкира из Капштата.')
link('andrew-geddes-bain', 'bainskloof-pass', 'took_part', 5, 'Тут уже начиналось создание Бена -- шоссе.', note='Bain built the pass road')
link(G, 'siyolo', 'saw', 5, 'На одном лежал Сейоло, на другом его жена.')
link('siyolo', 'eighth-xhosa-war', 'took_part', 5, 'Сейоло -- один из второстепенных вождей. Он взят в плен в нынешнюю войну.')
link(G, 'schooner-vostok', 'visited', 5, '11 апреля вечером, при свете луны, мы поехали с Унковским и Посьетом на шлюпке к В.А. Корсакову на шкуну "Восток", которая снималась с якоря.')
link('voin-rimsky-korsakov', 'schooner-vostok', 'took_part', 5, 'к В.А. Корсакову на шкуну "Восток"', note='commander of the schooner')
link(G, 'savich', 'travelled_with', 6, '-- сказал мне Н.Н. Савич')
link(G, 'hoo-ah-kay', 'saw', 7, 'Здесь есть громкое коммерческое имя Вампоа.')
link(G, 'hk-italian-bishop', 'met', 8, 'итальянский епископ с несколькими монахами')
link(G, 'george-bonham', 'saw', 8, 'Зовут его сэр Бонэм (sir Bonham).')
link('jardine-matheson', 'hong-kong', 'located_in', 8, 'устроено торговое заведение, с верфью, Джердина и Маттисона')
link('frigate-pallada', 'typhoon-1853', 'took_part', 9, 'в ночи с 8-го на 9-е и все 9-е число июля, выходя из Китайского моря в Тихий океан')
link('savich', 'typhoon-1853', 'took_part', 9, 'лейтенант Савич гремел в рупор над ревом бури')
link(G, 'nathaniel-savory', 'met', 9, 'как нам подтвердил и сам Севри, или Севрэ, здешний старожил')
link(G, 'corvette-olivutsa', 'saw', 9, 'Корвет "Оливуца" и транспорт Американской компании "Князь Меньшиков".')
link(G, 'transport-knyaz-menshikov', 'saw', 9, 'Корвет "Оливуца" и транспорт Американской компании "Князь Меньшиков".')
for a, b in [('st-pauls-cathedral', 'london'), ('westminster-abbey', 'london'), ('british-museum', 'london'), ('thames-tunnel', 'london'),
             ('london-zoo', 'london'), ('welchs-hotel', 'cape-town'), ('fountain-hotel-simonstown', 'simons-town'),
             ('praia', 'santiago-cape-verde'), ('funchal', 'madeira'), ('anjer', 'java'), ('chichijima', 'bonin-islands'),
             ('victoria-hong-kong', 'hong-kong'), ('simons-town', 'false-bay')]:
    LK.append(dict(from_key=a, to_key=b, kind='located_in', passage_seq=None, during=None, status='verified_wiki' if a not in ('welchs-hotel', 'fountain-hotel-simonstown') else 'book_only', quote=None, note='geography'))

# ---------------- facts ----------------
F = []
def fact(ent_key, key, value, fc, status, seq=None, quote=None, url=None, title=None, layer='then', note=None, stop_ref=None, book=False):
    d = dict(key=key, layer=layer, lang='ru', value=value, fact_class=fc, status=status, source_url=url, source_title=title,
             passage_seq=seq, quote=quote, note=note, created_by=CB)
    if book: d = {'book_key': BK, **d}
    elif stop_ref: d = {'stop_ref': stop_ref, **d}
    else: d = {'entity_key': ent_key, **d}
    F.append(d)
def bf(e, key, value, fc, seq, q, **kw):  # book fact
    fact(e, key, value, fc, 'book_only', seq, chk(seq, q), **kw)
def wf(e, key, value, fc, lang, title, q, layer='then', status='verified_wiki', note=None):
    fact(e, key, value, fc, status, None, wchk(lang, title, q), wurl(lang, title), f'Википедия: {title}' if lang == 'ru' else f'Wikipedia: {title}', layer, note)

# wiki facts: people
wf('putyatin', 'wiki.nagasaki-arrival', 'Паллада пришла в Нагасаки 12 августа 1853 г.', 'history', 'ru', 'Путятин, Евфимий Васильевич',
   'Спустя месяц после первого визита Перри, 12 августа 1853 года «Паллада» прибыла в порт Нагасаки')
wf('posyet', 'wiki.role', 'Старший офицер и переводчик в миссии Путятина на «Палладе»', 'identity', 'ru', 'Посьет, Константин Николаевич',
   'Путятина на фрегате «Паллада» в качестве старшего офицера и переводчика документов')
wf('unkovsky', 'wiki.role', 'Командир фрегата «Паллада» (капитан-лейтенант)', 'identity', 'ru', 'Унковский, Иван Семёнович',
   'Флагманским кораблём эскадры — фрегатом «Паллада» — командовал капитан-лейтенант Иван Унковский.')
wf('goshkevich', 'wiki.role', 'Драгоман и советник миссии Путятина', 'identity', 'ru', 'Гошкевич, Иосиф Антонович',
   'В 1852 году отправлен в качестве драгомана и советника с миссией Евфимия Путятина в Японию на фрегате «Паллада».')
wf('avvakum-chestnoy', 'wiki.role', 'Священник фрегата «Паллада»', 'identity', 'ru', 'Аввакум (Честной)',
   'Во время экспедиции Аввакум исполнял также обязанности священнослужителя на фрегате «Паллада».')
wf('voin-rimsky-korsakov', 'wiki.role', 'Командир шхуны «Восток» в экспедиции Путятина', 'identity', 'ru', 'Римский-Корсаков, Воин Андреевич',
   'В 1852 году Воин Андреевич поступил в распоряжение адмирала Евфимия Путятина, был назначен командиром шхуны «Восток»')
wf('ivan-butakov', 'wiki.role', 'Старший офицер «Паллады» на переходе Кронштадт — Сингапур', 'identity', 'ru', 'Бутаков, Иван Иванович',
   'В должности старшего офицера 52-пушечного фрегата «Паллада» лейтенант Бутаков совершил в 1852 году переход из Кронштадта в Сингапур')
wf('schlippenbach', 'wiki.role', 'Перешёл на «Палладе» в Англию, затем старший офицер шхуны «Восток»', 'identity', 'ru', 'Шлиппенбах, Александр Егорович',
   'В октябре этого же года в составе команды фрегата «Паллада» перешёл в Англию, где вступил в должность старшего офицера шхуны «Восток».')
wf('kolokoltsov', 'wiki.role', 'Служил в экипаже фрегата «Паллада»', 'identity', 'ru', 'Колокольцов, Александр Александрович',
   'Зачислен в 23-й флотский экипаж, а затем в экипаж фрегата «Паллада».')
wf('andrew-geddes-bain', 'wiki.geology', 'Составил первую сводную геологическую карту Южной Африки (1852)', 'identity', 'en', 'Andrew Geddes Bain',
   'produced the first comprehensive geological map of South Africa in 1852')
wf('hoo-ah-kay', 'wiki.identity', 'Сингапурский купец Ху А Кей, известный как Вампоа', 'identity', 'en', 'Hoo Ah Kay', 'better known as Whampoa')
wf('nathaniel-savory', 'wiki.identity', 'Один из первых американских поселенцев на островах Бонин', 'identity', 'en', 'Nathaniel Savory',
   'one of the first American colonists who settled on the Bonin (Ogasawara) Islands')
# vessel
wf('frigate-pallada', 'wiki.departure', 'Вышла из Кронштадта 7 октября 1852 г., экипаж 426 человек', 'history', 'ru', 'Паллада (фрегат)',
   'Фрегат вышел из Кронштадта 7 октября 1852 года, укомплектованный экипажем из 426 матросов и офицеров.')
wf('frigate-pallada', 'wiki.hongkong', 'Пришла в Гонконг 12 июня 1853 г.', 'history', 'ru', 'Паллада (фрегат)', '12 июня «Паллада» пришла в Гонконг.')
wf('frigate-pallada', 'wiki.typhoon', 'Тайфун 9 июля на пути к островам Бонин', 'history', 'ru', 'Паллада (фрегат)',
   'На пути к островам Бонин, в районе Филиппинской впадины, 9 июля фрегат попал в свирепый тайфун.')
wf('frigate-pallada', 'wiki.bonin-departure', 'Ушла из порта Ллойд 4 августа, через 6 дней в Нагасаки', 'history', 'ru', 'Паллада (фрегат)',
   'После исправления повреждений отряд Путятина покинул порт Ллойд 4 августа и через 6 дней бросил якорь в средней гавани Нагасаки.')
wf('frigate-pallada', 'wiki.simonstown', 'По Википедии — вошла в Саймонстаун 24 марта 1853 (в книге — 10 марта)', 'history', 'ru', 'Паллада (фрегат)',
   'После 78-дневного перехода через Атлантику, 24 марта 1853 года «Паллада» вошла в бухту Саймонстаун', status='disputed',
   note='book (p5): «Наконец 10 марта, часу в шестом вечера»')
wf('frigate-pallada', 'now.fate', 'Затоплена экипажем в 1855 г. в Крымскую войну', 'preservation', 'en', 'Russian frigate Pallada',
   'She was scuttled by her own crew in the Crimean War due to the poor condition of her hull in 1855', layer='now')
wf('frigate-pallada', 'now.monument', 'Памятник на берегу бухты Постовой, где затоплен фрегат (1963)', 'preservation', 'ru', 'Паллада (фрегат)',
   'На берегу бухты Постовой, где затоплен фрегат, в октябре 1963 года был открыт памятник', layer='now')
wf('schooner-vostok', 'wiki.hongkong', 'Пришла на Гонконгский рейд в ночь на 12 июня 1853', 'history', 'ru', 'Восток (шхуна, 1852)',
   'На Гонконгский рейд «Восток» зашёл в ночь с 11 на 12 июня.')
wf('schooner-vostok', 'wiki.bonin', 'Пришла в порт Ллойд 20 июля 1853, застала там «Оливуцу»', 'history', 'ru', 'Восток (шхуна, 1852)',
   'Выдержав штиль и шторм, «Восток» 20 июля прибыл в порт Лойд (острова Бонин-Сима), где застал корвет «Оливуца».')
wf('hms-camperdown', 'wiki.rename', 'Переименован в HMS Camperdown 22 февраля 1825', 'identity', 'en', 'HMS Trafalgar (1820)',
   'She was renamed HMS Camperdown on 22 February 1825.')
wf('hms-camperdown', 'wiki.guardship', 'С 1854 — брандвахта в Портсмуте', 'history', 'en', 'HMS Trafalgar (1820)',
   'Camperdown was placed on harbour service as a guard ship at Portsmouth in 1854')
wf('hms-camperdown', 'now.fate', 'Разобран в Чарлтоне (Лондон)', 'preservation', 'en', 'HMS Trafalgar (1820)', 'was broken up at Charlton, London', layer='now')
wf('bainskloof-pass', 'wiki.built', 'Открыт в 1854, построен А. Г. Бейном с трудом заключённых', 'history', 'en', 'Bainskloof Pass',
   'opened in 1854, was constructed by road engineer Andrew Geddes Bain with the use of convict labour')
wf('bainskloof-pass', 'now.monument', 'Перевал — национальный памятник', 'preservation', 'en', 'Bainskloof Pass', 'Bainskloof Pass is now a national monument.', layer='now')
# book-level wiki fact
fact(None, 'wiki.route', 'Маршрут по статье о книге: Кронштадт → Портсмут (30 октября) → Мадейра (18 января 1853) → … мыс Доброй Надежды (10 марта)', 'history',
     'verified_wiki', None, wchk('ru', 'Фрегат «Паллада»', 'Кронштадт → Портсмут (30 октября) → Мадейра (18 января 1853)'),
     wurl('ru', 'Фрегат «Паллада»'), 'Википедия: Фрегат «Паллада»', book=True)

# book facts (then layer)
bf('goncharov', 'book.p02.departure', 'Фрегат «Паллада» снялся с якоря в Кронштадте 7 октября 1852', 'visit', 2, 'Наконец 7 октября фрегат "Паллада" снялся с якоря')
bf('frigate-pallada', 'book.p02.cholera', 'На фрегате открылась холера, до Дании похоронили троих', 'history', 2,
   'На фрегате открылась холера, и мы, дойдя только до Дании, похоронили троих людей')
bf('frigate-pallada', 'book.p02.dock', 'В Портсмуте фрегат ввели в док, людей перевели на «Кемпердоун»', 'history', 2,
   'фрегат втянули в гавань и ввели в док, а людей перевели на "Кемпердоун"')
bf('spithead', 'book.p02.anchor', 'Якорная стоянка между островом Уайт и стенами Портсмута', 'visit', 2,
   'Ночью мы бросили якорь на Спитгедском рейде, между островом Байтом и крепостными стенами Портсмута.')
bf('london', 'book.p02.wellington-funeral', 'Гончаров видел в Лондоне похоронную процессию Веллингтона', 'visit', 2,
   'Меня выручила из недоумения процессия похорон Веллингтона.')
bf('st-pauls-cathedral', 'book.p02.visit', 'Гончаров пробрался в собор Св. Павла', 'visit', 2, 'пробрались в самую церковь св. Павла')
bf('westminster-abbey', 'book.p02.visit', 'Гончаров посетил Вестминстерское аббатство', 'visit', 2, 'наткнулся на великолепное прошедшее: на Вестминстерское аббатство')
bf('british-museum', 'book.p02.visit', 'Гончаров ходил в Британский музей', 'visit', 2, 'пошел вслед за другими в Британский музеум')
bf('london-zoo', 'book.p02.visit', 'Утро в зоологическом саду', 'visit', 2, 'целое утро обозрению зоологического сада')
bf('thames-tunnel', 'book.p02.visit', 'Гончаров видел туннель под Темзой', 'visit', 2, 'туннель под Темзой')
bf('gosport', 'book.p02.hotel', 'В Госпорте — гостиница India Arms', 'trivia', 2, 'очень хорошая гостиница Indiaarms')
bf('lizard-point', 'book.p02.pass', 'Прошли мыс Лизард 11 января 1853', 'visit', 2,
   'Сегодня, 11-го января, утро ясное, море стихает. Виден Эддистонский маяк и гладкий, безотрадный утес Лизарда.')
bf('funchal', 'book.p03.arrival', 'Пришли на Мадейру 18 января 1853, на восьмой день от Англии', 'visit', 3, '18-го января, восьмой день по выходе из Англии, часов в 9 утра')
bf('madeira-consul', 'book.p03.identity', 'Русский консул на Мадейре — португалец, крупный виноторговец', 'identity', 3, 'Наш консул считается значительным виноторговцем')
bf('praia', 'book.p04.arrival', 'Пришли в Порто-Прайя через неделю после Мадейры, в воскресенье', 'visit', 4,
   'Ровно через неделю после прогулки на Мадере, также в воскресенье')
bf('praia', 'book.p04.perry', 'В Порто-Прайя стояли американские корветы, шедшие к эскадре Перри', 'trivia', 4, 'к эскадре, коммодора Перри')
bf('equator-crossing-1853', 'book.p04.equator', 'Фрегат пересёк экватор на 18° з. д.', 'transport', 4, 'в пять часов фрегат пересек экватор в 18° западной долготы')
bf('putyatin', 'book.p04.naval-code', 'Адмирал вслух читал морской устав Петра Великого', 'trivia', 4, 'адмирал вышел с книгой и вслух прочел морской устав Петра Великого')
bf('simons-town', 'book.p05.arrival', 'Пришли в Саймонстаун 10 марта 1853 около шести вечера', 'visit', 5, 'Наконец 10 марта, часу в шестом вечера')
bf('simons-town', 'book.p05.departure', 'Ушли из Саймонстауна 12 апреля 1853', 'visit', 5, 'На другой день, 12-го апреля, ушли и мы.')
bf('simons-town', 'book.p05.hotel', 'В Саймонстауне заходили в гостиницу Fountain hotel', 'trivia', 5, 'мы зашли в здешнюю гостиницу Fountain hotel')
bf('waterloo-veteran', 'book.p05.identity', 'Старик, дрался при Ватерлоо, взят англичанами в плен и завезён на мыс', 'trivia', 5,
   'при Ватерлоо дрался с англичанами, взят ими, завезен сюда')
bf('cape-town', 'book.p05.hotel', "В Кейптауне жили в гостинице Welch's hotel", 'visit', 5, "это Welch's hotel")
bf('elsenburg', 'book.p05.farm', 'Голландская ферма Эльзенборг, принадлежавшая приятелю доктора', 'visit', 5,
   'Это была голландская ферма Эльзенборг, принадлежащая приятелю доктора.')
bf('andrew-geddes-bain', 'book.p05.geology', 'Бейн — геолог-любитель', 'identity', 5, 'Разговор зашел о геологии, любимом его занятии')
bf('andrew-geddes-bain', 'book.p05.roads', 'Главная специальность Бейна — прокладка дорог', 'identity', 5, 'Третья и главная специальность его -- прокладывание дорог.')
bf('bainskloof-pass', 'book.p05.bridges', 'В ущелье длиной 14 миль построено до сорока каменных мостов', 'history', 5,
   'Во всем ущелье, простирающемся на четырнадцать английских миль, сделано до сорока каменных мостов')
bf('siyolo', 'book.p05.prisoner', 'Сейоло — второстепенный вождь, взятый в плен в нынешнюю войну', 'history', 5,
   'Сейоло -- один из второстепенных вождей. Он взят в плен в нынешнюю войну.')
bf('siyolo', 'book.p05.surrender', 'Сдался полковнику «Меклину»', 'history', 5, 'он добровольно сдался начальнику войск, полковнику Меклину')
bf('schooner-vostok', 'book.p05.bought', 'Шхуна «Восток» куплена адмиралом в Англии', 'history', 5, 'эта шкуна, купленная адмиралом в Англии')
bf('schooner-vostok', 'book.p05.departure', 'Вечером 11 апреля «Восток» снимался с якоря у мыса', 'transport', 5,
   '11 апреля вечером, при свете луны, мы поехали с Унковским и Посьетом на шлюпке к В.А. Корсакову на шкуну "Восток", которая снималась с якоря.')
bf('christmas-island', 'book.p06.pass', 'Прошли в виду необитаемого острова Рождества 13 мая', 'visit', 6, '13-го мая мы прошли в виду необитаемого острова Рождества')
bf('anjer', 'book.p06.arrival', 'Пришли в Анжер 17 мая (по русскому стилю)', 'visit', 6, 'наконец 17 мая нашего стиля')
bf('anjer', 'book.p06.departure', 'Ушли на другой день; европейцев в Анжере всего трое', 'trivia', 6,
   'На другой день утром мы ушли, не видав ни одного европейца, которых всего трое в Анжере.')
bf('singapore', 'book.p07.arrival', 'Пришли в Сингапур 24 мая около 11 утра', 'visit', 7, 'Это было 24-го мая, часов в одиннадцать утра')
bf('singapore', 'book.p07.stay', 'Стоянка в Сингапуре с 24 мая по 2 июня 1853', 'visit', 7, 'С 24 мая по 2 июня 1853')
bf('hoo-ah-kay', 'book.p07.villa', 'Купец Вампоа и его вилла', 'visit', 7, 'Купец Вампоа и его вилла')
bf('hong-kong', 'book.p08.canton', 'Часть офицеров уехала из Гонконга в Кантон', 'visit', 8, 'Наши уехали в Кантон')
bf('george-bonham', 'book.p08.governor', 'Губернатор Гонконга — сэр Бонэм', 'identity', 8, 'Зовут его сэр Бонэм (sir Bonham).')
bf('avvakum-chestnoy', 'book.p08.latin', 'С китайцем отец Аввакум говорил по-латыни', 'trivia', 8, 'а с китайцем отец Аввакум говорил по-латыни')
bf('hong-kong', 'book.p09.departure', 'Вышли из Гонконга 26 июня 1853', 'visit', 9, 'Мы вышли из Гон-Конга 26 июня')
bf('typhoon-1853', 'book.p09.when', 'Тайфун в ночь на 9 июля и весь день 9 июля при выходе в Тихий океан', 'history', 9,
   'в ночи с 8-го на 9-е и все 9-е число июля, выходя из Китайского моря в Тихий океан')
bf('batan-island', 'book.p09.pass', 'Вечером 7 июля подошли к Батану', 'visit', 9, '7-го числа вечером мы подошли к главному из островов, Батану')
bf('chichijima', 'book.p09.names', 'Остров Пиль, порт Ллойд', 'identity', 9, 'Побольше остров называется Пиль, а порт, как я сказал, Ллойд.')
bf('chichijima', 'book.p09.rendezvous', 'В порту Ллойд ждали корвет из Камчатки, транспорт из Ситхи и курьеры', 'history', 9,
   'Там ожидали нас: корвет из Камчатки, транспорт из Ситхи и курьеры из России')
bf('chichijima', 'book.p09.departure', 'Ушли с Бонин-Сима 4 августа около 4 утра', 'visit', 9, 'Наконец 4-го августа, часа в четыре утра')
bf('nathaniel-savory', 'book.p09.oldtimer', 'Севри — старожил острова', 'identity', 9, 'как нам подтвердил и сам Севри, или Севрэ, здешний старожил')

# ---------------- quotes ----------------
Q = []
def quote(seq, frag, tags, ents=(), stop=None, whole=True):
    t = S(seq, frag) if whole else chk(seq, frag)
    Q.append(dict(passage_seq=seq, text=t, stop_ref=stop, entity_keys=list(ents), tags=tags))
quote(1, 'Автор этой, вновь являющейся', ['people'], ['goncharov'])
quote(2, 'Морских ног нет у вас', ['sea', 'humour'])
quote(2, 'Робко ходит в первый раз человек на корабле', ['sea'])
quote(2, 'С этой минуты мы уже с ним неразлучны до сих пор.', ['people'], ['faddeev'])
quote(2, 'Королева рассердилась: штанов не дала', ['humour'])
quote(2, 'Курица была поймана и возвращена на свое место.', ['humour', 'sea'])
quote(2, 'Барон Криднер в трех шагах от меня насвистывал', ['sea', 'people'], ['krudener'])
quote(2, 'Решили: излишек в экономии от вина приложить к сумме, определенной на библиотеку.', ['humour', 'food'])
quote(2, 'Тяжеловато, грубовато, а впрочем, очень хорошо и дешево', ['food', 'culture-clash'], ['portsmouth'])
quote(2, 'Эти добродетели приложены там, где их нужно, и вертятся, как колеса', ['culture-clash'], ['london'])
quote(2, 'Гоголь отчасти испортил мне впечатление', ['humour', 'culture-clash'])
quote(2, 'Меня выручила из недоумения процессия похорон Веллингтона.', ['people'], ['wellington', 'wellington-funeral', 'london'])
quote(2, 'Но одно блюдо за обедом -- этого мало', ['food', 'culture-clash'])
quote(3, 'Нигде человек не бывает так жалок, дерзок и по временам так внезапно счастлив, как на море.', ['sea'])
quote(3, 'Что это за житье -- никогда не солги!', ['humour'])
quote(3, 'Человек мечется в тоске, ищет покойного угла', ['sea'])
quote(3, 'Утомленный, заснешь опять; вдруг удар', ['sea'])
quote(3, 'Гребцы, все португальцы, одетые очень картинно', ['people', 'culture-clash'], ['funchal'])
quote(3, 'Везде по стенам и около окон фестоном лепится бесконечный плющ', ['nature'], ['funchal'])
quote(3, '"Вино-то и помогает: без него устали бы"', ['food', 'humour'], ['madeira'])
quote(3, 'Нет, тонкими ароматами этой удивительной почвы', ['nature'], ['madeira'])
quote(3, 'А все на русского человека говорят, что просит на водку', ['culture-clash', 'humour'], ['madeira'])
quote(3, '"А это что? Посмотрите-ка, ведь это наш зеленый лук!"', ['food', 'humour'], ['ivan-butakov', 'madeira'])
quote(4, 'Пальмы уныло повесили головы', ['nature', 'humour'], ['praia'])
quote(4, 'Я решился купить у старой негритянки', ['food', 'humour', 'people'], ['praia'])
quote(4, 'Мы по дороге сошли в долину; она была цветущим оазисом', ['nature'], ['praia'])
quote(4, 'Наши матросы засучили панталоны и соскочили в воду', ['people', 'culture-clash'], ['praia'])
quote(4, 'Там есть у него другие цвета, в Балтийском, например, желтый', ['sea', 'nature'])
quote(4, 'Матросы уж отобедали (они обедают рано', ['people', 'food', 'sea'])
quote(4, 'Сон и спокойствие объемлют море и небо', ['sea', 'nature'])
quote(4, 'Посмотрите: фиолетовая пелена покрыла небо', ['sea', 'nature'])
quote(4, 'адмирал вышел с книгой и вслух прочел морской устав Петра Великого', ['sea', 'people'], ['putyatin', 'equator-crossing-1853'])
quote(5, 'Соломенная шляпа, как цветок, видна была между бычачьей ногой и арбузами.', ['food', 'humour'])
quote(5, 'А вон на ту гору охота влезть!', ['nature', 'humour'], ['table-mountain'])
quote(5, 'Стол накрыт, как для обеда; стоит блюд шесть и дымятся', ['food'], ['welchs-hotel'])
quote(5, 'Кроме их, медленными кругами носились в воздухе коршуны', ['nature'])
quote(5, 'Я вышел на двор, на широкое крыльцо, густо осененное', ['nature'])
quote(5, 'Англичанам было хорошо: они были здесь как у себя дома, но голландцы', ['culture-clash'], ['cape-town'])
quote(5, 'pittoresque, -- думалось мне', ['culture-clash'])
quote(5, 'Зрелые девы, перестав мечтать', ['humour', 'people'])
quote(5, 'Их победят не порохом, а комфортом.', ['culture-clash'], ['eighth-xhosa-war'])
quote(5, 'Не стоит ему давать таких хороших сигар', ['culture-clash', 'humour'], ['siyolo'])
quote(5, 'Тут уже начиналось создание Бена -- шоссе.', ['people', 'nature'], ['andrew-geddes-bain', 'bainskloof-pass'])
quote(5, 'Разговор зашел о геологии, любимом его занятии', ['people'], ['andrew-geddes-bain'])
quote(6, 'Индийский океан встретил нас еще хуже, нежели Атлантический', ['sea'])
quote(6, 'Целые каскады начали хлестать в каюту', ['sea', 'humour'])
quote(6, 'Кажется, это в первый раз случилось -- служба в православной церкви, в южном полушарии', ['sea', 'tolerance'], ['avvakum-chestnoy'])
quote(6, 'Все они кричали, показывая один -- обезьяну', ['people', 'food', 'culture-clash'], ['anjer'])
quote(6, 'Тут пальмы, как по обдуманному плану, перемешаны с кустами', ['nature'], ['java'])
quote(6, 'Мы шли по деревне, видели в первый раз китайцев', ['people', 'culture-clash'], ['anjer'])
quote(6, 'Несколько человек ощупью пошли по опушке леса', ['food', 'people'], ['anjer'])
quote(7, 'Глаз, привыкший к необозримым полям ржи', ['nature', 'culture-clash'], ['singapore'])
quote(7, 'Я разрезал плод: под красною мякотью', ['food'], ['singapore'])
quote(7, 'Всех европейцев здесь до четырехсот человек', ['people', 'tolerance'], ['singapore'])
quote(7, 'Роскошь -- порок, уродливость', ['culture-clash'], ['singapore'])
quote(7, 'Лавка похожа на магазины целого мира', ['culture-clash'], ['singapore'])
quote(7, 'Но и наши матросы молодцы: в белых рубашках', ['people'], ['singapore'])
quote(7, '"Вот гвоздичное, вот перцовое дерево', ['nature', 'food'], ['hoo-ah-kay', 'singapore'])
quote(7, 'В городе уже сияли огни; особенно ярко освещаются китайские ряды', ['culture-clash'], ['singapore'])
quote(8, 'Китайцам, конечно, не грезилось, когда они в 1842 году', ['culture-clash'], ['hong-kong'])
quote(8, 'Везде увидишь семейные сцены: обедают, занимаются рукодельем', ['people'], ['hong-kong'])
quote(8, 'Кроме ананасов и маленьких апельсинов, называемых мандаринами', ['food'], ['hong-kong'])
quote(8, 'Здесь, в этом чаду криков, запахов, в тесноте', ['people', 'culture-clash'], ['hong-kong'])
quote(8, 'Я ушел, оставя его разведываться как знает', ['humour', 'culture-clash'], ['hong-kong'])
quote(8, 'а с китайцем отец Аввакум говорил по-латыни', ['tolerance', 'humour'], ['avvakum-chestnoy', 'hong-kong'])
quote(9, 'Поэтому нас ветер кидал лишь по морю, играл нами, как кошка мышью', ['sea'], ['typhoon-1853'])
quote(9, 'Тут громадный вал вдруг ударил в сетки', ['sea'], ['typhoon-1853'])
quote(9, 'лейтенант Савич гремел в рупор над ревом бури', ['sea', 'people'], ['savich', 'typhoon-1853'])
quote(9, 'Каюта моя, во время моей болезни, обыкновенно полнехонька была посетителей', ['people', 'humour'])
quote(9, 'Наступил вечер: лес с каждой минутой менял краски', ['nature'], ['chichijima'])
quote(9, 'Между тем около нас все так красиво: над нами веерные пальмы', ['nature'], ['chichijima'])
quote(9, 'В Индии старались разводить виноград -- не родится', ['food', 'nature'])
quote(9, 'Это берега Бонин-Сима: прощай, Бонин-Сима!', ['sea'], ['bonin-islands'])

# ---------------- mentions ----------------
SURF = {
 'goncharov': [], 'putyatin': ['адмирал'], 'posyet': ['Посьет'], 'unkovsky': ['Унковск', 'Иван Семенович'],
 'goshkevich': ['Гошкевич'], 'avvakum-chestnoy': ['отец Аввакум', 'о. Аввакум'], 'voin-rimsky-korsakov': ['Корсаков'],
 'ivan-butakov': ['Бутаков'], 'schlippenbach': ['Шлипенбах'], 'kolokoltsov': ['Колокольцев'], 'tikhmenev': ['Тихменев'],
 'krudener': ['Криднер'], 'boltin': ['Болтин'], 'losev': ['Лосев'], 'savich': ['Савич'], 'zelenoy': ['Зеленым', 'Зеленый', 'Зеленого'],
 'l-a-popov': ['Попов'], 'weyrich': ['Вейрих'], 'faddeev': ['Фаддеев'], 'commodore-talbot': ['Тальбот'],
 'mrs-welch': ['мистрис Вельч'], 'caroline': ['Каролин'], 'richard-malay': ['Ричард'], 'dr-whetherhead': ['Ведерхед'],
 'vandik': ['Вандик'], 'ferstfeld': ['Ферстфельд'], 'andrew-geddes-bain': ['Бен'], 'siyolo': ['Сейоло'], 'colonel-mackinnon': ['Меклин'],
 'wellington': ['Веллингтон'], 'hoo-ah-kay': ['Вампоа'], 'george-bonham': ['Бонэм'], 'nathaniel-savory': ['Севри'],
 'matthew-c-perry': ['Перри'], 'frigate-pallada': ['Паллад'], 'schooner-vostok': ['"Восток"'], 'hms-camperdown': ['Кемпердоун'],
 'corvette-olivutsa': ['Оливуц'], 'transport-knyaz-menshikov': ['Князь Меньшиков'], 'jardine-matheson': ['Джердин'],
 'kronstadt': ['Кронштадт'], 'saint-petersburg': ['Петербург'], 'gotland': ['Готланд'], 'oresund': ['Зунд'], 'kattegat': ['Каттегат'],
 'skagerrak': ['Скагеррак'], 'dogger-bank': ['Доггерсбанк', 'Доггер'], 'dover': ['Дувр'], 'spithead': ['Спитгед'], 'isle-of-wight': ['Байт'],
 'portsmouth': ['Портсмут'], 'gosport': ['Гос-порт', 'Госпорт'], 'london': ['Лондон'], 'st-pauls-cathedral': ['св. Павла'],
 'westminster-abbey': ['Вестминстерск'], 'british-museum': ['Британский музеум'], 'thames-tunnel': ['туннель под Темзой'], 'london-zoo': ['зоологического сада'], 'wellington-funeral': ['похорон Веллингтона'], 'cholera-1852': ['холер'], 'typhoon-1853': ['тайфун'], 'equator-crossing-1853': ['экватор'], 'eighth-xhosa-war': ['нынешнюю войну'], 'madeira-consul': ['консул'], 'waterloo-veteran': ['Ватерлоо'], 'hk-italian-bishop': ['епископ'],
 'lizard-point': ['Лизард'], 'madeira': ['Мадер'], 'funchal': ['Фунчал'], 'cape-verde': ['Зеленого Мыса'], 'santiago-cape-verde': ['С.-Яго', 'Сант-Яго'],
 'praia': ['Порто-Прайя'], 'cape-of-good-hope': ['мыс Доброй Надежды', 'мыса Доброй Надежды'], 'false-bay': ['Фальсбэ', 'Falsebay'],
 'simons-town': ['Саймонстоун', 'Симонстоун', "Simon's"], 'cape-town': ['Капштат'], 'table-mountain': ['Столов'], 'lions-head': ['Львин'],
 'devils-peak': ['Чертов'], 'companys-garden': ['Ботанический сад'], 'wynberg': ['Винберг'], 'somerset-west': ['Сомерсет'],
 'stellenbosch': ['Стелленбош'], 'elsenburg': ['Эльзенборг'], 'paarl': ['Паарль'], 'wellington-south-africa': ['въехали в Веллингтон'],
 'worcester-south-africa': ['Устер'], 'christmas-island': ['острова Рождества'], 'sunda-strait': ['Зондск'], 'java': ['Ява', 'Яве', 'Яву'],
 'anjer': ['Анжер'], 'batavia': ['Батави'], 'singapore': ['Сингапур'], 'hong-kong': ['Гон-Конг', 'Хонкон'], 'victoria-hong-kong': ['Виктория'],
 'guangzhou': ['Кантон'], 'macau': ['Макао'], 'south-china-sea': ['Китайского моря', 'Китайское море'], 'batan-island': ['Батан'],
 'bonin-islands': ['Бонин-Сима'], 'chichijima': ['Пиль', 'Ллойд'], 'nagasaki': ['Нагасаки'], 'india-arms-gosport': ['Indiaarms'],
 'welchs-hotel': ["Welch's hotel"], 'fountain-hotel-simonstown': ['Fountain hotel'], 'bainskloof-pass': ['создание Бена'],
}
M = []
for k, surfs in SURF.items():
    for seq in range(1, 10):
        b = BODY[seq]; seen = set()
        for s in surfs:
            for m in re.finditer(re.escape(s) + r'\w*', b):
                w = m.group(0)
                if k == 'andrew-geddes-bain' and w not in ('Бен', 'Бена', 'Беном', 'Бену', 'Бене'): continue
                if k == 'chichijima' and not w.startswith(('Пиль', 'Ллойд')): continue
                if k == 'java' and w not in ('Ява', 'Яве', 'Яву', 'Явы', 'Явой'): continue
                if k == 'batan-island' and not w.startswith('Батан'): continue
                ONLY={'madeira-consul':3,'hk-italian-bishop':8,'waterloo-veteran':5,'equator-crossing-1853':4,'typhoon-1853':9,'cholera-1852':2,'eighth-xhosa-war':5,'victoria-hong-kong':8}
                if k in ONLY and seq != ONLY[k]: continue
                if k == 'wellington' and 'въехали в Веллингтон' in b[max(0, m.start()-12):m.end()]: continue
                if k == 'putyatin' and w != 'адмирал' and not w.startswith('адмирал'): continue
                if w not in seen:
                    seen.add(w); M.append(dict(passage_seq=seq, entity_key=k, surface=w))
# add goncharov mention for preface
M.append(dict(passage_seq=1, entity_key='goncharov', surface='Автор'))

# ---------------- sources ----------------
SRC = [dict(url='http://az.lib.ru/g/goncharow_i_a/text_0082.shtml', title='И. А. Гончаров. Фрегат «Паллада», том I (passages 1–9)', publisher='az.lib.ru',
            tier='primary', lang='ru', licence='public domain')]
seen = set()
for f in F:
    if f['source_url'] and f['source_url'] not in seen:
        seen.add(f['source_url'])
        lang = f['source_url'][8:10]
        SRC.append(dict(url=f['source_url'], title=f['source_title'], publisher='Wikipedia', tier='secondary', lang=lang, licence='CC BY-SA 4.0'))
SRC.append(dict(url='https://www.wikidata.org/', title='Wikidata (ids, dates, coordinates)', publisher='Wikimedia', tier='secondary', lang='en', licence='CC0'))

# ---------------- validate ----------------
print('PRE-ERR:', *ERR, sep=chr(10))
keys = [e['key'] for e in E]
assert len(keys) == len(set(keys)), [k for k in keys if keys.count(k) > 1]
KS = set(keys)
EN = dict(kind={'person', 'place', 'building', 'event', 'artwork', 'organisation', 'vessel'},
          status={'verified_source', 'verified_wiki', 'book_only', 'unverified', 'disputed', 'obsolete'},
          gp={None, 'exact', 'street', 'district', 'city', 'region', 'approx'},
          pres={None, 'intact', 'rebuilt', 'altered', 'ruin', 'lost', 'unknown'})
for e in E:
    assert e['kind'] in EN['kind'] and e['status'] in EN['status'] and e['geo_precision'] in EN['gp'] and e['preservation'] in EN['pres'], e
    if e['parent_key']: assert e['parent_key'] in KS, e
    if e['wikidata']: assert re.fullmatch(r'Q\d+', e['wikidata'])
wds = [e['wikidata'] for e in E if e['wikidata']]
assert len(wds) == len(set(wds)), 'dup wikidata'
for s in ST:
    assert s['place_key'] in KS and s['kind'] in {'stay', 'pass', 'mention_only'} and s['date_precision'] in {'day', 'month', 'year', 'unknown'} and s['status'] in EN['status'], s
for l in LK:
    assert l['from_key'] in KS and l['to_key'] in KS, l
    assert l['kind'] in {'met', 'stayed_at', 'saw', 'visited', 'located_in', 'took_part', 'portrait_of', 'host_of', 'travelled_with'}, l
fk = set()
for f in F:
    k = (f.get('entity_key'), f.get('stop_ref'), f.get('book_key'), f['key'], f['lang'])
    assert k not in fk, k; fk.add(k)
    if f.get('entity_key'): assert f['entity_key'] in KS, f
    assert f['layer'] in {'then', 'now', 'go'} and f['fact_class'] in {'history', 'identity', 'preservation', 'visit', 'transport', 'trivia'} and f['status'] in EN['status'], f
    assert f['quote'], f
    if f['status'] == 'book_only': assert f['passage_seq'] and f['quote'] in BODY[f['passage_seq']]
    else: assert f['source_url']
for q in Q:
    assert q['text'] in BODY[q['passage_seq']], q['text'][:60]
    for k in q['entity_keys']: assert k in KS, k
for m in M:
    assert m['entity_key'] in KS and m['surface'] in BODY[m['passage_seq']], m
for l in LK:
    if l['quote']: assert l['quote'] in BODY[l['passage_seq']]
qt = [q['text'] for q in Q]
dups = [t for t in qt if qt.count(t) > 1]
if dups: ERR.append(f'dup quotes {len(dups)}')

def w(name, rows):
    with open(os.path.join(OUT, name), 'w', encoding='utf8', newline='\n') as fh:
        for r in rows: fh.write(json.dumps(r, ensure_ascii=False) + '\n')
for n, rows in [('entities.jsonl', E), ('stops.jsonl', ST), ('entity_links.jsonl', LK), ('mentions.jsonl', M), ('facts.jsonl', F),
                ('quotes.jsonl', Q), ('sources.jsonl', SRC)]:
    w(n, rows)
# re-parse
for n in os.listdir(OUT):
    for i, l in enumerate(open(os.path.join(OUT, n), encoding='utf8')): json.loads(l)
print('entities', len(E), 'wd', len(wds), f'{100*len(wds)/len(E):.0f}%', 'stops', len(ST), 'links', len(LK), 'mentions', len(M),
      'facts', len(F), 'quotes', len(Q), 'sources', len(SRC))
used = {m['entity_key'] for m in M}
print('entities without mentions:', sorted(KS - used))
print('long quotes:', [(q['passage_seq'], len(q['text'])) for q in Q if len(q['text']) > 350 or len(q['text']) < 25])
print('\n'.join(ERR) or 'NO ERRORS')
