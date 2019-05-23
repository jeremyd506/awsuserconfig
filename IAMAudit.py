#! /usr/bin/python
import boto3
from pprint import pprint
import json
import datetime
import sys
client = boto3.client('iam')

#Helper to convert dates for json output
def timeConvert(date):
    if isinstance(date, datetime.datetime):
        return date.__str__()

def getUser(username):
  userjson = client.get_user(
    UserName=username
  )
  return userjson

def getManaged(username):
    managed = client.list_attached_user_policies(
      UserName=username
    )
    return managed

def getInline(username):
    inline = client.list_user_policies(
    UserName=username,
    )
    return inline   

def getGroups(username):
    groups = client.list_groups_for_user(
    UserName=username
    )
    return groups

def singleUser(username, outputfile):
    userjson = getUser(username)
    managed = getManaged(username)
    inline = getInline(username)
    groups = getGroups(username)

    #Build Json object
    s = {username: {}}
    s[username].update(userjson)
    s[username].update(managed)
    s[username].update(inline)
    s[username].update(groups)
    jsonout = json.dumps(s, default = timeConvert, sort_keys=True, indent=4, separators=(',', ': '))
    if outputfile != '':
        with open(outputfile, 'w') as output:
            output.write(jsonout)
    else:
        print(jsonout)
    return


def multipleUser(inputfile,outputfile):
    with open(inputfile) as infile: 
        user = infile.readline()
        s = {'users': {}}
        while user:
            user = user.strip()
            userjson = getUser(user)
            managed = getManaged(user)
            inline = getInline(user)
            groups = getGroups(user)
            d = {user: {}}
            s['users'].update(d)
            s['users'][user].update(userjson)
            s['users'][user].update(managed)
            s['users'][user].update(inline)
            s['users'][user].update(groups)
            user = infile.readline()
        jsonout = json.dumps(s, default = timeConvert, sort_keys=True, indent=4, separators=(',', ': '))
        if outputfile != '':
            with open(outputfile, 'a+') as output:
                output.write(jsonout)
        else:
            print(jsonout)
           
    return


#main
inputfile=''
outputfile=''
user=''
for i in range(len(sys.argv)):
    if sys.argv[i] == "-i":
        inputfile = sys.argv[i+1]
    elif sys.argv[i] == "-u":
        user = sys.argv[i+1]
    elif sys.argv[i] == "-o":
        outputfile = sys.argv[i+1]
    elif sys.argv[i] == "-h":
        print "Usage: python IAMAudit.py -u myuser"
        print "Usage: python IAMAudit.py -u myuser -o outputfile"
        print "Usage: python IAMAudit.py -i inputfile"
        print "Usage: python IAMAudit.py -i inputfile -o outputfile"
        print "Usage: input files must be singline line username values"
        sys.exit()

if user != '' and inputfile != '':
    print "Two inputs given at -u and -i please only use one"
    sys.exit()
elif user == '' and inputfile == '':
    print "No input given"
    sys.exit()
elif user != '' and inputfile == '':
    singleUser(user,outputfile)
elif user == '' and inputfile != '':
    multipleUser(inputfile,outputfile)