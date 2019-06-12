# written by junying, 2019-06-10
# accumulate small accounts balance into one.
#######################################################################################################################
## database file ######################################################################################################
## htdf	htdf1yc8xyy47j3ysq5dzwlhd48mtueg0vrhz4e0e82	725f8dce588fd7c5e485a4d37e1236f5fdbbf51754187f253ef947f09e4e6d98 ##
#######################################################################################################################
CHAIN_ID = testchain
DEFAULT_TX_GAS = 200000
DEFAULT_TX_FEE = 20

DB_DIR_ACCU = $(CURDIR)/db/accu
DB_DIR_DISTR = $(CURDIR)/db/distr
DB_DIR = $(DB_DIR_ACCU)
# [htdf]
REST_IP_PORT_HTDF = 47.98.194.7:1317
DB_HTDF = $(DB_DIR)/htdf.privkey
GOV_ACC_PRIVKEY_HTDF = d3a29ac68982125f46421e2c06be95b151f3a94ca02a9edcde1d8179c0750d10
GOV_ACC_ADDR_HTDF = htdf1aax569cs769m33yuss5kqzuxh7ylvjyuv3epk3
DISTR_ACC_PRIVKEY_HTDF= c9960987611a40cac259f2c989c43a79754df356415f164ad3080fdc10731e65
DISTR_ACC_ADDR_HTDF = htdf12sc78p9nr9s8qj06e2tqfqhlwlx0ncuq8l9gsh
# [usdp]
REST_IP_PORT_USDP = 39.106.90.41:1317
DB_USDP = $(DB_DIR)/usdp.privkey
GOV_ACC_PRIVKEY_USDP = 28fb2d33f42c29031ea5820951d89070dc1f2631bb92e49cf9dda9b48a164d48
GOV_ACC_ADDR_USDP = usdp1vwhmsa58xd5ehymexedlmrmcyje0wmsdtf30ly
DISTR_ACC_PRIVKEY_USDP= 28fb2d33f42c29031ea5820951d89070dc1f2631bb92e49cf9dda9b48a164d48
DISTR_ACC_ADDR_USDP = usdp1vwhmsa58xd5ehymexedlmrmcyje0wmsdtf30ly
#+ &&&&& 
#+{@ | @}
#++  _  +	>>>	Main
# accumulate 
accu.htdf:
	@python -c "from accu import accumulate; accumulate(toaddr='${GOV_ACC_ADDR_HTDF}',\
														privkeyfile='${DB_HTDF}',\
														restapi='${REST_IP_PORT_HTDF}',\
														chainid='${CHAIN_ID}',\
														ndefault_gas=${DEFAULT_TX_GAS},\
														ndefault_fee=${DEFAULT_TX_FEE})";
ACCU_AMOUNT = 10000#satoshi, defautl:None
accu.usdp:
	@python -c "from accu import accumulate; accumulate(toaddr='${GOV_ACC_ADDR_USDP}',\
														privkeyfile='${DB_USDP}',\
														restapi='${REST_IP_PORT_USDP}',\
														chainid='${CHAIN_ID}',\
														ndefault_gas=${DEFAULT_TX_GAS},\
														ndefault_fee=${DEFAULT_TX_FEE},\
														nAmount=${ACCU_AMOUNT})";

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
	 											  fromprivkey='${GOV_ACC_PRIVKEY_HTDF}',\
												  toaddr='$$toaddr',\
												  namount=$$amount,\
												  restapi='${REST_IP_PORT_HTDF}',\
												  chainid='${CHAIN_ID}',\
												  ngas=${DEFAULT_TX_GAS},\
												  nfee=${DEFAULT_TX_FEE})";
# check account
chkacc.one.htdf:
	@read -p "Type htdf address: " addr; \
	 python -c "from tx import accountinfo; print accountinfo('$$addr','${REST_IP_PORT_HTDF}')"
chkacc.one.usdp:
	@read -p "Type usdp address: " addr; \
	 python -c "from tx import accountinfo; print accountinfo('$$addr','${REST_IP_PORT_USDP}')"

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
ACC_COUNT = 10000
genkey2db.multi.htdf:
	@if ! [ -d "${DB_DIR}" ]; then mkdir ${DB_DIR}; fi
	@python -c "from key import genkeys; genkeys('htdf',${ACC_COUNT},'${DB_HTDF}')";
genkey2db.multi.usdp:
	@if ! [ -d "${DB_DIR}" ]; then mkdir ${DB_DIR}; fi
	@python -c "from key import genkeys; genkeys('usdp',${ACC_COUNT},'${DB_USDP}')";


chkacc.all.htdf:
	@python -c "from tx import accountinfo; print accountinfo('${DISTR_ACC_ADDR_HTDF}')"
	@python -c "from tx import accountinfo; print accountinfo('${GOV_ACC_ADDR_HTDF}')"
	@python -c "from accu import report; report(privkeyfile='${DB_HTDF}')";

# ACC_INDEX = $$(python -c "print ' '.join(str(item) for item in range(${ACC_COUNT}))")
# chkacc.all.htdf.old:
# @for index in ${ACC_INDEX}; do \
#  addr=$$(row $$index ${DB_HTDF} 1|column 2); \
#  python -c "from multiprocessing import Process;from tx import accountinfo;\
#  			Process(target=accountinfo,args=('$$addr','${REST_IP_PORT_HTDF}',True)).start();"; done

chkacc.all.usdp:
	@python -c "from tx import accountinfo; print accountinfo('${DISTR_ACC_ADDR_USDP}','${REST_IP_PORT_USDP}')"
	@python -c "from tx import accountinfo; print accountinfo('${GOV_ACC_ADDR_USDP}','${REST_IP_PORT_USDP}')"
	@python -c "from accu import report; report(privkeyfile='${DB_USDP}')";
# chkacc.all.usdp.old:
# @for index in ${ACC_INDEX}; do \
#  addr=$$(row $$index ${DB_USDP} 1|column 2); \
#  python -c "import threading;from tx import accountinfo;\
# 			threading.Thread(target=accountinfo,args=('$$addr','${REST_IP_PORT_USDP}',True)).start();"; done

# distribution
distr.htdf:
	@python -c "from distr import distr; distr(fromprivkey='${DISTR_ACC_PRIVKEY_HTDF}',\
											  hrp='htdf',\
											  privkeyfile='${DB_HTDF}',\
											  restapi='${REST_IP_PORT_HTDF}',\
											  chainid='${CHAIN_ID}',\
											  ndefault_gas=${DEFAULT_TX_GAS},\
											  ndefault_fee=${DEFAULT_TX_FEE})";
DISTR_AMOUNT = 1000000
distr.usdp:
	@python -c "from distr import distr; distr(fromprivkey='${DISTR_ACC_PRIVKEY_USDP}',\
											  hrp='htdf',\
											  privkeyfile='${DB_USDP}',\
											  restapi='${REST_IP_PORT_USDP}',\
											  chainid='${CHAIN_ID}',\
											  ndefault_gas=${DEFAULT_TX_GAS},\
											  ndefault_fee=${DEFAULT_TX_FEE},\
											  nAmount=${DISTR_AMOUNT})";
#  %%%%%
# {^ | ^} 
#    _		>>>	Maid
# clean
clean:
	@find -name "*.pyc" -exec rm -f {} \;
	@find -name __pycache__ | xargs rm -rf
	@find -name .pytest_cache | xargs rm -rf

tar: clean
	@tar cf ../accu.tar.gz *
.PHONY: chkacc.all.htdf chkacc.all.usdp