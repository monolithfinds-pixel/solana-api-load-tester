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
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.compute_budget import set_compute_unit_price

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

# Smart Contract Memos to simulate DApp interaction
MEMOS = ["OrcaSwap", "PythFeed", "JitoStake", "EclipseBridge", "ZKCompression", "MintNFT", "RaydiumLP"]

# Memo Program ID
MEMO_PROGRAM_ID = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWuMy6or3pJPZmQYsA")

def create_memo_instruction(text):
    return Instruction(MEMO_PROGRAM_ID, [], text.encode('utf-8'))

print(f"=== GOD SCRIPT: Anti-Sybil DApp Matrix Started ({len(wallets)} Wallets) ===")

# Load all Keypairs
keypairs = []
for idx, key_data in enumerate(wallets):
    try:
        keypairs.append(Keypair.from_bytes(bytes(key_data)))
    except:
        pass

# 1. Claim Airdrops
for idx, kp in enumerate(keypairs):
    rpc_url = rpcs[idx % len(rpcs)]
    pubkey = kp.pubkey()
    print(f"\n--- Wallet {idx+1}/{len(keypairs)} | Claiming Airdrop... ---")
    
    air_resp = rpc_call(rpc_url, "requestAirdrop", [str(pubkey), 1000000000])
    if "error" in air_resp:
        print(f"  Airdrop failed (Rate limited).")
    else:
        print(f"  Airdrop success (1 SOL).")
    time.sleep(random.uniform(2, 6))

print("\nWaiting 10 seconds for airdrops to finalize...")
time.sleep(10)

# 2. Anti-Sybil DApp Transaction Web
print("\n=== Starting Elite DApp Transaction Web ===")
for idx, kp in enumerate(keypairs):
    rpc_url = rpcs[idx % len(rpcs)]
    sender_pubkey = kp.pubkey()
    receiver_kp = keypairs[(idx + 1) % len(keypairs)]
    receiver_pubkey = receiver_kp.pubkey()
    
    bal_resp = rpc_call(rpc_url, "getBalance", [str(sender_pubkey)])
    balance = bal_resp.get("result", {}).get("value", 0)
    
    if balance > 0:
        print(f"\n--- Wallet {idx+1} -> Wallet {(idx % len(keypairs)) + 2} ---")
        for i in range(3):
            try:
                # Randomize amount
                random_lamports = random.randint(100000, 1000000)
                
                bh_resp = rpc_call(rpc_url, "getLatestBlockhash")
                blockhash_str = bh_resp["result"]["value"]["blockhash"]
                blockhash = Hash.from_string(blockhash_str)
                
                # INSTRUCTION 1: System Transfer (Volume)
                ix_transfer = transfer(TransferParams(from_pubkey=sender_pubkey, to_pubkey=receiver_pubkey, lamports=random_lamports))
                
                # INSTRUCTION 2: Compute Budget (Priority Fee - Simulates DeFi/MEV user)
                ix_priority = set_compute_unit_price(random.randint(1000, 50000))
                
                # INSTRUCTION 3: Memo (Simulates DApp interaction)
                memo_text = random.choice(MEMOS) + "_" + str(random.randint(100, 999))
                ix_memo = create_memo_instruction(memo_text)
                
                # Combine 3 instructions into 1 transaction (Elite Protocol Diversity)
                tx = Transaction.new_signed_with_payer(
                    [ix_priority, ix_transfer, ix_memo], 
                    sender_pubkey, [kp], blockhash
                )
                
                tx_b64 = base64.b64encode(bytes(tx)).decode("utf-8")
                send_resp = rpc_call(rpc_url, "sendTransaction", [tx_b64, {"encoding": "base64"}])
                print(f"  Tx {i+1}/3 sent! Memo: {memo_text}")
                
                time.sleep(random.uniform(1, 5))
            except Exception as e:
                print(f"  Tx failed: {e}")
                break
    else:
        print(f"\n--- Wallet {idx+1} has no balance. Skipping. ---")

print("\n=== God Script Matrix Run Complete ===")
