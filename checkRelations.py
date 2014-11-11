from blockchain import blockexplorer, util
import json

lastBlock = blockexplorer.get_latest_block()

index = lastBlock.height

block1 = blockexplorer.get_block(str(index))



tx1 = block1.transactions


ipaddressesInput = []
ipaddressesOutput = []

for i in range(index, 329580, -1):
	block2 = blockexplorer.get_block(str(i))
	tx2 = block2.transactions
	skip1 = True
	skip2 = True
	print i
	for x in tx1:
		if skip1:
			skip1 = False
		else:
			inputs = x.inputs
			for y in tx2:
				if skip2:
					skip2 = False
				else:
					outputs = y.outputs
					for z in inputs:
						for b in outputs:
							if z.address == b.address:
								try:
									ipaddressesInput.append(x.relayed_by)
									ipaddressesOutput.append(y.relayed_by)
								except Exception, e:
									print e

								#print "input address: {0}\n Output address: {1}\n".format(z.address, b.address)

for x in xrange(0,len(ipaddressesOutput)):
	print "IP address input: {0}\n IP address output: {1}".format(ipaddressesInput[x],ipaddressesOutput[x])