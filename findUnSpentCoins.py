from blockchain import blockexplorer, util
import json

block = blockexplorer.get_block(str(329000))

#print block.hash
#data = blockexplorer.get_inventory_data(txs[1].hash)

txs = block.transactions
#print txs[1].hash
#data = blockexplorer.get_inventory_data(txs[1].hash)
#print data.initial_ip

skip = True
for x in txs:
	if (skip):
		skip = False
	else:
		data = blockexplorer.get_inventory_data(x.hash)
		print data.initial_ip