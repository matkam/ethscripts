import json

from web3.auto.infura import w3

OSM_ADDRESS = '0x81FE72B5A8d1A857d176C3E7d5Bd2679A9B85763'
POSITION_CUR = 3
POSITION_NXT = 4

def lambda_handler(event, context):
  cur = w3.eth.getStorageAt(OSM_ADDRESS, POSITION_CUR)
  currentPrice = w3.fromWei(w3.toInt(cur[16:]), 'ether')
  print(currentPrice)

  nxt = w3.eth.getStorageAt(OSM_ADDRESS, 4)
  nextPrice = w3.fromWei(w3.toInt(nxt[16:]), 'ether')
  print(nextPrice)

  return {
      'statusCode': 500,
      'body': json.dumps(nextPrice)
  }
