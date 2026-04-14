import os
from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
import json
from event import pickScene, month
from characterInfo import changeAffection,unlockFriend,getFriends
#from time import sleep

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)
#app.app_context().push()

class Char(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    int = db.Column(db.Integer)
    phy = db.Column(db.Integer)
    chr = db.Column(db.Integer)
    luk = db.Column(db.Integer)
    yr = db.Column(db.Integer)
    month = db.Column(db.Integer)
    hp = db.Column(db.Integer)
    friend = db.Column(db.JSON)
    
friends = {
    'Albert':{'unlock': False,'affection':0},
    'Jessica':{'unlock': False,'affection':0},
    'Sophie':{'unlock': False,'affection':0},
    'Tom':{'unlock': False,'affection':0},
    'Ophelia':{'unlock': False,'affection':-100}
    }
fl = json.dumps(friends)

#test = Char(name='Test',int=1,phy=1,chr=1,luk=1,yr=1,month=1,hp=100,friend=fl)
    #name,bday, int, phy, chr, luk, yr, mth, hp, friends

#db.create_all()

#db.session.add(test)
#db.session.commit()
    
class CharLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    char_id = db.Column(db.Integer,db.ForeignKey('char.id'),nullable=False,index=True)
    date = db.Column(db.String(5)) #Y1MMM
    event_type = db.Column(db.String(15))
    scenario_text = db.Column(db.String(100))
    status_change = db.Column(db.String(150))
    bonus = db.Column(db.Boolean)
    bonus_scenario = db.Column(db.String(100))
    
#db.create_all()

def nextTurn(char):
    date = f'Y{char.yr}{month(char.month)}'
    #sleep(3)
    if char.yr == 1:
        if char.month == 3:
            majorEvent('exam1',char,date)
        elif char.month == 6:
            majorEvent('exam2',char,date)
        elif char.month == 8:
            majorEvent('sport1',char,date)
        elif char.month == 10:	
            majorEvent('exam3',char,date)
    elif char.yr == 2:
        if char.month == 3:
            majorEvent('exam4',char,date)
        elif char.month == 6:
            majorEvent('exam5',char,date)
        elif char.month == 8:
            majorEvent('sport2',char,date)
        elif char.month == 10:
            majorEvent('exam6',char,date)
        elif char.month == 11:
            trip(char,date)
    else:
        if char.month == 3:
            majorEvent('exam7',char,date)
        elif char.month == 6:
            majorEvent('exam8',char,date)
        elif char.month == 8:
            majorEvent('sport3',char,date)
        elif char.month == 10:
            prom(char,date)
            #sleep(3)
            majorEvent('exam9',char,date)
    
    char.month += 1
    if char.month > 12:
        char.month = 1
        char.yr +=1
        
    db.session.commit()
    return None
        
def statUpdate(scene, char):
    status_change = ''
    if scene['event'] == 'Friend':
        char.friend = changeAffection(char.friend,scene['friend_name'],scene['friend_change'])
        status_change += f"+{scene['friend_change']} {scene['friend_name']} affection, "
    elif scene['event'] == 'Friend Unlock':
        char.friend = unlockFriend(char.friend,scene['friend_name'])
        status_change += f"Became friends with {scene['friend_name']}. "
        
    #print(scene['stat_change'])
    for stat, val in scene['stat_change'].items():
        if val != 0:
            status_change += f'+{val}{stat.upper()}, '
            if stat == 'int':
                char.int += val
            elif stat == 'phy':
                char.phy += val
            elif stat == 'chr':
                char.chr += val
            else:
                char.luk += val
    
    status_change += f"{'+' if scene['hp']> 0 else ''}{scene['hp']}HP"
    char.hp += scene['hp']
    
    return status_change

@app.route('/')
def home():
    return redirect('/tutorial')

#/tutorial
@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

#/create-character/?name=name
@app.route('/create_character/')
def create_character():
    name = request.args.get('name')
    
    newChar = Char(name=name,int=1,phy=1,chr=1,luk=1,yr=1,month=1,hp=100,friend=fl)
    #name,bday, int, phy, chr, luk, yr, mth, hp, friends
    db.session.add(newChar)
    db.session.commit()
    charID = newChar.id
    introCeremony = CharLog(char_id=charID,
                            date="Y1Sep",
                            event_type="Welcome Ceremony",
                            scenario_text="Listened to the principal speak for an hour.",
                            status_change = "It's the first day.",
                            bonus=False,
                            bonus_scenario="")
    db.session.add(introCeremony)
    db.session.commit()
    
    
    return redirect (f'/game/?id={charID}')

#/game/?id={charID}
@app.route('/game/')
def main_page():
    charID = request.args.get('id')
    char = Char.query.filter_by(id=charID).one()
    
    logs = CharLog.query.filter_by(char_id=charID).all()
    latest = CharLog.query.filter_by(char_id=charID).order_by(CharLog.id.desc()).first()
    
    friendList = getFriends(char.friend)
    return render_template('game_ui.html', char=char, logs=logs,latest=latest,friends=friendList)

#/action/study/?id=id
@app.route('/<int:char_id>/action/study/', methods=['POST'])
def self_study(char_id):
    #charID = request.args.get('id')
    char = Char.query.filter_by(id=char_id).one_or_none()
    if char.hp <= 0:
        return redirect(f'/game_over/?id={char.id}')
    if char.yr == 3 and char.month == 11:
        return redirect(f'/graduated/?id={char.id}')
    
    if char is None:
        return "Character not found.", 404
    #wire = str(char_id)
    #return wire
    scene = pickScene('sstudy',char.int,char.phy,char.chr,char.luk,char.friend)
    #{bonus:bool,bonus_type:stat,event_rarity:int,event:str,stat_change:dict,hp:int}
    # if friend {friend_name,friend_change,affection_bonus}
    #return scene
    if scene['bonus']:
        extra = scene['bonus_type']
        if extra == 'hp':
            val = 2
        else:
            val = 1
            #
        bonus_scenario = f"Bonus! Gained {val} {scene['bonus_type'].upper()}"
    else:
        bonus_scenario = ''
        
    status_change = statUpdate(scene, char)

    date = f'Y{char.yr}{month(char.month)}'
    #create month function
    log = CharLog(char_id=char_id, date=date, event_type=scene['event'],scenario_text=scene['event_text'],status_change=status_change,bonus=scene['bonus'],bonus_scenario=bonus_scenario)
    db.session.add(log)
    db.session.commit()
    
    nextTurn(char)
    
    return redirect (f'/game/?id={char_id}')
#/action/workout
@app.route('/<int:char_id>/action/workout/', methods=['POST'])
def self_workout(char_id):
    char = Char.query.filter_by(id=char_id).one_or_none()
    if char.hp <= 0:
        return redirect(f'/game_over/?id={char.id}')
    if char.yr == 3 and char.month == 11:
        return redirect(f'/graduated/?id={char.id}')
    
    if char is None:
        return "Character not found.", 404
    scene = pickScene('sworkout',char.int,char.phy,char.chr,char.luk,char.friend)
    
    if scene['bonus']:
        extra = scene['bonus_type']
        if extra == 'hp':
            val = 2
        else:
            val = 1
            #
        bonus_scenario = f"Bonus! Gained {val} {scene['bonus_type'].upper()}"
    else:
        bonus_scenario = ''
        
    status_change = statUpdate(scene, char)

    date = f'Y{char.yr}{month(char.month)}'
    #create month function
    log = CharLog(char_id=char_id, date=date, event_type=scene['event'],scenario_text=scene['event_text'],status_change=status_change,bonus=scene['bonus'],bonus_scenario=bonus_scenario)
    db.session.add(log)
    db.session.commit()
    
    nextTurn(char)
    
    return redirect (f'/game/?id={char_id}')
#/action/act
@app.route('/<int:char_id>/action/act/', methods=['POST'])
def self_act(char_id):
    char = Char.query.filter_by(id=char_id).one_or_none()
    if char.hp <= 0:
        return redirect(f'/game_over/?id={char.id}')
    if char.yr == 3 and char.month == 11:
        return redirect(f'/graduated/?id={char.id}')
    
    if char is None:
        return "Character not found.", 404
    scene = pickScene('sact',char.int,char.phy,char.chr,char.luk,char.friend)
    
    if scene['bonus']:
        extra = scene['bonus_type']
        if extra == 'hp':
            val = 2
        else:
            val = 1
            #
        bonus_scenario = f"Bonus! Gained {val} {scene['bonus_type'].upper()}"
    else:
        bonus_scenario = ''
        
    status_change = statUpdate(scene, char)

    date = f'Y{char.yr}{month(char.month)}'
    #create month function
    log = CharLog(char_id=char_id, date=date, event_type=scene['event'],scenario_text=scene['event_text'],status_change=status_change,bonus=scene['bonus'],bonus_scenario=bonus_scenario)
    db.session.add(log)
    db.session.commit()
    
    nextTurn(char)
    
    return redirect (f'/game/?id={char_id}')

#/action/pray
@app.route('/<int:char_id>/action/pray/', methods=['POST'])
def self_pray(char_id):
    char = Char.query.filter_by(id=char_id).one_or_none()
    if char.hp <= 0:
        return redirect(f'/game_over/?id={char.id}')
    if char.yr == 3 and char.month == 11:
        return redirect(f'/graduated/?id={char.id}')
    
    if char is None:
        return "Character not found.", 404
    scene = pickScene('spray',char.int,char.phy,char.chr,char.luk,char.friend)
    
    if scene['bonus']:
        extra = scene['bonus_type']
        if extra == 'hp':
            val = 2
        else:
            val = 1
            #
        bonus_scenario = f"Bonus! Gained {val} {scene['bonus_type'].upper()}"
    else:
        bonus_scenario = ''
        
    status_change = statUpdate(scene, char)

    date = f'Y{char.yr}{month(char.month)}'
    #create month function
    log = CharLog(char_id=char_id, date=date, event_type=scene['event'],scenario_text=scene['event_text'],status_change=status_change,bonus=scene['bonus'],bonus_scenario=bonus_scenario)
    db.session.add(log)
    db.session.commit()
    
    nextTurn(char)
    
    return redirect (f'/game/?id={char_id}')
#/action/read
@app.route('/<int:char_id>/action/read/', methods=['POST'])
def rest_read(char_id):
    char = Char.query.filter_by(id=char_id).one_or_none()
    if char.hp <= 0:
        return redirect(f'/game_over/?id={char.id}')
    if char.yr == 3 and char.month == 11:
        return redirect(f'/graduated/?id={char.id}')
    
    if char is None:
        return "Character not found.", 404
    scene = pickScene('rread',char.int,char.phy,char.chr,char.luk,char.friend)
    
    if scene['bonus']:
        extra = scene['bonus_type']
        if extra == 'hp':
            val = 2
        else:
            val = 1
            #
        bonus_scenario = f"Bonus! Gained {val} {scene['bonus_type'].upper()}"
    else:
        bonus_scenario = ''
        
    status_change = statUpdate(scene, char)

    date = f'Y{char.yr}{month(char.month)}'
    #create month function
    log = CharLog(char_id=char_id, date=date, event_type=scene['event'],scenario_text=scene['event_text'],status_change=status_change,bonus=scene['bonus'],bonus_scenario=bonus_scenario)
    db.session.add(log)
    db.session.commit()
    
    nextTurn(char)
    
    return redirect (f'/game/?id={char_id}')

#/action/yoga
@app.route('/<int:char_id>/action/yoga/', methods=['POST'])
def rest_yoga(char_id):
    char = Char.query.filter_by(id=char_id).one_or_none()
    if char.hp <= 0:
        return redirect(f'/game_over/?id={char.id}')
    if char.yr == 3 and char.month == 11:
        return redirect(f'/graduated/?id={char.id}')
    
    if char is None:
        return "Character not found.", 404
    scene = pickScene('ryoga',char.int,char.phy,char.chr,char.luk,char.friend)
    
    if scene['bonus']:
        extra = scene['bonus_type']
        if extra == 'hp':
            val = 2
        else:
            val = 1
            #
        bonus_scenario = f"Bonus! Gained {val} {scene['bonus_type'].upper()}"
    else:
        bonus_scenario = ''
        
    status_change = statUpdate(scene, char)

    date = f'Y{char.yr}{month(char.month)}'
    #create month function
    log = CharLog(char_id=char_id, date=date, event_type=scene['event'],scenario_text=scene['event_text'],status_change=status_change,bonus=scene['bonus'],bonus_scenario=bonus_scenario)
    db.session.add(log)
    db.session.commit()
    
    nextTurn(char)
    
    return redirect (f'/game/?id={char_id}')

#/action/nothing
@app.route('/<int:char_id>/action/nothing/', methods=['POST'])
def rest_nothing(char_id):
    char = Char.query.filter_by(id=char_id).one_or_none()
    if char.hp <= 0:
        return redirect(f'/game_over/?id={char.id}')
    if char.yr == 3 and char.month == 11:
        return redirect(f'/graduated/?id={char.id}')
    
    if char is None:
        return "Character not found.", 404
    scene = pickScene('rnothing',char.int,char.phy,char.chr,char.luk,char.friend)
    
    if scene['bonus']:
        extra = scene['bonus_type']
        if extra == 'hp':
            val = 2
        else:
            val = 1
            #
        bonus_scenario = f"Bonus! Gained {val} {scene['bonus_type'].upper()}"
    else:
        bonus_scenario = ''
        
    status_change = statUpdate(scene, char)

    date = f'Y{char.yr}{month(char.month)}'
    #create month function
    log = CharLog(char_id=char_id, date=date, event_type=scene['event'],scenario_text=scene['event_text'],status_change=status_change,bonus=scene['bonus'],bonus_scenario=bonus_scenario)
    db.session.add(log)
    db.session.commit()
    
    nextTurn(char)
    
    return redirect (f'/game/?id={char_id}')

#/action/sleep
@app.route('/<int:char_id>/action/sleep/', methods=['POST'])
def rest_sleep(char_id):
    char = Char.query.filter_by(id=char_id).one_or_none()
    if char.hp <= 0:
        return redirect(f'/game_over/?id={char.id}')
    if char.yr == 3 and char.month == 11:
        return redirect(f'/graduated/?id={char.id}')
    
    if char is None:
        return "Character not found.", 404
    scene = pickScene('rsleep',char.int,char.phy,char.chr,char.luk,char.friend)
    
    if scene['bonus']:
        extra = scene['bonus_type']
        if extra == 'hp':
            val = 2
        else:
            val = 1
            #
        bonus_scenario = f"Bonus! Gained {val} {scene['bonus_type'].upper()}"
    else:
        bonus_scenario = ''
        
    status_change = statUpdate(scene, char)

    date = f'Y{char.yr}{month(char.month)}'
    #create month function
    log = CharLog(char_id=char_id, date=date, event_type=scene['event'],scenario_text=scene['event_text'],status_change=status_change,bonus=scene['bonus'],bonus_scenario=bonus_scenario)
    db.session.add(log)
    db.session.commit()
    
    nextTurn(char)
    
    return redirect (f'/game/?id={char_id}')

#/friend/study

#/friend/sports

#/friend/chat

#/friend/outing

def majorEvent(event, char, date):
    #char = Char.query.filter_by(id=charID).one()
    minVal = 0
    avgVal = 0
    maxVal = 0
    
    if 'exam' in event:
        reqStat = char.int
        
        if '1' in event:
            minVal = 4
            avgVal = 6
            maxVal = 8
        elif '2' in event:
            minVal = 6
            avgVal = 8
            maxVal = 10
        elif '3' in event:
            minVal = 10
            avgVal = 12
            maxVal = 14
        elif '4' in event:
            minVal = 14
            avgVal = 16
            maxVal = 18
        elif '5' in event:
            minVal = 20
            avgVal = 22
            maxVal = 24
        elif '6' in event:
            minVal = 22
            avgVal = 24
            maxVal = 26
        elif '7' in event:
            minVal = 26
            avgVal = 28
            maxVal = 30
        elif '8' in event:
            minVal = 30
            avgVal = 32
            maxVal = 34
        else:
            minVal = 36
            avgVal = 39
            maxVal = 42
            
        event = 'Exam'
        if reqStat >= maxVal:
            #exceled 3chr, -4hp
            scenario_text = 'Top scorer on the exam!'
            status_change = '+3CHR, -4HP'
            char.chr += 3
            char.hp -=4
            
        elif reqStat >= avgVal:
            #passed -5hp
            scenario_text = 'Passed the exam.'
            status_change = '-5HP'
            char.hp -=5
        elif reqStat >= minVal:
            #65, -6hp
            scenario_text = "Barely passed the exam."
            status_change = '-6HP'
            char.hp -=5
        else:
            #failed -10hp
            scenario_text = "DId not understand a single thing."
            status_change = '-10HP'
            char.hp -=10
        
    else:
        reqStat = char.phy
        if '1' in event:
            minVal = 2
            avgVal = 4
            maxVal = 6
        elif '2' in event:
            minVal = 6
            avgVal = 9
            maxVal = 12
        else:
            minVal = 12
            avgVal = 14
            maxVal = 16
        
        event='Sports Day'
            
        if reqStat >= maxVal:
            #exceled 3chr, 1phy -4hp
            scenario_text = 'Carried the team to victory!'
            status_change = '+3CHR, +1PHY, -4HP'
            char.chr += 3
            char.phy += 1
            char.hp -= 4
        elif reqStat >= avgVal:
            #passed 1phy, -5hp
            scenario_text = 'Did your best to win.'
            status_change = "+1PHY, -5HP"
            char.phy += 1
            char.hp -= 5
        elif reqStat >= minVal:
            #health issues, -8hp
            scenario_text = 'Tripped midrace'
            status_change = "-8HP"
            char.hp -= 8
        else:
            #failed -10hp
            scenario_text = "Spectating the event due to illness."
            status_change = "-10HP"
            char.hp -= 10
    
    log = CharLog(char_id=char.id, date=date, event_type=event,scenario_text=scenario_text,status_change=status_change,bonus=False,bonus_scenario='')
    db.session.add(log)
    db.session.commit()
        
def trip(char,date):
    char.chr += 5
    char.phy += 2
    char.luk += 2
    char.hp -= 10
    
    scenario_text = 'Went on a overnight trip with the entire school.'
    status_change = '+2PHY, +5CHR, +2LUK, -10HP'
    
    log = CharLog(char_id=char.id, date=date, event_type='School Trip',scenario_text=scenario_text,status_change=status_change,bonus=False,bonus_scenario='')
    db.session.add(log)
    db.session.commit()

def prom(char,date):
    friendList = getFriends(char.friend)
    
    status_change = ""
    scenario_text = ""
    
    if len(friendList) == 0:
        char.hp-= 50
        status_change += '-50HP'
        scenario_text += 'Huddled in the corner depressed all alone.'
    elif len(friendList) == 1:
        char.hp-= 2
        char.chr+= 1
        status_change += '+1CHR, -2HP'
        scenario_text += 'Chilled with a friend'
    else:
        char.hp-= 2
        char.chr+= 3
        status_change += '+3CHR, -2HP'
        scenario_text += 'Partied all night with friends'
    
    log = CharLog(char_id=char.id, date=date, event_type='Prom Night',scenario_text=scenario_text,status_change=status_change,bonus=False,bonus_scenario='')
    db.session.add(log)
    db.session.commit()
    
#/game_over/?id={{char.id}}')
@app.route('/game_over/')
def game_over():
    return 'Game Over!'
@app.route('/graduated/')
def graduated():
    return 'You graduated!'

    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False)
   # app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))