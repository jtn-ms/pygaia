import os
from decimal import Decimal

def getitems(filepath):
    if not os.path.exists(filepath): return []
    items = []
    with open(filepath,'r') as file:
        for line in file: items.append(line.split())
    return items


def write_log(logMessage):
    with open('./log/log.txt', mode='a') as filename:
        filename.write('%s\n' % logMessage)


if __name__ == '__main__':
    for item in getitems("./db/txs/tx.list"):
        # print(item)
        toAddr = item[0]
        decAmount =  Decimal(item[1])
        satoshiAmount = decAmount * (10**8)
        print("toAddr=%s|satoshiAmount=%d" %( toAddr,satoshiAmount))
        write_log("toAddr=%s|satoshiAmount=%d" %( toAddr,satoshiAmount))
