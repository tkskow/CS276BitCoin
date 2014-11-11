from blockchain import blockexplorer, exceptions
import requests, json, pymongo
 

location_service_url = "http://www.geoplugin.net/json.gp?ip="

dickRelay = {}
dickInitial ={}


def checkBlock(block):

	skip = True
	for transaction in block.transactions:
		print "##### TRANSCATION: {0} #####".format(transaction.hash)
		if(skip):
			skip = False
		else:
			relayed_by = transaction.relayed_by
			print "### RELAYED BY: ",relayed_by

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


				#print "Relayed by: {0} Initial ip: {1}".format(relayed_by, inv.initial_ip)
				#print "Relay information: init_time: {0} relayed_count: {1} relayed_percent: {2}".format(inv.initial_time, inv.relayed_count, inv.relayed_percent)
				
			except Exception, e:
				print e


def get_location_json():

	for ip in dickRelay:
		print "Relayed_by: {0} Count: {1}".format(ip, dickRelay[ip])


	for ip in sorted(dickInitial, key=dickInitial.get, reverse=True):
		print "Initial_ip: {0} Count: {1}".format(ip, dickInitial[ip])

		response = requests.get(location_service_url + ip)
		data = response.json()

		print data


def database():
	client = pymongo.MongoClient()




#latest_block = blockexplorer.get_latest_block()

#block = blockexplorer.get_block(str(latest_block.block_index))

#checkBlock(block)



database()




