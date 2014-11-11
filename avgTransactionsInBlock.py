from blockchain import blockexplorer, util
import json



latest_block = blockexplorer.get_latest_block()

numberOfTXs = len(latest_block.tx_indexes)


#print numberOfTXs
numberOfInputs = 0
numberOfOutputs = 0
for x in range (0, numberOfTXs):
	txs = blockexplorer.get_tx(str(latest_block.tx_indexes[x]))
	numberOfInputs += len(txs.inputs)
	numberOfOutputs += len(txs.outputs)

print "avg outputs per transactions " + str (numberOfOutputs/numberOfTXs)
print "avg inputs per transactions " + str(numberOfInputs/numberOfTXs)
