from blockchain import blockexplorer, exceptions
from collections import OrderedDict
import requests, json, pymongo, datetime, time
 
LATEST_HASH_URL = "https://blockchain.info/q/latesthash"
LOCATION_SERVICE_URL = "http://www.geoplugin.net/json.gp?ip="

SORT_ORDER = ["geoplugin_request","geoplugin_city", "geoplugin_longitude", "geoplugin_latitude", "geoplugin_region", "geoplugin_regionName", "geoplugin_countryCode", "geoplugin_countryName", "geoplugin_continentCode", "geoplugin_regionCode", "geoplugin_areaCode", "geoplugin_dmaCode"]

RELAYED_BY_IPS = {}
INITIAL_IPS = {}

LATEST_BLOCK_HASH = ""
#INITIAL_IPS = {"107.170.219.42" : 17, "146.185.142.86" : 6, "192.241.230.87" : 28, "182.241.230.87" : 8, "147.145.32.14" : 1}

def traverse_block(block):

	skip = True
	for transaction in block.transactions:
		print "##### TRANSCATION: {0} #####".format(transaction.hash)
		if(skip):
			skip = False
		else:
			relayed_by = transaction.relayed_by

			if not relayed_by in RELAYED_BY_IPS:
				RELAYED_BY_IPS[relayed_by] = 1
			else:
				RELAYED_BY_IPS[relayed_by] += 1

			try:
				inv = blockexplorer.get_inventory_data(transaction.hash)
				initial_ip = inv.initial_ip

				if not initial_ip in INITIAL_IPS:
					INITIAL_IPS[initial_ip] = 1
				else:
					INITIAL_IPS[initial_ip] += 1

			except Exception, e:
				print e

def create_document(ip_address, ip_count):

	# query geolocation about location of ip address
	response = requests.get(LOCATION_SERVICE_URL + ip_address)
	document = response.json()

	# remove stupid stuff
	document.pop("geoplugin_currencyConverter")
	document.pop("geoplugin_currencySymbol")
	document.pop("geoplugin_currencySymbol_UTF8")
	document.pop("geoplugin_credit")
	document.pop("geoplugin_currencyCode")
	document.pop("geoplugin_status")

	orderedJson = OrderedDict()
	for item in sorted(document.iteritems(), key=lambda (k, v): SORT_ORDER.index(k)):
		orderedJson[item[0]] = item[1]
	
	# add count and timestamp
	orderedJson["count"] = str(ip_count)
	orderedJson["last_updated"] = str(datetime.datetime.utcnow())
	
	return orderedJson

def update_database():
	client = pymongo.MongoClient('localhost', 27017)
	connection = client['mynewdb']
	db_collection = connection.testdocuments

	for ip in sorted(INITIAL_IPS, key=INITIAL_IPS.get, reverse=True):
		ip_count = INITIAL_IPS[ip]

		document = create_document(ip, ip_count)

		existing_document = db_collection.find( { "geoplugin_request" : str(ip) } ).limit(1)	

		if(existing_document.count() > 0):
			# ip already in database. Let's update it.
			current_count = existing_document[0]['count']
			db_collection.update(
				{ "geoplugin_request" : str(ip)},
				{ "$set":
					{
						'count' : str(int(current_count) + int(ip_count)),
						'last_updated' : document['last_updated']
					}
				})
		else:
			# add ip to database with count
			db_collection.insert(document_formatted)

	client.close()

def wait_for_new_block():

	response = requests.get(LATEST_HASH_URL)
	latest_hash = response.text

	while(latest_hash == LATEST_BLOCK_HASH):
		# Sleep for how long?
		time.sleep(480) # 8 minutes?
		response = requests.get(LATEST_HASH_URL)
		latest_hash = response.text

	LATEST_BLOCK_HASH = latest_hash

def clean_up():
	INITIAL_IPS = {}
	RELAYED_BY_IPS = {}

def main():

	testrun = 0
	while(testrun > 10):
		wait_for_new_block()

		latest_block = blockexplorer.get_block(LATEST_BLOCK_HASH)

		traverse_block(latest_block)

		update_database()

		clean_up()

		testrun += 1


main()

