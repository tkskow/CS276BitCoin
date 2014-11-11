from blockchain import blockexplorer, util
import json

lastBlock = blockexplorer.get_latest_block()

block = blockexplorer.get_block(str(lastBlock.block_index))


blockHash = block.hash
print blockexplorer.get_inventory_data(blockHash).initial_ip


tx = block.transactions[2]

#for x in tx.inputs:
invData = blockexplorer.get_inventory_data(tx.hash)
print invData.initial_ip


