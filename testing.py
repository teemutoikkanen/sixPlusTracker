from tracker import *
# from hud import *

# for hand in getHands():
#     print(getHoleCards('gaiggibeliin', hand))


#### TESTING #####

# with open('tempHand.txt', "r") as h:

#     hand = h.read()

def testPlayersDb():
    playerDb = getDb().players.find({})

    allPlayers = []
    for player in playerDb:
        print(player)
        allPlayers.append(player['screenName'])

    return allPlayers


def testHandsDb():
    cursor = getDb().hands.find({})

    player = 'gaiggibeliin'
    n = 0
    for item in cursor:
        n += 1
        hand = item['data']
        # print(hand)
        pos = getTableName(hand)
        print(pos)

        if (n >= 200):
            break


def getHandCount():
       cursor = getDb().hands.find({})
       print(len(cursor))

       print("hep")


       

if __name__ == '__main__':
    # testPlayersDb()
    res = testPlayersDb()
    print("res")