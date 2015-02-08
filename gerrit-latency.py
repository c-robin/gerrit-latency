#! /usr/bin/python
# -*- coding: UTF-8 -*-

import urllib
import bs4 as bs
from datetime import date, datetime
import locale

class Commit():

    def __init__(self, start_date, merge_date):
        self.start= start_date
        self.merge = merge_date

def parseDate(date_string):
    return datetime.strptime(date_string, "%d. %b %I:%M")

gerrit_url="localhost:8080"
#DO not forget to use status:merged in request
gerrit_request="owner:self status:merged"


# ENV variables for strptime
locale.setlocale(locale.LC_ALL, 'en_US')

query_url = gerrit_url + gerrit_request
query_url="/home/zycho/workspace/gerrit-latency/data/list.html"

#commits_list = []

#query_html = bs.BeautifulSoup(urllib.urlopen(query_url).read())
#for commit in query_html.findAll("td","cSUBJECT"):
#    commit_url = commit.a.get("href")
commit_url = "/home/zycho/workspace/gerrit-latency/data/change1.html"
commit_html = bs.BeautifulSoup(urllib.urlopen(commit_url).read())
change_history = commit_html.findAll("div", "com-google-gerrit-client-change-Message_BinderImpl_GenCss_style-header")
start_date = date.today()
stop_date = date.today()
for row in change_history:
    if "Uploaded patch set 1." in row.findChildren()[1]:
        print row.findChildren()[2].contents[0]
        start_date = parseDate(row.findChildren()[2].contents[0])
    if "successfully merged" in row.findChildren()[1] or "successfully merged" in row.findChildren()[1]:
        stop_date = parseDate(row.findChildren()[2].contents[0])
c1 = Commit(start_date, stop_date)
commits_list.append(c1)

        
