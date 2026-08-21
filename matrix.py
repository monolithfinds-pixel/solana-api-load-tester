import os
import json
import time
import base64
import requests
import random
from solders.keypair import Keypair
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solders.hash import Hash

# Load Secrets
keys_str = os.environ.get("SOL_PRIVATE_KEYS")
rpcs_str = os.environ.get("HELIUS_RPC_URLS")

if not keys_str or not rpcs_str:
    print("ERROR: Missing secrets.")
    exit()

# Parse wallets
try:
    wallets = json.loads(keys_str)
    if not isinstance(wallets[0], list):
        wallets = [wallets]
except:
    print("Error parsing wallet keys.")
    exit()

# Parse RPCs
rpcs = [r.strip() for r in rpcs_str.split(',') if r.strip()]
if not rpcs:
    print("Error parsing RPC URLs.")
    exit()

def rpc_call(rpc_url, method, params=None):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params: payload["params"] = params
    r = requests.post(rpc_url, json=payload)
    return r.json()

print(f"=== SOlana Anti-Sybil Matrix Farm Started ({len(wallets)} Wallets) ===")

# Load all Keypairs first
keypairs = []
for idx, key_data in enumerate(wallets):
    try:
        kp = Keypair.from_bytes(bytes(key_data))
        keypairs.append(kp)
    except:
        pass

# 1. Claim Airdrops for all wallets
for idx, kp in enumerate(keypairs):
    rpc_url = rpcs[idx % len(rpcs)]
    pubkey = kp.pubkey()
    print(f"\n--- Wallet {idx+1}/{len(keypairs)} | Claiming Airdrop... ---")
    
    air_resp = rpc_call(rpc_url, "requestAirdrop", [str(pubkey), 1000000000])
    if "error" in air_resp:
        print(f"  Airdrop failed (Rate limited).")
    else:
        print(f"  Airdrop success (1 SOL).")
    
    # Random sleep to look human
    time.sleep(random.uniform(2, 6))

# Wait for airdrops to finalize
print("\nWaiting 10 seconds for airdrops to finalize...")
time.sleep(10)

# 2. Anti-Sybil Transaction Web (Wallet 1 -> Wallet 2 -> Wallet 3 -> Wallet 1)
print("\n=== Starting Anti-Sybil Transaction Web ===")
for idx, kp in enumerate(keypairs):
    rpc_url = rpcs[idx % len(rpcs)]
    sender_pubkey = kp.pubkey()
    
    # Send to the NEXT wallet in the circle (or back to 0 if it's the last one)
    receiver_kp = keypairs[(idx + 1) % len(keypairs)]
    receiver_pubkey = receiver_kp.pubkey()
    
    # Check sender balance
    bal_resp = rpc_call(rpc_url, "getBalance", [str(sender_pubkey)])
    balance = bal_resp.get("result", {}).get("value", 0)
    
    if balance > 0:
        print(f"\n--- Tx: Wallet {idx+1} -> Wallet {(idx % len(keypairs)) + 2} ---")
        # Do 3 transactions per wallet to build volume
        for i in range(3):
            try:
                # Randomize amount (0.0001 to 0.001 SOL)
                random_lamports = random.randint(100000, 1000000)
                
                bh_resp = rpc_call(rpc_url, "getLatestBlockhash")
                blockhash_str = bh_resp["result"]["value"]["blockhash"]
                blockhash = Hash.from_string(blockhash_str)
                
                ix = transfer(TransferParams(from_pubkey=sender_pubkey, to_pubkey=receiver_pubkey, lamports=random_lamports))
                tx = Transaction.new_signed_with_payer([ix], sender_pubkey, [kp], blockhash)
                
                tx_b64 = base64.b64encode(bytes(tx)).decode("utf-8")
                send_resp = rpc_call(rpc_url, "sendTransaction", [tx_b64, {"encoding": "base64"}])
                print(f"  Sent {random_lamports/1000000000} SOL. Hash: {send_resp.get('result', 'FAILED')[:15]}...")
                
                # Randomize sleep time to look human (1 to 5 seconds)
                time.sleep(random.uniform(1, 5))
            except Exception as e:
                print(f"  Tx failed: {e}")
                break
    else:
        print(f"\n--- Wallet {idx+1} has no balance. Skipping. ---")

print("\n=== Anti-Sybil Matrix Run Complete ===")
