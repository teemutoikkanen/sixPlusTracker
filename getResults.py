import re
import glob

hero = 'gaiggibeliin'


def getHandResult(hand):
	#get ante size
	ante = float(hand.split()[9].strip('$'))
	


	#init money put in the pot
	moneyPut = 0
	moneyPut += ante

	# get btn player
	btnSeatMatchObject = re.search(r'Seat #\d is the button', hand)
	btnSeat = btnSeatMatchObject.group().split(' ')[1][1]
	btnPlayerMatchObject = re.search(r'Seat ' + btnSeat + ': ([^\s]+)', hand)
	btnPlayer = btnPlayerMatchObject.group().split()[2]

	# ways to put money in the pot: 'ante', btn blind, 'calls', 'raises', 'bets'
	# ways to get money from the pot: Uncalled bet, **SUMMARY *** -> won ($x), SUMMARY -> collected
	# exceptions: button raises: no record of blind when raising (i.e. all btn raises are raise-1bb) !!!!!


	# calc money put into the pot AND got back from the pot
	rePutGetMoneys = re.findall(r'' + hero +': calls .+|'+ hero + ': raises .+|' + hero +': bets .+' + '|.+ returned to ' + hero + '|^gaiggibeliin coll.+', hand, re.MULTILINE)
	# print(rePutGetMoneys)


	for line in rePutGetMoneys:
		strArray = line.split(' ')
		if (strArray[1] == 'calls'):
			amount = strArray[2].strip('$')
			moneyPut += float(amount)
		if (strArray[1] == 'raises'):
			amount = strArray[4].strip('$')
			moneyPut += float(amount)
		if (strArray[1] == 'bets'):
			amount = strArray[2].strip('$')
			moneyPut += float(amount)
		if (strArray[0] == 'Uncalled'):
			amount = strArray[2].strip("(").strip(")").strip("$")
			moneyPut -= float(amount)
		if (strArray[1] == 'collected'):
			amount = strArray[2].strip('$')
			moneyPut -= float(amount)

	
	# if hero is on the button, add 1 to moneyPut
	if (btnPlayer == hero):
		moneyPut += ante
	# btnPlayer == hero AND hero raise preflop, reduce one ante from moneyPut
	preflopAction = hand.split('*** HOLE CARDS ***')[1].split('*** FLOP ***')[0]
	if (hero + ': raises' in preflopAction and btnPlayer == hero):
		moneyPut -= ante


	# print('Total money invested: ', moneyPut)

	return moneyPut



### parse hh files into an array of hand strings
filePaths = glob.glob("C:/Users/Teemu/AppData/Local/PokerStars.EU/HandHistorygaiggibeliin/*.txt")

#skip other games
sixPlusHandHistories = []
for path in filePaths:
	if ('Button Blind' in path):
		sixPlusHandHistories.append(path)
		
hands = []
for path in sixPlusHandHistories:
	with open(path, "r") as textFile:
		textFileStr = textFile.read()
		hands.extend(textFileStr.split('\n\n\n'))
		#remove the extra newline before EOF from pokerstars .txt format'
		try:
			hands.remove('\n')
		except:
			print("no newlines to remove")



result = 0
for hand in hands:
	result += getHandResult(hand)


result *= -1
print(result)
print('hh file count: ', len(filePaths))
print('hands: ', len(hands))
print('profit per 100 hands', result/(len(hands)/100))


# print("correct result: " + str(5855.7-5706.84))

































