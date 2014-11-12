from blockchain import blockexplorer, exceptions
from collections import OrderedDict
import requests, json, pymongo
 
location_service_url = "http://www.geoplugin.net/json.gp?ip="
sort_order = ["geoplugin_request","geoplugin_city", "geoplugin_longitude", "geoplugin_latitude", "geoplugin_region", "geoplugin_regionName", "geoplugin_countryCode", "geoplugin_countryName", "geoplugin_continentCode", "geoplugin_regionCode", "geoplugin_areaCode", "geoplugin_dmaCode"]


dickRelay = {}
dickInitial ={}

def check_block(block):

	skip = True
	for transaction in block.transactions:
		print "##### TRANSCATION: {0} #####".format(transaction.hash)
		if(skip):
			skip = False
		else:
			relayed_by = transaction.relayed_by

			if not relayed_by in dickRelay:
				dickRelay[relayed_by] = 1
			else:
				dickRelay[relayed_by] += 1

			try:
				inv = blockexplorer.get_inventory_data(transaction.hash)
				initial_ip = inv.initial_ip

				if not initial_ip in dickInitial:
					dickInitial[initial_ip] = 1
				else:
					dickInitial[initial_ip] += 1

			except Exception, e:
				print e

def add_to_database():
	client = pymongo.MongoClient('localhost', 27017)

	connection = client['mynewdb']

	db = connection.delete.testdata

	for ip in sorted(dickInitial, key=dickInitial.get, reverse=True):

		response = requests.get(location_service_url + ip)
		data = response.json()
		db.insert(format_geotag(data))

	client.close()

def format_geotag(existing):

	existing.pop("geoplugin_currencyConverter")
	existing.pop("geoplugin_currencySymbol")
	existing.pop("geoplugin_currencySymbol_UTF8")
	existing.pop("geoplugin_credit")
	existing.pop("geoplugin_currencyCode")
	existing.pop("geoplugin_status")

	orderedJson = OrderedDict()

	for item in sorted(existing.iteritems(), key=lambda (k, v): sort_order.index(k)):
		orderedJson[item[0]] = item[1]
	
	return orderedJson



latest_block = blockexplorer.get_latest_block()

block = blockexplorer.get_block(str(latest_block.block_index))

check_block(block)

add_to_database()




