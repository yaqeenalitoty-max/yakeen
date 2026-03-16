# -*- coding: utf-8 -*-
"""
دوال مساعدة عامة (نسخة محسّنة نهائياً)
"""

import logging
from datetime import datetime
from typing import Optional, Tuple

from config import Config
from database import session_scope, User

logger = logging.getLogger(__name__)


def setup_logging():
    """إعداد نظام التسجيل"""
    import os
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, Config.LOG_LEVEL),
        handlers=[
            logging.FileHandler(Config.LOG_FILE, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def format_currency(amount: float) -> str:
    """تنسيق العملة"""
    return f"{amount:,.0f} ل.س"


def validate_amount(amount_str: str, min_val: float, max_val: float) -> Tuple[bool, Optional[float], str]:
    """التحقق من صحة المبلغ"""
    try:
        amount = float(amount_str)
        if amount <= 0:
            return False, None, "❌ المبلغ يجب أن يكون أكبر من صفر"
        if amount < min_val:
            return False, None, f"❌ الحد الأدنى هو {format_currency(min_val)}"
        if amount > max_val:
            return False, None, f"❌ الحد الأقصى هو {format_currency(max_val)}"
        return True, amount, ""
    except ValueError:
        return False, None, "❌ يرجى إدخال رقم صحيح"


def get_user_display_name(user: User) -> str:
    """الحصول على اسم المستخدم للعرض"""
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    elif user.username:
        return f"@{user.username}"
    else:
        return f"المستخدم {user.telegram_id}"


def is_admin(user_id: int) -> bool:
    """التحقق من صلاحية المشرف"""
    return user_id in Config.ADMIN_IDS


def is_banned(user_id: int) -> bool:
    """التحقق من حظر المستخدم (بدون التسبب في DetachedInstanceError)"""
    with session_scope() as session:
        user = session.query(User).filter(User.telegram_id == user_id).first()
        if user:
            return user.is_banned
        return False


def generate_reference() -> str:
    """توليد رقم مرجعي عشوائي"""
    import secrets
    import hashlib
    return hashlib.md5(secrets.token_bytes(16)).hexdigest()[:12].upper()


def generate_transaction_reference() -> str:
    """توليد مرجع المعاملة"""
    import uuid
    return str(uuid.uuid4())[:8].upper()


async def error_handler(update, context):
    """معالج الأخطاء العام"""
    logger.error(f"حدث خطأ: {context.error}", exc_info=True)
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ حدث خطأ غير متوقع. الرجاء المحاولة لاحقاً أو التواصل مع الإدارة."
            )
        elif update and update.callback_query and update.callback_query.message:
            await update.callback_query.message.reply_text(
                "❌ حدث خطأ غير متوقع. الرجاء المحاولة لاحقاً أو التواصل مع الإدارة."
            )
    except Exception as e:
        logger.error(f"فشل إرسال رسالة الخطأ: {e}")


def get_pending_counts():
    """الحصول على أعداد الطلبات المعلقة (للوحة المشرف)"""
    from database import session_scope, PendingCharge, PendingWithdrawal, Message
    with session_scope() as session:
        charges = session.query(PendingCharge).filter(PendingCharge.status == "pending").count()
        withdrawals = session.query(PendingWithdrawal).filter(PendingWithdrawal.status == "pending").count()
        messages = session.query(Message).filter(Message.is_read == False).count()
        return {"charges": charges, "withdrawals": withdrawals, "messages": messages}