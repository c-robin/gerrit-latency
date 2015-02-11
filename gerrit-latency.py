#! /usr/bin/python
# -*- coding: UTF-8 -*-

import urllib
import subprocess
import re
from urllib2 import Request, urlopen, URLError, HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, build_opener, install_opener
import json
from requests.auth import HTTPDigestAuth
import requests
from datetime import datetime

class Commit():

    def __init__(self, start_date, merge_date):
        self.start= start_date
        self.merge = merge_date
        
    def __str__(self):
        return str(self.start) + " " + str(self.merge)

def parseDate(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

#Loading config
config = {}
execfile("conf.py", config)
gerrit_user = config["gerrit_user"]
gerrit_pass = config["gerrit_pass"]
gerrit_ssh_port = config["gerrit_ssh_port"]
gerrit_http_port = config["gerrit_http_port"]
gerrit_url = config["gerrit_url"]
ssh_public_key = config["ssh_public_key"]
gerrit_request = config["gerrit_request"]

#Get changes list
ret = subprocess.Popen(["ssh","-p",gerrit_ssh_port, "-i", ssh_public_key, gerrit_user + "@" + gerrit_url, "gerrit query " + gerrit_request], stdout=subprocess.PIPE);
out, err = ret.communicate()

commits_list = []
changes_list = list(set(re.findall("change (.{40})", out)))

commit_start_date = None
commit_merge_date = None

#Call gerrit_REST_API
for change in changes_list:
    try:
        url = "http://" + gerrit_url + ":" + gerrit_http_port + "/a/" + "changes/" + change + "/detail"
        print url
        print "sending request"
        r = requests.get(url, auth = HTTPDigestAuth(gerrit_user, gerrit_pass), timeout=None, proxies = None)
        print "request sent"
        with open("Output.txt", "w") as text_file:
            text_file.write(r.text)

        data = json.loads(r.text[4:]) #We have to remove ")]}'" from the beginning of the response

        for message in data["messages"]:
            if "Uploaded patch set 1." in message["message"]:
                commit_start_date = parseDate(message["date"][0:19])
            if "successfully merged" in message["message"] or "successfully merged" in message["message"]:
                commit_merge_date = parseDate(message["date"][0:19])
                commits_list.append(Commit(commit_start_date, commit_merge_date))
    except URLError, e:
        print 'REST error:', e
for commit in commits_list:
    print commit