facts=[]
def F(ek,key,layer,value,fc,status='book_only',seq=None,start=None,n=1,src=None,title=None,quote=None,note=None,lang='ru'):
    if seq:
        quote=S_(seq,start,n)
        if not quote: return
    facts.append({'entity_key':ek,'key':key,'layer':layer,'lang':lang,'value':value,'fact_class':fc,'status':status,
      'source_url':src,'source_title':title,'passage_seq':seq,'quote':quote,'note':note,'created_by':'agent:'+CB})
F('nagasaki-port','stay-1853','then','Фрегат пришёл на Нагасакский рейд 10 августа и ушёл 11 ноября 1853 г. (ст. ст.)','visit',seq=10,start='Часа в три мы снялись с якоря, пробыв ровно три месяца в Нагасаки')
F('nagasaki-port','arrival-date-conflict','then','В гл. II.II приход в Японию назван 5 августа — расходится с 10 августа','visit','disputed',seq=11,start='Страшно подумать, что с 5-го августа')
F('tokugawa-ieyoshi','death-reported','then','Японцы сообщили, что сёгун умер 14 августа, через четыре дня после прихода русских','history',seq=10,start='По их словам, сиогун умер 14 августа')
F('nagasaki-port','departure-1854','then','Из Нагасаки ушли 24 января 1854 г. (у Энгельгардта — 27 января)','visit','disputed',seq=12,start='поставив все паруса, 24-го января')
F('tsutsui-masanori','book-name','then','В книге старший полномочный — Тсутсуй Хизе-но-ками, второй — Кавадзи','identity',seq=12,start='Пора назвать их: старика зовут Тсутсуй')
F('tsutsui-masanori','portrait','then','Старший полномочный — старик со старческой умной и приветливой добротой','trivia',seq=12,start='Морщины лучами окружали глаза и губы')
F('kawaji-toshiakira','gift-sabre','then','Кавадзи подарил Гончарову саблю, Тсутсуй — украшения к ней','trivia',seq=12,start='Я не знаю толку в саблях, но не мог довольно налюбоваться',n=2)
F('nagasaki-negotiations-1853','plenipotentiaries-arrived','then','28 декабря 1853 г. японцы сообщили, что полномочные из Эдо прибыли','history',seq=12,start='Сегодня, 28-го декабря русского стиля, приехали Хагивари')
F('nagasaki-negotiations-1853','letter','then','Полномочные объявили, что вручат письмо от верховного совета','history',seq=12,start='Тсутсуй и Кавадзи объявили, что они имеют вручить письмо')
F('naha','stay-1854','then','Фрегат стоял в порту Напа-Киян с 31 января по 9 февраля 1854 г.','visit',seq=13,start='Порт Напа-Киян, с 31-го января')
F('shuri-castle','king-prisoner','then','Король Рюкю живёт как пленник в своём крепком замке и никому не показывается','history',seq=13,start='Король живет здесь как пленник')
F('bettelheim','visit','then','2 февраля 1854 г. к русским явился английский миссионер Беттельгейм','visit',seq=13,start='На другой день, 2-го февраля, мы только собрались было на берег')
F('perry','naha-coal-shed','then','Американцы построили в Напе сарай для угля, после чего Перри отплыл в Японию','history',seq=13,start='Они выстроили и сарай для склада каменного угля')
F('manila','arrival-1854','then','Пришли в Манилу утром 16 февраля 1854 г.','visit',seq=14,start='Лишь только встали мы утром 16 февраля')
F('manila','departure-1854','then','Вышли из Манилы 21 февраля (заголовок главы и Энгельгардт — 27 февраля)','visit','disputed',seq=15,start='Мы вышли из Манилы 21-го февраля вечером')
F('corregidor','lighthouse','then','Посредине входа в Манильскую бухту — островок Коррехидор с маяком','history',seq=14,start='Посредине входа лежит островок Коррехидор с маяком.')
F('demien','hotel','then','В Маниле был отель, который держал француз Демьен','trivia',seq=14,start='"Отель, -- прибавили они в последнее утешение нам')
F('camiguin-babuyan','arrival','then','11 марта 1854 г. фрегат вошёл в бухту Пио-Квинто','visit',seq=15,start='Утром уже на другой день, 11-го марта')
F('port-hamilton','arrival','then','2 апреля 1854 г. пришли на Гамильтон (у Энгельгардта — 6 апреля)','visit','disputed',seq=15,start='4-е апреля. Наконец, 2-го апреля, пришли и на Гамильтон.')
F('tumen-river','found','then','9 мая 1854 г. нашли пограничную реку Тай-маньга','visit',seq=15,start='9-е мая. Наконец отыскали и пограничную реку')
F('strait-of-tartary','entered','then','18 мая 1854 г. фрегат вошёл в Татарский пролив','visit',seq=15,start='18 мая мы вошли в Татарский пролив.')
F('frigate-pallada','left-imperial-harbour','then','«Палладу» разоружили и оставили в Императорской бухте Татарского пролива','history',seq=19,start='Ее оставили в Татарском проливе, в Императорской бухте.',n=2)
F('frigate-diana','replacement','then','«Диана» пришла на смену «Палладе»','history',seq=19,start='Фрегат "Диана" уже пришел на смену "Палладе"')
F('schooner-vostok','muravyov','then','Муравьёв пробыл на фрегате дня два и уехал в Николаевск','visit',seq=19,start='Муравьев и, пробыв у нас дня два на фрегате, уехал в Николаевск')
F('goncharov','left-frigate','then','На шхуне «Восток» Гончаров уехал с фрегата','transport',seq=19,start='На этой шкуне я и отправился с фрегата')
F('amur-liman','shoals','then','Амурский лиман весь усеян мелями','transport',seq=19,start='Он весь усеян мелями')
F('muravyov-amursky','arrival','then','12 августа 1854 г. путешественники во главе с генерал-губернатором Восточной Сибири вышли на берег','visit',seq=16,start='Наконец, 12 августа, толпа путешественников')
F('siege-of-petropavlovsk','footnote','then','Сноска о том, что в это же время, 16 августа, шла оборона на Камчатке','history',seq=16,start='* В это самое время, именно 16 августа')
F('ayan','size','then','Аян — скромный маленький уголок России в 10 500 верстах от Петербурга','history',seq=16,start='Теперь же пока это скромный, маленький уголок России')
F('ayan','route','then','Летом от Аяна ехали верхом около 200 верст, багаж — вьюками','transport',seq=16,start='Летом надо ехать верхом верст двести')
F('innocent-of-alaska','ayan-road','then','Нынешний путь к Охотскому морю найден трудами Иннокентия и Завойко','history',seq=16,start='Трудами преосвященного Иннокентия')
F('ayan','service','then','В Аяне казаки несут военную службу, а якуты — статскую','trivia',seq=16,start='Казаки исправляют здесь военную службу, а якуты статскую.')
F('dzhugdzhur','descent','then','Зимой с Джукджура не сходят и не съезжают, а сползают','trivia',seq=16,start='Тут же рассказали мне, что зимой не сходят и не съезжают')
F('yakutsk','no-hotel','then','В Якутске нет гостиницы','trivia',seq=17,start='"Однако гостиницы нет в Якутске", -- перебил смотритель.')
F('yakutsk','ferry','then','От юрты до Якутска девять верст: пять водой и четыре берегом','transport',seq=17,start='От юрты до Якутска считается девять верст')
F('yakutsk','missionaries','then','В Якутске два миссионера — священники Хитров и Запольский','history',seq=17,start='Здесь их, в Якутске, два: священники Хитров и Запольский.')
F('dionisy-khitrov','yakut-grammar','then','Священник Хитров составляет грамматику якутского языка','history',seq=17,start='Один из миссионеров, именно священник Хитров')
F('yakutsk','departure','then','Гончаров выехал из Якутска 26 ноября 1854 г. при 36° мороза','visit',seq=18,start='Я выехал из Якутска 26 ноября при 36° мороза')
F('vitim','village','then','Витим — слобода с церковью Преображения','history',seq=18,start='Витима -- слобода, с церковью Преображения')
F('kirensk','province-border','then','От Жербинской станции начинается Иркутская губерния и Киренский округ','history',seq=18,start='От Жербинской станции начинается Иркутская губерния')
F('irkutsk','arrival','then','Гончаров въехал в Иркутск в заутреню Рождества 1854 г.','visit',seq=18,start='В самую заутреню Рождества Христова я въехал в город.')
F('shimoda','tsunami','then','Второй вал покрыл Симоду и смыл её до основания','history',seq=19,start='Второй вал покрыл весь Симодо и смыл его до основания.')
F('frigate-diana','42-turns','then','Водоворот развернул «Диану» сорок два раза','trivia',seq=19,start='Потом стало ворочать его то в одну')
F('frigate-diana','guns-saved','then','60 орудий «Дианы» отдали на хранение японцам, и те сберегли их в особых сараях','history',seq=19,start='Фрегат разоружили: свезли все шестьдесят орудий',n=2)
F('heda','repair-bay','then','Повреждённую «Диану» с фальшивым рулём повели в закрытую бухту Хе-да','history',seq=19,start='Фрегат повели, приделав фальшивый руль')
F('treaty-of-shimoda','context','then','Дело о торговом трактате и границе на Сахалине, начатое с Японией','history',seq=19,start='Дело, начатое с Японией о заключении торгового трактата')
F('goncharov','secretary','then','Гончаров был командирован секретарём при адмирале','identity',seq=19,start='Я был "командирован для исправления должности секретаря')
for k,desc,qid in [('putyatin','Russian admiral (1803-1883)','Q957601'),('posyet','Russian admiral (1820-1899)','Q3198773'),
  ('goshkevich','Belarus orientalist and diplomat (1814–1875)','Q2493535'),('voin-rimsky-korsakov','Russian navigator and geographer (1822–1871)','Q4394687'),
  ('bettelheim','Hungarian missionary (1811–1870)','Q690658'),('donker-curtius','Dutch diplomat (1813–1879)','Q1052889'),
  ('unkovsky','Imperial Russian admiral (1822-1886)','Q2025113'),('zavoyko','Imperial Russian navy admiral (1810–1898)','Q163876'),
  ('innocent-of-alaska','Russian bishop and saint (1797–1879)','Q982977'),('furuhjelm','Finno-Russian nobleman, admiral, and governor (1821–1909)','Q1354978'),
  ('tokugawa-ieyoshi','Japanese shogun (1793–1853)','Q439675'),('wrangel','Baltic German explorer and Russian admiral (1797-1870)','Q135329'),
  ('treaty-of-shimoda','treaty between the Russian Empire, and the Empire of Japan (Tokugawa shogunate)','Q497189'),
  ('siege-of-petropavlovsk','1854 main operation on the Pacific Theatre of the Crimean War','Q815197'),
  ('muravyov-amursky','Russian noble (1809-1881)','Q545912'),('perry','American naval officer (1794–1858)','Q61855'),
  ('basil-hall','Royal Navy officer (1788-1844)','Q280479')]:
    F(k,'wd-description','then',desc,'identity','verified_wiki',src=WD+qid,title='Wikidata '+qid,quote=desc,lang='en')
PW='https://en.wikipedia.org/wiki/Russian_frigate_Pallada'; DW='https://en.wikipedia.org/wiki/Dejima'; SW='https://en.wikipedia.org/wiki/Shuri_Castle'
F('frigate-pallada','scuttled','now','Фрегат затоплен собственной командой в 1855 г. из-за ветхости корпуса','preservation','verified_wiki',src=PW,title='Russian frigate Pallada',quote='She was scuttled by her own crew in the Crimean War due to the poor condition of her hull in 1855.')
F('frigate-pallada','overwinter','then','«Паллада» зимовала в Императорской гавани','history','verified_wiki',src=PW,title='Russian frigate Pallada',quote='she overwintered at Imperatorskaya Gavan.')
F('frigate-pallada','wreck-souvenirs','now','Остов лежит на глубине ~20 м; русские, потом японские ныряльщики брали с него мелкие предметы на сувениры','preservation','verified_wiki',src=PW,title='Russian frigate Pallada',quote='As the ship was only at a depth of 20 meters, it was common for Russian, and later Japanese, divers to retrieve small items from the sunken vessel as souvenirs.')
F('dejima','restoration','now','С 1996 г. идёт восстановление Дэдзимы: план — 25 зданий в виде начала XIX в.','preservation','verified_wiki',src=DW,title='Dejima',quote='In 1996, restoration of Dejima began with plans for reconstructing 25 buildings in their early 19th-century state.')
F('dejima','restored-2017','now','В 2017 г. восстановлены ещё шесть зданий и мост Омотэмон','preservation','verified_wiki',src=DW,title='Dejima',quote='In 2017, six new buildings, as well as the Omotemon Bridge (the old bridge to the mainland), were restored.')
F('dejima','work-in-progress','now','Восстановление Дэдзимы продолжается','preservation','verified_wiki',src=DW,title='Dejima',quote='Dejima today is a work in progress.')
F('shuri-castle','destroyed-1945','now','Замок почти полностью разрушен в 1945 г. в битве за Окинаву','preservation','verified_wiki',src=SW,title='Shuri Castle',quote='In 1945, during the Battle of Okinawa, it was almost completely destroyed.')
F('shuri-castle','rebuilt-1992','now','С 1992 г. цитадель и стены в основном восстановлены на прежнем месте','preservation','verified_wiki',src=SW,title='Shuri Castle',quote='Beginning in 1992, the central citadel and walls were largely reconstructed on the original site')
F('shuri-castle','unesco','now','С 2000 г. — объект Всемирного наследия','preservation','verified_wiki',src=SW,title='Shuri Castle',quote='In 2000, Shuri Castle was designated as a World Heritage Site')
F('shuri-castle','fire-2019','now','31 октября 2019 г. главные постройки снова сгорели','preservation','verified_wiki',src=SW,title='Shuri Castle',quote='On the morning of 31 October 2019, the main courtyard structures of the castle were again destroyed in a fire.')
F('shuri-castle','reconstruction-2026','now','Восстановление ожидается к осени 2026 г.','preservation','verified_wiki',src=SW,title='Shuri Castle',quote='Reconstruction is ongoing and is expected to be fully completed by the autumn of 2026,',note='проверить на дату публикации')
