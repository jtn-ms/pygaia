#!coding:utf8
#author:yqq
#date: 2019-05-31 整理
#description:
#   此demo HTDF 和 USDP 交易的示例, 仅用于参考,  生产环境需自行设置
#


import hashlib
import coincurve
import base64
import requests


#HTDF测试节点ip和端口
g_node_ip_port = '47.98.194.7:1317'

#USDP测试节点ip和端口
# g_node_ip_port = '47.99.81.158:1317'

g_chainId = 'testchain'  #测试网
# g_chainId = 'mainchain'  #主网


# 以下是 USDP的测试地址
# g_strFrom = 'usdp1cl77rzpxd9t7fn0c2eq66qhvv355ztwkxhpqyk'
# g_PrivKey = '6da0717e95540c78e7480b790354cf4f0b59ec6e010b04f4ebeb111fdf3ffca5'
# g_PubKey = '03f17ab909f37dd55504af581f396fbaa0cd29c2f982336b2a6ae6cffdeaba97ed'


#以下是  HTDF 的测试地址
g_strFrom = 'htdf12sc78p9nr9s8qj06e2tqfqhlwlx0ncuq8l9gsh'
g_PrivKey = 'c9960987611a40cac259f2c989c43a79754df356415f164ad3080fdc10731e65'
g_PubKey = '02fa63a1fc6f38936562bac0649dde139b527d37788dd466d27259753fe5e555d0'


g_gas = 200000  #默认即可
g_fee =  20  #默认即可


def ecsign(rawhash, key):
    if coincurve and hasattr(coincurve, 'PrivateKey'):
        pk = coincurve.PrivateKey(key)
        signature = pk.sign_recoverable(rawhash, hasher=None)
        # v = safe_ord(signature[64]) + 27
        r = signature[0:32]
        s = signature[32:64]
        return r, s



def Transfer(strFrom, strTo, nAmount):



    #------------------------------步骤1 : 获取地址信息拼装要签名的数据-----------------------------------
    #获取地址的一些信息, 用于签名
    #此demo仅用于提供参考, 方便理解, 实际生产环境中
    #最核心的是 sequence,  在生产环境中, 如果进行大批量转账, 每笔交易要固定sequence, 而不要从节点获取!
    #固定sequence, 防止因为网络拥堵, 节点数据不同步,导致重复转账的问题
    try:
        rsp =  requests.get('http://%s/auth/accounts/%s' % (g_node_ip_port.strip(), strFrom.strip()))
        rspJson = rsp.json()
        nAccountNumber = int(rspJson['value']['account_number'], 10)
        nSequence = int(rspJson['value']['sequence'], 10)
    except Exception as e:
        #如果from地址不存在, 会返回  204错误
        if rsp.status_code == 204:
            print("from 地址, 不存在交易, 余额为0")
            return
        else:
            print (e)
        return

    print('account_number : %d' % nAccountNumber)
    print('sequence: %d' % nSequence)



    #使用字符拼装即可, 因为和字段的顺序有关, 不要使用json对象
    jUnTxStr = """{\
    "account_number": "%d",\
	"chain_id": "%s",\
	"fee": {\
		"amount": [{\
			"amount": "%d",\
			"denom": "satoshi"\
		}],\
		"gas": "%d"\
	},\
    "memo": "",\
	"msgs": [{\
		"Amount": [{\
			"amount": "%d",\
            "denom": "satoshi"\
		}],\
		"From": "%s",\
		"To": "%s"\
	}],\
    "sequence": "%d"\
}"""  % (nAccountNumber, g_chainId, g_fee, g_gas, nAmount, strFrom, strTo , nSequence)



    print('\n--------------------------------------\n')
    #去掉多余的空格, 制表符, 换行符
    jUnTxStr = jUnTxStr.replace(' ', '')
    jUnTxStr = jUnTxStr.replace('\t', '')
    jUnTxStr = jUnTxStr.replace('\n', '')
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
    privKey = g_PrivKey.decode('hex')
    print("strPrivKey: %s" % privKey.encode('hex'))
    print('\n--------------------------------------\n')

    #ECC签名
    print('\n--------------------------------------\n')
    r, s = ecsign(shaData,  privKey)  #只需要 r,s  不需要 v
    print('r:' + r.encode('hex'))
    print('s:' + s.encode('hex'))
    print('\n--------------------------------------\n')


    #拼装 r, s  , 并进行 base64编码     注意  ECC不需要
    print('\n--------------------------------------\n')
    b64Data = base64.b64encode(r + s)
    print("base64编码后的签名信息: %s" % b64Data)
    print('\n--------------------------------------\n')



    #-------------------------- 步骤2: 拼装广播数据 -----------------------------------------


    print('\n--------------------------------------\n')
    pubKey = g_PubKey
    b64PubKey = base64.b64encode(pubKey.decode('hex'))
    print("base64编码后的公钥:" + b64PubKey)
    print('\n--------------------------------------\n')

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
                    }]
                }
            }],
            "fee": {
                "amount": [{
                    "denom": "satoshi",
                    "amount": "%d"
                }],
                "gas": "%d"
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
    }""" %(strFrom, strTo , nAmount, g_fee, g_gas, b64PubKey, b64Data)

    #去掉多余的空白字符
    strBroadcast = strBroadcast
    strBroadcast = strBroadcast.replace(' ', '')
    strBroadcast = strBroadcast.replace('\t', '')
    strBroadcast = strBroadcast.replace('\n', '')
    bcastData = strBroadcast.encode('hex')
    print('\n--------------------------------------\n')
    print("广播的数据:"+ bcastData)
    print('\n--------------------------------------\n')



    # ---------------------------- 步骤3: 调用节点rpc接口,广播交易-----------------------------------

    #调用节点的rpc接口进行广播
    import json
    bcastData = {'tx' :  bcastData }   #rpc参数
    postData = json.dumps(bcastData)
    rsp = requests.post('http://%s/hs/broadcast' % (g_node_ip_port),  postData)


    #处理rpc接口
    try:
        if rsp.status_code == 200:
            rspJson = rsp.json()
            txid = str(rspJson['txhash'])
            print("%s 转给 %s 金额: %d  的交易广播成功, txid:%s" % (strFrom, strTo , nAmount, txid))
        else:
            #注意, 如果报 Timed out waiting for tx to be included in a block  的错, 说明已经广播成功,只是为被打包
            if 'Timed' in rsp.text:
                print("已经广播成功, 但是为获取到txid, 此交易稍后会被节点") 
                return
            if 'already' in rsp.text:
                print("交易已经存在")
                return
            print("广播失败: %s " % str(rsp.text))
            return
    except Exception as e:
        print(e)
        return


if __name__ == '__main__':

    strTo = 'htdf18rudpyaewcku05c87xzgaw4rl8z3e5s6vefu4r'
    nAmount = 0.001234 * (10**8)    #以satoshi为单位,    1USDP  = 10^8 satoshi    1HTDF=10^8 satoshi
    Transfer(g_strFrom, strTo.strip(), nAmount)

