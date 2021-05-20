# User Guide
## Available Modes
    Accumulator: DB_DIR=$(DB_DIR_ACCU)
    Distributor: DB_DIR=$(DB_DIR_DISTR)

## Available Commands
#### sscq
    make accu.sscq
    make chkacc.all.sscq
    make distr.sscq
    make flood.sscq
#### usdp
## Accumulate
When some variables need to change, you could edit Makefile and modify the corresponding parts.
#### 1. to set privatekey db files
    DB_DIR = $(CURDIR)/db
    DB_SSCQ = $(DB_DIR)/sscq.privkey
#### 2. to set a summingup address.
    GOV_ACC_ADDR_SSCQ = sscq1aax569cs769m33yuss5kqzuxh7ylvjyuv3epk3
#### 3. to set blockchain environment variables.
    CHAIN_ID = testchain
    DEFAULT_TX_GAS = 200000
    DEFAULT_TX_FEE = 20
    REST_IP_PORT_SSCQ = 47.98.194.7:1317
#### 4. to trigger the accumulator.
    make accu.sscq

## Check Account
    make chkacc.all.sscq

## Distribute
#### 1. to set variables
    DB_DIR = $(DB_DIR_DISTR)
#### 2. to distribute
    make distr.sscq

## Generate DataBase
#### 1. set variables
    DB_DIR = $(DB_DIR_DISTR) or $(DB_DIR_ACCU)
    ACC_COUNT = 10
#### 2. to generate dbs
    make genkey2db.multi.sscq

## Characteristics
   - multiprocessing over threading
