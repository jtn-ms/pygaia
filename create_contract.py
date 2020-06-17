# -*- coding: utf-8 -*-
# written by junying, 2020-06-16
# developed for creating contract
import hashlib
import coincurve
import base64
import requests
from tx import ecsign,accountinfo

def broadcast(fromaddr, namount, gasprice, gaswanted, b64PubKey, b64Data, data="",restapi='47.98.194.7:1317'):
    
    strBroadcast = """{
        "type": "auth/StdTx",
        "value":{
            "msg": [{
                "type": "htdfservice/send",  
                "value":{
                    "From": "%s",
                    "To": "",
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
    }""" %(fromaddr, namount, data, gasprice, gaswanted, gaswanted, gasprice, b64PubKey, b64Data)

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
            print("%s 创建合约  的交易广播成功, txid:%s" % (fromaddr, txid))
            querytx(restapi,txid)
        else:
            #注意, 如果报 Timed out waiting for tx to be included in a block  的错, 说明已经广播成功,只是为被打包
            if 'Timed' in rsp.text: print("已经广播成功, 但是为获取到txid, 此交易稍后会被节点"); return
            if 'already' in rsp.text: print("交易已经存在"); return
            print("广播失败: %s " % str(rsp.text)); return
    except Exception as e:
        print(e)
        return

def querytx(restapi,txid):
    import time
    time.sleep(6)
    #调用节点的rpc接口进行广播
    import json
    rsp = requests.get('http://%s/txs/%s'%(restapi,  txid))
    try:
        if rsp.status_code == 200:
            rspJson = rsp.json()
            contract_addr = str(rspJson['logs'])
            print("contract_addr:%s successfully created" % contract_addr)
            
        else:
            #注意, 如果报 Timed out waiting for tx to be included in a block  的错, 说明已经广播成功,只是为被打包
            if 'Timed' in rsp.text: print("已经广播成功, 但是为获取到txid, 此交易稍后会被节点"); return
            if 'already' in rsp.text: print("交易已经存在"); return
            print("查寻失败: %s " % str(rsp.text)); return
    except Exception as e:
        print(e)
        return

def sign(hrp,fromprivkey, namount,nsequence, naccnumber,chainid='testchain',gasprice=100,gaswanted=20000,data=""):
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
		"To": ""\
	}],\
    "sequence": "%d"\
    }"""  % (naccnumber, chainid, gasprice, gaswanted, namount, data, fromaddr,gasprice,gaswanted,nsequence)

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
def execute(hrp,fromprivkey, data, chainid='testchain',gasprice=100, gaswanted=15000000,restapi='127.0.0.1:1317'):
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

    b64PubKey, b64Data = sign(hrp, fromprivkey, 0,nsequence, naccnumber,chainid,gasprice,gaswanted,data)
    broadcast(fromaddr,0,gasprice,gaswanted,b64PubKey,b64Data,data,restapi)

# usage: python create_contract.py 
# block gas limit: 15,000,000
# tx gas limit: 75,00,000
if __name__ == "__main__":
    fromprivkey = 'c06d9c5b991122f7c51a2cb89fc8efbf3e47e746c980f5afdbf2ac45f88aaf3d'
    restapi = '127.0.0.1:1317'
    chainid = 'testchain'
    gaswanted=7500000
    data='6060604052600080556000600160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550341561005557600080fd5b61046e806100646000396000f300606060405260043610610078576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806330a658241461007d5780633f62cfef146100ab5780634279fdc8146100f15780634d853ee514610137578063a3e76c0f1461018c578063c4cbfd8914610196575b600080fd5b341561008857600080fd5b6100a9600480803515159060200190919080359060200190919050506101dc565b005b34156100b657600080fd5b6100d760048080351515906020019091908035906020019091905050610274565b604051808215151515815260200191505060405180910390f35b34156100fc57600080fd5b61011d600480803515159060200190919080359060200190919050506102f1565b604051808215151515815260200191505060405180910390f35b341561014257600080fd5b61014a61038a565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6101946103b0565b005b34156101a157600080fd5b6101c2600480803515159060200190919080359060200190919050506103c1565b604051808215151515815260200191505060405180910390f35b6000339050821561020d57600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1690505b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166108fc839081150290604051600060405180830381858888f19350505050151561026f57600080fd5b505050565b60008033905083156102a657600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1690505b8073ffffffffffffffffffffffffffffffffffffffff1661753084604051600060405180830381858888f1935050505015156102e557600091506102ea565b600191505b5092915050565b600080339050831561032357600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1690505b8073ffffffffffffffffffffffffffffffffffffffff16836001600360405180831515151581526020018260ff1681526020019250505060006040518083038185876187965a03f192505050151561037e5760009150610383565b600191505b5092915050565b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b346000808282540192505081905550565b60008033905083156103f357600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1690505b8073ffffffffffffffffffffffffffffffffffffffff166108fc849081150290604051600060405180830381858888f1935050505015610436576000915061043b565b600191505b50929150505600a165627a7a72305820b81ae56510ac97a5963b60aab96b119c9cd244fdf4a3b44a4436053de16a57a10029'
    execute('htdf',fromprivkey=fromprivkey,data=data,gaswanted=gaswanted)
    