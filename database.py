# -*- coding: utf-8 -*-
"""
نموذج قاعدة البيانات باستخدام SQLAlchemy
"""

import os
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    BigInteger,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from contextlib import contextmanager

from config import Config

# إنشاء المحرك
engine = create_engine(Config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# ========== النماذج ==========
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    balance = Column(Float, default=0.0)
    referral_code = Column(String, unique=True, index=True)
    referred_by = Column(String, nullable=True)  # كود المحيل
    referral_count = Column(Integer, default=0)
    referral_earnings = Column(Float, default=0.0)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    language = Column(String, default="ar")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # معلومات حساب Ichancy
    ichancy_username = Column(String, nullable=True)
    ichancy_created_at = Column(DateTime, nullable=True)

    # العلاقات
    transactions = relationship("Transaction", back_populates="user")
    messages = relationship("Message", back_populates="user")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # deposit, withdraw, gift, referral
    amount = Column(Float)
    method = Column(String, nullable=True)  # طريقة الدفع
    status = Column(String, default="pending")  # pending, completed, failed
    reference = Column(String, unique=True, nullable=True)  # رقم مرجعي
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="transactions")


class PendingCharge(Base):
    __tablename__ = "pending_charges"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    method = Column(String)
    transaction_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    admin_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PendingWithdrawal(Base):
    __tablename__ = "pending_withdrawals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    method = Column(String)
    account_details = Column(Text)
    status = Column(String, default="pending")
    admin_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GiftCode(Base):
    __tablename__ = "gift_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True)
    amount = Column(Float)
    max_uses = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class GiftCodeUsage(Base):
    __tablename__ = "gift_code_usages"

    id = Column(Integer, primary_key=True)
    code_id = Column(Integer, ForeignKey("gift_codes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    used_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message_type = Column(String)  # user_to_admin, admin_reply
    content = Column(Text)
    file_id = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)
    admin_reply = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True)
    type = Column(String)  # referral_welcome, main, admin
    content = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Jackpot(Base):
    """الجاكبوت اليومي"""
    __tablename__ = "jackpots"

    id = Column(Integer, primary_key=True)
    name = Column(String, default="الجاكبوت اليومي")
    total_amount = Column(Float, default=0.0)
    last_winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_win_amount = Column(Float, default=0.0)
    draw_time = Column(DateTime, default=datetime.utcnow)  # موعد السحب القادم
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class JackpotEntry(Base):
    """مشاركات الجاكبوت"""
    __tablename__ = "jackpot_entries"

    id = Column(Integer, primary_key=True)
    jackpot_id = Column(Integer, ForeignKey("jackpots.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, default=0.0)  # المبلغ المساهم به
    tickets = Column(Integer, default=1)  # عدد التذاكر
    created_at = Column(DateTime, default=datetime.utcnow)


class Bet(Base):
    """سجل الرهانات والألعاب"""
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_type = Column(String)  # casino, sports, slots, etc.
    game_name = Column(String, nullable=True)
    amount = Column(Float)  # مبلغ الرهان
    outcome = Column(String, default="pending")  # win, loss, pending
    win_amount = Column(Float, default=0.0)  # مبلغ الفوز
    ichancy_bet_id = Column(String, nullable=True)  # معرف الرهان من ichancy
    details = Column(Text, nullable=True)  # تفاصيل إضافية
    created_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime, nullable=True)


class Gift(Base):
    """الهدايا بين المستخدمين"""
    __tablename__ = "gifts"

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    message = Column(Text, nullable=True)
    status = Column(String, default="completed")  # completed, pending, failed
    created_at = Column(DateTime, default=datetime.utcnow)


class UserActivity(Base):
    """سجل نشاطات المستخدمين"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String)  # login, bet, deposit, withdraw, etc.
    details = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Backup(Base):
    """سجل النسخ الاحتياطية"""
    __tablename__ = "backups"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer, default=0)
    status = Column(String, default="success")  # success, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ========== دوال مساعدة ==========
def init_db():
    """إنشاء الجداول إذا لم تكن موجودة"""
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope():
    """سياق لجلسة قاعدة البيانات"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_user_by_telegram_id(telegram_id: int):
    """الحصول على مستخدم بواسطة معرف التليجرام"""
    with session_scope() as session:
        return session.query(User).filter(User.telegram_id == telegram_id).first()


def create_user(
    telegram_id: int,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    referred_by: str = None,
):
    """إنشاء مستخدم جديد"""
    import secrets
    import hashlib

    with session_scope() as session:
        # توليد كود إحالة فريد
        while True:
            code = hashlib.md5(
                f"{telegram_id}{secrets.token_hex(4)}".encode()
            ).hexdigest()[:8].upper()
            if not session.query(User).filter(User.referral_code == code).first():
                break

        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            referral_code=code,
            referred_by=referred_by,
            is_admin=(telegram_id in Config.ADMIN_IDS),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user