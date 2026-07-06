Описание проекта
Perimeter Scanner - автоматизированная система сканирования сетевого периметра на основе Docker, Python, Nmap, IVRE и Netbox.

Система выполняет следующие задачи:

Получение IP-адресов из Netbox по тегу nmap_scanning

Запуск TCP и UDP сканирования через Nmap

Импорт результатов в IVRE

Сравнение с предыдущим сканом

Отправка email-отчетов

Технологический стек:

Docker / Docker Compose

Python 3

Nmap

IVRE

Netbox

MongoDB

PostgreSQL

Redis

Структура проекта:
perimeter-scanner/
├── opt/
│ ├── orchestrator.py - главный оркестратор
│ ├── pscan_spawn_jobs.py - запуск Nmap
│ ├── pscan_db_job.sh - импорт в IVRE
│ ├── print_recent_scan.py - вывод результатов
│ ├── export_recent_changes.py - экспорт изменений
│ ├── create_email_report.py - отправка email
│ └── email_template.j2 - шаблон письма
├── ivre/docker/docker-compose.yml
├── netbox-docker/docker-compose.yml
├── Dockerfile
├── docker-compose.yml
├── .env.template
└── README.md

Установка и настройка:

Клонировать репозиторий:
https://github.com/MashonovAmal/perimeter-scanner.gitcd perimeter-scanner

Создать общую сеть для контейнеров:
docker network create shared-network

Запустить IVRE:
cd ivre/docker
docker compose up -d

Запустить Netbox:
cd netbox-docker
docker compose up -d

Собрать образ сканера:
docker build -t perimeter-scanner .

Запустить сканер:
docker compose up -d

Настройка переменных окружения:
Создать файл .env из шаблона .env.template:
cp .env.template .env

Заполнить настройки в файле .env:
NETBOX_URL=http://netbox:8000
NETBOX_TOKEN=ваш_токен_netbox
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=scanner@example.com
SMTP_PASSWORD=ваш_пароль
SMTP_FROM=scanner@example.com
SMTP_TO=admin@example.com

Настройка автоматического запуска по расписанию:
Добавить в crontab для ежедневного запуска в 8:00 утра:
0 8 * * * cd /opt/perimeter-scanner && docker compose up --abort-on-container-exit >> /var/log/perimeter-scanner.log 2>&1

Решение типичных проблем:

Сканер не подключается к Netbox:

Проверьте NETBOX_URL в .env файле

Проверьте сеть: docker network ls

Убедитесь, что контейнер Netbox запущен: docker ps | grep netbox

Сканер не подключается к IVRE:

Проверьте настройки IVRE_DB в скриптах

Убедитесь, что контейнеры IVRE запущены: docker ps | grep ivre

Email не отправляется:

Проверьте настройки SMTP в .env

Убедитесь, что SMTP сервер разрешает ретрансляцию

Проверьте правила фаервола для порта 587

Нет результатов в веб-интерфейсе IVRE:

Проверьте наличие XML файлов в папке share

Проверьте завершение импорта: docker logs ivreclient

Пересоберите представление IVRE: docker exec -it ivreclient ivre db2view nmap

## Usage

```bash
python3 main.py
```
