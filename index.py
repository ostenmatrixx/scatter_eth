import os
import time
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not RPC_URL or not PRIVATE_KEY:
    raise Exception("❌ Missing RPC_URL or PRIVATE_KEY in .env")

# Connect to provider
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise Exception("❌ Failed to connect to RPC")

# Load wallet
account = w3.eth.account.from_key(PRIVATE_KEY)
sender_address = account.address

print(f"\nUsing wallet: {sender_address}")

# ---- LOAD RECIPIENTS ----
try:
    with open("receivers.txt", "r") as f:
        raw_lines = [line.strip() for line in f]
except FileNotFoundError:
    raise Exception("❌ receivers.txt file not found")

# Error if file exists but empty
if len(raw_lines) == 0:
    raise Exception("❌ receivers.txt is empty. No addresses found.")

# Validate addresses
valid_recipients = []
invalid_count = 0

for line in raw_lines:
    if not line:
        continue
    if w3.is_address(line):
        valid_recipients.append(w3.to_checksum_address(line))
    else:
        invalid_count += 1
        print(f"⚠️ Invalid address skipped: {line}")

# Error if no valid addresses
if len(valid_recipients) == 0:
    raise Exception("❌ No valid Ethereum addresses found in .txt")

recipient_count = len(valid_recipients)

print(f"\n📬 Valid addresses   : {recipient_count}")
print(f"⚠️ Invalid addresses : {invalid_count}")

# ---- ASK AMOUNT ----
while True:
    try:
        amount_eth = float(input("\n💸 Enter ETH amount to send per address: "))
        if amount_eth <= 0:
            raise ValueError
        break
    except ValueError:
        print("❌ Please enter a valid positive number")

amount_wei = w3.to_wei(amount_eth, "ether")
total_eth = amount_eth * recipient_count
total_wei = amount_wei * recipient_count

# ---- BALANCE CHECK ----
balance_wei = w3.eth.get_balance(sender_address)
balance_eth = float(w3.from_wei(balance_wei, "ether"))

print("\n========== SUMMARY ==========")
print(f"Per address : {amount_eth} ETH")
print(f"Addresses   : {recipient_count}")
print(f"Total send  : {total_eth} ETH")
print(f"Wallet bal  : {balance_eth} ETH")
print("=============================")

if balance_wei < total_wei:
    raise Exception("❌ Insufficient balance for this batch")

# ---- FINAL CONFIRMATION ----
confirm = input("\nType YES to confirm and send transactions: ")
if confirm != "YES":
    print("❌ Transaction cancelled by user")
    exit()

# ---- SEND TXS ----
nonce = w3.eth.get_transaction_count(sender_address)

for idx, recipient in enumerate(valid_recipients, start=1):
    tx = {
        "to": recipient,
        "value": amount_wei,
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce,
        "chainId": w3.eth.chain_id
    }

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    try:
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"\n✅ [{idx}/{recipient_count}] Sent {amount_eth} ETH → {recipient}")
        print(f"   TX: {tx_hash.hex()}")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"   Mined in block {receipt.blockNumber}")

        nonce += 1
        time.sleep(10)

    except Exception as e:
        print(f"\n❌ Failed sending to {recipient}")
        print(f"   Reason: {str(e)}")
        print("❌ Stopping further transactions to prevent nonce issues")
        break
