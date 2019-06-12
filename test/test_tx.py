# -*- coding: utf-8 -*-
# written by junying, 2019-06-10

import hashlib
import coincurve
import base64
import requests
import py.test

from tx import accountinfo,transfer

block_time = 30

def test_tx_htdf():
    hrp='htdf'
    fromprivkey = 'c9960987611a40cac259f2c989c43a79754df356415f164ad3080fdc10731e65'
    frompubkey = '02fa63a1fc6f38936562bac0649dde139b527d37788dd466d27259753fe5e555d0'
    fromaddr = 'htdf12sc78p9nr9s8qj06e2tqfqhlwlx0ncuq8l9gsh'
    toaddr = 'htdf18rudpyaewcku05c87xzgaw4rl8z3e5s6vefu4r'
    restapi = '47.98.194.7:1317'
    chainid = 'testchain'
    ngas,nfee = 200000, 20
    nAmount = 0.001234 * (10**8)    #以satoshi为单位,    1USDP  = 10^8 satoshi    1HTDF=10^8 satoshi
    from key import privkey2addr
    assert (frompubkey,fromaddr) == privkey2addr(fromprivkey,hrp)
    tic=accountinfo(fromaddr)
    transfer(hrp,fromprivkey, toaddr, nAmount, chainid, nfee, ngas,restapi)
    import time
    time.sleep(block_time)
    assert tic != accountinfo(fromaddr)
    
# def test_tx_usdp():
#     hrp='usdp'
#     fromprivkey = '6da0717e95540c78e7480b790354cf4f0b59ec6e010b04f4ebeb111fdf3ffca5'
#     frompubkey = '03f17ab909f37dd55504af581f396fbaa0cd29c2f982336b2a6ae6cffdeaba97ed'
#     fromaddr = 'usdp1cl77rzpxd9t7fn0c2eq66qhvv355ztwkxhpqyk'
#     toaddr = 'usdp1e8wudwgqz9c26qjy0km5g4dlmc3dptk4rztn8k'
#     restapi = '47.99.81.158:1317'
#     chainid = 'testchain'
#     ngas,nfee = 200000, 20
#     nAmount = 0.001234 * (10**8)    #以satoshi为单位,    1USDP  = 10^8 satoshi    1HTDF=10^8 satoshi
#     from key import privkey2addr
#     assert (frompubkey,fromaddr) == privkey2addr(fromprivkey,hrp)
#     tic=accountinfo(fromaddr)
#     transfer(hrp,fromprivkey, toaddr, nAmount, chainid, nfee, ngas,restapi)
#     import time
#     time.sleep(block_time)
#     assert tic != accountinfo(fromaddr)