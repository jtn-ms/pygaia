
from tx import transfer,accountinfo
from key import privkey2addr
from accu import getitems

# one to all
blk_time=10
def distr(fromprivkey='c9960987611a40cac259f2c989c43a79754df356415f164ad3080fdc10731e65',
          hrp='htdf',privkeyfile = 'htdf.privkey',
          restapi='47.98.194.7:1317', chainid='testchain',
          ndefault_gas=200000,ndefault_fee=20, nAmount = 0.001234 * (10**8)):
    for item in getitems(privkeyfile):
        toaddr=item[1]
        transfer(hrp,fromprivkey, toaddr, nAmount, chainid, ndefault_fee, ndefault_gas,restapi)
        import time
        time.sleep(blk_time)

def count(privkeyfile='htdf.privkey',restapi='47.98.194.7:1317',debug=False):
    nonzeros,zeros = [],[]
    for item in getitems(privkeyfile):
        addr,privkey=item[1],item[2]
        try: balance = accountinfo(addr,restapi)["balance"]
        except: continue
        nonzeros.append([addr,balance,privkey]) if balance > 0 else zeros.append(addr)
    if debug: print(len(nonzeros),len(zeros))
    return nonzeros,zeros

# nonzeros to zeros
from multiprocessing import Process
def distrex(hrp='htdf',privkeyfile='htdf.privkey',
            restapi='47.98.194.7:1317', chainid='testchain',
            ndefault_gas=200000,ndefault_fee=20):
    nonzeros,zeros = count(privkeyfile,restapi)
    num = 0
    while len(zeros)>0 and num < 10:
        for index,nonzero in enumerate(nonzeros):
            fromaddr,balance,fromprivkey = nonzero
            namount = balance * (10**8) - ndefault_fee
            if namount <= 0: continue
            if index >= len(zeros): break
            toaddr=zeros[index]
            try: Process(target=transfer,args=(hrp,fromprivkey, toaddr, int(namount/2), chainid, ndefault_fee, ndefault_gas,restapi)).start()
            except: continue
        nonzeros,zeros = count(privkeyfile,restapi)
        num += 1

# db to db
def distrp2p(hrp='htdf',fromdb='db/100/htdf.privkey',todb='db/10000/htdf.privkey',
            restapi='47.98.194.7:1317', chainid='testchain',
            ndefault_gas=200000,ndefault_fee=20):
    nonzeros,_ = count(fromdb,restapi)
    _,zeros = count(todb,restapi)
    num = 0
    while len(zeros)>0 and num < 10:
        for index,nonzero in enumerate(nonzeros):
            fromaddr,balance,fromprivkey = nonzero
            namount = balance * (10**8) - ndefault_fee
            if namount <= 0: continue
            if index >= len(zeros): break
            toaddr=zeros[index]
            try: Process(target=transfer,args=(hrp,fromprivkey, toaddr, int(namount/2), chainid, ndefault_fee, ndefault_gas,restapi)).start()
            except: continue
        _,zeros = count(todb,restapi)
        num += 1

if __name__ == "__main__":
    distrp2p(restapi='120.79.130.139:1317')