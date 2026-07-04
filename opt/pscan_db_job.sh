#!/bin/bash
# -*- coding: utf-8 -*-

echo "=== Очистка представлений ==="
echo yes | ivre view --purgedb

CURRENT_DATE=$(cat "/opt/ivre/ivre-opt/current_scan_date.txt")
PREVIOUS_DATE=$(cat "/opt/ivre/ivre-opt/previous_scan_date.txt")

echo "Текущее сканирование: $CURRENT_DATE"
echo "Предыдущее сканирование: $PREVIOUS_DATE"

if [ -z "$CURRENT_DATE" ] || [ -z "$PREVIOUS_DATE" ]; then
    echo "ОШИБКА: не удалось прочитать даты сканирования из файлов. Прерываю выполнение."
    exit 1
fi

echo "=== Импорт в IVRE ==="
ivre scan2db --open-ports -s ivredb -c pscan_${CURRENT_DATE} /opt/ivre/ivre-share/${CURRENT_DATE}_*.xml

echo "=== Создание представлений ==="
ivre db2view --no-merge nmap --category pscan_${PREVIOUS_DATE}
ivre db2view --no-merge nmap --category pscan_${CURRENT_DATE}

echo "=== Готово ==="