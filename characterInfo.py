import json

#Returns list of friends
def getFriends(jsonData):
    data = json.loads(jsonData)
    friendList = []
    for friend,value in data.items():
        if value['unlock']==True:
            friendList.append(friend)
    #print(friendList)
    return friendList

#Returns affection value of given friend
def checkAffection(jsonData,friend):
    data = json.loads(jsonData)
    affection = data[friend]['affection']
    #print(affection)
    return affection

#Returns json with affection update
def changeAffection(jsonData,friend,val):
    data = json.loads(jsonData)
    data[friend]['affection'] += val
    new_data = json.dumps(data)
    return new_data

#Returns json with friend unlock status updated
def unlockFriend(jsonData,friend):
    data = json.loads(jsonData)
    data[friend]['unlock'] = True
    new_data = json.dumps(data)
    return new_data

if __name__ == '__main__':
    stats= {
        'int':1,
        'phy':1,
        'chr':1,
        'luk':1
    }
    friends = {
        'Albert':{
            'unlock': False,
            'affection':0
            },
        'Jessica':{
            'unlock': False,
            'affection':0
            },
        'Sophie':{
            'unlock': False,
            'affection':0
            },
        'Tom':{
            'unlock': False,
            'affection':0
            },
        'Ophelia':{
            'unlock': False,
            'affection':-100
            }
        }

    friendlist = json.dumps(friends)
    test = json.dumps(stats)
    print(getFriends(friendlist))
    print(checkAffection(friendlist,"Albert"))
