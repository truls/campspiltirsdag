#!/usr/bin/python2

from json import JSONDecoder
import urllib2
import codecs
from dateutil.parser import parse as dateparser
import os
import cPickle as pickle
import time

json = JSONDecoder()

users = {'Athas': {'commits': 0},
         'blackplague': {'commits': 0},
         'jlouis': {'commits': 0},
         'kjmikkel': {'commits': 0},
         'Munter': {'commits': 0},
         'NajaWulff': {'commits': 0},
         'omegahm': {'commits': 0},
         'roschnowski': {'commits': 0},
         'svip': {'commits': 0},
         'truls': {'commits': 0},
         'degeberg': {'commits': 0},
         }

commit= {}

#lanstart = 1302883200
lanstart = dateparser("2011-04-15T16:00:00+01:00")

lcaseusers = []
for user in users.iterkeys():
    lcaseusers.append(user.lower())

# Load users and their commits
if os.path.exists("commits.pickle"):
    with open("commits.pickle") as f:
        users = pickle.load(f)

# Create directories and get list of user repostiroes

for user in users.iterkeys():
    print "Processing user:", user
    
    # Get all repos for suer
    ghjson = urllib2.urlopen("http://github.com/api/v2/json/repos/show/" + user)
    #gh = ghjson
    repos = json.decode(ghjson.read())
    #print repos
    for repo in repos["repositories"]:
        reponame = repo["name"]
        print "Processing repo:,", reponame

        try:
            users[user][reponame]
        except:
            users[user][reponame] = {}
        

        ghjson = urllib2.urlopen("http://github.com/api/v2/json/repos/show/" + user + "/" + reponame + "/branches")
        time.sleep(2)
        branches = json.decode(ghjson.read())
        #print branches["branches"]
        for branch, head in branches["branches"].iteritems():
            print "Processing branch", branch

            try:
                users[user][reponame][branch]
            except:
                users[user][reponame][branch] = ""

            
            oldhead = users[user][reponame][branch]
            if oldhead == head:
                print "No updates in %s/%s" % (reponame, branch)
                continue
            print "Updates for repository", reponame, "old head:", oldhead, "new head:", head
            users[user][reponame][branch] = head

            page = 1

            stoploop = False

            while True:
                try:
                    url = "http://github.com/api/v2/json/commits/list/" + \
                          user + "/" + reponame + "/" + branch + "?page=" + str(page)
                    print "Fetching URL:", url
                    decoder = codecs.getdecoder('utf-8')
                    commitinfo = urllib2.urlopen(url).read()
                    try:
                        commitinfo =  decoder(commitinfo)[0]
                        # Github only 60 requests every minute
                        time.sleep(2)
                    except UnicodeDecodeError:
                        print "FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU"
                        # Let's try next page to see if that's any better
                        page += 1
                        continue
                    
                    commits = json.decode(commitinfo)["commits"]
                except urllib2.HTTPError:
                    print "Fetching commits from github failed. That we have reached the end of the list."
                    stoploop = True
                
                for commit in commits:
                    #print commit
                    ctime = dateparser(commit["committed_date"])
                    print ctime, "<",  lanstart, ctime < lanstart

                    print oldhead, "==", commit["id"], oldhead == commit["id"]
                    if ctime < lanstart or oldhead == commit["id"]:
                        print "stoploop"
                        stoploop = True
                        break 

                    comitter = commit["committer"]["login"]
                    if comitter == '':
                        # We need something. Lets try using name instead
                        print "Login was empty... Wierd... Using name instead"
                        comitter = commit["committer"]["name"].lower()
                    if not comitter.lower() in lcaseusers:
                        print "Not our commit. This was comitted by", comitter
                        if comitter.strip() == "":
                            print commit
                        continue

                    # Increment commitcount
                    users[comitter]["commits"] += 1
                    print "One more commit for %s :)" % comitter

                if stoploop:
                    break
                page += 1
 


print "Commit counts"
with open("commitcount.txt", "w") as f:
    for name in users.iterkeys():
        userline = "%s %d\n" % (name, users[name]["commits"])
        f.write(userline)
        print userline
        

print "Pickling sate"
with open("commits.pickle", "w") as f:
    pickle.dump(users, f)

