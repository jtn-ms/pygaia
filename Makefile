# written by junying, 2019-06-10
# accumulate small accounts balance into one.
#######################################################################################################################
## database file ######################################################################################################
## htdf	htdf1yc8xyy47j3ysq5dzwlhd48mtueg0vrhz4e0e82	725f8dce588fd7c5e485a4d37e1236f5fdbbf51754187f253ef947f09e4e6d98 ##
#######################################################################################################################
#					   children
#			  		  |---------->|
#	mother(facet) -->-|---------->|-->- father(gather)
#			  		  |~~~~~~~~~~~|
#			  		  |---------->|
HTDF_CONFIG_FILE = $(CURDIR)/config/testnet/htdf.json
USDP_CONFIG_FILE = $(CURDIR)/config/10000/usdp.json
# [htdf]
HTDF_REST_SERVER = $$(findkey rest-server ${HTDF_CONFIG_FILE})
HTDF_CHAIN_ID = $$(findkey chain-id ${HTDF_CONFIG_FILE})
HTDF_DEFAULT_TX_GAS = $$(findkey default-gas ${HTDF_CONFIG_FILE})
HTDF_DEFAULT_TX_FEE = $$(findkey default-fee ${HTDF_CONFIG_FILE})
HTDF_DB_KEY = $$(findkey child-key-path ${HTDF_CONFIG_FILE})
HTDF_GOV_KEY = $$(findkey father-key ${HTDF_CONFIG_FILE})
HTDF_GOV_ADDR = $$(python -c "from key import privkey2addr; print privkey2addr('${HTDF_GOV_KEY}',hrp='htdf')[1]")
#HTDF_GOV_ADDR = $$(findkey father-addr ${HTDF_CONFIG_FILE})
HTDF_DISTR_KEY= $$(findkey mother-key ${HTDF_CONFIG_FILE})
HTDF_DISTR_ADDR = $$(python -c "from key import privkey2addr; print privkey2addr('${HTDF_DISTR_KEY}',hrp='htdf')[1]")
# [usdp]
USDP_REST_SERVER = $$(findkey rest-server ${USDP_CONFIG_FILE})
USDP_CHAIN_ID = $$(findkey chain-id ${USDP_CONFIG_FILE})
USDP_DEFAULT_TX_GAS = $$(findkey default-gas ${USDP_CONFIG_FILE})
USDP_DEFAULT_TX_FEE = $$(findkey default-fee ${USDP_CONFIG_FILE})
USDP_DB_KEY = $$(findkey child-key-path ${USDP_CONFIG_FILE})
USDP_GOV_KEY = $$(findkey father-key ${USDP_CONFIG_FILE})
USDP_GOV_ADDR = $$(python -c "from key import privkey2addr; print privkey2addr('${USDP_GOV_KEY}',hrp='usdp')[1]")
#USDP_GOV_ADDR = $$(findkey father-addr ${USDP_CONFIG_FILE})
USDP_DISTR_KEY= $$(findkey mother-key ${USDP_CONFIG_FILE})
USDP_DISTR_ADDR = $$(python -c "from key import privkey2addr; print privkey2addr('${USDP_DISTR_KEY}',hrp='usdp')[1]")

HRC_DEFAULT_TX_GAS = 500000

# CHECK
check:
	@echo ${HTDF_REST_SERVER}
	@echo ${HTDF_CHAIN_ID}
	@echo ${HTDF_DEFAULT_TX_GAS}
	@echo ${HTDF_DB_KEY}
	@echo ${HTDF_GOV_KEY}
	@echo ${HTDF_DISTR_KEY}
	@echo ${HTDF_GOV_ADDR}
	@echo ${HTDF_DISTR_ADDR}
	@echo ${USDP_REST_SERVER}
	@echo ${USDP_CHAIN_ID}
	@echo ${USDP_DEFAULT_TX_GAS}
	@echo ${USDP_DB_KEY}
	@echo ${USDP_GOV_KEY}
	@echo ${USDP_DISTR_KEY}
	@echo ${USDP_GOV_ADDR}
	@echo ${USDP_DISTR_ADDR}

# this is for single mode
# first account to mother address
send2faucet:
	@hscli tx send $$(hscli accounts list | sed -n '1p') ${HTDF_GOV_ADDR} 10000000000000satoshi --gas-price=100

#+ &&&&& 
#+{@ | @}
#++  _  +	>>>	Main
# accumulate 
accu.htdf:
	@python -c "from accu import accumulateEx; accumulateEx(toaddr='${HTDF_GOV_ADDR}',\
														privkeyfile='${HTDF_DB_KEY}',\
														restapi='${HTDF_REST_SERVER}',\
														chainid='${HTDF_CHAIN_ID}',\
														ndefault_gas=${HTDF_DEFAULT_TX_GAS},\
														ndefault_fee=${HTDF_DEFAULT_TX_FEE})";
ACCU_AMOUNT = 10000#satoshi, default:None
accu.usdp:
	@python -c "from accu import accumulateEx; accumulateEx(toaddr='${USDP_GOV_ADDR}',\
														privkeyfile='${USDP_DB_KEY}',\
														restapi='${USDP_REST_SERVER}',\
														chainid='${USDP_CHAIN_ID}',\
														ndefault_gas=${USDP_DEFAULT_TX_GAS},\
														ndefault_fee=${USDP_DEFAULT_TX_FEE})";

#  %%%%%
# {@ | ~} 
#    _		>>>	Singleton
# transfer token
# In:  htdf1yc8xyy47j3ysq5dzwlhd48mtueg0vrhz4e0e82,100000
# Out: 
transfer.one.htdf:
	@echo ${HTDF_DISTR_KEY}
	@read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import transfer; transfer(hrp='htdf',\
	 											  fromprivkey='${HTDF_DISTR_KEY}',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${HTDF_REST_SERVER}',\
												  chainid='${HTDF_CHAIN_ID}',\
												  gaswanted=${HTDF_DEFAULT_TX_GAS},\
												  gasprice=${HTDF_DEFAULT_TX_FEE})";

transfer.one.hrc20:
	@echo ${HTDF_DISTR_KEY}
	@read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import transfer_hrc20; transfer_hrc20(hrp='htdf',\
	 											  contractaddr='htdf1nkkc48lfchy92ahg50akj2384v4yfqpm4hsq6y',\
	 											  fromprivkey='${HTDF_DISTR_KEY}',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${HTDF_REST_SERVER}',\
												  chainid='${HTDF_CHAIN_ID}',\
												  gaswanted=${HRC_DEFAULT_TX_GAS},\
												  gasprice=${HTDF_DEFAULT_TX_FEE})";

run.contract.htdf:
	@echo ${HTDF_DISTR_KEY}
	@read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 read -p "Type Data: " data; \
	 python -c "from tx import transfer; transfer(hrp='htdf',\
	 											  fromprivkey='${HTDF_DISTR_KEY}',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${HTDF_REST_SERVER}',\
												  chainid='${HTDF_CHAIN_ID}',\
												  gaswanted=${HTDF_DEFAULT_TX_GAS},\
												  gasprice=${HTDF_DEFAULT_TX_FEE},\
												  data='$$data')";

# multiple transactions from one account
# into a block
transfer.one.htdf.test:
	@echo ${HTDF_DISTR_KEY}
	@read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import test_transfer; test_transfer(hrp='htdf',\
															fromprivkey='${HTDF_DISTR_KEY}',\
															toaddr='$$toaddr',\
															namount=$$amount,\
															restapi='${HTDF_REST_SERVER}',\
															chainid='${HTDF_CHAIN_ID}',\
															gaswanted=${HTDF_DEFAULT_TX_GAS},\
															gasprice=${HTDF_DEFAULT_TX_FEE})";

transfer.two.htdf:
	@read -p "Type From Private Key: " fromprivkey; \
	 read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import transfer; transfer(hrp='htdf',\
	 											  fromprivkey='$$fromprivkey',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${HTDF_REST_SERVER}',\
												  chainid='${HTDF_CHAIN_ID}',\
												  gaswanted=${HTDF_DEFAULT_TX_GAS},\
												  gasprice=${HTDF_DEFAULT_TX_FEE})";

transfer.one.usdp:
	@echo ${USDP_DISTR_KEY}
	@read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import transfer; transfer(hrp='usdp',\
	 											  fromprivkey='${USDP_DISTR_KEY}',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${USDP_REST_SERVER}',\
												  chainid='${USDP_CHAIN_ID}',\
												  gaswanted=${USDP_DEFAULT_TX_GAS},\
												  gasprice=${USDP_DEFAULT_TX_FEE})";

transfer.two.usdp:
	@read -p "Type From Private Key: " fromprivkey; \
	 read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import transfer; transfer(hrp='usdp',\
	 											  fromprivkey='$$fromprivkey',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${USDP_REST_SERVER}',\
												  chainid='${USDP_CHAIN_ID}',\
												  gaswanted=${USDP_DEFAULT_TX_GAS},\
												  gasprice=${USDP_DEFAULT_TX_FEE})";

transfer.multi.htdf:
	@python -c "from tx import transferMulti; transferMulti(hrp='htdf',\
	 											  fromprivkey='b948544b053ebfac33f21f2a7a9e1bb8dc5e78c1bf3d6b0f5b6eaed94ea49797',\
												  txlistfile='./db/txs/tx.list',\
												  restapi='39.108.251.132:1317',\
												  chainid='testchain',\
												  gaswanted=30000,\
												  gasprice=100)";
# check account
chkacc.one.htdf:
	@read -p "Type htdf address: " addr; \
	 python -c "from tx import accountinfo; print accountinfo('$$addr','${HTDF_REST_SERVER}')"

chkacc.one.hrc20:
	@read -p "Type contract address: " contractaddr; \
	 read -p "Type htdf address: " addr; \
	 querydata=$$(python -c "from tx import queryGetBalance; print queryGetBalance('$$addr')");\
	 curl -X GET "http://${HTDF_REST_SERVER}/hs/contract/$$contractaddr/$$querydata" -H "accept: application/json"

chkacc.one.usdp:
	@read -p "Type usdp address: " addr; \
	 python -c "from tx import accountinfo; print accountinfo('$$addr','${USDP_REST_SERVER}')"

chkacc.multi.htdf:
	@python -c "from tx import chkaccMulti; chkaccMulti('db/txs/acnts.list','39.108.251.132:1317')"


compare.multi:
	@python -c "from tx import compareBalances; compareBalances()"
# generate random key
genkey.one.usdp:
	@python -c "from key import genkey; print genkey('usdp')"
genkey.one.htdf:
	@python -c "from key import genkey; print genkey('htdf')"
# generate key with keystring
genkey.key.usdp:
	@read -p "Type KeyString: " keystring; \
	 python -c "from key import genkey; print genkey('usdp','$$keystring')"
genkey.key.htdf:
	@read -p "Type KeyString: " keystring; \
	 python -c "from key import genkey; print genkey('htdf','$$keystring')"
# 2020-03-19
genkey.keys.htdf:
	@read -p "Type KeyString: " keystring; \
	 python -c "from key import genkey; keys=[genkey('htdf','$$keystring%d'%i)[0] for i in range(8)]; print '\n'.join(keys)"

recover.keys:
	@read -p "Type KeyString: " keystring; \
	 for index in  $$(python -c "print ' '.join(str(item) for item in range(1,8))"); do \
	 privkey=$$(python -c "from key import genkey; print genkey('htdf','$$keystring$$index')[0]");\
	 echo $$privkey;\
	 ansible $$keystring$$index -m shell -a "hscli accounts recover $$privkey 123456789";\
	 done;

# convert
privkey2addr.htdf:
	@read -p "Type htdf privkey: " privkey; \
	 python -c "from key import privkey2addr; print privkey2addr('$$privkey',hrp='htdf')"
privkey2addr.usdp:
	@read -p "Type usdp privkey: " privkey; \
	 python -c "from key import privkey2addr; print privkey2addr('$$privkey',hrp='usdp')"

#  $$$$$
# {~ | ~} 
#    _		>>>	Simulation
# generate
ACC_COUNT = 100#10000
genkey2db.multi.htdf:
	@python -c "from key import genkeys; genkeys('htdf',${ACC_COUNT},'${HTDF_DB_KEY}')";
genkey2db.multi.usdp:
	@python -c "from key import genkeys; genkeys('usdp',${ACC_COUNT},'${USDP_DB_KEY}')";

airdrop.input.data:
	@addrs=$$(python -c "print hex(${ACC_COUNT})");\
	 values=$$(python -c "print hex(${ACC_COUNT})");\
	 for index in  $$(python -c "print ' '.join(str(item) for item in range(${ACC_COUNT}))"); do \
	 addr=$$(python -c "from key import genkey; print genkey('htdf','$$keystring$$index')[2]");\
	 value=$$(python -c "import random; print random.randint(100000,10000000)");\
	 echo $$addr;\
	 done;	

chkacc.all.htdf:
	# @python -c "from tx import accountinfo; print accountinfo('${HTDF_DISTR_ADDR}','${HTDF_REST_SERVER}')"
	@python -c "from tx import accountinfo; print accountinfo('${HTDF_GOV_ADDR}','${HTDF_REST_SERVER}')"
	@python -c "from accu import report; report(privkeyfile='${HTDF_DB_KEY}',restapi='${HTDF_REST_SERVER}')";
# ACC_INDEX = $$(python -c "print ' '.join(str(item) for item in range(${ACC_COUNT}))")
# chkacc.all.htdf.old:
# @for index in ${ACC_INDEX}; do \
#  addr=$$(row $$index ${HTDF_DB_KEY} 1|column 2); \
#  python -c "from multiprocessing import Process;from tx import accountinfo;\
#  			Process(target=accountinfo,args=('$$addr','${HTDF_REST_SERVER}',True)).start();"; done

chkacc.all.usdp:
	# @python -c "from tx import accountinfo; print accountinfo('${USDP_DISTR_ADDR}','${USDP_REST_SERVER}')"
	@python -c "from tx import accountinfo; print accountinfo('${USDP_GOV_ADDR}','${USDP_REST_SERVER}')"
	@python -c "from accu import report; report(privkeyfile='${USDP_DB_KEY}',restapi='${USDP_REST_SERVER}')";
# chkacc.all.usdp.old:
# @for index in ${ACC_INDEX}; do \
#  addr=$$(row $$index ${USDP_DB_KEY} 1|column 2); \
#  python -c "import threading;from tx import accountinfo;\
# 			threading.Thread(target=accountinfo,args=('$$addr','${USDP_REST_SERVER}',True)).start();"; done

# distribution
distr.htdf:
	@python -c "from distr import distr; distr(fromprivkey='${HTDF_DISTR_KEY}',\
											  hrp='htdf',\
											  privkeyfile='${HTDF_DB_KEY}',\
											  restapi='${HTDF_REST_SERVER}',\
											  chainid='${HTDF_CHAIN_ID}',\
											  ndefault_gas=${HTDF_DEFAULT_TX_GAS},\
											  ndefault_fee=${HTDF_DEFAULT_TX_FEE})";

distr.hrc20:
	@python -c "from distr import distr_erc20; distr_erc20(fromprivkey='${HTDF_DISTR_KEY}',\
											  contractaddr='htdf12dvguqedrvgfrdl35hcgfmz4fz6rm6chrvf96g',\
											  hrp='htdf',\
											  privkeyfile='${HTDF_DB_KEY}',\
											  restapi='${HTDF_REST_SERVER}',\
											  chainid='${HTDF_CHAIN_ID}',\
											  ndefault_gas=${HRC_DEFAULT_TX_GAS},\
											  ndefault_fee=${HTDF_DEFAULT_TX_FEE})";
DISTR_AMOUNT = 1000000
distr.usdp:
	@python -c "from distr import distr; distr(fromprivkey='${USDP_DISTR_KEY}',\
											  hrp='usdp',\
											  privkeyfile='${USDP_DB_KEY}',\
											  restapi='${USDP_REST_SERVER}',\
											  chainid='${USDP_CHAIN_ID}',\
											  ndefault_gas=${USDP_DEFAULT_TX_GAS},\
											  ndefault_fee=${USDP_DEFAULT_TX_FEE},\
											  nAmount=${DISTR_AMOUNT})";

distr.usdp.count:
	@python -c "from distr import count; count(privkeyfile='${USDP_DB_KEY}',\
											   restapi='${USDP_REST_SERVER}',\
											   debug=True)";

distr.htdf.count:
	@python -c "from distr import count; count(privkeyfile='${HTDF_DB_KEY}',\
											   restapi='${HTDF_REST_SERVER}',
											   debug=True)";

distrex.usdp:
	@python -c "from distr import distrex;  distrex(hrp='usdp',\
											  	    privkeyfile='${USDP_DB_KEY}',\
											  		restapi='${USDP_REST_SERVER}',\
											  		chainid='${USDP_CHAIN_ID}',\
											  		ndefault_gas=${USDP_DEFAULT_TX_GAS},\
											  		ndefault_fee=${USDP_DEFAULT_TX_FEE})";

distrex.htdf:
	@python -c "from distr import distrex;  distrex(hrp='htdf',\
											  	    privkeyfile='${HTDF_DB_KEY}',\
											  		restapi='${HTDF_REST_SERVER}',\
											  		chainid='${HTDF_CHAIN_ID}',\
											  		ndefault_gas=${HTDF_DEFAULT_TX_GAS},\
											  		ndefault_fee=${HTDF_DEFAULT_TX_FEE})";

flood.htdf:
	@python -c "from flood import flood;  flood(hrp='htdf',\
											  	privkeyfile='${HTDF_DB_KEY}',\
											  	restapi='${HTDF_REST_SERVER}',\
											  	chainid='${HTDF_CHAIN_ID}',\
											  	ndefault_gas=${HTDF_DEFAULT_TX_GAS},\
											  	ndefault_fee=${HTDF_DEFAULT_TX_FEE})";

flood.usdp:
	@python -c "from flood import flood;  flood(hrp='usdp',\
											  	privkeyfile='${USDP_DB_KEY}',\
											  	restapi='${USDP_REST_SERVER}',\
											  	chainid='${USDP_CHAIN_ID}',\
											  	ndefault_gas=${USDP_DEFAULT_TX_GAS},\
											  	ndefault_fee=${USDP_DEFAULT_TX_FEE})";
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
.PHONY: chkacc.all.htdf chkacc.all.usdp
