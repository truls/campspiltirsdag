#!/usr/bin/python2


from json import JSONDecoder
import urllib2
from subprocess import Popen, PIPE, call
import codecs
import os
import sys


class Directory:
    def __init__(self):
        self.dirs = []

    def pushd(self, dir):
        self.dirs.append(os.getcwd())
        os.chdir(dir)

    def popd(self):
        os.chdir(self.dirs.pop())


json = JSONDecoder()
d = Directory()

users = ['Athas', 'blackplague', 'jlouis', 'kjmikkel', 'Munksgaard', 'Munter', 'NajaWulff', 'omegahm', 'roschnowski ', 'svip', 'truls']

commit = {}




# Basepath. Set to pwd if not specifie
cwd = os.getcwd()
if len(sys.argv) > 1:
    cwd = sys.argv[1]
    

# Create directories and get list of user repostiroes

for user in users:
    userstate = []
    os.chdir(cwd)
    #d.pushd(cwd)
    try:
        os.mkdir(user)
        print "Creating dir for ", user
    except OSError:
        pass

    
    try:
        # Get user fullname
        with open(user + ".name", "r") as f:
            username = f.read().strip()
    except:
        with codecs.open(user + ".name", "w", encoding="utf-8") as f:
            userinfo = urllib2.urlopen("http://github.com/api/v2/json/user/show/" + user)
            userjson = json.decode(userinfo.read())
            try:
                username = userjson["user"]["name"]
            except:
                username = "user"
            f.write(username)



    commit[user] = 0

    os.chdir(os.path.join(cwd, user))

    ghjson = urllib2.urlopen("http://github.com/api/v2/json/repos/show/" + user)
    #gh = ghjson
    repos = json.decode(ghjson.read())
    #print repos
    for repo in repos["repositories"]:
        try:
            print "Current dir:", os.getcwd()
            # Get latest commit
            with open(repo["name"] + ".status", "r") as f:
                latestcommit = f.read().strip()
            print "Loaded saved lastest commit:", latestcommit
        except IOError, e:
            #print e
            if not e.errno == 2:
                raise
            latestcommit = ""
            print "No saved lastest commit"
        
        try:
            commitinfo = urllib2.urlopen("http://github.com/api/v2/json/commits/list/" + user + "/" + repo["name"] + "/master")
            commitjson = json.decode(commitinfo.read())
            currentcommit = commitjson["commits"][0]["id"]
            print "Github says current commit is", currentcommit
        except:
            print "Fetching latest commit from ghithub failed. WTF??"
            currentcommit = "failed"
 
        if latestcommit != currentcommit:

            print "********New commit. Updating"

            with open(repo["name"] + ".status", "w") as f:
                f.write(currentcommit)
        
            #print repo
            if not os.path.isdir(os.path.join(os.getcwd(), repo["name"])):
                print "Cloning repository ", repo["name"]
                call(["git", "clone", repo["url"]])
            else:
                print "Pulling repository ", repo["name"]
                ocwd = os.getcwd()
                os.chdir(os.path.join(ocwd, repo["name"]))
                call(["git", "pull"])
                os.chdir(ocwd)

        ocwd = os.getcwd()
        os.chdir(os.path.join(ocwd,repo["name"]))
        print "Commit count for", user, "is now", commit[user]
        commit[user] += len(Popen(["git", "log", "--pretty=format:\"%H\"", "--since=1302883200"], stdout=PIPE).communicate()[0].split())
        print "Commit count for", user, "is now", commit[user]
        os.chdir(ocwd)
        #"--author=\"%s\"" % username
os.chdir(cwd)
with open("commitcount.txt", "w") as f:
    for name, commits in commit.iteritems():
        f.write("%s %d\n" % (name, commits))

print commit    

