# -*- coding: utf-8 -*-
# written by junying, 2019-06-10
import hashlib
import coincurve
import base64
import requests

from tx import ecsign,accountinfo

def broadcast(fromaddr, b64PubKey, b64Data,restapi='localhost:1317'):
    
    strBroadcast = """{
        "type": "auth/StdTx",
        "value":{
            "msg": [{
                "type": "sscq/MsgEditValidator", 
                "value": {
                    "Description": {
                        "details": "To infinity and beyond!", 
                        "identity": "23870f5bb12ba2c4967c46db", 
                        "moniker": "sss", 
                        "website": "https://sscq.network"
                    }, 
                    "address": "sscqvaloper1v8j6r7ttfac07nuhy8uhxgumy7442ck532287d", 
                    "commission_rate": "0.102000000000000000", 
                    "min_self_delegation": null
                }
            }],
            "fee": {
                "gas_wanted": "200000",
                "gas_price": "100"
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
    }""" %(b64PubKey, b64Data)

    #去掉多余的空白字符
    strBroadcast = strBroadcast.replace(' ', '').replace('\t', '').replace('\n', '')
    bcastData = strBroadcast.encode('hex')
    print('\n--------------------------------------\n')
    print("广播的数据:"+ bcastData)
    print('\n--------------------------------------\n')

    # ---------------------------- 步骤3: 调用节点rpc接口,广播交易-----------------------------------

    #调用节点的rpc接口进行广播
    # import json
    # bcastData = {'tx' :  bcastData }   #rpc参数
    # postData = json.dumps(bcastData)
    # rsp = requests.post('http://%s/ss/broadcast'%restapi,  postData)


    # #处理rpc接口
    # try:
    #     if rsp.status_code == 200:
    #         rspJson = rsp.json()
    #         txid = str(rspJson['txhash'])
    #         print("txid:%s" % txid)
    #     else:
    #         #注意, 如果报 Timed out waiting for tx to be included in a block  的错, 说明已经广播成功,只是为被打包
    #         if 'Timed' in rsp.text: print("已经广播成功, 但是为获取到txid, 此交易稍后会被节点"); return
    #         if 'already' in rsp.text: print("交易已经存在"); return
    #         print("广播失败: %s " % str(rsp.text)); return
    # except Exception as e:
    #     print(e)
    #     return

def sign(hrp,fromprivkey,nsequence, naccnumber,chainid='testchain'):
    from key import privkey2addr
    frompubkey,fromaddr = privkey2addr(fromprivkey,hrp)
    
    #使用字符拼装即可, 因为和字段的顺序有关, 不要使用json对象
    jUnTxStr = """{\
    "account_number": "%d",\
	"chain_id": "%s",\
	"fee": {\
        "gas_price": "100",\
		"gas_wanted": "200000"\
	},\
    "memo": "",\
	"msgs": [{\
        "type": "sscq/MsgEditValidator",\
        "value": {\
            "Description": {\
                "details": "To infinity and beyond!",\
                "identity": "23870f5bb12ba2c4967c46db",\
                "moniker": "sss",\
                "website": "https://sscq.network"\
            },\
            "address": "sscqvaloper1v8j6r7ttfac07nuhy8uhxgumy7442ck532287d",\
            "commission_rate": "0.102000000000000000",\
            "min_self_delegation": null\
        }
	}],\
    "sequence": "%d"\
    }"""  % (naccnumber, chainid, nsequence)

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

def transfer(hrp,fromprivkey, chainid='testchain',restapi='0.0.0.0:1317',debug=True):
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
    if debug: end = time.time();print('accountinfo: %d'%int(end-start));start=end
    if naccnumber < 0 or nsequence < 0: return
    print('account_number : %d' % naccnumber)
    print('sequence: %d' % nsequence)
    #-------------------------- 步骤2: 签名 -----------------------------------------
    b64PubKey, b64Data = sign(hrp, fromprivkey, nsequence, naccnumber,chainid)
    if debug: end = time.time();print('sign: %d'%int(end-start));start=end
    #-------------------------- 步骤3: 拼装广播数据 -----------------------------------------
    broadcast(fromaddr,b64PubKey,b64Data,restapi)
    if debug: end = time.time();print('broadcast: %d'%int(end-start));start=end
   
if __name__ == "__main__":
    fromprivkey = '8841dba4617c63425f502c763bbd113fc49e6a69d223985f93f4d53d28616ba1'
    frompubkey = '03fd3ccea6fbf44d0aca9fec7fc3ba0ff6863845c07216ecf2247ad4b70d93e245'
    fromaddr = 'sscq1v8j6r7ttfac07nuhy8uhxgumy7442ck5mnj7fx'
    restapi = '120.77.170.207:1317'
    chainid = 'testchain'
    from key import privkey2addr
    print accountinfo(fromaddr,restapi=restapi)
    print privkey2addr(fromprivkey,hrp='sscq')
    transfer('sscq',fromprivkey,restapi=restapi)
    