from pymongo import MongoClient


client = MongoClient()

db6 = client.sixPlusDb6
db9 = client.sixPlusDb9



cursor = db6.hands.find()


n = 0
for item in cursor:
	n += 1	
	# print(item['data'])

print(n)