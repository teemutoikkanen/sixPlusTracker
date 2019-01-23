import re
import glob

hero = 'gaiggibeliin'

### parse hh files into an array of hand strings
filePaths = glob.glob("data/*.txt")
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


print(len(hands))


### for each hand, sum hero $ results
# ways to put money in the pot: 'ante', btn blind, 'calls', 'raises', 'bets'
# ways to get money from the pot: Uncalled bet, **SUMMARY *** -> won ($x), SUMMARY -> collected
# exceptions: button raises: no record of blind when raising (i.e. all btn raises are raise-1bb) !!!!!


with open('tempHand.txt', 'r') as f:
	hand = f.read()

	#get ante size
	ante = hand.split()[9][1]
	print(ante)

	#init money put in the pot
	moneyPut = 0
	moneyPut += float(ante)

	# get btn player
	btnSeatMatchObject = re.search(r'Seat #\d is the button', hand)
	btnSeat = btnSeatMatchObject.group().split(' ')[1][1]
	btnPlayerMatchObject = re.search(r'Seat ' + btnSeat + ': ([^\s]+)', hand)
	btnPlayer = btnPlayerMatchObject.group().split()[2]

	#calc money put into the pot
	rePutMoney = re.findall(r'' + hero +': calls .+|'+ hero + ': raises .+|' + hero +': bets .+', hand)
	
	print(rePutMoney)

	for line in rePutMoney:
		strArray = line.split(' ')
		if (strArray[1] == 'calls'):
			amount = strArray[2].strip('$')
			moneyPut += float(amount)
			print(amount)
		if (strArray[1] == 'raises'):
			amount = strArray[4].strip('$')
			moneyPut += float(amount)
			print(amount)
		if (strArray[1] == 'bets'):
			amount = strArray[2].strip('$')
			moneyPut += float(amount)


	








	print('total put: ', moneyPut)


	#TODO exception: if hero btn & raise, -1 from moneyPut






























