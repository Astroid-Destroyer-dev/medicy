import os
import json
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException
from web3 import Web3
from dotenv import load_dotenv
from models.bcmodels import LogIn,LogOut

load_dotenv()

RPC_URL = os.environ.get('RPC_URL')
CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
CHAIN_ID = int(os.environ.get('CHAIN_ID', '11155111'))

HERE = Path(__file__).parent
ABI = json.loads((HERE / 'LogStore.abi.json').read_text())

app = FastAPI(title='LogStore API')

def get_w3():
    if not RPC_URL:
        raise RuntimeError('RPC_URL not set')
    return Web3(Web3.HTTPProvider(RPC_URL))


def get_contract(w3: Web3):
    if not CONTRACT_ADDRESS:
        raise RuntimeError('CONTRACT_ADDRESS not set')
    return w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)


@app.post('/logs', response_model=dict)
def add_log(item: LogIn):
    if not PRIVATE_KEY:
        raise HTTPException(status_code=500, detail="PRIVATE_KEY not configured for server-side signing")
    
    w3 = get_w3()
    contract = get_contract(w3)
    acct = w3.eth.account.from_key(PRIVATE_KEY)
    
    try:
        nonce = w3.eth.get_transaction_count(acct.address)
        tx = contract.functions.addLog(
            item.doctorName, 
            item.reason, 
            item.patientId, 
            item.logTime, 
            item.message
        ).build_transaction({
            'from': acct.address,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'gas': 400000,
            'gasPrice': w3.eth.gas_price,
        })
        
        signed = acct.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'tx_hash': tx_hash.hex(),
            'block_number': receipt.blockNumber,
            'gas_used': receipt.gasUsed,
            'status': 'success'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/logs/{index}', response_model=LogOut)
def get_log(index: int):
    w3 = get_w3()
    contract = get_contract(w3)
    try:
        res = contract.functions.getLog(index).call()
        # Handle both old (3-field) and new (7-field) contract responses
        if len(res) == 7:
            sender, blockTimestamp, doctorName, reason, patientId, logTime, message = res
            return LogOut(
                sender=sender,
                blockTimestamp=blockTimestamp,
                doctorName=doctorName,
                reason=reason,
                patientId=patientId,
                logTime=logTime,
                message=message
            )
        elif len(res) == 3:
            # Old contract format - fill missing fields with defaults
            sender, timestamp, message = res
            return LogOut(
                sender=sender,
                blockTimestamp=timestamp,
                doctorName="",
                reason="",
                patientId="",
                logTime=0,
                message=message
            )
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected contract response format: {len(res)} fields")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get('/logs', response_model=List[LogOut])
def get_all_logs():
    w3 = get_w3()
    contract = get_contract(w3)
    try:
        count = contract.functions.count().call()
        logs = []
        for i in range(count):
            res = contract.functions.getLog(i).call()
            if len(res) == 7:
                sender, blockTimestamp, doctorName, reason, patientId, logTime, message = res
                logs.append(LogOut(
                    sender=sender,
                    blockTimestamp=blockTimestamp,
                    doctorName=doctorName,
                    reason=reason,
                    patientId=patientId,
                    logTime=logTime,
                    message=message
                ))
            elif len(res) == 3:
                sender, timestamp, message = res
                logs.append(LogOut(
                    sender=sender,
                    blockTimestamp=timestamp,
                    doctorName="",
                    reason="",
                    patientId="",
                    logTime=0,
                    message=message
                ))
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/count', response_model=int)
def count_logs():
    w3 = get_w3()
    contract = get_contract(w3)
    return contract.functions.count().call()
