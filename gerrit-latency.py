#! /usr/bin/python
# -*- coding: UTF-8 -*-

import urllib
import subprocess
import re
import json
from requests.auth import HTTPDigestAuth
import requests
from datetime import datetime
from workdays import networkdays

class Commit():

    def __init__(self, start_date, merge_date):
        self.start= start_date
        self.merge = merge_date
    
    def latency(self):
        return (self.merge - self.start).days

    def __str__(self):
        return str(self.start) + " " + str(self.merge)

def parseDate(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

#Loading config
config = {}
execfile("conf.py", config)
gerrit_user = config["gerrit_user"]
gerrit_pass = config["gerrit_pass"]
gerrit_http_port = config["gerrit_http_port"]
gerrit_url = config["gerrit_url"]
gerrit_request = config["gerrit_request"]

changes_id_list = []
commits_list = []
data_list = []

def get_changes(gerrit_request=""):
    if gerrit_request == "":
        gerrit_request = config["gerrit_request"]
    url =  "http://" + gerrit_url + ":" + gerrit_http_port + "/a/" + "changes/?q=" + gerrit_request
    r = requests.get(url, auth = HTTPDigestAuth(gerrit_user, gerrit_pass), timeout=None, proxies = None)
    #We have to remove ")]}'" from the beginning of the response
    json_changes = json.loads(r.text[4:])
    return json_changes

def get_changes_detail(gerrit_request=""):
    json_changes = get_changes(gerrit_request)

    for change in json_changes:
        changes_id_list.append(change["id"])

    data_list = []

    #Call gerrit_REST_API
    for change in changes_id_list:
        url = "http://" + gerrit_url + ":" + gerrit_http_port + "/a/" + "changes/" + change + "/detail"
        r = requests.get(url, auth = HTTPDigestAuth(gerrit_user, gerrit_pass), timeout=None, proxies = None)

        #We have to remove ")]}'" from the beginning of the response
        data = json.loads(r.text[4:])
        data_list.append(data)
    return data_list

def analyse_detail(data_list):
    commits_list = []

    #Construction of commits_list
    for data in data_list:
        # We take the first message as commit_date
        commit_start_date = parseDate(data["messages"][0]["date"][0:19])
        for message in data["messages"]:
            if "successfully merged" in message["message"] or "successfully rebased" in message["message"]:
                commit_merge_date = parseDate(message["date"][0:19])
                commits_list.append(Commit(commit_start_date, commit_merge_date))

    print str(len(commits_list)), str(len(changes_id_list))
    for commit in commits_list:
        print commit

    #Compute Latency annd display
    latency = [commit.latency() for commit in commits_list]
    print latency

def analyse(data_list):
    commits_list = []

    #Construction of commits_list
    for data in data_list:
        # We take the first message as commit_date
        commit_start_date = parseDate(data["created"][0:19])
        commit_merge_date = parseDate(data["updated"][0:19])

        commits_list.append(Commit(commit_start_date, commit_merge_date))

    print str(len(commits_list)), str(len(changes_id_list))
    for commit in commits_list:
        print commit

    #Compute Latency annd display
    latency = [commit.latency() for commit in commits_list]
    print latency




