# -*- coding: utf-8 -*-
# written by junying, 2020-06-16
# developed for testing airdrop/batchsend/exchange/...
import hashlib
import coincurve
import base64
import requests
from tx import ecsign,accountinfo

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
            from create_contract import querytx
            print("%s 执行　合约 %s 金额: %d  的交易广播成功, txid:%s" % (fromaddr, toaddr , namount, txid))
            querytx(restapi,txid)            
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

# smart contract manual execution test
def execute(hrp,contractaddr,fromprivkey, data, namount=0, chainid='testchain',gasprice=100, gaswanted=15000000,restapi='127.0.0.1:1317'):
    import time
    start = time.time()
    from key import privkey2addr
    _,fromaddr = privkey2addr(fromprivkey,hrp=hrp)
    #------------------------------步骤1 : 获取地址信息拼装要签名的数据-----------------------------------
    print(restapi)
    rsp = accountinfo(fromaddr,restapi)
    print(rsp)
    naccnumber, nsequence = rsp["accountnumber"],rsp["sequence"]
    nbalance = rsp["balance"] * (10**8) - gaswanted*gasprice # transfer all balance if namount < 0
    if nbalance < 0: print('no balance'); return
    if naccnumber < 0 or nsequence < 0: return
    print('account_number : %d' % naccnumber)
    print('sequence: %d' % nsequence)
    #-------------------------- 步骤2: 签名 -----------------------------------------

    b64PubKey, b64Data = sign(hrp, fromprivkey, contractaddr, namount,nsequence, naccnumber,chainid,gasprice,gaswanted,data)
    broadcast(fromaddr,contractaddr,namount,gasprice,gaswanted,b64PubKey,b64Data,data,restapi)

# usage: python call_contract.py 
# block gas limit: 15,000,000
# tx gas limit: 75,00,000
# [batchsend]
# 
# [payabletest]
# contract: htdf1ktzygz7ms80977m678dywt45zk5kz2c8gr7dke
# transfer: 30a65824000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000003e8
# receive: a3e76c0f
# send: c4cbfd89
# call: 4279fdc8
# callex: 3f62cfef
# **********************************************************************
# **********************************************************************
# **********************************************************************
# [PAYABLE]
# the htdf token which is transfered to a contract address by payable function is used insides the contract.
# anyone call any functions of the contract to move the fund. but nothing more.
# you can transfer the fund to any account if the contract code has no restriction
# ,but the amount can't exceed the one that is transfered to the contract by payable function callings.
# htdf of msg.value to contract is used by anyone to be touched.
# [AIRDROP]
# anyone call drop function to move any accounts' token, which is approved in token contract, to any account.
# allowed[donater.address][airdrop.contract] = x allowed you to use airdrop.contract to touch donater' token as you wish.
# **********************************************************************
# **********************************************************************
# *************************************************************************
# [exchange]
# contract: htdf100had89f22avvncvwswjdqcy2z43mgxa33zk4y(0000000000000000000000007befd69ca952bac64f0c741d26830450ab1da0dd)
# token2htdf: 038ebf0c000000000000000000000000067f88bea92e3b6ac737ab75bee310df50e46d750000000000000000000000000000000000000000000000000000000000989680
# htdf2token: 52d07be9000000000000000000000000067f88bea92e3b6ac737ab75bee310df50e46d75
# [hrc20]
# founder: 4d853ee5
# contract: htdf1qelc304f9cak43eh4d6maccsmagwgmt4gugz45(000000000000000000000000067f88bea92e3b6ac737ab75bee310df50e46d75)
# approve.data:095ea7b30000000000000000000000007befd69ca952bac64f0c741d26830450ab1da0dd00000000000000000000000000000000000000000000021e19e0c9bab2400000
# transfer: a9059cbb00000000000000000000000006024f431d43244453661bd77bfcaa67f025210d00000000000000000000000000000000000000000000003635c9adc5dea00000
# balanceOf: 70a0823100000000000000000000000006024f431d43244453661bd77bfcaa67f025210d
#            70a0823100000000000000000000000085ced8ddf399d75c9e381e01f3bddcefb9132fe9 
# *************************************************************************
# [private keys]
# founder = c06d9c5b991122f7c51a2cb89fc8efbf3e47e746c980f5afdbf2ac45f88aaf3d # htdf1sh8d3h0nn8t4e83crcql80wua7u3xtlfj5dej3 # 00000000000000000000000085ced8ddf399d75c9e381e01f3bddcefb9132fe9
# user = dcc7debf1e3d432a7e1cf94d5340f68fd5d1019381e0074ed4fd6512c007b9d2 # htdf1qcpy7scagvjyg5mxr0thhl92vlcz2ggdvfkh2u # 00000000000000000000000006024f431d43244453661bd77bfcaa67f025210d
# [procedures]
# 1. approves to founder, user
# 2. transfer htdf,token to founder, user
# 3. 
localhost = '127.0.0.1'
testnet = '39.108.251.132'
port = '1317'
if __name__ == "__main__":
    fromprivkey = '82467e3de6c1499866eda81f493aa502f1a65bd6d7f7e669df63139e9fe37adb'#htdf1qcpy7scagvjyg5mxr0thhl92vlcz2ggdvfkh2u
    contractaddr='htdf1czghxg3ln8vv7dpk3rxvx2zns2asqd5lxp69ch'#'htdf1tdm4fyfc0z3ynl44kj8ykyjptx5h484r0q6gj7'
    restapi = '%s:%s'%(testnet,port)#'127.0.0.1:1317'
    chainid = 'testchain'
    gaswanted=750000
    data='bb3ded46'#receive:'a3e76c0f'
    namount=0#100000
    execute('htdf',contractaddr=contractaddr,fromprivkey=fromprivkey,namount=namount,data=data,gaswanted=gaswanted,restapi=restapi)
    