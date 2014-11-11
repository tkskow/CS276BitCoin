from blockchain import blockexplorer, util
import json

latest_block = blockexplorer.get_latest_block()
#print latest_block
#print latest_block.time
#print latest_block.tx_indexes
#print latest_block.block_index
block = blockexplorer.get_block(str(latest_block.block_index))
#print block.relayed_by

tx = blockexplorer.get_tx(str(latest_block.tx_indexes[2]))
#print tx
#print tx.relayed_by
#data = blockexplorer.get_inventory_data(tx.hash)
#print data.initial_ip

inn = tx.inputs
#print inn
#print inn[0].address
#print inn[0].n
#address = blockexplorer.get_address(inn[0].address)
#print address
#print address.final_balance

#out = tx.outputs
#print out
#print out[0]
#print out[0].address

#outAddress = blockexplorer.get_address(out[0].address)
#print outAddress
#print outAddress.final_balance


#print address
#blocks = blockexplorer.get_blocks()
#print blocks