'''
This module get information from blockchain using toncenter api
'''
import requests
import json
import time
import db


MAINNET_API_BASE = "https://toncenter.com/api/v2/"
TESTNET_API_BASE = "https://testnet.toncenter.com/api/v2/"

with open('config.json', 'r') as f:
    config_json = json.load(f)
    MAINNET_API_TOKEN = config_json['MAINNET_API_TOKEN']
    TESTNET_API_TOKEN = config_json['TESTNET_API_TOKEN']
    MAINNET_WALLET = config_json['MAINNET_WALLET']
    TESTNET_WALLET = config_json['TESTNET_WALLET']
    WORK_MODE = config_json['WORK_MODE']

if WORK_MODE == "mainnet":
    API_BASE = MAINNET_API_BASE
    API_TOKEN = MAINNET_API_TOKEN
    WALLET = MAINNET_WALLET
else:
    API_BASE = TESTNET_API_BASE
    API_TOKEN = TESTNET_API_TOKEN
    WALLET = TESTNET_WALLET


def detect_address(address):
    '''
    Detect address
    '''

    url = f"{API_BASE}detectAddress?address={address}&api_key={API_TOKEN}"
    r = requests.get(url)
    response = json.loads(r.text)
    try:
        return response['result']['bounceable']['b64url']
    except:
        return False


def get_address_information(address):
    '''
    Get information about address
    '''

    url = f"{API_BASE}getAddressInformation?address={address}&api_key={API_TOKEN}"
    r = requests.get(url)
    response = json.loads(r.text)
    return response


def get_address_transactions():
    '''
    Get transactions for address
    '''

    url = f"{API_BASE}getTransactions?address={WALLET}&limit=30&archival=true&api_key={API_TOKEN}"
    r = requests.get(url)
    response = json.loads(r.text)
    return response['result']


def find_transaction(user_wallet, value, comment):
    '''
    Find transaction by user wallet, value and comment
    '''

    transactions = get_address_transactions()
    for transaction in transactions:
        msg = transaction['in_msg']
        if msg['source'] == user_wallet and msg['value'] == value and msg['message'] == comment:
            t = db.check_transaction(msg['body_hash'])
            if t == False:
                db.add_v_transaction(
                    msg['source'], msg['body_hash'], msg['value'], msg['message'])
                print("find transaction")
                print(
                    f"transaction from: {msg['source']} \nValue: {msg['value']} \nComment: {msg['message']}")
                return True
            else:
                pass
    return False
