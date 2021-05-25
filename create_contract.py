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
                "type": "sscqservice/send",  
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
    rsp = requests.post('http://%s/ss/broadcast'%restapi,  postData)


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
def execute(hrp,fromprivkey,namount, data, chainid='testchain',gasprice=100, gaswanted=15000000,restapi='127.0.0.1:1317'):
    import time
    start = time.time()
    from key import privkey2addr
    _,fromaddr = privkey2addr(fromprivkey,hrp=hrp)
    #------------------------------步骤1 : 获取地址信息拼装要签名的数据-----------------------------------
    print(restapi)
    rsp = accountinfo(fromaddr,restapi)
    print(rsp)
    naccnumber, nsequence = rsp["accountnumber"],rsp["sequence"]
    nbalance = rsp["balance"] * (10**8) - gaswanted*gasprice - namount # transfer all balance if namount < 0
    if nbalance < 0: print('no balance'); return
    if naccnumber < 0 or nsequence < 0: print(naccnumber); print(nsequence); return
    print('account_number : %d' % naccnumber)
    print('sequence: %d' % nsequence)
    #-------------------------- 步骤2: 签名 -----------------------------------------

    b64PubKey, b64Data = sign(hrp, fromprivkey, namount,nsequence, naccnumber,chainid,gasprice,gaswanted,data)
    broadcast(fromaddr,namount,gasprice,gaswanted,b64PubKey,b64Data,data,restapi)

# usage: python create_contract.py 
# block gas limit: 15,000,000
# tx gas limit: 75,00,000

localhost = '127.0.0.1'
testnet = '47.57.2.187'
mainnet = 'sscq2020-node01.orientwalt.cn'

port = '1317'

if __name__ == "__main__":
    fromprivkey = 'c06d9c5b991122f7c51a2cb89fc8efbf3e47e746c980f5afdbf2ac45f88aaf3d'
    restapi = '%s:%s'%(testnet,port)#'127.0.0.1:1317'
    chainid = 'mainchain'#'mainchain'#
    gaswanted=1500000#7500000
    namount=0
    data='606060405260028054600160a060020a0319169055341561001f57600080fd5b6aa49be39dc14cb8270000006003819055600160a060020a03331660008181526020819052604090209190915560028054600160a060020a03191690911790556106e98061006e6000396000f3006060604052600436106100ae5763ffffffff7c010000000000000000000000000000000000000000000000000000000060003504166306fdde0381146100b3578063095ea7b31461013d57806318160ddd1461017357806323b872dd14610198578063313ce567146101c05780634d853ee5146101e957806370a082311461021857806393c32e061461023757806395d89b4114610258578063a9059cbb1461026b578063dd62ed3e1461028d575b600080fd5b34156100be57600080fd5b6100c66102b2565b60405160208082528190810183818151815260200191508051906020019080838360005b838110156101025780820151838201526020016100ea565b50505050905090810190601f16801561012f5780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561014857600080fd5b61015f600160a060020a03600435166024356102e9565b604051901515815260200160405180910390f35b341561017e57600080fd5b61018661038f565b60405190815260200160405180910390f35b34156101a357600080fd5b61015f600160a060020a0360043581169060243516604435610395565b34156101cb57600080fd5b6101d36104cd565b60405160ff909116815260200160405180910390f35b34156101f457600080fd5b6101fc6104d2565b604051600160a060020a03909116815260200160405180910390f35b341561022357600080fd5b610186600160a060020a03600435166104e1565b341561024257600080fd5b610256600160a060020a03600435166104fc565b005b341561026357600080fd5b6100c6610546565b341561027657600080fd5b61015f600160a060020a036004351660243561057d565b341561029857600080fd5b610186600160a060020a036004358116906024351661066a565b60408051908101604052600981527f414a4320636861696e0000000000000000000000000000000000000000000000602082015281565b600081158061031b5750600160a060020a03338116600090815260016020908152604080832093871683529290522054155b151561032657600080fd5b600160a060020a03338116600081815260016020908152604080832094881680845294909152908190208590557f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b9259085905190815260200160405180910390a350600192915050565b60035481565b600160a060020a03808416600090815260016020908152604080832033851684529091528120549091841615156103cb57600080fd5b808311156103d857600080fd5b600160a060020a038516600090815260208190526040902054610401908463ffffffff61069516565b600160a060020a038087166000908152602081905260408082209390935590861681522054610436908463ffffffff6106a716565b600160a060020a03851660009081526020819052604090205561045f818463ffffffff61069516565b600160a060020a03808716600081815260016020908152604080832033861684529091529081902093909355908616917fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef9086905190815260200160405180910390a3506001949350505050565b601281565b600254600160a060020a031681565b600160a060020a031660009081526020819052604090205490565b60025433600160a060020a0390811691161461051757600080fd5b6002805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a0392909216919091179055565b60408051908101604052600381527f414a430000000000000000000000000000000000000000000000000000000000602082015281565b6000600160a060020a038316151561059457600080fd5b600160a060020a0333166000908152602081905260409020546105bd908363ffffffff61069516565b600160a060020a0333811660009081526020819052604080822093909355908516815220546105f2908363ffffffff6106a716565b60008085600160a060020a0316600160a060020a031681526020019081526020016000208190555082600160a060020a031633600160a060020a03167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef8460405190815260200160405180910390a350600192915050565b600160a060020a03918216600090815260016020908152604080832093909416825291909152205490565b6000828211156106a157fe5b50900390565b6000828201838110156106b657fe5b93925050505600a165627a7a7230582089c7fe6368d992b6d647b28a2818fc5dbb303c38cd33205911cd7fce76c6f0b20029'
    execute('sscq',fromprivkey=fromprivkey,namount=namount,data=data,restapi=restapi,gaswanted=gaswanted,chainid=chainid)
    
