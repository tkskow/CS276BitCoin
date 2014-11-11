from blockchain import blockexplorer, util
import json

lastBlock = blockexplorer.get_latest_block()

index = lastBlock.height
print index
block1 = blockexplorer.get_block(str(index - 1))



tx1 = block1.transactions

skip1 = True

for x in tx1:
	if skip1:
		skip1 = False
	else:
		outputs = x.outputs
		for z in outputs:
			print z.spent