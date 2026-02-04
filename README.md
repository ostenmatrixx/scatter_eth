# ETH Scatter Script (Python)

A simple and safe Python script to **send ETH to multiple addresses** from a single wallet using **Web3.py**.

This script:
- Reads recipient addresses from a `.txt` file
- Asks how much ETH to send per address
- Calculates the total ETH required
- Confirms before sending
- Uses environment variables to protect private keys

---

## ⚠️ Security Notice

**Never hard-code private keys.**  
This project uses a `.env` file to store sensitive data, which is ignored by Git.

Make sure `.env` is listed in `.gitignore`.

---

## 📦 Requirements

- Python **3.9+**
- `web3`
- `python-dotenv`

Install dependencies:
```bash
pip install web3 python-dotenv
