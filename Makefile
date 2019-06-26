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
HTDF_CONFIG_FILE = $(CURDIR)/config/1000/htdf.json
USDP_CONFIG_FILE = $(CURDIR)/config/1000/usdp.json
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
	@read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import transfer; transfer(hrp='htdf',\
	 											  fromprivkey='${HTDF_GOV_KEY}',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${HTDF_REST_SERVER}',\
												  chainid='${HTDF_CHAIN_ID}',\
												  ngas=${HTDF_DEFAULT_TX_GAS},\
												  nfee=${HTDF_DEFAULT_TX_FEE})";

transfer.one.usdp:
	@read -p "Type Toaddress: " toaddr; \
	 read -p "Type Amount: " amount; \
	 python -c "from tx import transfer; transfer(hrp='usdp',\
	 											  fromprivkey='${DISTR_ACC_PRIVKEY_USDP}',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${USDP_REST_SERVER}',\
												  chainid='${USDP_CHAIN_ID}',\
												  ngas=${USDP_DEFAULT_TX_GAS},\
												  nfee=${USDP_DEFAULT_TX_FEE})";
# check account
chkacc.one.htdf:
	@read -p "Type htdf address: " addr; \
	 python -c "from tx import accountinfo; print accountinfo('$$addr','${HTDF_REST_SERVER}')"
chkacc.one.usdp:
	@read -p "Type usdp address: " addr; \
	 python -c "from tx import accountinfo; print accountinfo('$$addr','${USDP_REST_SERVER}')"

# generate random key
genkey.one.usdp:
	@python -c "from key import genkey; print genkey('usdp')"
genkey.one.htdf:
	@python -c "from key import genkey; print genkey('htdf')"

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
ACC_COUNT = 1000#10000
genkey2db.multi.htdf:
	@if ! [ -d "${DB_DIR}" ]; then mkdir ${DB_DIR}; fi
	@python -c "from key import genkeys; genkeys('htdf',${ACC_COUNT},'${HTDF_DB_KEY}')";
genkey2db.multi.usdp:
	@if ! [ -d "${DB_DIR}" ]; then mkdir ${DB_DIR}; fi
	@python -c "from key import genkeys; genkeys('usdp',${ACC_COUNT},'${USDP_DB_KEY}')";


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
