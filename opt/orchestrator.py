#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
from datetime import datetime

SCRIPT_DIR = "/opt/ivre/ivre-opt"

SCRIPTS = [
    {
        "name": "pscan_spawn_jobs.py",
        "type": "python",
        "description": "Запуск Nmap сканирования",
        "required": True
    },
    {
        "name": "pscan_db_job.sh",
        "type": "bash",
        "description": "Импорт результатов в IVRE",
        "required": False
    },
    {
        "name": "export_recent_changes.py",
        "type": "python",
        "description": "Экспорт изменений",
        "required": False
    },
    {
        "name": "print_recent_scan.py",
        "type": "python",
        "description": "Вывод результатов сканирования",
        "required": False
    },
    {
        "name": "create_email_report.py",
        "type": "python",
        "description": "Создание и отправка email-отчета",
        "required": False
    }
]

def print_header(text):
    border = "=" * 60
    print(f"\n{border}")
    print(f"  {text}")
    print(f"{border}\n")

def run_script(script_info):
    script_name = script_info["name"]
    script_type = script_info["type"]
    description = script_info["description"]
    
    print_header(f"Запуск: {description}")
    print(f"Файл: {script_name}")
    print(f"Тип: {script_type}")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    script_path = os.path.join(SCRIPT_DIR, script_name)
    
    if not os.path.exists(script_path):
        print(f"Предупреждение: Файл не найден: {script_path}")
        print("   Пропускаем...")
        return True
    
    interpreter = "python3" if script_type == "python" else "bash"
    
    try:
        process = subprocess.Popen(
            [interpreter, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        print(f"Выполнение {script_name}:\n")
        for line in process.stdout:
            print(f"  {line}", end='')
        
        return_code = process.wait()
        
        if return_code == 0:
            print(f"\nУспешно: {script_name} завершен (код: {return_code})")
            return True
        else:
            print(f"\nОшибка: {script_name} завершен с кодом {return_code}")
            return False
            
    except FileNotFoundError:
        print(f"Ошибка: интерпретатор '{interpreter}' не найден")
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def main():
    print_header("ПЕРИМЕТР СКАНЕР - ОРКЕСТРАТОР")
    print(f"Старт: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Скриптов для выполнения: {len(SCRIPTS)}")
    print(f"Рабочая директория: {SCRIPT_DIR}\n")
    
    total = len(SCRIPTS)
    success = 0
    failed = 0
    skipped = 0
    
    for i, script in enumerate(SCRIPTS, 1):
        print(f"\n{'=' * 60}")
        print(f"  ШАГ {i} ИЗ {total}")
        print(f"{'=' * 60}")
        
        result = run_script(script)
        
        if result:
            success += 1
            print(f"Шаг {i} выполнен")
        else:
            failed += 1
            print(f"Шаг {i} не выполнен")
            
            if script["required"]:
                print(f"\nОстановка: {script['name']} обязателен")
                break
    
    print_header("РЕЗУЛЬТАТЫ")
    print(f"Всего скриптов: {total}")
    print(f"Успешно: {success}")
    print(f"Ошибок: {failed}")
    print(f"Пропущено: {skipped}")
    print(f"Завершение: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed > 0:
        print("\nЕсть ошибки. Проверьте логи.")
        sys.exit(1)
    else:
        print("\nВсе скрипты выполнены успешно!")
        sys.exit(0)

if __name__ == "__main__":
    main()