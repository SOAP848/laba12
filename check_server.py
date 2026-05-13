import urllib.request
import sys

try:
    resp = urllib.request.urlopen('http://localhost:8000/docs', timeout=5)
    print('Status:', resp.status)
    print('Response length:', len(resp.read()))
except Exception as e:
    print('Error:', e)