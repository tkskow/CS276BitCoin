from blockchain import blockexplorer, util
import json

lastBlock = blockexplorer.get_latest_block()

index = lastBlock.height

block1 = blockexplorer.get_block(str(index))



tx1 = block1.transactions


ipaddressesInput = []
ipaddressesOutput = []
communicationBetweenTwoNodes = {}

f = open("test.txt", 'w')

for i in range(index, 329620, -1):
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
								if not x.relayed_by + " " + y.relayed_by in communicationBetweenTwoNodes:
									communicationBetweenTwoNodes [x.relayed_by + " " + y.relayed_by] = 1
								else:
									communicationBetweenTwoNodes[x.relayed_by +" " + y.relayed_by] += 1
								ipaddressesInput.append(x.relayed_by)
								ipaddressesOutput.append(y.relayed_by)
								
								#print "input address: {0}\n Output address: {1}\n".format(z.address, b.address)

#for x in xrange(0,len(ipaddressesOutput)):
#	print "IP address input: {0}\n IP address output: {1}".format(ipaddressesInput[x],ipaddressesOutput[x])
for i in communicationBetweenTwoNodes:
	f.write(i + " " + str(communicationBetweenTwoNodes[i]) + "\n")
	print "IPaddresses: {0} Count: {1}".format(i, communicationBetweenTwoNodes[i])

f.close()