#!/bin/bash

# 1. Install official Solana CLI (Standard dev tool, unbannable)
echo "Installing Solana CLI..."
sh -c "$(curl -sSfL https://release.solana.com/v1.18.4/install)"
export PATH="/home/runner/.local/share/solana/install/active_release/bin:$PATH"

# 2. Configure to use Devnet (Free test network)
echo "Configuring Devnet..."
solana config set --url https://api.devnet.solana.com

# 3. Import Private Key from GitHub Secrets
echo "${SOL_PRIVATE_KEY}" > /home/runner/id.json
solana config set --keypair /home/runner/id.json

# 4. Check Balance and claim free Devnet SOL (2 SOL max per IP/day)
echo "Checking balance and claiming free test SOL..."
BALANCE=$(solana balance --lamports)
if [ "$BALANCE" -lt 100000000 ]; then
  echo "Claiming airdrop..."
  solana airdrop 2
  sleep 5
fi

echo "Current Balance: $(solana balance)"

# 5. Farm Volume (Send 0.01 SOL to ourselves 30 times)
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
