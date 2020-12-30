#!/usr/bin/env python
import json

import boto3
from web3 import Web3

import config

OSM_CONTRACT_ADDRESS = '0x81FE72B5A8d1A857d176C3E7d5Bd2679A9B85763'
POSITION_CUR = 3
POSITION_NXT = 4

YEARN_3CRV = '0x9cA85572E6A3EbF24dEDd195623F188735A5179f'
YEARN_3CRV_STRAT = '0xC59601F0CC49baa266891b7fc63d2D5FE097A79D'


def main():
    w3 = Web3(Web3.HTTPProvider(config.LOCAL_ETH_NODE))

    if not w3.isConnected():
        print("Could not connect to local node")
        w3 = Web3(Web3.HTTPProvider(
            'https://mainnet.infura.io/v3/' + config.INFURA_ACCOUNT))

    if not w3 or not w3.isConnected():
        print('Could not connect to Infura')
        msg = 'Could not check OSM ETH price'
        print(msg)
        sendAlert(msg)
        exit(1)

    if config.YEARN_3POOL_WITHDRAW_THRESHOLD:
        withdraw3pool(w3)

    if config.OSM_NEXT_ALERT_THRESHOLD:
        osmNext(w3)


def withdraw3pool(w3):
    with open('abi/yVault.json') as json_file:
        abi = json.load(json_file)
        yVault = w3.eth.contract(
            address=YEARN_3CRV,
            abi=abi,
        )
        vaultBalance = w3.fromWei(yVault.functions.balance().call(), 'ether')

    with open('abi/StrategyCurve3CrvVoterProxy.json') as json_file:
        abi = json.load(json_file)
        yVaultStrat = w3.eth.contract(
            address=YEARN_3CRV_STRAT,
            abi=abi,
        )
        stratBalance = w3.fromWei(
            yVaultStrat.functions.balanceOfPool().call(), 'ether')

    availableWithdraw = vaultBalance-stratBalance
    msg = f"3pool Vault balance: {vaultBalance}. Strat balance: {stratBalance}. Available: {availableWithdraw}."
    print(msg)
    if availableWithdraw > config.YEARN_3POOL_WITHDRAW_THRESHOLD:
        sendAlert(msg)


def osmNext(w3):
    curPrice = readPrice(w3, POSITION_CUR)
    nxtPrice = readPrice(w3, POSITION_NXT)
    msg = f"Current price: {curPrice}. Next price: {nxtPrice}."
    print(msg)

    if curPrice <= config.OSM_NEXT_ALERT_THRESHOLD or nxtPrice <= config.OSM_NEXT_ALERT_THRESHOLD:
        sendAlert(msg)


def readPrice(w3, storagePosition):
    price = w3.eth.getStorageAt(OSM_CONTRACT_ADDRESS, storagePosition)
    return w3.fromWei(w3.toInt(price[16:]), 'ether')


def sendAlert(msg):
    if config.AWS_ACCESS_KEY_ID:
        snsClient = boto3.client(
            'sns',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
    else:
        session = boto3.Session(profile_name=config.AWS_PROFILE_NAME)
        snsClient = session.client('sns')

    snsClient.publish(
        TopicArn=config.ALERT_TOPIC_ARN,
        Message=f"Please alert Mathew: {msg}"
    )


if __name__ == "__main__":
    main()
