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
import matplotlib.pyplot as plt
import numpy as np

class Commit():
    """ This class represent one commit
    
    Attrributes:
    start_date (datetime): The date when the commit was created
    merge_date (datetime): The date when the commit was merged
    sizeadd (int): The number of lines of code added by the commit
    sizedel (int): The number of lines of code deleted by the commit
    revision (int): The number of revisions (patchsets) of the commit
    """

    def __init__(self, start_date, merge_date, sizeadd, sizedel, revision):
        self.start= start_date
        self.merge = merge_date
        self.sizeadd = sizeadd
        self.sizedel = sizedel
        self.revision = revision
        
    
    def latency(self):
        """ This method give the latency of the commit in workdays

        Returns:
            int representing the latency of the commit in days
        """
        #return (self.merge - self.start).days
        return networkdays(self.start, self.merge)

    def __str__(self):
        return str(self.start) + " " + str(self.merge) + " " + str(self.sizeadd) + "/" + str(self.sizedel) + " " + str(revision)


def parseDate(date_string):
    """ This method allow to parse a datetime from a string

    Args:
        date_string (string): a string representing a date

    Returns:
        datetime corresponding to the date_string
    """
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

#Loading config
config = {}
execfile("conf.py", config)
gerrit_user = config["gerrit_user"]
gerrit_pass = config["gerrit_pass"]
gerrit_http_port = config["gerrit_http_port"]
gerrit_url = config["gerrit_url"]
gerrit_request = config["gerrit_request"]

def get_changes(gerrit_request=""):
    """ This method allow to retrieves the data corresponding to a gerrit query

    Args:
        gerrit_request (string): a string representing the query in gerrit

    Returns:
        json corresponding to the response by gerrit_api
    """
    if gerrit_request == "":
        gerrit_request = config["gerrit_request"]
    url =  "http://" + gerrit_url + ":" + gerrit_http_port + "/a/" + "changes/?q=" + gerrit_request
    r = requests.get(url, auth = HTTPDigestAuth(gerrit_user, gerrit_pass), timeout=None, proxies = None)
    #We have to remove ")]}'" from the beginning of the response
    json_changes = json.loads(r.text[4:])
    return json_changes

def get_changes_detail(gerrit_request=""):
    """ This method allow to retrieves detailed data to all changes corresponding to a gerrit query

    Args:
        gerrit_request (string): a string representing the query in gerrit

    Returns:
        json corresponding to detailed data
    """
    json_changes = get_changes(gerrit_request)
    changes_id_list = []
    
    for change in json_changes:
        changes_id_list.append(change["id"])

    data_list = []

    #Call gerrit_REST_API http://git.ullink.lan:8080/a/changes/Id83e45438a520def11872600f3fed2021d9e8988/detail
    for change in changes_id_list:
        url = "http://" + gerrit_url + ":" + gerrit_http_port + "/a/" + "changes/" + change + "/detail"
        r = requests.get(url, auth = HTTPDigestAuth(gerrit_user, gerrit_pass), timeout=None, proxies = None)

        #We have to remove ")]}'" from the beginning of the response
        data = json.loads(r.text[4:])
        data_list.append(data)
    return data_list

def analyse_detail(data_list):
    """ This method allow to analyse all detailed data of gerrit changes

    Args:
        data_list (json_object): a json object representing a list of all  detailed changes
    """
    commits_list = []

    #Construction of commits_list
    for data in data_list:
        # We take the first message as commit_date
        commit_start_date = parseDate(data["messages"][0]["date"][0:19])
        for message in data["messages"]:
            if "successfully merged" in message["message"] or "successfully rebased" in message["message"]:
                commit_merge_date = parseDate(message["date"][0:19])
                revision = int(message["_revision_number"])
                commits_list.append(Commit(commit_start_date, commit_merge_date, data["insertions"], data["deletions"], revision))

    #for commit in commits_list:
    #    print commit

    #Compute Latency annd display
    latency = [commit.latency() for commit in commits_list]
    sizeadd = [commit.sizeadd for commit in commits_list]
    sizedel = [commit.sizedel for commit in commits_list]
    sizechange = [commit.sizedel + commit.sizeadd for commit in commits_list]
    revisions = [commit.revision for commit in commits_list]
    print graph(latency, sizeadd)
    print "size add =", np.corrcoef(latency, sizeadd) [0][1]
    print "size del =", np.corrcoef(latency, sizedel) [0][1]
    print "size total =", np.corrcoef(latency, sizechange) [0][1]
    print "corr revisions =", np.corrcoef(latency, revisions) [0][1]
    print "revision/size =", np.corrcoef(revisions, sizechange) [0][1]
        
    
def analyse(data_list):
    """ This method allow to analyse data corresponding to a gerrit query

    Args:
        data_list (json_object): a json object representing a list of all changes
    """
    commits_list = []

    #Construction of commits_list
    for data in data_list:
        # We take the first message as commit_date
        commit_start_date = parseDate(data["created"][0:19])
        commit_merge_date = parseDate(data["updated"][0:19])

        commits_list.append(Commit(commit_start_date, commit_merge_date))

    #print str(len(commits_list)), str(len(changes_id_list))
    #for commit in commits_list:
    #    print commit

    #Compute Latency annd display
    latency = [commit.latency() for commit in commits_list]
    #print latency

def graph(x, y):
    """ This method allow to print a basic graph of 2 lists. The 2 lists must have the same size.

    Args:
        x (list of double): list of all abscissae of the points in a system of Cartesian coordinate
        y (list of double): list of all ordinates of the points in a system of Cartesian coordinate
    """
    plt.plot(x, y, 'ro')
    plt.margins(0.2)
    plt.subplots_adjust(bottom=0.15)
    plt.show()

def export_data(path, gerrit_request=""):
    """ This method allow to export data in a json file from a gerrit request

    Args:
        path (string): path of the file in which you want to export
        gerrit_request (string): a string representing the query in gerrit
    """
    data = get_changes_detail(gerrit_request);
    with open(path, 'w') as outfile:
        json.dump(data, outfile)
        
def import_data(path):
    """ This method allow to import data from a json file

    Args:
        path (string): path of the json file

    Returns:
        json object corresponding to json_file
    """
    with open(path) as data_file:    
        return json.load(data_file)
