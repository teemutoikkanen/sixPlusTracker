import re
import glob
from pymongo import MongoClient
from pprint import pprint




hero = 'gaiggibeliin'

# 1. idea: käydään läpi käsihistorioita ja luodaan niistä database

# - Hands
# 	*id 
# 	*data
# 	(*date, *players, yms...)

# - Players
# 	*n_hands
# 	*vpip
# 	*rfi
# 	*openLimp


# *** Suunnitelmaa (mongoDB) ***
# - vastaavasti kun resultissa käydään manuaalisesti HH:t läpi
# - jokaisen kohdalla tsekataan onko käsi jo DB:ssä
# - tsekataan onko pelaaja jo tietokannassa olemassa vai luodaanko uusi
# - aluksi vaikka yksi statsi: rfi: tän saa helposti napattua jo samalla kun regexpaa kättä 1. kerral (eka xx 'raises')
# - siis kolme vaihtoehtoa (?): 
# 			rfi mahdollista ja raise
# 			rfi mahdollista ja limp/fold
# 			joku reissaa ennen meitä
# - eli siis



#rfi mahdollista jos ei 'raises' ennen gaiggibeliin vuoroa
def rfiPossible(screenName,hand):



	actions = hand.split('*** HOLE CARDS ***')[1].split('*** SUMMARY ***')[0]
	actionsArray = actions.split('\n')[2:]	

	# print(actionsArray)


	for line in actionsArray:
		if (screenName in line):
			return True
		if ('raises' in line and screenName not in line):
			return False
		#todo: if everyone folds and btn wins the pot return False


		


	#split *** HOLE CARDS *** ja gaiggibeliin -- jos raises ennen meitä, return False

	return True
def getPreflopActions(hand):

	lineArray = hand.split("\n").split['*** HOLE CARDS ***'][1]

	print(lineArray)

	#jos *** flop *** -> perus parse

	#else 'Uncalled bet parse



def rfi(screenName, hand):
	# jos eka preflop raises on herolta, return True

	preflop = getPreflopActions(hand)



	return False

def dbAddRfi(screenName):
	# total_rfi = n_did_Rfi/(n_didNOT_Rfi+n_did_rfi)
	return True

def dbDecRfi(screenName):
	return True

def getHands():
	### parse hh files into an array of hand strings
	filePaths = glob.glob("trackerData/*.txt")
	hands = []
	for path in filePaths:
		with open(path, "r") as textFile:
			textFileStr = textFile.read()
			hands.extend(textFileStr.split('\n\n\n'))
			#remove the extra newline before EOF from pokerstars .txt format'
			try:
				hands.remove('\n')
			except:
				print("no newlines to remove")


	return hands

def main():

	#init client, db
	client = MongoClient()
	db = client.sixPlusDb
	#init collections (equilavent to a table in relationals)
	dbHands = db.hands
	dbPlayers = db.players

	#get hand array from /trackerData
	hands = getHands()

	#for each hand
	for hand in hands:

		#check if hand in DB (compare id)
		handId = hand.split(" ")[2].strip('#').strip(':')
		result = dbHands.find_one({'id' : handId})
		# if (result == None):
		if (True):
			#if the hand is new:

			# 1) update dbHands
			handData = {
			'id': handId,
			'data': hand
			} 

			# insertResult = dbHands.insert_one(handData)
			# print('Added: {0}'.format(insertResult.inserted_id))

			# 2) update dbPlayers

			# get player names
			regexp = re.findall(r'^Seat .+', hand,re.MULTILINE)
			l = int(len(regexp)/2)
			del regexp[-l:]

			screenNames = []
			for item in regexp:
				screenNames.append(item.split(" ")[2])

			print(handId)
			print("screenNames: ", screenNames)


			# for each player, update rfi stat
			for screenName in screenNames:
				print(rfiPossible(screenName, hand))
				if (rfiPossible(screenName, hand)):
					if rfi(screenName, hand):
						dbAddRfi(screenName)
					else:
						dbDecRfi(screenName)


















main()










# hand = "gaiggibeliin opens, everyone folds, gaiggibelin wins 1M$"
# handId =  "1298321955"


# client = MongoClient('localhost', 27017)
# db = client.pymongo_test

# dbHands = db.hands


# hand_data = {
# 	'id' : handId,
# 	'data' : hand
# }

# # result = dbHands.insert_one(hand_data)


# print(db.hands.find_one({}))

# print("end")

