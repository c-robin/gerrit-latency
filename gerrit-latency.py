#! /usr/bin/python
# -*- coding: UTF-8 -*-

import urllib
from datetime import date, datetime
import subprocess
import re

class Commit():

    def __init__(self, start_date, merge_date):
        self.start= start_date
        self.merge = merge_date

def parseDate(date_string):
    return datetime.strptime(date_string, "%d. %b %I:%M")

gerrit_user = "crobin"
gerrit_port = "29418"
gerrit_url = "localhost:8080"
ssh_public_key = "~/.ssh/id_rsa"
#DO not forget to use status:merged in request
gerrit_request = "owner:self status:merged"


# locale variable for strptime (windows)
# locale.setlocale(locale.LC_ALL, 'american')
# locale variable for strptime (Unix)
# locale.setlocale(locale.LC_ALL, 'en_US')


ret = subprocess.Popen(["ssh","-p",gerrit_port, "-i", ssh_public_key, gerrit_user + "@" + gerrit_url, "gerrit query " + gerrit_request], stdout=subprocess.PIPE);
out, err = ret.communicate()

commits_list = []
changes_list = list(set(re.findall("change (.{40})", out)))

#Call gerrit_REST_API
for change in changes_list:
    pass