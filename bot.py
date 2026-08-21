import os
import json
import time
import base64
import requests
from solders.keypair import Keypair
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solders.hash import Hash

# 1. Load Private Key
key_str = os.environ.get("SOL_PRIVATE_KEY")
if key_str.startswith('['):
    key_bytes = bytes(json.loads(key_str))
else:
    key_bytes = key_str.encode()

kp = Keypair.from_bytes(key_bytes)
pubkey = kp.pubkey()

# 2. Use VIP Helius RPC (Bypasses GitHub IP ban)
RPC_URL = os.environ.get("RPC_URL", "https://api.devnet.solana.com")

def rpc_call(method, params=None):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params: payload["params"] = params
    r = requests.post(RPC_URL, json=payload)
    return r.json()

# 3. Claim Free SOL
print(f"Connected to Devnet. Wallet: {pubkey}")
print("Requesting Airdrop 1 SOL...")
rpc_call("requestAirdrop", [str(pubkey), 1000000000])
time.sleep(10)

# 4. Check Balance
resp = rpc_call("getBalance", [str(pubkey)])
balance = resp.get("result", {}).get("value", 0)
print(f"Current Balance: {balance / 1000000000} SOL")

# 5. Farm Volume
if balance > 0:
    print("Starting API Load Test (Volume Farm)...")
    for i in range(30):
        try:
            # Get blockhash
            bh_resp = rpc_call("getLatestBlockhash")
            blockhash_str = bh_resp["result"]["value"]["blockhash"]
            blockhash = Hash.from_string(blockhash_str)
            
            # Create transfer instruction
            ix = transfer(TransferParams(from_pubkey=pubkey, to_pubkey=pubkey, lamports=1000000))
            
            # Sign transaction
            tx = Transaction.new_signed_with_payer([ix], pubkey, [kp], blockhash)
            
            # Serialize and send
            tx_b64 = base64.b64encode(bytes(tx)).decode("utf-8")
            send_resp = rpc_call("sendTransaction", [tx_b64, {"encoding": "base64"}])
            print(f"Transaction {i+1}/30 sent! Hash: {send_resp.get('result')}")
        except Exception as e:
            print(f"Transaction {i+1}/30 failed: {e}")
        time.sleep(3)
    print("Load test complete.")
else:
    print("Airdrop failed (GitHub IP rate limited). Cannot farm.")
