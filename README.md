# LogStore blockchain integration

This folder contains a simple Solidity contract `LogStore.sol` and Python tools to compile, deploy, and interact with it via Web3 and a FastAPI wrapper.

Files added:
- `LogStore.sol` - Solidity contract storing logs
- `deploy.py` - compile & deploy to testnet
- `send_log.py` - sign & send addLog transactions
- `app.py` - FastAPI app exposing endpoints (needs `CONTRACT_ADDRESS` set)
- `requirements.txt` - Python dependencies
- `.env.example` - example env variables

Quick start (PowerShell):

1. Create virtual env and install:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Copy `.env.example` -> `.env` and fill `RPC_URL` and `PRIVATE_KEY`. For Sepolia use Infura or Alchemy RPC.

3. Deploy contract:

```powershell
python deploy.py
```

This prints the deployed address. Save it to `.env` as `CONTRACT_ADDRESS` and also writes ABI file manually if needed.

4. Run FastAPI server:

```powershell
$env:CONTRACT_ADDRESS="0x..."; uvicorn app:app --reload
```

5. Send a log via script:

```powershell
python send_log.py "Test message"
```

Notes:
- Keep your private key secret. For production use a secure signer or a wallet.
- ABI is expected at `LogStore.abi.json` after compile; deploy.py prints ABI and address.
