"""
strains.py

Get cannabis strain information from Leafly

Created By:
    - Rory Holland <https://github.com/roryholland>

License:
    MIT
"""

import requests
import sys
import json

if not __name__ == "__main__":
    from cloudbot import hook

SEARCH_URL = "https://www.cannabisreports.com/api/v1.0/strains/search/{}"

def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None

def get_top_strain(strain_name):
    r = requests.get(SEARCH_URL.format(strain_name))
    data = json.loads(r.text)['data']
    return data

# main command
#@hook.command("strain", "dank")
def get_strain_info(text):
    return get_top_strain(text)

# Allow testing
if __name__ == "__main__":
    pp_json(get_strain_info(sys.argv[1]))
