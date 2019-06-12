# Accumulator Guider Guide
## Available Commands
    make accu.htdf
    make chkacc.all.htdf
## Accumulate
When some variables need to change, you could edit Makefile and modify the corresponding parts.
#### 1. to set privatekey db files
        DB_HTDF = $(DB_DIR)/htdf.privkey
#### 2. to set a summingup address.
        GOV_ACC_ADDR_HTDF = htdf1aax569cs769m33yuss5kqzuxh7ylvjyuv3epk3
#### 3. to set blockchain environment variables.
        CHAIN_ID = testchain
        DEFAULT_TX_GAS = 200000
        DEFAULT_TX_FEE = 20
        REST_IP_PORT_HTDF = 47.98.194.7:1317
#### 4. to trigger the accumulator.
        make accu.htdf
## Check Account
    make chkacc.all.htdf