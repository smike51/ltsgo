# history.ltsgo.ru — выкладка прототипа карты

Что: статичные файлы `proto/map` (≈300 КБ). Где: starpom-app (45.43.166.101), `/opt/ltsgo/history`.
Контейнер `ltsgo-history` (caddy:2-alpine, file-server, без публичного порта, сеть `ai_network`, 64 МБ).

## 1. DNS (владелец, панель Jino)
`history.ltsgo.ru` A → `45.43.166.101` (сейчас указывает на 195.161.114.253 — хостинг Jino).

## 2. Файлы и контейнер (Релиз), из корня репозитория ltsgo
```sh
ssh starpom-app "mkdir -p /opt/ltsgo/history/site.new"
scp deploy/history/docker-compose.yml starpom-app:/opt/ltsgo/history/
tar -C proto/map -cf - . | ssh starpom-app "tar -C /opt/ltsgo/history/site.new -xf -"
ssh starpom-app "cd /opt/ltsgo/history && { [ -d site ] && mv site site.old; true; } && mv site.new site && docker compose up -d"
ssh starpom-app "docker exec ltsgo-history wget -qO- http://localhost/ | head -c 80"
```
Повторная выкладка — те же шаги (старая версия остаётся в `site.old` для отката).

## 3. Адрес в Caddy (Инфра, `/app/aurav/Caddyfile`)
```
history.ltsgo.ru {
	encode gzip
	header {
		X-Content-Type-Options "nosniff"
		Referrer-Policy "strict-origin-when-cross-origin"
		-Server
	}
	reverse_proxy ltsgo-history:80
}
```
Если сайт закрыт паролем — добавить `basic_auth { <user> <bcrypt-хеш> }`; пароль хранить в `_private\`.

## 4. Проверка
https://history.ltsgo.ru/#goncharov-1852/20 — карта, остановка «Аньер (Анжер)», блок «Сегодня».
