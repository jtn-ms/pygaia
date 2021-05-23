# written by junying, 2019-06-10
# accumulate small accounts balance into one.
#######################################################################################################################
## database file ######################################################################################################
## sscq	sscq1yc8xyy47j3ysq5dzwlhd48mtueg0vrhz4e0e82	725f8dce588fd7c5e485a4d37e1236f5fdbbf51754187f253ef947f09e4e6d98 ##
#######################################################################################################################
#					   children
#			  		  |---------->|
#	mother(facet) -->-|---------->|-->- father(gather)
#			  		  |~~~~~~~~~~~|
#			  		  |---------->|
SSCQ_CONFIG_FILE = $(CURDIR)/config/mainnet/sscq.json
# [sscq]
SSCQ_REST_SERVER = $$(findkey rest-server ${SSCQ_CONFIG_FILE})
SSCQ_CHAIN_ID = $$(findkey chain-id ${SSCQ_CONFIG_FILE})
SSCQ_DEFAULT_TX_GAS = $$(findkey default-gas ${SSCQ_CONFIG_FILE})
SSCQ_DEFAULT_GAS_PRICE = $$(findkey default-fee ${SSCQ_CONFIG_FILE})
SSCQ_DB_KEY = $$(findkey child-key-path ${SSCQ_CONFIG_FILE})
SSCQ_GOV_KEY = $$(findkey father-key ${SSCQ_CONFIG_FILE})
SSCQ_GOV_ADDR = $$(python -c "from key import privkey2addr; print privkey2addr('${SSCQ_GOV_KEY}',hrp='sscq')[1]")
#SSCQ_GOV_ADDR = $$(findkey father-addr ${SSCQ_CONFIG_FILE})
SSCQ_DISTR_KEY= $$(findkey mother-key ${SSCQ_CONFIG_FILE})
SSCQ_DISTR_ADDR = $$(python -c "from key import privkey2addr; print privkey2addr('${SSCQ_DISTR_KEY}',hrp='sscq')[1]")
# [usdp]
USDP_REST_SERVER = $$(findkey rest-server ${USDP_CONFIG_FILE})
USDP_CHAIN_ID = $$(findkey chain-id ${USDP_CONFIG_FILE})
USDP_DEFAULT_TX_GAS = $$(findkey default-gas ${USDP_CONFIG_FILE})
USDP_DEFAULT_GAS_PRICE = $$(findkey default-fee ${USDP_CONFIG_FILE})
USDP_DB_KEY = $$(findkey child-key-path ${USDP_CONFIG_FILE})
USDP_GOV_KEY = $$(findkey father-key ${USDP_CONFIG_FILE})
USDP_GOV_ADDR = $$(python -c "from key import privkey2addr; print privkey2addr('${USDP_GOV_KEY}',hrp='usdp')[1]")
#USDP_GOV_ADDR = $$(findkey father-addr ${USDP_CONFIG_FILE})
USDP_DISTR_KEY= $$(findkey mother-key ${USDP_CONFIG_FILE})
USDP_DISTR_ADDR = $$(python -c "from key import privkey2addr; print privkey2addr('${USDP_DISTR_KEY}',hrp='usdp')[1]")

HRC_DEFAULT_TX_GAS = 500000

# CHECK
check:
	@echo ${SSCQ_REST_SERVER}
	@echo ${SSCQ_CHAIN_ID}
	@echo ${SSCQ_DEFAULT_TX_GAS}
	@echo ${SSCQ_DEFAULT_GAS_PRICE}
	@echo ${SSCQ_DB_KEY}
	@echo ${SSCQ_GOV_KEY}
	@echo ${SSCQ_DISTR_KEY}
	@echo ${SSCQ_GOV_ADDR}
	@echo ${SSCQ_DISTR_ADDR}

# this is for single mode
# first account to mother address
send2faucet:
	@sscli tx send $$(sscli accounts list | sed -n '1p') ${SSCQ_GOV_ADDR} 10000000000000satoshi --gas-price=100

#+ &&&&& 
#+{@ | @}
#++  _  +	>>>	Main
# accumulate 
accu.sscq:
	@python -c "from accu import accumulateEx; accumulateEx(toaddr='${SSCQ_GOV_ADDR}',\
														privkeyfile='${SSCQ_DB_KEY}',\
														restapi='${SSCQ_REST_SERVER}',\
														chainid='${SSCQ_CHAIN_ID}',\
														ndefault_gas=${SSCQ_DEFAULT_TX_GAS},\
														ndefault_fee=${SSCQ_DEFAULT_GAS_PRICE})";
ACCU_AMOUNT = 10000#satoshi, default:None

#  %%%%%
# {@ | ~} 
#    _		>>>	Singleton
# transfer token
# In:  sscq1yc8xyy47j3ysq5dzwlhd48mtueg0vrhz4e0e82,100000
# Out: 
transfer.one.sscq:
	@echo ${SSCQ_DISTR_KEY}
	@read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import transfer; transfer(hrp='sscq',\
	 											  fromprivkey='${SSCQ_DISTR_KEY}',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${SSCQ_REST_SERVER}',\
												  chainid='${SSCQ_CHAIN_ID}',\
												  gaswanted=${SSCQ_DEFAULT_TX_GAS},\
												  gasprice=${SSCQ_DEFAULT_GAS_PRICE})";

transfer.one.hrc20:
	@echo ${SSCQ_DISTR_KEY}
	@read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import transfer_hrc20; transfer_hrc20(hrp='sscq',\
	 											  contractaddr='sscq1gjqlacff7tttnk7shaqgszexvt74avrh507knj',\
	 											  fromprivkey='${SSCQ_DISTR_KEY}',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${SSCQ_REST_SERVER}',\
												  chainid='${SSCQ_CHAIN_ID}',\
												  gaswanted=${HRC_DEFAULT_TX_GAS},\
												  gasprice=${SSCQ_DEFAULT_GAS_PRICE})";

run.contract.sscq:
	@echo ${SSCQ_DISTR_KEY}
	@read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 read -p "Type Data: " data; \
	 python -c "from tx import transfer; transfer(hrp='sscq',\
	 											  fromprivkey='${SSCQ_DISTR_KEY}',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${SSCQ_REST_SERVER}',\
												  chainid='${SSCQ_CHAIN_ID}',\
												  gaswanted=${SSCQ_DEFAULT_TX_GAS},\
												  gasprice=${SSCQ_DEFAULT_GAS_PRICE},\
												  data='$$data')";

# multiple transactions from one account
# into a block
transfer.one.sscq.test:
	@echo ${SSCQ_DISTR_KEY}
	@read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import test_transfer; test_transfer(hrp='sscq',\
															fromprivkey='${SSCQ_DISTR_KEY}',\
															toaddr='$$toaddr',\
															namount=$$amount,\
															restapi='${SSCQ_REST_SERVER}',\
															chainid='${SSCQ_CHAIN_ID}',\
															gaswanted=${SSCQ_DEFAULT_TX_GAS},\
															gasprice=${SSCQ_DEFAULT_GAS_PRICE})";

transfer.two.sscq:
	@read -p "Type From Private Key: " fromprivkey; \
	 read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import transfer; transfer(hrp='sscq',\
	 											  fromprivkey='$$fromprivkey',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${SSCQ_REST_SERVER}',\
												  chainid='${SSCQ_CHAIN_ID}',\
												  gaswanted=${SSCQ_DEFAULT_TX_GAS},\
												  gasprice=${SSCQ_DEFAULT_GAS_PRICE})";

transfer.multi.sscq:
	@python -c "from tx import transferMulti; transferMulti(hrp='sscq',\
	 											  fromprivkey='b948544b053ebfac33f21f2a7a9e1bb8dc5e78c1bf3d6b0f5b6eaed94ea49797',\
												  txlistfile='./db/txs/tx.list',\
												  restapi='39.108.251.132:1317',\
												  chainid='testchain',\
												  gaswanted=30000,\
												  gasprice=100)";
# check account
chkacc.one.sscq:
	@read -p "Type sscq address: " addr; \
	 python -c "from tx import accountinfo; print accountinfo('$$addr','${SSCQ_REST_SERVER}')"

chkacc.one.hrc20:
	@read -p "Type contract address: " contractaddr; \
	 read -p "Type sscq address: " addr; \
	 querydata=$$(python -c "from tx import queryGetBalance; print queryGetBalance('$$addr')");\
	 curl -X GET "http://${SSCQ_REST_SERVER}/ss/contract/$$contractaddr/$$querydata" -H "accept: application/json"

chkacc.multi.sscq:
	@python -c "from tx import chkaccMulti; chkaccMulti('db/txs/acnts.list','39.108.251.132:1317')"


compare.multi:
	@python -c "from tx import compareBalances; compareBalances()"
# generate random key
genkey.one.usdp:
	@python -c "from key import genkey; print genkey('usdp')"
genkey.one.sscq:
	@python -c "from key import genkey; print genkey('sscq')"
# generate key with keystring
genkey.key.sscq:
	@read -p "Type KeyString: " keystring; \
	 python -c "from key import genkey; print genkey('sscq','$$keystring')"
# 2020-03-19
genkey.keys.sscq:
	@read -p "Type KeyString: " keystring; \
	 python -c "from key import genkey; keys=[genkey('sscq','$$keystring%d'%i)[0] for i in range(8)]; print '\n'.join(keys)"

recover.keys:
	@read -p "Type KeyString: " keystring; \
	 for index in  $$(python -c "print ' '.join(str(item) for item in range(1,8))"); do \
	 privkey=$$(python -c "from key import genkey; print genkey('sscq','$$keystring$$index')[0]");\
	 echo $$privkey;\
	 ansible $$keystring$$index -m shell -a "sscli accounts recover $$privkey 123456789";\
	 done;

# convert
privkey2addr.sscq:
	@read -p "Type sscq privkey: " privkey; \
	 python -c "from key import privkey2addr; print privkey2addr('$$privkey',hrp='sscq')"
#  $$$$$
# {~ | ~} 
#    _		>>>	Simulation
# generate
ACC_COUNT = 2#10000
genkey2db.multi.sscq:
	@python -c "from key import genkeys; genkeys('sscq',${ACC_COUNT},'${SSCQ_DB_KEY}')";

airdrop.input.data:
	@addrs=$$(python3 -c "hexstr=hex(${ACC_COUNT})[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 values=$$(python3 -c "hexstr=hex(${ACC_COUNT})[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 for index in  $$(python -c "print ' '.join(str(item) for item in range(${ACC_COUNT}))"); do \
	 bechaddr=$$(python -c "from key import genkey; print genkey('sscq','$$keystring$$index')[2]");\
	 hexaddr=$$(ssutils bech2hex $$bechaddr|row 3|fromstr ": ");\
	 lowerhexaddr=$$(lowerstr $$hexaddr);\
	 param_addr=$$(python -c "print( '0'*(64-len('$$lowerhexaddr'))+'$$lowerhexaddr')");\
	 value=$$(python -c "import random; print random.randint(100000,10000000)");\
	 echo $$bechaddr $$value;\
	 addrs=$$addrs$$param_addr;\
	 values=$$values$$(python3 -c "hexstr=hex($$value)[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 done;\
	 token_addr=0000000000000000000000004fabb8cc1740cd9849371f2a574ae4e4a502a59e;\
	 pos_addrs=$$(python3 -c "hexstr=hex(32*3)[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 pos_values=$$(python3 -c "hexstr=hex(32*(3+1+${ACC_COUNT}))[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 echo 7da5efc8$$token_addr$$pos_addrs$$pos_values$$addrs$$values;

batchsend.input.data:
	@addrs=$$(python3 -c "hexstr=hex(${ACC_COUNT})[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 values=$$(python3 -c "hexstr=hex(${ACC_COUNT})[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 for index in  $$(python -c "print ' '.join(str(item) for item in range(${ACC_COUNT}))"); do \
	 privkey=$$(python -c "from key import genkey; print genkey('sscq','$$keystring$$index')[0]");\
	 bechaddr=$$(python -c "from key import privkey2addr; print privkey2addr('$$privkey',hrp='sscq')[1]");\
	 hexaddr=$$(ssutils bech2hex $$bechaddr|row 3|fromstr ": ");\
	 lowerhexaddr=$$(lowerstr $$hexaddr);\
	 param_addr=$$(python -c "print( '0'*(64-len('$$lowerhexaddr'))+'$$lowerhexaddr')");\
	 value=$$(python -c "import random; print random.randint(100000,10000000)");\
	 echo $$bechaddr $$privkey $$value;\
	 addrs=$$addrs$$param_addr;\
	 values=$$values$$(python3 -c "hexstr=hex($$value)[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 done;\
	 pos_addrs=$$(python3 -c "hexstr=hex(32*2)[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 pos_values=$$(python3 -c "hexstr=hex(32*(2+1+${ACC_COUNT}))[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 echo 2929abe6$$pos_addrs$$pos_values$$addrs$$values;

qutoareceive.contract.data:
	@addrs=$$(python3 -c "hexstr=hex(${ACC_COUNT})[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 values=$$(python3 -c "hexstr=hex(${ACC_COUNT})[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 contract='6060604052341561000f57600080fd5b6040516103a43803806103a48339810160405280805182019190602001805182019190505060008090505b82518110156100c157818181518110151561005157fe5b90602001906020020151600080858481518110151561006c57fe5b9060200190602002015173ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550808060010191505061003a565b5050506102d1806100d36000396000f300606060405260043610610057576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680633ccfd60b1461005c57806370a08231146100895780638be79003146100d6575b600080fd5b341561006757600080fd5b61006f610123565b604051808215151515815260200191505060405180910390f35b341561009457600080fd5b6100c0600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610245565b6040518082815260200191505060405180910390f35b34156100e157600080fd5b61010d600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190505061028d565b6040518082815260200191505060405180910390f35b6000806000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050600081111561023c5760008060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055503373ffffffffffffffffffffffffffffffffffffffff166108fc829081150290604051600060405180830381858888f19350505050151561023b57806000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000208190555060009150610241565b5b600191505b5090565b60008060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050919050565b600060205280600052604060002060009150905054815600a165627a7a723058207158cbed54d1a55c0c779c233a6c3e440b05975892c7fc45aaa4f9bcb2ba3c8f0029';\
	 for index in  $$(python -c "print ' '.join(str(item) for item in range(${ACC_COUNT}))"); do \
	 privkey=$$(python -c "from key import genkey; print genkey('sscq','$$keystring$$index')[0]");\
	 bechaddr=$$(python -c "from key import privkey2addr; print privkey2addr('$$privkey',hrp='sscq')[1]");\
	 hexaddr=$$(ssutils bech2hex $$bechaddr|row 3|fromstr ": ");\
	 lowerhexaddr=$$(lowerstr $$hexaddr);\
	 param_addr=$$(python -c "print( '0'*(64-len('$$lowerhexaddr'))+'$$lowerhexaddr')");\
	 value=$$(python -c "import random; print random.randint(100000,10000000)");\
	 echo $$bechaddr $$value $$privkey;\
	 addrs=$$addrs$$param_addr;\
	 values=$$values$$(python3 -c "hexstr=hex($$value)[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 done;\
	 pos_addrs=$$(python3 -c "hexstr=hex(32*2)[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 pos_values=$$(python3 -c "hexstr=hex(32*(2+1+${ACC_COUNT}))[2:]; print('0'*(64-len(hexstr))+hexstr)");\
	 echo $$contract$$pos_addrs$$pos_values$$addrs$$values;

chkacc.all.sscq:
	# @python -c "from tx import accountinfo; print accountinfo('${SSCQ_DISTR_ADDR}','${SSCQ_REST_SERVER}')"
	@python -c "from tx import accountinfo; print accountinfo('${SSCQ_GOV_ADDR}','${SSCQ_REST_SERVER}')"
	@python -c "from accu import report; report(privkeyfile='${SSCQ_DB_KEY}',restapi='${SSCQ_REST_SERVER}')";
# ACC_INDEX = $$(python -c "print ' '.join(str(item) for item in range(${ACC_COUNT}))")
# chkacc.all.sscq.old:
# @for index in ${ACC_INDEX}; do \
#  addr=$$(row $$index ${SSCQ_DB_KEY} 1|column 2); \
#  python -c "from multiprocessing import Process;from tx import accountinfo;\
#  			Process(target=accountinfo,args=('$$addr','${SSCQ_REST_SERVER}',True)).start();"; done


# distribution
distr.sscq:
	@python -c "from distr import distr; distr(fromprivkey='${SSCQ_DISTR_KEY}',\
											  hrp='sscq',\
											  privkeyfile='${SSCQ_DB_KEY}',\
											  restapi='${SSCQ_REST_SERVER}',\
											  chainid='${SSCQ_CHAIN_ID}',\
											  ndefault_gas=${SSCQ_DEFAULT_TX_GAS},\
											  ndefault_fee=${SSCQ_DEFAULT_GAS_PRICE})";

distr.hrc20:
	@python -c "from distr import distr_erc20; distr_erc20(fromprivkey='${SSCQ_DISTR_KEY}',\
											  contractaddr='sscq12dvguqedrvgfrdl35hcgfmz4fz6rm6chrvf96g',\
											  hrp='sscq',\
											  privkeyfile='${SSCQ_DB_KEY}',\
											  restapi='${SSCQ_REST_SERVER}',\
											  chainid='${SSCQ_CHAIN_ID}',\
											  ndefault_gas=${HRC_DEFAULT_TX_GAS},\
											  ndefault_fee=${SSCQ_DEFAULT_GAS_PRICE})";
DISTR_AMOUNT = 1000000

distr.sscq.count:
	@python -c "from distr import count; count(privkeyfile='${SSCQ_DB_KEY}',\
											   restapi='${SSCQ_REST_SERVER}',
											   debug=True)";

distrex.sscq:
	@python -c "from distr import distrex;  distrex(hrp='sscq',\
											  	    privkeyfile='${SSCQ_DB_KEY}',\
											  		restapi='${SSCQ_REST_SERVER}',\
											  		chainid='${SSCQ_CHAIN_ID}',\
											  		ndefault_gas=${SSCQ_DEFAULT_TX_GAS},\
											  		ndefault_fee=${SSCQ_DEFAULT_GAS_PRICE})";

flood.sscq:
	@python -c "from flood import flood;  flood(hrp='sscq',\
											  	privkeyfile='${SSCQ_DB_KEY}',\
											  	restapi='${SSCQ_REST_SERVER}',\
											  	chainid='${SSCQ_CHAIN_ID}',\
											  	ndefault_gas=${SSCQ_DEFAULT_TX_GAS},\
											  	ndefault_fee=${SSCQ_DEFAULT_GAS_PRICE})";

#  %%%%%
# {^ | ^} 
#    _		>>>	Maid
# utils: clean,tar
clean:
	@find -name "*.pyc" -exec rm -f {} \;
	@find -name __pycache__ | xargs rm -rf
	@find -name .pytest_cache | xargs rm -rf

tar: clean
	@tar cf ../accu.tar.gz *
.PHONY: chkacc.all.sscq chkacc.all.usdp

#### borrowed from orientwalt/sscq
# create method_id
# from ethereum.abi import method_id
# hex(method_id("minter",[]))
# hex(method_id("balances",['address']))
# hex(method_id("mint",['address','uint256']))
# hex(method_id("send",['address','uint256']))
# Usage:
# function name: minter
# parameters: 
# function name: mint
# parameters: 'address','uint256'
get.method.id:
	@read -p "function name: " funcname;\
	 read -p "parameters: " paramstr;\
	 data=$$(python -c "from ethereum.abi import method_id;\
	 				 	code=hex(method_id('$$funcname',[$$paramstr]));\
						print(code[:2]+'0'*(10-len(code))+code[2:]);\
						");\
	 echo $$data

# param: address
# In:  sscq1ha7ryup8nc2avgesfunx2pm22waqv2cx6dj0ac
# Out: BF7C3270279E15D623304F2665076A53BA062B06
# 	   bf7c3270279e15d623304f2665076a53ba062b06
#	   000000000000000000000000bf7c3270279e15d623304f2665076a53ba062b06
param.address:
	@read -p "bech32addr: " bech32addr;\
	 byteaddr=$$(ssutils bech2hex $$bech32addr|row 3|fromstr ": ");\
	 loweraddr=$$(lowerstr $$byteaddr);\
	 param_addr=$$(python -c "print( '0'*(64-len('$$loweraddr'))+'$$loweraddr')");\
	 echo $$param_addr

# param: int
# In:  100000
# Out: 
# 	   
#	   
param.int:
	@read -p "uint: " uint;\
	 python3 -c "hexstr=hex($$uint)[2:];\
	 			 print('0'*(64-len(hexstr))+hexstr)"

# In:aaa
# Out:0000000000000000000000000000000000000000000000000000000000616161
param.string:
	@read -p "string: " string;\
	 python3 -c "hexstr=b'$$string'.hex();\
	 			 print('0'*(64-len(hexstr))+hexstr)"

# In:616161
# Out:aaa
hex2str:
	@read -p "hexstr: " hexstr;\
	 python3 -c "string=bytes.fromhex('$$hexstr').decode('utf-8') ;\
	 			 print(string)"	 
