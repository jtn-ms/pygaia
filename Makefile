# written by junying, 2019-06-10
# accumulate small accounts balance into one.

# input
PRVKEY_PATH_USDP = $(HOME)/.prvkey/usdp_prvkey.bin
PRVKEY_PATH_HTDF = $(HOME)/.prvkey/htdf_prvkey.bin
##
CHAIN_ID = testchain
DEFAULT_TX_GAS = 200000
DEFAULT_TX_FEE = 20
REST_IP_PORT_USDP = 47.99.81.158:1317
REST_IP_PORT_HTDF = 47.98.194.7:1317

# generate
ACC_COUNT = 10
ACC_INDEX = $$(python -c "print ' '.join(str(item) for item in range(${ACC_COUNT}))")
DB_DIR = $(CURDIR)/db
DB_HTDF = $(DB_DIR)/htdf.privkey
DB_USDP = $(DB_DIR)/usdp.privkey

genacc:
	@if ! [ -d "${DB_DIR}" ]; then mkdir ${DB_DIR}; fi
	@for index in ${ACC_INDEX}; do \
	 python -c "from key import genkeys; genkeys('htdf',10,'${DB_HTDF}')";\
	 python -c "from key import genkeys; genkeys('usdp',10,'${DB_USDP}')";\
	 done

# distribution
DISTR_ACC_HTDF = htdf12sc78p9nr9s8qj06e2tqfqhlwlx0ncuq8l9gsh
distr:
	@python -c "from accu import distr; distr(privkeyfile='${DB_HTDF}')";

# accumulate
GOV_ACC_PRIVKEY_HTDF = d3a29ac68982125f46421e2c06be95b151f3a94ca02a9edcde1d8179c0750d10
GOV_ACC_ADDR_HTDF = htdf1aax569cs769m33yuss5kqzuxh7ylvjyuv3epk3
accu:
	@python -c "from accu import accumulate; accumulate(toaddr='${GOV_ACC_ADDR_HTDF}',privkeyfile='${DB_HTDF}')";

# test
genkey:
	@python -c "from key import genkey; print genkey('usdp')"
	@python -c "from key import genkey; print genkey('htdf')"

chkacc:
	@python -c "from tx import accountinfo; print accountinfo('${DISTR_ACC_HTDF}')"
	@python -c "from tx import accountinfo; print accountinfo('${GOV_ACC_ADDR_HTDF}')"
	@python -c "from accu import report; report(privkeyfile='${DB_HTDF}')";

# clean
clean:
	@find -name "*.pyc" -exec rm -f {} \;
	@find -name __pycache__ | xargs rm -rf
	@find -name .pytest_cache | xargs rm -rf

.PHONY: test


