import os
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



PartialTopic = "/@SAMPLE_Client/#CMD#"
FullTopicList =  []
FullTopicList.append("/@SAMPLE_Client/#CMD#/GO/fw")
FullTopicList.append("/Sensors/COMPASS/02")
FullTopicList.append("/Sensors/BATTERY")
FullTopicList.append("/Input/Keyboard")
FullTopicList.append("/Input/Telegram")
FullTopicList.append("/Input/Joystic")


def SingleTopicMatched(FullTopic, PartialTopic) -> bool:
    rs = splitall(PartialTopic)
    ts = splitall(FullTopic)
    
    IsMatchOK = True
    for i in range(len(rs)):
        if (rs[i] != ts[i]):
            IsMatchOK = False
    if (IsMatchOK):
        print(rs)
        print(ts)
    return IsMatchOK
     
def TopicMatched(FullTopicList, PartialTopic):
    RetList = []
    
    for ft in FullTopicList:
        if SingleTopicMatched(ft,PartialTopic):
           RetList.append(ft)
           
    return RetList
            

print(TopicMatched(FullTopicList, PartialTopic))
        
    
