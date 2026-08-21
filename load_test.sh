#!/bin/bash

# 1. Download Solana CLI directly (Bypasses curl SSL errors)
echo "Downloading Solana CLI..."
wget -q https://release.solana.com/v1.18.4/solana-release-x86_64-unknown-linux-gnu.tar.bz2 -O solana.tar.bz2
tar jxf solana.tar.bz2
export PATH="/home/runner/solana-release/bin:$PATH"

# 2. Configure to use Devnet (Free test network)
echo "Configuring Devnet..."
solana config set --url https://api.devnet.solana.com

# 3. Import Private Key from GitHub Secrets
echo "${SOL_PRIVATE_KEY}" > /home/runner/id.json
solana config set --keypair /home/runner/id.json

# 4. Claim free Devnet SOL
echo "Claiming free test SOL (1)..."
solana airdrop 1
sleep 5

echo "Claiming free test SOL (2)..."
solana airdrop 1
sleep 5

echo "Current Balance: $(solana balance)"

# 5. Farm Volume (Send 0.001 SOL to ourselves 30 times)
echo "Starting API Load Test (Volume Farm)..."
MY_ADDRESS=$(solana address)
echo "Testing Address: $MY_ADDRESS"

for i in {1..30}
do
  echo "Transaction $i/30"
  # We send 0.001 SOL to ourselves to generate network activity
  solana transfer $MY_ADDRESS 0.001 --allow-unfunded-recipient --fee-payer /home/runner/id.json --quiet
  # Sleep 3 seconds to avoid rate limits
  sleep 3
done

echo "Load test complete."
