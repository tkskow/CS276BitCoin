from blockchain import blockexplorer, exceptions
from collections import OrderedDict
import requests, json, pymongo, datetime, time, ssl, logging, os, urllib2
 
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

			handle_inventory_data(transaction)

def handle_inventory_data(transaction):
	max_tries = 10
	current = 0
	while(current < max_tries):
		try:
			inv = blockexplorer.get_inventory_data(transaction.hash)
			initial_ip = inv.initial_ip

			if not initial_ip in INITIAL_IPS:
				INITIAL_IPS[initial_ip] = 1
				return
			else:
				INITIAL_IPS[initial_ip] += 1
				return

		except ssl.SSLError, e:
			logger.debug("SSL - SSLError. Current try = {0}".format(current))
			pass

		except exceptions.APIException, e:

			if "no inventory data" in e:
				current = 10
			else:
				logger.debug("Blockchain - APIException. Current try = {0}".format(current))

		except requests.exceptions.ConnectionError, e:
			logger.debug("Requests - ConnectionError. Current try = {0}".format(current))
			pass

		except urllib2.URLError:
			logger.debug("Urllib2 - URLError. Current try = {0}".format(current))
			pass

		finally:
			current += 1

	logger.debug("Transaction {0} failed 10 times. Moving on.".format(transaction.hash))

def create_document(ip_address, ip_count):
	# query geoplugin about location of ip address
	response = requests.get(LOCATION_SERVICE_URL + ip_address)

	try:
		document = response.json()
	except ValueError, e:
		logger.debug("Response from GeoLogin: 403 None. Bitch got blacklisted.")
		return None

	# remove stupid stuff
	document.pop("geoplugin_currencyConverter")
	document.pop("geoplugin_currencySymbol")
	document.pop("geoplugin_currencySymbol_UTF8")
	document.pop("geoplugin_credit")
	document.pop("geoplugin_currencyCode")
	document.pop("geoplugin_status")

	ordered_document = OrderedDict()
	for item in sorted(document.iteritems(), key=lambda (k, v): SORT_ORDER.index(k)):
		ordered_document[item[0]] = item[1]
	
	# add count and timestamp
	ordered_document["count"] = str(ip_count)
	ordered_document["last_updated"] = str(datetime.datetime.utcnow())
	
	return ordered_document

def update_database():
	client = pymongo.MongoClient('localhost', 27017)
	logger.info("Database opened.")
	connection = client['mynewdb']
	db_collection = connection.testdocuments

	spam_counter = 1
	spam_warning = 115

	for ip in sorted(INITIAL_IPS, key=INITIAL_IPS.get, reverse=True):
		ip_count = INITIAL_IPS[ip]

		# ninjahack to avoid getting blacklisted by GeoPlugin
		if(spam_counter > spam_warning):
			time.sleep(60)
			spam_counter = 1
			logger.info("Sleeping for 60 seconds to prevent spamming GeoPlugin.")

		document = create_document(ip, ip_count)

		if document is None:
			logger.debug("Skipped {0}".format(ip))
			continue

		existing_document = db_collection.find( { "geoplugin_request" : str(ip) } ).limit(1)	

		if(existing_document.count() > 0):
			# ip already in database. Let's update it.
			current_count = existing_document[0]['count']
			db_collection.update(
				{ "geoplugin_request" : str(ip)},
				{ "$set":
					{
						'count' : str(int(current_count) + int(ip_count)),
						'last_updated' : str(datetime.datetime.utcnow())
					}
				})
		else:
			# add ip to database with count
			db_collection.insert(document)

		spam_counter += 1

	client.close()
	logger.info("Database closed.")

def wait_for_new_block():
	global LATEST_BLOCK_HASH

	response = requests.get(LATEST_HASH_URL)
	latest_hash = response.text

	while(latest_hash == LATEST_BLOCK_HASH):
		logger.info("No new hash... goes to sleep for 3 minutes ... ")
		# Sleep for how long?
		time.sleep(180) # 3 minutes?
		response = requests.get(LATEST_HASH_URL)
		latest_hash = response.text

	LATEST_BLOCK_HASH = latest_hash

def clean_up():
	INITIAL_IPS = {}
	RELAYED_BY_IPS = {}

def init_logging():
    # Set logging format

    logfile = "error{0}.log".format(str(datetime.datetime.utcnow()))
    normal_log_format='[%(asctime)s][%(levelname)s] %(message)s'
    
    try:
        os.unlink(logfile)
    except OSError:
        pass
    logging.basicConfig(level=logging.DEBUG,format=normal_log_format,filename=logfile)
    logger = logging.getLogger()
    fileh = logging.FileHandler(logfile)
    fileh.formatter = logging.Formatter(fmt=normal_log_format)
    #logger.addHandler(fileh)
    return logger

def main():

	testrun = 0

	while(testrun < 10):
		logger.info("... Starting new testrun ...")
		logger.info("... Looking for new hash ...")
		wait_for_new_block()
		logger.info("New hash found: {0}".format(LATEST_BLOCK_HASH))
		try:
			latest_block = blockexplorer.get_block(LATEST_BLOCK_HASH)
			traverse_block(latest_block)
			update_database()
			clean_up()
			logger.info("Run completed.")
		except ssl.SSLError, e:
			logger.debug("SSLError! {0}".format(e))
			logger.info("Run failed.")
		finally:
			testrun += 1

logger = init_logging()

main()


