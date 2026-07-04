# -*- coding: utf-8 -*-
import requests
import json
import datetime
from jinja2 import Template
import smtplib
import os

# ===== НАСТРОЙКИ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ =====
NETBOX_URL = os.getenv('NETBOX_URL', 'http://netbox:8000')
NETBOX_TOKEN = os.getenv('NETBOX_TOKEN', 'token')
NETBOX_HEADERS = {'Authorization': "Bearer {}".format(NETBOX_TOKEN)}

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.example.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER', 'user@example.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'password')
SMTP_FROM = os.getenv('SMTP_FROM', 'scanner@example.com')
SMTP_TO = os.getenv('SMTP_TO', 'admin@example.com').split(',')

date_parser = datetime.datetime.now()
date_stamp = date_parser.strftime("%Y-%m-%d")

recent_scan_filename = "/opt/ivre/ivre-opt/recent_scan_result.json"
whats_changed_filename = "/opt/ivre/ivre-opt/whats_changed.json"

output_list_no_reason = []
output_list_all = []

# Получение обоснования открытых портов из Netbox
def get_netbox_known_ports_justification(ip_address, port):
    ipam_api_call = requests.get(
        NETBOX_URL + "/api/ipam/ip-addresses/?address=" + ip_address,
        headers=NETBOX_HEADERS,
        verify=False
    ).json()

    if len(ipam_api_call['results']) > 0:
        known_ports_list = ipam_api_call['results'][0].get('custom_fields')
        if known_ports_list and known_ports_list.get('known_open_ports') is not None:
            for known_port in known_ports_list['known_open_ports']:
                if known_port.get('port') == port:
                    return known_port.get('reason', "No Justification")
    return "No Justification"

def get_recent_scan(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Загрузка данных
recent_scan_results_dict = get_recent_scan(recent_scan_filename)
whats_changed_dict = get_recent_scan(whats_changed_filename)

# Сравнение каждого открытого порта с данными из Netbox
for entry in recent_scan_results_dict:
    for discovered_port in entry['ports']:
        if discovered_port['state_state'] != 'open':
            continue

        reason = get_netbox_known_ports_justification(
            entry['ip_address'],
            discovered_port['port']
        )

        item = {
            "IP Address": entry['ip_address'],
            "Open Port": discovered_port['port'],
            "Reason": reason
        }

        if reason == "No Justification":
            output_list_no_reason.append(item)
        else:
            output_list_all.append(item)

# Формирование email-отчета
with open('/opt/ivre/ivre-opt/email_template.j2', 'r') as f:
    rendered = Template(f.read()).render(
        date_stamp=date_stamp,
        output_list_no_reason=output_list_no_reason,
        output_list_all=output_list_all,
        whats_changed_dict=whats_changed_dict
    )

message = 'Subject: {}\n\n{}'.format("Network Perimeter Port Scanner Summary", rendered)

# Отправка email
s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
s.starttls()
s.login(SMTP_USER, SMTP_PASSWORD)
s.sendmail(SMTP_FROM, SMTP_TO, message)
s.quit()

print("Email sent to", SMTP_TO)