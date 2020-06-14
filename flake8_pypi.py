import json
import re
from pathlib import Path

import requests as rq

pat = re.compile(b'href="/simple/([^/]+)/">')
req = rq.get('https://pypi.org/simple')

ADDL_PKGS = ['pep8-naming', 'mccabe', 'pyflakes', 'pycodestyle', 'pydocstyle']

results = {}

for mch in pat.finditer(req.content):
    pkg = mch.group(1).decode()
    if "flake8" in pkg or pkg in ADDL_PKGS:
        print(f"Retrieving {pkg}...", end='')
        try:
            req_pkg = rq.get("https://pypi.org/pypi/{}/json".format(pkg))
        except Exception:
            results.update({pkg: "JSON DOWNLOAD FAILED"})
            print("FAILED")
            continue
        
        if req_pkg.ok:
            print("OK")
            results.update({pkg: json.loads(req_pkg.content)})
#            try:
#                msg = json.loads(req_pkg.content)['info']['summary']
#            except Exception:
#                print("{}: SUMMARY SEARCH FAILED".format(pkg))
#            else:
#                print("{}: {}".format(pkg, msg))
        else:
            print("BAD RESPONSE")
            results.update({pkg: "JSON API PAGE NOT FOUND"})

with Path("f8_search.json").open('w') as f:
    json.dump(results, f)
