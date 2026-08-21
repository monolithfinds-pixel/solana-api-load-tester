import os
import json
import time
import base64
import requests
from solders.keypair import Keypair
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solders.hash import Hash

# Load Secrets
keys_str = os.environ.get("SOL_PRIVATE_KEYS")
rpcs_str = os.environ.get("HELIUS_RPC_URLS")

if not keys_str or not rpcs_str:
    print("ERROR: Missing secrets. Ensure SOL_PRIVATE_KEYS and HELIUS_RPC_URLS are set.")
    exit()

# Parse the 50 wallets
try:
    wallets = json.loads(keys_str)
    if not isinstance(wallets[0], list):
        wallets = [wallets] # Fallback if only 1 key
except:
    print("Error parsing wallet keys.")
    exit()

# Parse the 10 Helius RPCs
rpcs = [r.strip() for r in rpcs_str.split(',') if r.strip()]
if not rpcs:
    print("Error parsing RPC URLs.")
    exit()

def rpc_call(rpc_url, method, params=None):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params: payload["params"] = params
    r = requests.post(rpc_url, json=payload)
    return r.json()

print(f"=== SOlana Matrix Farm Started ({len(wallets)} Wallets, {len(rpcs)} RPCs) ===")

# Loop through all 50 wallets
for idx, key_data in enumerate(wallets):
    # Assign an RPC to this wallet (Round-robin style: Wallet 0 uses RPC 0, Wallet 10 uses RPC 0 again)
    rpc_url = rpcs[idx % len(rpcs)]
    
    try:
        kp = Keypair.from_bytes(bytes(key_data))
    except Exception as e:
        print(f"Wallet {idx+1}: Invalid key format. Skipping.")
        continue
        
    pubkey = kp.pubkey()
    print(f"\n--- Wallet {idx+1}/{len(wallets)} | Using RPC {idx % len(rpcs) + 1} ---")
    print(f"Address: {pubkey}")
    
    # 1. Request Airdrop (1 SOL)
    air_resp = rpc_call(rpc_url, "requestAirdrop", [str(pubkey), 1000000000])
    if "error" in air_resp:
        print(f"Airdrop failed: {air_resp['error']['message']}")
        continue
        
    time.sleep(5)
    
    # 2. Check Balance
    bal_resp = rpc_call(rpc_url, "getBalance", [str(pubkey)])
    balance = bal_resp.get("result", {}).get("value", 0)
    print(f"Balance: {balance / 1000000000} SOL")
    
    # 3. Farm Volume (10 transactions per wallet to keep it fast and avoid rate limits)
    if balance > 0:
        for i in range(10):
            try:
                bh_resp = rpc_call(rpc_url, "getLatestBlockhash")
                blockhash_str = bh_resp["result"]["value"]["blockhash"]
                blockhash = Hash.from_string(blockhash_str)
                
                ix = transfer(TransferParams(from_pubkey=pubkey, to_pubkey=pubkey, lamports=1000000))
                tx = Transaction.new_signed_with_payer([ix], pubkey, [kp], blockhash)
                
                tx_b64 = base64.b64encode(bytes(tx)).decode("utf-8")
                send_resp = rpc_call(rpc_url, "sendTransaction", [tx_b64, {"encoding": "base64"}])
                print(f"  Tx {i+1}/10 sent!")
            except Exception as e:
                print(f"  Tx {i+1}/10 failed: {e}")
            time.sleep(2)
    else:
        print("  Skipping (No balance).")

print("\n=== Matrix Run Complete ===")
