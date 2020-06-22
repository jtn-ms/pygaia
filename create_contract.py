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
    data='606060405260008060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506000600155341561005557600080fd5b336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555061083c806100a46000396000f300606060405260043610610099576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063038ebf0c1461009e57806339e955a3146100ed5780634d853ee5146101595780634d9b3d5d146101ae57806352d07be9146101d7578063569c15041461020557806370a082311461025257806393c32e061461029f578063ed88c68e146102d8575b600080fd5b6100d3600480803573ffffffffffffffffffffffffffffffffffffffff169060200190919080359060200190919050506102e2565b604051808215151515815260200191505060405180910390f35b34156100f857600080fd5b610143600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190803573ffffffffffffffffffffffffffffffffffffffff1690602001909190505061049f565b6040518082815260200191505060405180910390f35b341561016457600080fd5b61016c610567565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b34156101b957600080fd5b6101c161058c565b6040518082815260200191505060405180910390f35b610203600480803573ffffffffffffffffffffffffffffffffffffffff169060200190919050506105ab565b005b341561021057600080fd5b61023c600480803573ffffffffffffffffffffffffffffffffffffffff169060200190919050506106e5565b6040518082815260200191505060405180910390f35b341561025d57600080fd5b610289600480803573ffffffffffffffffffffffffffffffffffffffff169060200190919050506106fd565b6040518082815260200191505060405180910390f35b34156102aa57600080fd5b6102d6600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190505061071e565b005b6102e06107bc565b005b6000816001541115156102f457600080fd5b8273ffffffffffffffffffffffffffffffffffffffff166323b872dd336000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff16856000604051602001526040518463ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019350505050602060405180830381600087803b15156103f457600080fd5b6102c65a03f1151561040557600080fd5b50505060405180519050151561041e5760009050610499565b3373ffffffffffffffffffffffffffffffffffffffff16826001600360405180831515151581526020018260ff1681526020019250505060006040518083038185876187965a03f19250505015156104795760009050610499565b61048e826001546107d990919063ffffffff16565b600181905550600190505b92915050565b60008273ffffffffffffffffffffffffffffffffffffffff166370a08231836000604051602001526040518263ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001915050602060405180830381600087803b151561054457600080fd5b6102c65a03f1151561055557600080fd5b50505060405180519050905092915050565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60003073ffffffffffffffffffffffffffffffffffffffff1631905090565b6105c0346001546107f290919063ffffffff16565b6001819055508073ffffffffffffffffffffffffffffffffffffffff166323b872dd6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1633346000604051602001526040518463ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019350505050602060405180830381600087803b15156106c657600080fd5b6102c65a03f115156106d757600080fd5b505050604051805190505050565b60026020528060005260406000206000915090505481565b60008173ffffffffffffffffffffffffffffffffffffffff16319050919050565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614151561077957600080fd5b806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050565b6107d1346001546107f290919063ffffffff16565b600181905550565b60008282111515156107e757fe5b818303905092915050565b600080828401905083811015151561080657fe5b80915050929150505600a165627a7a72305820f1dfff2f6a4c74050e454347314f96f1c227839dfa00076850d807b69b2796010029'
    execute('htdf',fromprivkey=fromprivkey,data=data,gaswanted=gaswanted)
    