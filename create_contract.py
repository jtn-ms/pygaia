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

localhost = '127.0.0.1'
testnet = '39.108.251.132'
port = '1317'

if __name__ == "__main__":
    fromprivkey = 'c06d9c5b991122f7c51a2cb89fc8efbf3e47e746c980f5afdbf2ac45f88aaf3d'
    restapi = '%s:%s'%(testnet,port)#'127.0.0.1:1317'
    chainid = 'testchain'
    gaswanted=7500000
    data='60606040526000600260006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550341561005157600080fd5b6a029f460b59cc2eb94000006003819055506003546000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550610d61806100b76000396000f3006060604052600436106100af576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806306fdde03146100b4578063095ea7b31461014257806318160ddd1461019c57806323b872dd146101c5578063313ce5671461023e5780634d853ee51461026d57806370a08231146102c257806393c32e061461030f57806395d89b4114610348578063a9059cbb146103d6578063dd62ed3e14610430575b600080fd5b34156100bf57600080fd5b6100c761049c565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156101075780820151818401526020810190506100ec565b50505050905090810190601f1680156101345780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561014d57600080fd5b610182600480803573ffffffffffffffffffffffffffffffffffffffff169060200190919080359060200190919050506104d5565b604051808215151515815260200191505060405180910390f35b34156101a757600080fd5b6101af61065c565b6040518082815260200191505060405180910390f35b34156101d057600080fd5b610224600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff16906020019091908035906020019091905050610662565b604051808215151515815260200191505060405180910390f35b341561024957600080fd5b610251610959565b604051808260ff1660ff16815260200191505060405180910390f35b341561027857600080fd5b61028061095e565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b34156102cd57600080fd5b6102f9600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610984565b6040518082815260200191505060405180910390f35b341561031a57600080fd5b610346600480803573ffffffffffffffffffffffffffffffffffffffff169060200190919050506109cc565b005b341561035357600080fd5b61035b610a6c565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561039b578082015181840152602081019050610380565b50505050905090810190601f1680156103c85780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b34156103e157600080fd5b610416600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091908035906020019091905050610aa5565b604051808215151515815260200191505060405180910390f35b341561043b57600080fd5b610486600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610c77565b6040518082815260200191505060405180910390f35b6040805190810160405280600981526020017f4d534c20636861696e000000000000000000000000000000000000000000000081525081565b60008082148061056157506000600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054145b151561056c57600080fd5b81600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925846040518082815260200191505060405180910390a36001905092915050565b60035481565b600080600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050600073ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff161415151561072057600080fd5b80831115151561072f57600080fd5b610780836000808873ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054610cfe90919063ffffffff16565b6000808773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550610813836000808773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054610d1790919063ffffffff16565b6000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055506108688382610cfe90919063ffffffff16565b600160008773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508373ffffffffffffffffffffffffffffffffffffffff168573ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef856040518082815260200191505060405180910390a360019150509392505050565b601281565b600260009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60008060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050919050565b600260009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16141515610a2857600080fd5b80600260006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050565b6040805190810160405280600381526020017f4d534c000000000000000000000000000000000000000000000000000000000081525081565b60008073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff1614151515610ae257600080fd5b610b33826000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054610cfe90919063ffffffff16565b6000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550610bc6826000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054610d1790919063ffffffff16565b6000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a36001905092915050565b6000600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054905092915050565b6000828211151515610d0c57fe5b818303905092915050565b6000808284019050838110151515610d2b57fe5b80915050929150505600a165627a7a723058200fc30f62107b9d60b8b13a489b616c9f07aeb6be72ab4eee2db3ee7358fc1b410029'
    execute('htdf',fromprivkey=fromprivkey,data=data,restapi=restapi,gaswanted=gaswanted)
    
