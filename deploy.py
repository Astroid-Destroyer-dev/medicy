import json
import os
from pathlib import Path

from solcx import compile_standard, install_solc
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.environ.get('RPC_URL')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
CHAIN_ID = int(os.environ.get('CHAIN_ID', '11155111'))

HERE = Path(__file__).parent
CONTRACT_SOURCE = (HERE / 'LogStore.sol').read_text()

def compile_contract():
    install_solc('0.8.19')
    compiled = compile_standard({
        'language': 'Solidity',
        'sources': {'LogStore.sol': {'content': CONTRACT_SOURCE}},
        'settings': {
            'outputSelection': {'*': {'*': ['abi', 'evm.bytecode.object']}}
        }
    }, solc_version='0.8.19')
    contract_data = compiled['contracts']['LogStore.sol']['LogStore']
    abi = contract_data['abi']
    bytecode = contract_data['evm']['bytecode']['object']
    # write ABI to file for client usage
    (HERE / 'LogStore.abi.json').write_text(json.dumps(abi))
    return abi, bytecode

def deploy():
    if not RPC_URL or not PRIVATE_KEY:
        raise SystemExit('RPC_URL and PRIVATE_KEY must be set in env')

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    abi, bytecode = compile_contract()
    acct = w3.eth.account.from_key(PRIVATE_KEY)

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(acct.address)

    tx = contract.constructor().build_transaction({
        'from': acct.address,
        'nonce': nonce,
        'chainId': CHAIN_ID,
        'gas': 6_000_000,
        'gasPrice': w3.eth.gas_price,
    })

    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print('Deploy tx sent:', tx_hash.hex())
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print('Contract deployed at:', receipt.contractAddress)
    return receipt.contractAddress, abi

if __name__ == '__main__':
    addr, abi = deploy()
    print(addr)
