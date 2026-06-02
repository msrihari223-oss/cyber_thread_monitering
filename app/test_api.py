import json
import urllib.request

base = 'http://127.0.0.1:8000'

tests = [
    ('/login', {'email': 'admin@example.com', 'password': 'password'}),
    ('/analyze', {'user_id': 1, 'comment': 'The system is under attack'})
]

for path, payload in tests:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        base + path,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        print(path, resp.status, resp.read().decode())

with urllib.request.urlopen(base + '/admin/stats') as resp:
    print('/admin/stats', resp.status, resp.read().decode())
