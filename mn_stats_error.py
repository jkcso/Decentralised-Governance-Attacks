from urllib.request import Request, urlopen
import json
import os
import ssl

# fix found from: http://blog.pengyifan.com/how-to-fix-python-ssl-certificate_verify_failed/

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

mn_stats = 'https://stats.masternode.me/network-report/latest/json'
req_stats = Request(mn_stats, headers={'User-Agent': 'Mozilla/5.0'})
stats = json.loads(urlopen(req_stats).read().decode("utf-8"))

print(stats["raw"]["mn_count"])
