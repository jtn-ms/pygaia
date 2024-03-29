# -*- coding: utf-8 -*-
# written by junying, 2019-06-10
import hashlib
import coincurve
import base64
import requests

def ecsign(rawhash, key):
    if coincurve and hasattr(coincurve, 'PrivateKey'):
        pk = coincurve.PrivateKey(key)
        signature = pk.sign_recoverable(rawhash, hasher=None)
        # v = safe_ord(signature[64]) + 27
        r = signature[0:32]
        s = signature[32:64]
        return r, s

def accountinfo(address,restapi='47.98.194.7:1317',debug=False):
    #获取地址的一些信息, 用于签名
    #此demo仅用于提供参考, 方便理解, 实际生产环境中
    #最核心的是 sequence,  在生产环境中, 如果进行大批量转账, 每笔交易要固定sequence, 而不要从节点获取!
    #固定sequence, 防止因为网络拥堵, 节点数据不同步,导致重复转账的问题
    balance, nAccountNumber,nSequence = -1,-1,-1
    try:
        rsp =  requests.get('http://%s/auth/accounts/%s' % (restapi.strip(), address.strip()))
        rspJson = rsp.json()
        balance = Decimal(rspJson['value']['coins'][0]['amount']) if rspJson['value']['coins'] else -2
        nAccountNumber = int(rspJson['value']['account_number'], 10)
        nSequence = int(rspJson['value']['sequence'], 10)
    except Exception as e:
        #如果from地址不存在, 会返回  204错误
        #if rsp.status_code == 204: print("from 地址, 不存在交易, 余额为0")
        #else: print (e)
        pass
    if debug and balance > 0: print('{0}\t\t{1}'.format(address,balance))
    return {
            "address":address,
            "balance":balance,
            "accountnumber":nAccountNumber,
            "sequence":nSequence
            }

def broadcast(fromaddr, toaddr, namount, gasprice, gaswanted, b64PubKey, b64Data, data="",restapi='47.98.194.7:1317'):
    
    strBroadcast = """{
        "type": "auth/StdTx",
        "value":{
            "msg": [{
                "type": "htdfservice/send",  
                "value":{
                    "From": "%s",
                    "To": "%s",
                    "Amount": [{
                        "denom": "satoshi",
                        "amount": "%d"
                    }],
                    "Data": "%s",
                    "GasPrice": "%d",
                    "GasWanted": "%d"
                }
            }],
            "fee": {
                "gas_wanted": "%d",
                "gas_price": "%d"
            },
            "signatures": [{
                "pub_key": {
                    "type": "tendermint/PubKeySecp256k1",
                    "value": "%s"
                },
                "signature": "%s"
            }],
            "memo": ""
        }
    }""" %(fromaddr, toaddr , namount, data, gasprice, gaswanted, gaswanted, gasprice, b64PubKey, b64Data)

    #去掉多余的空白字符
    strBroadcast = strBroadcast.replace(' ', '').replace('\t', '').replace('\n', '')
    bcastData = strBroadcast.encode('hex')
    print('\n--------------------------------------\n')
    print("广播的数据:"+ bcastData)
    print('\n--------------------------------------\n')

    # ---------------------------- 步骤3: 调用节点rpc接口,广播交易-----------------------------------

    #调用节点的rpc接口进行广播
    import json
    bcastData = {'tx' :  bcastData }   #rpc参数
    postData = json.dumps(bcastData)
    rsp = requests.post('http://%s/hs/broadcast'%restapi,  postData)


    #处理rpc接口
    try:
        if rsp.status_code == 200:
            rspJson = rsp.json()
            txid = str(rspJson['txhash'])
            print("%s 转给 %s 金额: %d  的交易广播成功, txid:%s" % (fromaddr, toaddr , namount, txid))
            
            from tools import write_log
            write_log("toAddr=%s|satoshiAmount=%d|txid=%s" % (toaddr, namount, txid))
        else:
            #注意, 如果报 Timed out waiting for tx to be included in a block  的错, 说明已经广播成功,只是为被打包
            if 'Timed' in rsp.text: print("已经广播成功, 但是为获取到txid, 此交易稍后会被节点"); return
            if 'already' in rsp.text: print("交易已经存在"); return
            print("广播失败: %s " % str(rsp.text)); return
    except Exception as e:
        print(e)
        return

def sign(hrp,fromprivkey, toaddr, namount,nsequence, naccnumber,chainid='testchain',gasprice=100,gaswanted=20000,data=""):
    from key import privkey2addr
    frompubkey,fromaddr = privkey2addr(fromprivkey,hrp)
    
    #使用字符拼装即可, 因为和字段的顺序有关, 不要使用json对象
    jUnTxStr = """{\
    "account_number": "%d",\
	"chain_id": "%s",\
	"fee": {\
        "gas_price": "%d",\
		"gas_wanted": "%d"\
	},\
    "memo": "",\
	"msgs": [{\
		"Amount": [{\
			"amount": "%d",\
            "denom": "satoshi"\
		}],\
        "Data": "%s",\
        "From": "%s",\
        "GasPrice": %s,\
        "GasWanted": %s,\
		"To": "%s"\
	}],\
    "sequence": "%d"\
    }"""  % (naccnumber, chainid, gasprice, gaswanted, namount, data, fromaddr,gasprice,gaswanted, toaddr , nsequence)

    print('\n--------------------------------------\n')
    #去掉多余的空格, 制表符, 换行符
    jUnTxStr = jUnTxStr.replace(' ', '').replace('\t', '').replace('\n', '')
    print(jUnTxStr)
    print('\n--------------------------------------\n')

    #被签名的数据
    print('\n--------------------------------------\n')
    print("json字符转为byteArray: ")
    for  i in bytearray(jUnTxStr):
        print('{0}({1}),'.format(i, chr(i))),
    print('\n--------------------------------------\n')

    #sha256
    print('\n-----------------------------------\n')
    shaData =  hashlib.sha256( bytearray(jUnTxStr) ).digest()
    print("Json的sha256结果:")
    print(shaData.encode('hex'))
    print('\n--------------------------------------\n')

    #获取私钥
    print('\n--------------------------------------\n')
    privkey = fromprivkey.decode('hex')
    print("strPrivKey: %s" % privkey.encode('hex'))
    print('\n--------------------------------------\n')

    #ECC签名
    print('\n--------------------------------------\n')
    r, s = ecsign(shaData,  privkey)  #只需要 r,s  不需要 v
    print('r:' + r.encode('hex'))
    print('s:' + s.encode('hex'))
    print('\n--------------------------------------\n')

    #拼装 r, s  , 并进行 base64编码     注意  ECC不需要
    print('\n--------------------------------------\n')
    b64data = base64.b64encode(r + s)
    print("base64编码后的签名信息: %s" % b64data)
    print('\n--------------------------------------\n')

    print('\n--------------------------------------\n')
    pubkey = frompubkey
    b64pubkey = base64.b64encode(pubkey.decode('hex'))
    print("base64编码后的公钥:" + b64pubkey)
    print('\n--------------------------------------\n')
    
    return b64pubkey, b64data

def transfer(hrp,fromprivkey, toaddr, namount, chainid='testchain',gasprice=100, gaswanted=20000,restapi='47.98.194.7:1317',data="",debug=False):
    import time
    start = time.time()
    from key import privkey2addr
    _,fromaddr = privkey2addr(fromprivkey,hrp=hrp)
    if debug: end = time.time();print('privkey2addr: %d'%int(end-start));start=end
    #------------------------------步骤1 : 获取地址信息拼装要签名的数据-----------------------------------
    print(restapi)
    rsp = accountinfo(fromaddr,restapi)
    print(rsp)
    naccnumber, nsequence = rsp["accountnumber"],rsp["sequence"]
    if namount < 0: namount = rsp["balance"] * (10**8) - gaswanted*gasprice # transfer all balance if namount < 0
    if namount < 0: print('no balance'); return
    if debug: end = time.time();print('accountinfo: %d'%int(end-start));start=end
    if naccnumber < 0 or nsequence < 0: return
    print('account_number : %d' % naccnumber)
    print('sequence: %d' % nsequence)
    #-------------------------- 步骤2: 签名 -----------------------------------------
    b64PubKey, b64Data = sign(hrp, fromprivkey, toaddr, namount,nsequence, naccnumber,chainid,gasprice,gaswanted,data)
    if debug: end = time.time();print('sign: %d'%int(end-start));start=end
    #-------------------------- 步骤3: 拼装广播数据 -----------------------------------------
    broadcast(fromaddr,toaddr,namount,gasprice,gaswanted,b64PubKey,b64Data,data,restapi)
    if debug: end = time.time();print('broadcast: %d'%int(end-start));start=end

def transferEx(hrp,fromprivkey, toaddr, namount, naccnumber, nsequence, chainid='testchain',gasprice=100, gaswanted=30000,restapi='47.98.194.7:1317',data="",debug=False):
    import time
    start = time.time()
    from key import privkey2addr
    _,fromaddr = privkey2addr(fromprivkey,hrp=hrp)
    #-------------------------- 步骤2: 签名 -----------------------------------------
    b64PubKey, b64Data = sign(hrp, fromprivkey, toaddr, namount,nsequence, naccnumber,chainid,gasprice,gaswanted,data)
    if debug: end = time.time();print('sign: %d'%int(end-start));start=end
    #-------------------------- 步骤3: 拼装广播数据 -----------------------------------------
    broadcast(fromaddr,toaddr,namount,gasprice,gaswanted,b64PubKey,b64Data,data,restapi)
    if debug: end = time.time();print('broadcast: %d'%int(end-start));start=end

from accu import getitems
from decimal import Decimal

def transferMulti(hrp,fromprivkey, txlistfile, chainid='testchain',gasprice=100, gaswanted=20000,restapi='test02.orientwalt.cn:1317',data="",debug=False):
    import time
    start = time.time()
    from key import privkey2addr
    _,fromaddr = privkey2addr(fromprivkey,hrp=hrp)
    if debug: end = time.time();print('privkey2addr: %d'%int(end-start));start=end
    print restapi
    rsp = accountinfo(fromaddr,restapi)
    print rsp
    naccnumber, nsequence, nbalance = rsp["accountnumber"], rsp["sequence"], Decimal(rsp["balance"]) * (10**8)
    print('account_number : %d' % naccnumber)
    for item in getitems(txlistfile):
        #------------------------------步骤1 : 获取地址信息拼装要签名的数据-----------------------------------
        toaddr, namount = item[0], Decimal(item[1])* (10**8)
        if naccnumber < 0 or nsequence < 0 or nbalance < namount: return
        print('sequence: %d' % nsequence)
        #-------------------------- 步骤2: 签名 -----------------------------------------
        b64PubKey, b64Data = sign(hrp, fromprivkey, toaddr, namount,nsequence, naccnumber,chainid,gasprice,gaswanted,data)
        if debug: end = time.time();print('sign: %d'%int(end-start));start=end
        #-------------------------- 步骤3: 拼装广播数据 -----------------------------------------
        broadcast(fromaddr,toaddr,namount,gasprice,gaswanted,b64PubKey,b64Data,data,restapi)
        if debug: end = time.time();print('broadcast: %d'%int(end-start));start=end
        nsequence+=1
        nbalance-=namount

def chkaccMulti(acclstfile,restapi):
    accumulated = 0
    for item in getitems(acclstfile):
        rsp = accountinfo(item[0],restapi)
        naccnumber, nsequence, nbalance = rsp["accountnumber"], rsp["sequence"], rsp["balance"]
        print '%s     %s'%(item[0],rsp["balance"])
        accumulated+=Decimal(nbalance)
    print accumulated
    
def compareBalances(balancebefore='./db/txs/balance.before',balanceafter='./db/txs/balance.after',txlist='./db/txs/tx.list',restapi='39.108.251.132:1317'):
    befores=getitems(balancebefore)
    afters=getitems(balanceafter)
    transations=getitems(txlist)
    for index,item in enumerate(transations):
        beforeaccount, beforebalance=befores[index][0], Decimal(befores[index][1])
        afteraccount, afterbalance=afters[index][0], Decimal(afters[index][1])
        toaddress, amount=transations[index][0], Decimal(transations[index][1])
        if amount !=(afterbalance-beforebalance): print '%s:%s,%s:%s,%s'%(beforeaccount,afteraccount,beforebalance,afterbalance,amount)
# 0x06fdde03 name()
# 0x095ea7b3 approve(address,uint256)
# 0x18160ddd totalSupply()
# 0x23b872dd transferFrom(address,address,uint256)
# 0x313ce567 decimals()
# 0x4d853ee5 founder()
# 0x70a08231 balanceOf(address)
# 0x93c32e06 changeFounder(address)
# 0x95d89b41 symbol()
# 0xa9059cbb transfer(address,uint256)
# 0xdd62ed3e allowance(address,address)
# BWC: htdf12dvguqedrvgfrdl35hcgfmz4fz6rm6chrvf96g
# CVS: htdf1ks6vgnp25r2eaa9k70dmsp448wmrma8mnucrsz

def queryGetBalance(bechaddr):
    hexfunc="70a08231"
    from key import bech2hex
    hexaddr=bech2hex(bechaddr)
    return hexfunc +\
          '0'*(64-len(hexaddr))+hexaddr

def completeData(bechaddr,amount):
    from ethereum.abi import method_id
    #code=hex(method_id('transfer',['address','uint256']))
    hexfunc="a9059cbb"#code[:2]+'0'*(10-len(code))+code[2:]
    from key import bech2hex
    hexaddr=bech2hex(bechaddr)
    hexint=hex(int(amount))[2:]
    hexint= hexint.strip('L')
    return hexfunc +\
          '0'*(64-len(hexaddr))+hexaddr+\
          '0'*(64-len(hexint))+hexint

def transfer_hrc20(hrp,contractaddr,fromprivkey, toaddr, namount, chainid='testchain',gasprice=100, gaswanted=500000,restapi='47.98.194.7:1317'):
    import time
    start = time.time()
    from key import privkey2addr
    _,fromaddr = privkey2addr(fromprivkey,hrp=hrp)
    #------------------------------步骤1 : 获取地址信息拼装要签名的数据-----------------------------------
    print restapi
    rsp = accountinfo(fromaddr,restapi)
    print rsp
    naccnumber, nsequence = rsp["accountnumber"],rsp["sequence"]
    nbalance = rsp["balance"] * (10**8) - gaswanted*gasprice # transfer all balance if namount < 0
    if nbalance < 0: print('no balance'); return
    if naccnumber < 0 or nsequence < 0: return
    print('account_number : %d' % naccnumber)
    print('sequence: %d' % nsequence)
    #-------------------------- 步骤2: 签名 -----------------------------------------
    data=completeData(toaddr,namount)
    b64PubKey, b64Data = sign(hrp, fromprivkey, contractaddr, 0,nsequence, naccnumber,chainid,gasprice,gaswanted,data)
    broadcast(fromaddr,contractaddr,0,gasprice,gaswanted,b64PubKey,b64Data,data,restapi)

def transferEx_hrc20(hrp,contractaddr,fromprivkey, toaddr, namount, naccnumber, nsequence, chainid='testchain',gasprice=100, gaswanted=500000,restapi='47.98.194.7:1317',debug=False):
    import time
    start = time.time()
    from key import privkey2addr
    _,fromaddr = privkey2addr(fromprivkey,hrp=hrp)
    data=completeData(toaddr,namount)
    b64PubKey, b64Data = sign(hrp, fromprivkey, contractaddr, 0,nsequence, naccnumber,chainid,gasprice,gaswanted,data)
    broadcast(fromaddr,contractaddr,0,gasprice,gaswanted,b64PubKey,b64Data,data,restapi)
    
# junying-todo, 2019-12-15
# multiple transactions from one account into one block
def test_transfer(hrp,fromprivkey, toaddr, namount, chainid='testchain',gasprice=100, gaswanted=20000,restapi='47.98.194.7:1317',debug=False):
    import time
    start = time.time()
    from key import privkey2addr
    _,fromaddr = privkey2addr(fromprivkey,hrp=hrp)
    if debug: end = time.time();print('privkey2addr: %d'%int(end-start));start=end
    #------------------------------步骤1 : 获取地址信息拼装要签名的数据-----------------------------------
    print restapi
    rsp = accountinfo(fromaddr,restapi)
    print rsp
    naccnumber, nsequence = rsp["accountnumber"],rsp["sequence"]
    if namount < 0: namount = rsp["balance"] * (10**8) - gaswanted*gasprice # transfer all balance if namount < 0
    if namount < 0: print('no balance'); return
    if debug: end = time.time();print('accountinfo: %d'%int(end-start));start=end
    if naccnumber < 0 or nsequence < 0: return
    print('account_number : %d' % naccnumber)
    for i in range(2):
        nseq = nsequence + i
        print('sequence: %d' % nseq)
        #-------------------------- 步骤2: 签名 -----------------------------------------
        b64PubKey, b64Data = sign(hrp, fromprivkey, toaddr, namount,nseq, naccnumber,chainid,gasprice,gaswanted)
        if debug: end = time.time();print('sign: %d'%int(end-start));start=end
        #-------------------------- 步骤3: 拼装广播数据 -----------------------------------------
        broadcast(fromaddr,toaddr,namount,gasprice,gaswanted,b64PubKey,b64Data,restapi)
        if debug: end = time.time();print('broadcast: %d'%int(end-start));start=end

if __name__ == "__main__":
    fromprivkey = 'c9960987611a40cac259f2c989c43a79754df356415f164ad3080fdc10731e65'
    frompubkey = '02fa63a1fc6f38936562bac0649dde139b527d37788dd466d27259753fe5e555d0'
    fromaddr = 'htdf12sc78p9nr9s8qj06e2tqfqhlwlx0ncuq8l9gsh'
    toaddr = 'htdf18rudpyaewcku05c87xzgaw4rl8z3e5s6vefu4r'
    restapi = '47.98.194.7:1317'
    chainid = 'testchain'
    gaswanted,gasprice = 200000, 100
    nAmount = 0.001234 * (10**8)    #以satoshi为单位,    1USDP  = 10^8 satoshi    1HTDF=10^8 satoshi
    from key import privkey2addr
    print accountinfo(fromaddr)
    print privkey2addr(fromprivkey,hrp='htdf')
    transfer('htdf',fromprivkey, toaddr, nAmount,chainid, gasprice, gaswanted,restapi)
    