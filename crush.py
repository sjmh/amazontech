#!/usr/bin/python

from bs4 import BeautifulSoup
from fabric.api import cd, run, sudo, env
from fabric.operations import put
from fabric.tasks import execute
import requests
import sys


def go(script, password):
  env.password = password
  with cd('/tmp'):
      put(script, '/tmp/script.sh')
      sudo('/bin/bash /tmp/script.sh')

purl = sys.argv[1]
page = requests.get(purl)
soup = BeautifulSoup(page.content, 'html.parser')

aurl = 'http://techchallenge.amazon.com'
post_url = '{0}{1}'.format(aurl, soup.form['action'])
payload = {}
for i in soup.find_all('input'):
  payload[i['name']] = i['value']

print 'submitting to {0}'.format(post_url)
session = requests.session()
req = requests.post(post_url, data=payload)
soup = BeautifulSoup(req.content, 'html.parser')

finish_url = '{0}{1}'.format(aurl, soup.find_all("a", {"class": "button small fit"})[0]['href'])
info = {}
for i in soup.blockquote.strings:
    i = i.strip()
    (name, val) = i.split(':')
    val = val.strip()
    info[name] = val

in_challenge = False
challenge = None
for t in soup.text.splitlines():
    if in_challenge:
        challenge = t.strip()
        break
    if t == 'First Question':
        in_challenge = True

if not challenge:
    print 'couldnt find challenge text'

script = None
if challenge == "You are required to serve the index file in /var/www/html successfully.":
    script = 'index'

if script:
    env.host_string = 'ec2-user@nat.techchallenge.amazon.com:{0}'.format(info['Port'])
    execute(go, script, info['Password'])
    requests.get(finish_url)
else:
    print 'couldnt determine script'
    print 'Challenge is: {0}'.format(challenge)
