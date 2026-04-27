from sqlalchemy.orm import Session
from app.models.TransactionModel import Transaction
from decimal import Decimal
from sqlalchemy import func
from datetime import datetime, timezone
from fastapi import HTTPException
from app.models.WalletModel import Wallet

async def checkDailyLimits (db: Session, user_id: int, amount: Decimal):

    today_total : Decimal = db.query(func.sum(Transaction.amount)).join(Wallet, Transaction.wallet_id == Wallet.wallet_id).filter (Wallet.user_id == user_id, func.date(Transaction.initiatedAt) == datetime.now(timezone.utc).date()).scalar() or 0

    if today_total + amount > 10000:
        raise HTTPException (status_code = 401, detail = "You reached the daily transaction limit")