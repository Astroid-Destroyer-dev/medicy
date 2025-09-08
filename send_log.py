import os
import json
from pathlib import Path
from typing import Optional

from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.environ.get('RPC_URL')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')

HERE = Path(__file__).parent
ABI = json.loads((HERE / 'LogStore.abi.json').read_text())


def send_log(doctor: str, reason: str, patient_id: str, log_time: int, message: str):
    if not RPC_URL or not PRIVATE_KEY or not CONTRACT_ADDRESS:
        raise SystemExit('Set RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS in env')

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    acct = w3.eth.account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

    nonce = w3.eth.get_transaction_count(acct.address)
    tx = contract.functions.addLog(doctor, reason, patient_id, log_time, message).build_transaction({
        'from': acct.address,
        'nonce': nonce,
        'chainId': int(os.environ.get('CHAIN_ID', '11155111')),
        'gas': 400000,
        'gasPrice': w3.eth.gas_price,
    })

    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print('tx_hash', tx_hash.hex())
    return receipt


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 6:
        print('Usage: python send_log.py <doctor> <reason> <patient_id> <log_time_unix> "message text"')
        raise SystemExit(1)
    doctor = sys.argv[1]
    reason = sys.argv[2]
    patient_id = sys.argv[3]
    log_time = int(sys.argv[4])
    message = sys.argv[5]
    r = send_log(doctor, reason, patient_id, log_time, message)
    print(r)
