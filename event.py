import characterInfo as cInfo
import random

#scenario dict (raw values)
def baseEvent(cChr,cLuk):
    scenario = {
        'bonus':False,
        'bonus_type':'none',
        'event_rarity': 0,
        'event':'',
        'event_text':''
        }
    
    bonus = random.randint(1,100)
    if cLuk < bonus:
        #Bonus Event Created
        scenario['bonus'] = True
        if bonus < 20:
            scenario['bonus_type'] = 'int'
        elif bonus < 40:
            scenario['bonus_type'] = 'phy'
        elif bonus < 60:
            scenario['bonus_type'] = 'chr'
        elif bonus < 80:
            scenario['bonus_type'] = 'luk'
        else:
            scenario['bonus_type'] = 'hp'
        
    #Generate normal event
    diff = (100 - cChr)/5
    badThresh = diff
    avgThresh = badThresh + (3*diff)
    gudThresh = avgThresh + diff
    
    rng = random.randint(1,100)
    if rng <= badThresh:
        scenario['event_rarity'] = 1
        scenario['event_text'] = 'poorly.'
        #Bad Event
    elif rng <= avgThresh:
        scenario['event_rarity'] = 2
        scenario['event_text'] = 'moderately well.'
        #Average Event
    elif rng <= gudThresh:
        #Good Event
        scenario['event_rarity'] = 4
        scenario['event_text'] = 'very well.'
    else:
        #Friend Event
        scenario['event_rarity'] = 3
        
    return scenario

#determine friend unlock, bonus?
def friendEvent(scenario,friend,name):
    frnList = cInfo.getFriends(friend)
    
    if name in frnList:
        #Friend unlocked
        cInfo.changeAffection(friend,name,10)
        change = {
            'event':'Friend',
            'friend_name':name,
            'friend_change': 10,
            'affection_bonus': False,
            'event_text':f'Hung out with {name} while '
            }
        if cInfo.checkAffection(friend,name) > 40:
            change['affection_bonus'] = True
        
    else:
        #Friend not unlocked
        #cInfo.unlockFriend(friend,name)
        change = {
            'event':'Friend Unlock',
            'friend_name': name,
            'event_text':f'Became friends with {name}.'
            }
    scenario.update(change)
    return scenario
    
def statfromFriendEvent(scenario):
    #resolve friend event
    if scenario['event'] == 'Friend':
        if scenario['affection_bonus']:
            return  3
        else:
            return 2
    else:
        return 0

def pickScene(action,cInt,cPhy,cChr,cLuk,friend):
    cat = action[:1]
    choice = action[1:]
    scenario = baseEvent(cChr,cLuk)
    
    stat_change = {
        'int':0,
        'phy':0,
        'chr':0,
        'luk':0
        }
    hp = 0
    
    if scenario['bonus']:
        if scenario['bonus_type'] == 'hp':
            hp = 2
        else:
            stat_change[scenario['bonus_type']] += 1
    
    if cat == 's':
    #self action tab
        scenario['event'] = choice.capitalize()
        
        val = scenario['event_rarity']
        trainingBonus = round(cInt/100,1) + 1
        
        fatigue = 6
        fatigueBonus = 1 - round(cPhy/100,1)
        
        stat = ''
        
        if choice == 'study':
            stat = 'int'
            
            if val == 3:
                #resolve friend event
                friendEvent(scenario,friend,'Albert')
                val = statfromFriendEvent(scenario)
                scenario['event_text'] += 'studying.'
            else:
                scenario['event_text'] = 'Studied ' + scenario['event_text']
            
            
        elif choice == 'workout':
            stat = 'phy'
            if val == 3:
                #resolve friend event
                friendEvent(scenario,friend,'Tom')
                val = statfromFriendEvent(scenario)
                scenario['event_text'] += 'working out.'
            else:
                scenario['event_text'] = 'Workout went ' + scenario['event_text']
        
        elif choice == 'act':
            stat = 'chr'
            if val == 3:
                #resolve friend event
                friendEvent(scenario,friend,'Jessica')
                val = statfromFriendEvent(scenario)
                scenario['event_text'] += 'acting.'
            else:
                scenario['event_text'] = 'Acting went ' + scenario['event_text']
                
        else: #pray
            stat = 'luk'
            if val == 3:
                #resolve friend event
                friendEvent(scenario,friend,'Sophie')
                val = statfromFriendEvent(scenario)
                scenario['event_text'] += 'praying.'
            else:
                scenario['event_text'] = 'Praying went ' + scenario['event_text']
        
        val *= trainingBonus
        fatigue *= fatigueBonus
        
        stat_change[stat] += round(val,1)
        hp -= round(fatigue,1)
        
    elif cat == 'r':
        scenario['event'] = choice.capitalize()
        #rest action
        stat = ''
        val = 0
        recovery = 20
        
        if choice == 'read':
            stat = 'int'
            val = 1
            scenario['event_text'] = 'Chilled and read some novels.'
        elif choice == 'yoga':
            stat = 'phy'
            val = 1
            scenario['event_text'] = 'Eased tensions in the body and mind.'
        elif choice == 'nothing':
            scenario['event_text'] = 'Stared into the void.'
       #     if cLuk > 50:
       #         cInfo.unlockFriend(friend,'Ophelia')
        else: #sleep
            scenario['event_text'] = 'Got some well needed rest.'
            recovery = 25
        
        #change HP += recovery
        if stat != '':
            stat_change[stat] += val
        hp += recovery
    else:
        #friend action
        scenario['event'] = choice.capitialize()
        frnList = cInfo.getFriends(friend)
        if not frnList:
            return 'Error'
        #if choice == 'study':
            #scenario['event'] = 'Group Study'
            
        #elif choice == 'sports':
            
        #elif choice == 'chat':
            
        #else: #outing
    scenario['hp'] = hp
    scenario['stat_change'] = stat_change
    return scenario

def month(mth):
    mmm = ''
    if mth > 6:
        if mth > 9:
            if mth > 11:
                mmm = 'Aug'
            elif mth > 10:
                mmm = 'Jul'
            else:
                mmm = 'Jun'
        else:
            if mth > 8:
                mmm = 'May'
            elif mth > 7:
                mmm = 'Apr'
            else:
                mmm = 'Mar'
    else:
        if mth > 3:
            if mth > 5:
                mmm = 'Feb'
            elif mth > 4:
                mmm = 'Jan'
            else:
                mmm = 'Dec'
        else:
            if mth > 2:
                mmm = 'Nov'
            elif mth > 1:
                mmm = 'Oct'
            else:
                mmm = 'Sep'
    
    return mmm
    
#def main():
    
#main()