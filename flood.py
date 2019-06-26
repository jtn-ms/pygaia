
from tx import transfer
from key import privkey2addr
from accu import getitems

# first-half to second-half
# second-half to first-half
from multiprocessing import Process
def flood(hrp='htdf',privkeyfile='htdf.privkey',
          restapi='47.98.194.7:1317', chainid='testchain',
          ndefault_gas=200000,ndefault_fee=20,namount=1000):
    accs = getitems(privkeyfile)
    for time in range(2):
        senders   = accs[:len(accs)/2] if not time else accs[len(accs)/2:]
        receivers = accs[len(accs)/2:] if not time else accs[:len(accs)/2]
        for index,sender in enumerate(senders):
            hrp,fromaddr,fromprivkey = sender
            toaddr=receivers[index][1]
            try: Process(target=transfer,args=(hrp,fromprivkey, toaddr, namount, chainid, ndefault_fee, ndefault_gas,restapi)).start()
            except: continue

if __name__ == "__main__":
    flood('db/10000/htdf.privkey')