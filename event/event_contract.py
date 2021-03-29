import json

import web3
import web3.eth
from web3 import Web3, HTTPProvider
from web3.contract import Contract



CONTRACT_ADDRESS = Web3.toChecksumAddress('4481FEE129F2D6B9DBD0BF40880B2662FD5EB077')#htdf1f74m3nqhgrxesjfhru49wjhyujjs9fv7v9u6w5
CREATOR_ADDRESS = Web3.toChecksumAddress('85CED8DDF399D75C9E381E01F3BDDCEFB9132FE9')#htdf1sh8d3h0nn8t4e83crcql80wua7u3xtlfj5dej3

ABI = '{"abi": [{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"founder","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"newFounder","type":"address"}],"name":"changeFounder","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"remaining","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"}]}'#, "checksum": "8cca4d0aff0db07a5578088c29efb7be1f7896bd"}'
ABI_JSON = json.loads(ABI)

def get_registry_contract(w3):
    return w3.eth.contract(
        address=CONTRACT_ADDRESS,
        abi=ABI_JSON['abi']
    )

import time

def handle_event(event):
    print(event)

def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        time.sleep(poll_interval)
        
w3 = Web3(HTTPProvider('http://localhost:1317'))

contract = get_registry_contract(w3)
transfer_filter = contract.events.Transfer.createFilter(fromBlock="0x0", argument_filters={'from': '0x85cED8Ddf399D75c9E381E01F3bddCeFb9132Fe9'})

event_signature_hash = w3.keccak(text="Transfer(address,address,uint256)").hex()
event_filter = w3.eth.filter({
  'fromBlock': 0,
  'toBlock': 'latest',
  'address': CONTRACT_ADDRESS,
  # 'topics':[event_signature_hash]
  })

log_loop(event_filter,2)    