import os
import json
import time
from solders.keypair import Keypair
from solana.rpc.api import Client
from solders.system_program import transfer, TransferParams

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
print("Requesting Airdrop 1 (1 SOL)...")
try:
    client.request_airdrop(pubkey, 1000000000)
except Exception as e:
    print(f"Airdrop error (this is normal if already claimed today): {e}")
time.sleep(10)

print("Requesting Airdrop 2 (1 SOL)...")
try:
    client.request_airdrop(pubkey, 1000000000)
except Exception as e:
    print(f"Airdrop error: {e}")
time.sleep(10)

try:
    balance = client.get_balance(pubkey).value
    print(f"Current Balance: {balance / 1000000000} SOL")
except Exception as e:
    print(f"Balance error: {e}")

# 4. Farm Volume
print("Starting API Load Test (Volume Farm)...")
for i in range(30):
    try:
        # Send 0.001 SOL to ourselves
        ix = transfer(TransferParams(from_pubkey=pubkey, to_pubkey=pubkey, lamports=1000000))
        resp = client.send_transaction(ix, kp)
        print(f"Transaction {i+1}/30 sent! Hash: {resp.value}")
    except Exception as e:
        print(f"Transaction {i+1}/30 failed: {e}")
    time.sleep(3)

print("Load test complete.")
