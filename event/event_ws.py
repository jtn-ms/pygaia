# ref
# https://web3py.readthedocs.io/en/stable/filters.html?highlight=event#event-log-filters
import json

import web3
import web3.eth
from web3 import Web3, WebsocketProvider
from web3.contract import Contract



CONTRACT_ADDRESS = Web3.toChecksumAddress('4481FEE129F2D6B9DBD0BF40880B2662FD5EB077')#htdf1gjqlacff7tttnk7shaqgszexvt74avrh507knj
CREATOR_ADDRESS = Web3.toChecksumAddress('85CED8DDF399D75C9E381E01F3BDDCEFB9132FE9')#htdf1sh8d3h0nn8t4e83crcql80wua7u3xtlfj5dej3
print(CONTRACT_ADDRESS)
print(CREATOR_ADDRESS)
ABI = '{"abi": [{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"founder","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"newFounder","type":"address"}],"name":"changeFounder","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"remaining","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"}]}'#, "checksum": "8cca4d0aff0db07a5578088c29efb7be1f7896bd"}'
ABI_JSON = json.loads(ABI)


def get_registry_contract(w3):
    return w3.eth.contract(
        address=CONTRACT_ADDRESS,
        abi=ABI_JSON['abi']
    )

# from web3.auto import w3
import time

def handle_event(event):
    print(event)

def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        time.sleep(poll_interval)

    
w3 = Web3(WebsocketProvider('ws://localhost:8546'))
# w3 = Web3(WebsocketProvider('ws://localhost:26657/websocket'))

def main_t():

    contract = get_registry_contract(w3)
    transfer_filter = contract.events.Transfer.createFilter(fromBlock="0x0", argument_filters={'from': '0x85cED8Ddf399D75c9E381E01F3bddCeFb9132Fe9'})
    transfer_filter.get_new_entries()

# passed
def test_block_filter():
    block_filter = w3.eth.filter('latest')
    log_loop(block_filter, 2)

def test_contract_event():
    contract = get_registry_contract(w3)
    transfer_filter = contract.events.Transfer.createFilter(fromBlock="0x0", argument_filters={'from': '0x85cED8Ddf399D75c9E381E01F3bddCeFb9132Fe9'})
    transfer_filter.get_new_entries()

    event_signature_hash = w3.keccak(text="Transfer(address,address,uint256)").hex()
    event_filter = w3.eth.filter({
    'fromBlock': 0,
    'toBlock': 'latest',
    'address': CONTRACT_ADDRESS,
    # 'topics':[event_signature_hash]
    })

    log_loop(event_filter,2)    

# https://web3py.readthedocs.io/en/stable/contracts.html#web3.contract.Contract.on
def test_transfer_filter():
    contract = get_registry_contract(w3)
    transfer_filter = contract.events.Transfer.createFilter(fromBlock="0x0", argument_filters={'from': '0x85cED8Ddf399D75c9E381E01F3bddCeFb9132Fe9'})
    log_loop(transfer_filter,1)  

def main():
    tx_filter = w3.eth.filter({
    'fromBlock': 0,
    'toBlock': 'latest',
    'address': CREATOR_ADDRESS,
    # 'topics':[event_signature_hash]
    })
    log_loop(tx_filter, 2)

if __name__ == '__main__':
    test_contract_event()
    # print(w3.eth.hashrate,w3.eth.gasPrice)
    # block = w3.eth.get_block('latest')
    # print(w3.eth.get_block(1))