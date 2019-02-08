from pymongo import MongoClient
client = MongoClient()
def getDb():
    return client.sixPlusDb17

def getClient():
    return client

def dbIncrRfi(screenName):
    # total_rfi = n_did_Rfi/(n_didNOT_Rfi+n_did_rfi)

    dbPlayers = getDb().players
    dbPlayers.update({'screenName': screenName},
                     {'$inc': {
                         'rfiTrue': 1
                     }})


def dbDecRfi(screenName):

    dbPlayers = getDb().players
    dbPlayers.update({'screenName': screenName},
                     {'$inc': {
                         'rfiFalse': 1
                     }})


def dbIncrHands(screenName):

    getDb().players.update({'screenName': screenName},
                           {'$inc': {
                               'nHands': 1
                           }})


def dbIncrVpip(screenName):

    getDb().players.update({'screenName': screenName},
                           {'$inc': {
                               'vpipTrue': 1
                           }})


def dbIncrLimp(screenName):

    getDb().players.update({'screenName': screenName},
                           {'$inc': {
                               'limpTrue': 1
                           }})


def dbDecLimp(screenName):

    getDb().players.update({'screenName': screenName},
                           {'$inc': {
                               'limpFalse': 1
                           }})


def dbIncrOpenLimp(screenName, hand):

    getDb().players.update({'screenName': screenName},
                           {'$inc': {
                               'openLimpTrue': 1
                           }})


def dbDecOpenLimp(screenName, hand):

    getDb().players.update({'screenName': screenName},
                           {'$inc': {
                               'openLimpFalse': 1
                           }})


def dbAddHoleCardLines(screenName, data):

    getDb().players.update({'screenName': screenName},
                           {'$push': {
                               'holeCardLines': data
                           }})

