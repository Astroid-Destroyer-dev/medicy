import os
from pathlib import Path
from typing import Any, Dict

from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.environ.get('RPC_URL')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
CHAIN_ID = int(os.environ.get('CHAIN_ID', '11155111'))

HERE = Path(__file__).parent

def get_w3():
    if not RPC_URL:
        raise SystemExit('RPC_URL not set')
    return Web3(Web3.HTTPProvider(RPC_URL))

def load_abi(abi_path: str):
    p = HERE / abi_path
    return p.read_text()

def get_contract(w3: Web3, abi: Any, address: str):
    return w3.eth.contract(address=address, abi=abi)
