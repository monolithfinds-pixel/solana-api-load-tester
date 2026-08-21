import os
import json
import time
import base64
import requests
from solders.keypair import Keypair
from solders.system_program import TransferParams, transfer
from solders.message import Message
from solders.transaction import Transaction
from solders.hash import Hash

# 1. Load Private Key from GitHub Secrets
key_str = os.environ.get("SOL_PRIVATE_KEY")
if key_str.startswith('['):
    key_bytes = bytes(json.loads(key_str))
else:
    key_bytes = key_str.encode()

kp = Keypair.from_bytes(key_bytes)
pubkey = kp.pubkey()
RPC_URL = "https://api.devnet.solana.com"

def rpc_call(method, params=None):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params: payload["params"] = params
    r = requests.post(RPC_URL, json=payload)
    return r.json()

# 2. Claim Free SOL
print(f"Connected to Devnet. Wallet: {pubkey}")
print("Requesting Airdrop 1 SOL...")
rpc_call("requestAirdrop", [str(pubkey), 1000000000])
time.sleep(10)

# 3. Check Balance
resp = rpc_call("getBalance", [str(pubkey)])
balance = resp.get("result", {}).get("value", 0)
print(f"Current Balance: {balance / 1000000000} SOL")

# 4. Farm Volume
print("Starting API Load Test (Volume Farm)...")
for i in range(30):
    try:
        # Get latest blockhash
        bh_resp = rpc_call("getLatestBlockhash")
        blockhash_str = bh_resp["result"]["value"]["blockhash"]
        blockhash = Hash.from_string(blockhash_str)
        
        # Create transfer instruction (send 0.001 SOL to self)
        ix = transfer(TransferParams(from_pubkey=pubkey, to_pubkey=pubkey, lamports=1000000))
        
        # Create message and transaction
        msg = Message.new_with_blockhash([ix], pubkey, blockhash)
        tx = Transaction.new([kp], msg, blockhash)
        
        # Serialize and send
        tx_b64 = base64.b64encode(bytes(tx)).decode("utf-8")
        send_resp = rpc_call("sendTransaction", [tx_b64, {"encoding": "base64"}])
        print(f"Transaction {i+1}/30 sent! Hash: {send_resp.get('result')}")
    except Exception as e:
        print(f"Transaction {i+1}/30 failed: {e}")
    time.sleep(3)

print("Load test complete.")
