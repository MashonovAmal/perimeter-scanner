# -*- coding: utf-8 -*-
import os
import ipaddress
import requests
import subprocess
import time
from datetime import datetime, timedelta
from netutils.ip import netmask_to_cidr

# Завершение всех процессов nmap (если они запущены)
subprocess.Popen(['killall', '-9', 'nmap'])

# Тег для фильтрации целей в Netbox
nmap_tag = "nmap_scanning"

# Настройки подключения к Netbox (берутся из переменных окружения)
netbox_url = os.getenv('NETBOX_URL', 'http://netbox:8000')
netbox_token = os.getenv('NETBOX_TOKEN', 'token')
netbox_headers = {'Authorization': "Bearer {}".format(netbox_token)}

# Создание файлов с датами сканирования
date_parser = datetime.now()
date_stamp = date_parser.strftime("%Y-%m-%d")
prev_date_parser = datetime.now() + timedelta(days=-7)
prev_date_stamp = prev_date_parser.strftime("%Y-%m-%d")
current_scan_fh = open("/opt/ivre/ivre-opt/current_scan_date.txt", "w")
previous_scan_fh = open("/opt/ivre/ivre-opt/previous_scan_date.txt", "w")
current_scan_fh.write(date_stamp)
current_scan_fh.close()
previous_scan_fh.write(prev_date_stamp)
previous_scan_fh.close()

# Аргументы nmap для TCP-сканирования
nmap_base_args = "nohup nmap --host-timeout 300s --max-rtt-timeout 2000ms --min-rtt-timeout 500ms --max-retries 2 --log-errors --open -T3 -Pn -sS --top-ports 2000 -oX /opt/ivre/ivre-share/"+date_stamp+"_tcp_"

# Аргументы nmap для UDP-сканирования
nmap_base_args_udp = "nohup nmap --host-timeout 120s --max-rtt-timeout 2000ms --min-rtt-timeout 500ms --max-retries 2 --log-errors --open -T3 -Pn -sU --top-ports 250 -oX /opt/ivre/ivre-share/"+date_stamp+"_udp_"

# Получение IP-адресов и префиксов из Netbox по тегу
netbox_api_ip_addr = requests.get(netbox_url+"/api/ipam/ip-addresses/?limit=0&tag="+nmap_tag, headers=netbox_headers, verify=False).json()
netbox_api_ip_prefix = requests.get(netbox_url+"/api/ipam/prefixes/?limit=0&tag="+nmap_tag, headers=netbox_headers, verify=False).json()

# Преобразование адреса в формат для имени файла
def explode_address_elements(address_to_scan):
    exploded_elements_dict = {}
    exploded_elements_dict['address_to_scan_exploded'] = str(
        ipaddress.IPv4Interface(address_to_scan).ip).replace('.', '_')
    exploded_elements_dict['address_to_scan_mask'] = str(
        netmask_to_cidr((ipaddress.IPv4Interface(address_to_scan).netmask)))
    return exploded_elements_dict

# Запуск сканирования для одного адреса или префикса
def spawn_nmap_jobs(address_to_scan, address_to_scan_exploded, address_to_scan_mask, is_prefix):
    if is_prefix:
        # TCP-сканирование сети
        nmap_raw_cmd = nmap_base_args+address_to_scan_exploded+"_" + address_to_scan_mask+".xml "+address_to_scan
        subprocess.Popen(nmap_raw_cmd.split())

        # UDP-сканирование сети
        nmap_raw_cmd = nmap_base_args_udp+address_to_scan_exploded+"_" + address_to_scan_mask+".xml "+address_to_scan
        subprocess.Popen(nmap_raw_cmd.split())

    else:
        # TCP-сканирование отдельного IP
        nmap_raw_cmd = nmap_base_args+address_to_scan_exploded+"_" + address_to_scan_mask+".xml "+address_to_scan.split("/")[0]
        subprocess.Popen(nmap_raw_cmd.split())

        # UDP-сканирование отдельного IP
        nmap_raw_cmd = nmap_base_args_udp+address_to_scan_exploded+"_" + address_to_scan_mask+".xml "+address_to_scan.split("/")[0]
        subprocess.Popen(nmap_raw_cmd.split())

# Запуск сканирования для всех IP-адресов из Netbox
for ip_addr in netbox_api_ip_addr['results']:
    ip_elements = explode_address_elements(ip_addr['address'])
    spawn_nmap_jobs(ip_addr['address'], ip_elements['address_to_scan_exploded'], ip_elements['address_to_scan_mask'], is_prefix=False)
    time.sleep(.3)

# Запуск сканирования для всех префиксов из Netbox
for prefix in netbox_api_ip_prefix['results']:
    ip_elements = explode_address_elements(prefix['prefix'])
    spawn_nmap_jobs(prefix['prefix'], ip_elements['address_to_scan_exploded'], ip_elements['address_to_scan_mask'], is_prefix=True)
    time.sleep(.3)

# Ожидание завершения всех запущенных сканирований
print("\nОжидание завершения всех сканирований...")

max_wait = 600
wait_interval = 10
waited = 0

while waited < max_wait:
    result = subprocess.run(['pgrep', 'nmap'], capture_output=True, text=True)
    if not result.stdout.strip():
        print("Все сканирования завершены")
        break
    print(f"  Ожидание... ({waited}/{max_wait} сек)")
    time.sleep(wait_interval)
    waited += wait_interval
else:
    print("Время ожидания истекло. Некоторые сканирования могут еще выполняться.")

print("=== ВСЕ СКАНИРОВАНИЯ ЗАВЕРШЕНЫ ===")