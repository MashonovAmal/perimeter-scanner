# -*- coding: utf-8 -*-
import os
os.environ['IVRE_DB'] = 'mongodb://ivredb:27017'

from ivre.db import db
import json

with open("/opt/ivre/ivre-opt/current_scan_date.txt", "r") as f:
    current_date = f.readline().strip()
with open("/opt/ivre/ivre-opt/previous_scan_date.txt", "r") as f:
    previous_date = f.readline().strip()

result_list = []

value_map = {
    "-1": "No Longer Detected",
    "0": "Still Open: Open in previous scan "+previous_date+" and open in current scan "+current_date,
    "1": "Newly Detected"
}

scan_export = list(db.view.diff_categories(
    category1="pscan_"+previous_date,
    category2="pscan_"+current_date,
    include_both_open=False
))

for result in scan_export:
    result_list.append({
        "ip_address": result['addr'],
        "protocol": result['proto'],
        "port": result['port'],
        "status": value_map[str(result['value'])]
    })

sorted_result_list = sorted(result_list, key=lambda d: d['status'])

with open("/opt/ivre/ivre-opt/whats_changed.json", "w") as outfile:
    json.dump(sorted_result_list, outfile, indent=2)