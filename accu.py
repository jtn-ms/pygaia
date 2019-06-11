# -*- coding: utf-8 -*-
# written by junying, 2019-06-11

import os

def getitems(filepath):
    if not os.path.exists(filepath): return []
    items = []
    with open(filepath,'r') as file:
        for line in file: items.append(line.split())
    return items

from tx import transfer,accountinfo
from key import privkey2addr

def accumulate(toaddr = 'htdf18rudpyaewcku05c87xzgaw4rl8z3e5s6vefu4r',
               privkeyfile = 'htdf.privkey',
               restapi='47.98.194.7:1317', chainid='testchain',
               ndefault_gas=200000,ndefault_fee=20):
    for item in getitems(privkeyfile):
        hrp = item[0].lower()
        fromprivkey = item[2]
        try: frompubkey,fromaddr = privkey2addr(fromprivkey,hrp)
        except: continue
        if fromaddr != item[1] or hrp != fromaddr[:4]: continue
        balance, _, _ = accountinfo(fromaddr,restapi)
        namount = balance * (10**8) - ndefault_fee#以satoshi为单位,    1USDP  = 10^8 satoshi    1HTDF=10^8 satoshi
        if namount < 0: continue
        transfer(hrp,fromprivkey, toaddr, namount, chainid, ndefault_fee, ndefault_gas,restapi)


blk_time=20
def distr(fromprivkey='c9960987611a40cac259f2c989c43a79754df356415f164ad3080fdc10731e65',
          hrp='htdf',privkeyfile = 'htdf.privkey',
          restapi='47.98.194.7:1317', chainid='testchain',
          ndefault_gas=200000,ndefault_fee=20, nAmount = 0.001234 * (10**8)):
    for item in getitems(privkeyfile):
        toaddr=item[1]
        transfer(hrp,fromprivkey, toaddr, nAmount, chainid, ndefault_fee, ndefault_gas,restapi)
        import time
        time.sleep(blk_time)

def report(privkeyfile='htdf.privkey',restapi='47.98.194.7:1317'):
    balance = 0
    for item in getitems(privkeyfile):
        addr=item[1]
        nbalance, _, _ = accountinfo(addr,restapi)
        balance += nbalance if nbalance > 0 else 0
    print(balance)
    
if __name__ == "__main__":
    #getitems('db/htdf.privkey')
    distr('db/htdf.privkey')
    #report('db/htdf.privkey')