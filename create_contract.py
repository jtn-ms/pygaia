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
testnet = '39.108.251.132'
mainnet = 'htdf2020-node01.orientwalt.cn'

port = '1317'

if __name__ == "__main__":
    fromprivkey = 'c06d9c5b991122f7c51a2cb89fc8efbf3e47e746c980f5afdbf2ac45f88aaf3d'
    restapi = '%s:%s'%(localhost,port)#'127.0.0.1:1317'
    chainid = 'testchain'#'mainchain'#
    gaswanted=1500000#7500000
    namount=100000000
    data='6060604052600080546001829055600160a060020a031916600160a060020a03331617815561003b9034640100000000610043810261041c1704565b600155610059565b60008282018381101561005257fe5b9392505050565b61045e806100686000396000f30060606040526004361061006c5763ffffffff7c010000000000000000000000000000000000000000000000000000000060003504166302d05d3f8114610071578063389cadb2146100a057806374580e2f146100d9578063ed88c68e146100fa578063f8a8fd6d14610102575b600080fd5b341561007c57600080fd5b610084610115565b604051600160a060020a03909116815260200160405180910390f35b34156100ab57600080fd5b6100c560043560243560ff60443516606435608435610124565b604051901515815260200160405180910390f35b34156100e457600080fd5b6100f8600160a060020a036004351661021b565b005b6100f8610280565b341561010d57600080fd5b6100c5610298565b600054600160a060020a031681565b60008054819033600160a060020a0390811691161461014257600080fd5b60015487901161015157600080fd5b6001868686866040516000815260200160405260006040516020015260405193845260ff90921660208085019190915260408085019290925260608401929092526080909201915160208103908084039060008661646e5a03f115156101b657600080fd5b5050602060405103519050600160a060020a03811687156108fc0288604051600060405180830381858888f1935050505015156101f65760009150610211565b600154610209908863ffffffff61040a16565b600190815591505b5095945050505050565b60005433600160a060020a0390811691161461023657600080fd5b600054600160a060020a038281169116141561025157600080fd5b6000805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a0392909216919091179055565b600154610293903463ffffffff61041c16565b600155565b6000805481908190819081908190819033600160a060020a039081169116146102c057600080fd5b60015461271096507fee3a08ca29bf6f48a55b8a9b4563f6593a0c69f09f85daa07af646d62d5e774c95507f7146d41c235b013f135e53f9a11bfc3c2f8a969e61af72ab1ced71d4fdabded594507f1c2d260a28f82e1e25367ff56799f31bfc403420d57b03668778334c7e5c3df89350601b925086901161034157600080fd5b6001858386866040516000815260200160405260006040516020015260405193845260ff90921660208085019190915260408085019290925260608401929092526080909201915160208103908084039060008661646e5a03f115156103a657600080fd5b5050602060405103519050600160a060020a03811686156108fc0287604051600060405180830381858888f1935050505015156103e65760009650610401565b6001546103f9908763ffffffff61040a16565b600190815596505b50505050505090565b60008282111561041657fe5b50900390565b60008282018381101561042b57fe5b93925050505600a165627a7a72305820e2f77199b5cd96a9d43842b0c9ebbdbb32afbd71b8d45363989aef37057b53460029'
    execute('htdf',fromprivkey=fromprivkey,namount=namount,data=data,restapi=restapi,gaswanted=gaswanted,chainid=chainid)
    
