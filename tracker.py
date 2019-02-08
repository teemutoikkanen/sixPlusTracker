import re
import glob
from pprint import pprint
from time import sleep
from dbFunction import *
# from hud import hud


currentPlayers = []

'''
1. idea: käydään läpi käsihistorioita ja luodaan niistä database

- Hands
	*id 
	*data
	(*date, *players, yms...)

- Players
	*screenName
	*nHands
	*vpip
	*rfi
	*openLimp


*** Suunnitelmaa (mongoDB) ***
- vastaavasti kun resultissa käydään manuaalisesti HH:t läpi
- jokaisen kohdalla tsekataan onko käsi jo DB:ssä
- tsekataan onko pelaaja jo tietokannassa olemassa vai luodaanko uusi
- aluksi vaikka yksi statsi: rfi: tän saa helposti napattua jo samalla kun regexpaa kättä 1. kerral (eka xx 'raises')
- siis kolme vaihtoehtoa (?): 
			rfi mahdollista ja raise
			rfi mahdollista ja limp/fold
			joku reissaa ennen meitä
'''

def getSnFromSeatLine(line):
    #Seat 3: gaiggibeliin ($183.28 in chips) 
    return line.split(": ")[1].split(" (")[0]

# rfi mahdollista jos ei 'raises' ennen gaiggibeliin vuoroa
def rfiPossible(screenName, hand):

    actions = hand.split('*** HOLE CARDS ***')[1].split('*** SUMMARY ***')[0]
    actionsArray = actions.split('\n')[2:]

    for line in actionsArray:
        if (screenName in line):
            return True
        if ('raises' in line and screenName not in line):
            return False
        # todo: if everyone folds and btn wins the pot return False

    # split *** HOLE CARDS *** ja gaiggibeliin -- jos raises ennen meitä,
    # return False

    return True


def getPreflopActions(hand):

    # jos *** flop *** -> perus parse
    try:
        if ('*** FLOP ***' in hand):
            preflop = hand.split(
                '*** HOLE CARDS ***')[1].split('*** FLOP ***')[0]
            return preflop
        else:
            preflop = hand.split(
                '*** HOLE CARDS ***')[1].split('*** SUMMARY ***')[0]
            return preflop
    except Exception as e:
        print(e)
        print("getPreflopActions error")
    return ""

    # else 'Uncalled bet parse


def getBigBlind(hand):
    return hand.split(" ")[10].strip("$")


def rfi(screenName, hand):
    # jos eka preflop raises on herolta, return True
    preflop = getPreflopActions(hand)

    # rivi kerrallaan läpi, kunnes löytyy eka raises -> ja return true jos
    # herolta
    for line in preflop.split('\n'):
        if ('raises' in line):
            if (screenName in line):
                return True
            else:
                return False

    return False


def limpPossible(screenName, hand):
        # 'jos ei reissuja ennen heron vuoroa' && hero ei oo napilla

    preflop = getPreflopActions(hand)

    for line in preflop.split('\n')[2:]:

        if ('raises' in line and screenName not in line):
            return False
        if (screenName in line and getBtnPlayer(hand) is not screenName):
            return True

    return False


def openLimpPossible(screenName, hand):
    '''ei takana limppejä tai raiseja'''

    for line in getPreflopActions(hand).split('\n')[2:]:
        if ('raises' in line or 'calls' in line):
            if (screenName not in line):
                return False
        if (screenName in line and getBtnPlayer(hand) is not screenName):
            return True
    return False


def limp(screenName, hand):

    preflop = getPreflopActions(hand)
    bb = getBigBlind(hand)
    if (screenName + ': calls ' + "$" + bb in preflop):
        return True
    return False


def getSummary(hand):
    return hand.split("*** SUMMARY ***")[1]


def sortAndRemoveSuits(c1, c2):
    '''input: Jh, Ad'''
    '''output AJ    '''

    ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']

    # init ranks, LOWER IS HIGHER RANK
    c1rank = 0
    c2rank = 0
    for i in range(len(ranks)):
        if (c1[0] == ranks[i]):
            c1rank = i
        if (c2[0] == ranks[i]):
            c2rank = i

    if (c1rank <= c2rank):
        return c1[0]+c2[0]
    else:
        return c2[0]+c1[0]


def getHoleCards(screenName, hand):

    for line in getSummary(hand).split("\n"):
        line = line.replace("(button blind) ", "")
        if (screenName + ' showed' in line):
            #Seat 3: Juodasis 23 showed [Ac Kh] and won ($111.08) with two pair, Aces and Kings
            card1 = line.split("showed ")[1].split(" and")[0][1:3]
            card2 = line.split("showed ")[1].split(" and")[0][4:6]
        elif (screenName + ' mucked' in line):
            card1 = line.split("mucked ")[1].split(" and")[0][1:3]
            card2 = line.split("mucked ")[1].split(" and")[0][4:6]
        else:
            continue

        # if pair
        if (card1[0] == card2[0]):
            return card1[0]+card2[0]
        # if suited
        if (card1[1] == card2[1]):
            return sortAndRemoveSuits(card1, card2)+"s"
        else:
            return sortAndRemoveSuits(card1, card2)+"o"
    return None


def newPlayer(screenName):

    db = getDb()

    if (db.players.find({'screenName': screenName}).count() > 0):
        return False
    else:
        return True


# def getPosition(sn, hand):

#     handAsLines = hand.split("*** SUMMARY ***")[0].split("\n")
#     data = []

#     for line in handAsLines:
#         # print(line[0:5])
#         if (line[0:5] == 'Seat ' or line[0:6] == 'Table '):
#             data.append(line)

#     print(data)

#     nPlayers = len(data)-1
#     btnSeat = data[0].split(" ")[4].strip("#")

#     seatArray = []

#     return

def getBtnSeat(hand):
    for line in hand.split("\n"):
        if (line[0:6] == 'Table '):
            return line.split("#")[1][0]





def getPosition(hand, sn, screenNames):


    # sn = 'zaph'

    # btnSn = 'marta'
    btnSn = getBtnPlayer(hand)
    # playerList = ['marta', 'zaph', 'gaiggi', 'angel', 'kis']
    playerList = screenNames
    tSize = len(playerList)
    posList = ['BTN', 'CO', 'HJ', 'LJ', 'MP', 'UG']
    playerIndex = playerList.index(sn)
    btnIndex = playerList.index(btnSn)

    pos = posList[0:tSize][btnIndex-playerIndex]
    return pos

    


def getHands():
    # parse hh files into an array of hand strings
    hhPath = 'C:/Users/Teemu/AppData/Local/PokerStars.EU/HandHistorygaiggibeliin'

    filePaths = glob.glob(hhPath + "/*.txt")

    # skip other games
    sixPlusHandHistories = []
    for path in filePaths:
        if ('Button Blind' in path):
            sixPlusHandHistories.append(path)

    hands = []
    for path in sixPlusHandHistories:
        with open(path, "r") as textFile:
            textFileStr = textFile.read()
            hands.extend(textFileStr.split('\n\n\n'))
            # remove the extra newline before EOF from pokerstars .txt format'
            try:
                hands.remove('\n')
            except Exception as e:
                print(e)
                print("getHands() error")

    return hands

# get btn player

def getBtnPlayer(hand):
    btnSeatMatchObject = re.search(r'Seat #\d is the button', hand)
    btnSeat = btnSeatMatchObject.group().split(' ')[1][1]

    for line in hand.split("\n"):
        if ('Seat ' + str(btnSeat) in line):
            return getSnFromSeatLine(line)
    return 


def checkOtb(screenName, hand):
    # TODO !!
    #preflop = getPreflopActions(hand)

    return False


def vpip(screenName, hand):

    # jos hero 'calls' tai 'raises' preflopis

    preflop = getPreflopActions(hand)

    if (screenName + ': raises' in preflop):
        return True
    if (screenName + ': calls' in preflop):
        return True
    return False


def getPreflopActionSize(line):
    if ('raises' in line):
        # gaig gibe liin: raises $7 to $8
        return float(line.split(": ")[1].split(" ")[3].strip("$"))
    if ('calls' in line):
        return float(line.split(": ")[1].split(" ")[1].strip("$"))



def getPreflopLine(screenName, hand):

    preflop = getPreflopActions(hand)
    bb = float(getBigBlind(hand))

    actions = ""
    raises = 0

    try:

        for line in preflop.split("\n")[2:]:
            if (screenName in line):
                if (raises == 0 and 'calls' in line):
                    actions += "L"
                if (raises > 0 and 'calls' in line):
                    callAmount = getPreflopActionSize(line)
                    actions += "C(" + str(callAmount) + ")"
                if ('raises' in line):
                    if (raises == 0):
                        size = getPreflopActionSize(line)
                        actions += "R1(" + str(size/bb) + ")"
                    if (raises == 1):
                        size = getPreflopActionSize(line)
                        actions += "3B(" + str(size/bb) + ")"
                    if (raises == 2):
                        size = getPreflopActionSize(line)
                        actions += "4B(" + str(size/bb) + ")"
                    if (raises == 3):
                        size = getPreflopActionSize(line)
                        actions += "5B(" + str(int(size/bb)) + ")"
            if ('raises' in line):
                raises += 1
    except Exception as e:
        print("getpreflopline error")
        print(e)

    return actions


def getTableName(hand):
    for line in hand.split("\n"):
        if (line[0:6] == 'Table '):
            return line.split("'")[1]

    return 'errortablename'


def printCmdHud(screenNames):

    print("--------------------------------")

    for sn in screenNames:
        if sn not in currentPlayers:
            print("*** NEW PLAYER JOINED *** ", sn)
            currentPlayers.append(sn)

    print("--")

    printLines = []
    for sn in currentPlayers:

        # get data
        db = getDb()
        cursor = db.players.find({'screenName': sn})

        # print data

        for playerData in cursor:

            name = '{0: <15}'.format(playerData['screenName'])
            hands = '{0: <4}'.format(playerData['nHands'])
            rfi = ''
            try:
                rfi = playerData['rfiTrue'] / \
                    (playerData['rfiTrue'] + playerData['rfiFalse'])
                rfi = '{0: <4}'.format(str(int(rfi*100)))
            except Exception as e:
                print("cmd hud rfi calc error")
                print(e)

            vpip = '{0: <4}'.format(
                str(int(playerData['vpipTrue'] / playerData['nHands'] * 100)))

            openLimp = ''
            try:
                openLimp = playerData['openLimpTrue'] / \
                    (playerData['openLimpTrue'] + playerData['openLimpFalse'])
                openLimp = '{0: <3}'.format(str(int(openLimp*100)))
            except Exception as e:
                print("cmd hud vpip calc error")
                print(e)

            limp = ''
            try:
                limp = playerData['limpTrue'] / \
                    (playerData['limpTrue'] + playerData['limpFalse'])
                limp = '{0: <4}'.format(str(int(limp*100)))
            except Exception as e:
                print(" cmd hud limp calc error")
                print(e)

            holeCardLines = ''
            try:
                holeCardLines = playerData['holeCardLines']
            except Exception as e:
                print("cmd hud holeCarcLines calc error")
                print(e)

            try:
                str1 = name + " Hands " + str(hands) + " Vpip " + vpip + " Rfi " + rfi + \
                    " Open-limp " + openLimp + " Limp " + \
                    limp + '{0: <1}'.format('Cards')

                for line in holeCardLines:
                    str1 += "  [" + line + "]"

                printLines.append(str1)
            except Exception as e:
                print("cmd hud lines error")
                print(e)

    for line in sorted(printLines, key=str.lower):
        print(line)

        # hudBox = hud(line)
        # hudBox.mainloop()

    # pop hud box

def getScreenNames(hand):
    regexp = re.findall(r'^Seat .+', hand, re.MULTILINE)
    l = int(len(regexp) / 2)
    del regexp[-l:]

    screenNames = []
    for item in regexp:
        # Seat 1: gaig gi beliin ($209.95 in chips)
        screenNames.append(item.split(
            ':')[1].split('($')[0].strip(" "))
    return screenNames


def getAllHandsFromDb(previousDb):

    #get all hands from previous dB
    cursor = previousDb.hands.find()
    hands = []
    for item in cursor:
        hands.append(item["data"])
    return hands



def importNewHands(testing = None, previousDb = None):

    newPlayers = []
    newTables = []

    # init client, db
    db = getDb()
    # init collections (equilavent to a table in relationals)
    dbHands = db.hands
    dbPlayers = db.players

    # get hand array from /trackerData
    hands = []
    if (testing == 'test'):
        hands = getAllHandsFromDb(previousDb)
    else:
        hands = getHands()
    

    # for each hand
    for hand in hands:

        # check if hand in DB (compare id)
        handId = hand.split(" ")[2].strip('#').strip(':')
        result = dbHands.find_one({'id': handId})
        if (result == None):
            # if the hand is new:

            # 1) update dbHands
            handData = {
                'id': handId,
                'data': hand
            }

            insertResult = dbHands.insert_one(handData)

            # print('Added: {0}'.format(
            #     insertResult.inserted_id) + " sleep() on!!")

            # 2) update dbPlayers

            # get player names
            screenNames = getScreenNames(hand)
            # upate current tables & screenNames
            newTable = {
                'name': getTableName(hand),
                'screenNames': screenNames
            }
            newPlayers.extend(screenNames)
            newTables.append(newTable)

            # for each player, update all stats

            for screenName in screenNames:
                # jos uus, init
                if (newPlayer(screenName)):
                    dbPlayers.insert_one({
                        'screenName': screenName,
                        'rfiTrue': 0,
                        'rfiFalse': 0,
                        'nHands': 0,
                        'vpipTrue': 0,
                        'limpTrue': 0,
                        'limpFalse': 0,
                        'openLimpTrue': 0,
                        'openLimpFalse': 0,
                        'holeCardLines': [],
                        #[btn, co, hj, lj, mp, ug]
                        'rfiTrueList': [0,0,0,0,0,0],
                        'rfiFalseList': [0,0,0,0,0,0],
                        'openLimpTrueList': [0,0,0,0,0,0],
                        'openLimpFalseList': [0,0,0,0,0,0],
                        'limpTrueList': [0,0,0,0,0,0],
                        'limpFalseList': [0,0,0,0,0,0],
                    })
                    print("new player initalized to db: ", screenName)

                # update rfi
                if (rfiPossible(screenName, hand)):
                    if rfi(screenName, hand):
                        dbIncrRfi(screenName)
                    else:
                        dbDecRfi(screenName)
                    

                # hands+1
                dbIncrHands(screenName)

                # vpip

                if not (checkOtb(screenName, hand)):
                    if (vpip(screenName, hand)):
                        dbIncrVpip(screenName)

                # limp%

                if limpPossible(screenName, hand):
                    if limp(screenName, hand):
                        dbIncrLimp(screenName)
                    else:
                        dbDecLimp(screenName)

                if openLimpPossible(screenName, hand):
                    if limp(screenName, hand):
                        dbIncrOpenLimp(screenName, hand)
                    else:
                        dbDecOpenLimp(screenName, hand)

                holeCards = getHoleCards(screenName, hand)
                if (holeCards):
                    '''
                    append sizings array, esim
                    'AdJKd: l 3b-100'
                    'JdJh: rfi-9'
                    'rfi-4'
                    'rfi-9 c'
                    '   AKs(): R1(3)    '
                    '''
                    preflopLine = getPreflopLine(screenName, hand)
                    pos = getPosition(hand, screenName, screenNames)
                    # data = holeCards + "(" + getPosition(hand, screenName, screenNames) + "): " + preflopLine

                    data = {
                        'preflopLine' : preflopLine,
                        'pos' : pos,
                        'holeCards' : holeCards

                    }   
                    dbAddHoleCardLines(screenName, data)
            # skiphero = []

            # for sn in screenNames:
            #     if ('gaiggibeliin' not in sn):
            #         skiphero.append(sn)
            # printCmdHud(skiphero)
    return newTables


if __name__ == '__main__':
    print("if __name__ ")

    # #uus db ohje: vaihda previousDb numero ja getDb() numero!
    # previousDb = getClient().sixPlusDb16
    # importNewHands('test', previousDb)

    hand = '''PokerStars Hand #195824029639:  6+ Hold'em No Limit (Button Blind $0.25 - Ante $0.25  USD) - 2019/01/16 18:35:56 EET [2019/01/16 11:35:56 ET]
Table 'Saiph f f ' 6-max Seat #3 is the button
Seat 1: barnoculars ($56.51 in chips) 
Seat 2: Pizzaschmied ($46.08 in chips) 
Seat 3: Juod asi s_23 ($54.54 in chips) 
Seat 4: Montana2707 ($59.32 in chips) 
Seat 5: Egption ($127.06 in chips) 
Seat 6: gaiggibeliin ($49 in chips) 
barnoculars: posts the ante $0.25
Pizzaschmied: posts the ante $0.25
Juodasis_23: posts the ante $0.25
Montana2707: posts the ante $0.25
Egption: posts the ante $0.25
gaiggibeliin: posts the ante $0.25
Juodasis_23: posts button blind $0.25
*** HOLE CARDS ***
Dealt to gaiggibeliin [Js Ks]
Montana2707: raises $0.50 to $0.75
Egption: calls $0.75
gaiggibeliin: calls $0.75
barnoculars: calls $0.75
Pizzaschmied: calls $0.75
Juodasis_23: raises $6.25 to $7
Montana2707: folds 
Egption: folds 
gaiggibeliin: folds 
barnoculars: raises $18.50 to $25.50
Pizzaschmied: folds 
Juodasis_23: raises $28.79 to $54.29 and is all-in
barnoculars: calls $28.79
*** FLOP *** [Qc 9h Kd]
*** TURN *** [Qc 9h Kd] [Ah]
*** RIVER *** [Qc 9h Kd Ah] [Jh]
*** SHOW DOWN ***
barnoculars: shows [Ad 8d] (a pair of Aces)
Juodasis_23: shows [Ac Kh] (two pair, Aces and Kings)
Juodasis_23 collected $111.08 from pot
*** SUMMARY ***
Total pot $113.08 | Rake $2 
Board [Qc 9h Kd Ah Jh]
Seat 1: barnoculars showed [Ad 8d] and lost with a pair of Aces
Seat 2: Pizzaschmied folded before Flop
Seat 3: Juodasis 23 (button blind) showed [Ac Kh] and won ($111.08) with two pair, Aces and Kings
Seat 4: Montana2707 folded before Flop
Seat 5: Egption folded before Flop
Seat 6: gaiggibeliin folded before Flop'''

    res = getBtnPlayer(hand)
    print(res)
    # for sn in getScreenNames(hand):
    #     res = getPosition(hand, sn, getScreenNames(hand))
    #     print(sn, res)

    # res1 = getSnFromSeatLine('Seat 3: Juod asi s_23 ($54.54 in chips)')
    # print(res1)