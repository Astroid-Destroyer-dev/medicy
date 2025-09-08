import os
import json
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

RPC_URL = os.getenv('RPC_URL')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')

if not RPC_URL or not CONTRACT_ADDRESS:
    raise SystemExit('RPC_URL and CONTRACT_ADDRESS must be set in .env')

ABI_PATH = os.path.join(os.path.dirname(__file__), 'LogStore.abi.json')
with open(ABI_PATH, 'r') as f:
    ABI = json.load(f)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise SystemExit('RPC connection failed')

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

def main():
    count = contract.functions.count().call()
    print('Log count:', count)
    for i in range(count):
        res = contract.functions.getLog(i).call()
        # support older contract (sender, timestamp, message) and newer (7-field) shape
        if isinstance(res, (list, tuple)):
            if len(res) == 3:
                sender, timestamp, message = res
                print(f'[{i}] sender={sender} timestamp={timestamp} message="{message}"')
            elif len(res) == 7:
                sender, blockTimestamp, doctorName, reason, patientId, logTime, message = res
                print(f'[{i}] sender={sender} blockTimestamp={blockTimestamp} doctorName="{doctorName}" reason="{reason}" patientId="{patientId}" logTime={logTime} message="{message}"')
            else:
                print(f'[{i}] unexpected return shape ({len(res)}): {res}')
        else:
            print(f'[{i}] unexpected single return: {res}')

if __name__ == '__main__':
    main()
