# -*- coding: utf-8 -*-
# Скрипт для вывода последних результатов сканирования из MongoDB
# Использует запрос: db.view.get_ips_ports() с фильтром по категории текущего сканирования
# Результат сохраняется в JSON-файл для дальнейшей обработки (email-отчеты)

import os
# Подключаемся к MongoDB в контейнере ivredb
os.environ['IVRE_DB'] = 'mongodb://ivredb:27017'

from ivre.db import db
import json

# Исправлено: правильный путь и закрытие файла
with open("/opt/ivre/ivre-opt/current_scan_date.txt", "r") as f:
    current_date = f.readline().strip()

result_list = []

# Data to be written
scan_export = list(db.view.get_ips_ports(flt=db.view.searchcategory("pscan_"+current_date))[0])

for result in scan_export:
    result_list.append({"ip_address": result['addr'], "ports": result['ports']})

# Сохранение в JSON
with open("/opt/ivre/ivre-opt/recent_scan_result.json", "w") as outfile:
    json.dump(result_list, outfile, indent=4)