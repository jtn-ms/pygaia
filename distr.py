
from tx import transfer,accountinfo
from key import privkey2addr
from accu import getitems

blk_time=30
def distr(fromprivkey='c9960987611a40cac259f2c989c43a79754df356415f164ad3080fdc10731e65',
          hrp='htdf',privkeyfile = 'htdf.privkey',
          restapi='47.98.194.7:1317', chainid='testchain',
          ndefault_gas=200000,ndefault_fee=20, nAmount = 0.001234 * (10**8)):
    for item in getitems(privkeyfile):
        toaddr=item[1]
        transfer(hrp,fromprivkey, toaddr, nAmount, chainid, ndefault_fee, ndefault_gas,restapi)
        import time
        time.sleep(blk_time)
        
if __name__ == "__main__":
    distr('db/distr/htdf.privkey')