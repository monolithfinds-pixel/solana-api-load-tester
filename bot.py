import os
import json
import time
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.system_program import TransferParams, transfer

# 1. Load Private Key from GitHub Secrets
key_str = os.environ.get("SOL_PRIVATE_KEY")
if key_str.startswith('['):
    key_bytes = bytes(json.loads(key_str))
else:
    key_bytes = key_str.encode()

kp = Keypair.from_bytes(key_bytes)
pubkey = kp.pubkey()

# 2. Connect to Devnet
client = Client("https://api.devnet.solana.com")
print(f"Connected to Devnet. Wallet: {pubkey}")

# 3. Claim Free SOL
print("Requesting Airdrop 1 SOL...")
try:
    client.request_airdrop(pubkey, 1000000000)
except Exception as e:
    print(f"Airdrop error (normal if already claimed today): {e}")
time.sleep(10)

# 4. Check Balance
balance = client.get_balance(pubkey).value
print(f"Current Balance: {balance / 1000000000} SOL")

# 5. Farm Volume
if balance > 0:
    print("Starting API Load Test (Volume Farm)...")
    for i in range(30):
        try:
            # Create transfer instruction (send 0.001 SOL to self)
            ix = transfer(TransferParams(from_pubkey=pubkey, to_pubkey=pubkey, lamports=1000000))
            # Send transaction (solana library handles all the blockhash/serialization magic)
            resp = client.send_transaction(ix, kp)
            print(f"Transaction {i+1}/30 sent! Hash: {resp.value}")
        except Exception as e:
            print(f"Transaction {i+1}/30 failed: {e}")
        time.sleep(3)
    print("Load test complete.")
else:
    print("ERROR: Balance is 0. Airdrop failed (GitHub IP might be rate-limited). Cannot farm.")
