import os

import os, sys
def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            if (parts[0] != "*"):
                allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            if (parts[1] != "*"):
                allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            if (parts[1] != "*"):
                allparts.insert(0, parts[1])
    return allparts



Request = "/Sensors/*"
TopicListToMatch =  []
TopicListToMatch.append("/Sensors/COMPASS/01")
TopicListToMatch.append("/Sensors/COMPASS/02")
TopicListToMatch.append("/Sensors/BATTERY")
TopicListToMatch.append("/Input/Keyboard")
TopicListToMatch.append("/Input/Telegram")
TopicListToMatch.append("/Input/Joystic")


def SingleTopicMatched(TopicToMatch, Request) -> bool:
    rs = splitall(Request)
    ts = splitall(TopicToMatch)
    print(rs)
    print(ts)
    IsMatchOK = True
    for i in range(len(rs)):
        if (rs[i] != ts[i]):
            IsMatchOK = False
    return IsMatchOK
     
def TopicMatched(TopicListToMatch, Request):
    RetList = []
    
    for t in TopicListToMatch:
        if SingleTopicMatched(t,Request):
           RetList.append(t)
           
    return RetList
            

print(TopicMatched(TopicListToMatch, Request))
        
    
