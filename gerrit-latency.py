#! /usr/bin/python
# -*- coding: UTF-8 -*-

import urllib
import subprocess
import re
from urllib2 import Request, urlopen, URLError, HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, build_opener, install_opener

class Commit():

    def __init__(self, start_date, merge_date):
        self.start= start_date
        self.merge = merge_date

def parseDate(date_string):
    return datetime.strptime(date_string, "%d. %b %I:%M")

gerrit_user = "crobin"
gerrit_ssh_port = "29418"
gerrit_http_port = "8080"
gerrit_url = "localhost"
ssh_public_key = "~/.ssh/id_rsa"
gerrit_pass = ""
#DO not forget to use status:merged in request
gerrit_request = "owner:self status:merged"

passman = HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, gerrit_url + ":" + gerrit_http_port, gerrit_user, gerrit_pass)
authhandler = HTTPBasicAuthHandler(passman)
opener = build_opener(authhandler)
install_opener(opener)

# locale variable for strptime (windows)
# locale.setlocale(locale.LC_ALL, 'american')
# locale variable for strptime (Unix)
# locale.setlocale(locale.LC_ALL, 'en_US')


ret = subprocess.Popen(["ssh","-p",gerrit_ssh_port, "-i", ssh_public_key, gerrit_user + "@" + gerrit_url, "gerrit query " + gerrit_request], stdout=subprocess.PIPE);
out, err = ret.communicate()

commits_list = []
changes_list = list(set(re.findall("change (.{40})", out)))

#Call gerrit_REST_API
for change in changes_list:
    try:
        request = Request("http://" + gerrit_url + ":8080/a/" + "changes/" + change + "/detail")
        print "http://" + gerrit_url + ":" + gerrit_http_port + "/a/" + "changes/" + change + "/detail"
        print "request sent"
        response = urlopen(request).read()
    
        print response
    except URLError, e:
        print 'REST error:', e