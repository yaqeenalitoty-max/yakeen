# -*- coding: utf-8 -*-
"""
إعدادات البوت - تقرأ من متغيرات البيئة
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # توكن البوت (إجباري)
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    # معرفات المشرفين (مفصولة بفواصل)
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

    # إعدادات قاعدة البيانات
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/bot.db")

    # إعدادات الإحالات
    REFERRAL_BONUS = float(os.getenv("REFERRAL_BONUS", "5000"))
    REFERRAL_PERCENT = float(os.getenv("REFERRAL_PERCENT", "0.10"))

    # حدود المعاملات
    MIN_DEPOSIT = float(os.getenv("MIN_DEPOSIT", "10"))
    MAX_DEPOSIT = float(os.getenv("MAX_DEPOSIT", "10000"))
    MIN_WITHDRAWAL = float(os.getenv("MIN_WITHDRAWAL", "20"))
    MAX_WITHDRAWAL = float(os.getenv("MAX_WITHDRAWAL", "5000"))
    MIN_GIFT = float(os.getenv("MIN_GIFT", "5"))

    # إعدادات Ichancy API
    ICHANCY_API_BASE = os.getenv("ICHANCY_API_BASE", "https://agents.ichancy.com/global/api")
    ICHANCY_AGENT_USERNAME = os.getenv("ICHANCY_AGENT_USERNAME", "")
    ICHANCY_AGENT_PASSWORD = os.getenv("ICHANCY_AGENT_PASSWORD", "")
    ICHANCY_PARENT_ID = os.getenv("ICHANCY_PARENT_ID", "")

    # معلومات الدفع
    SYRIATEL_CASH_NUMBER = os.getenv("SYRIATEL_CASH_NUMBER", "0988072836")
    MTN_CASH_NUMBER = os.getenv("MTN_CASH_NUMBER", "0947431181")
    SHAM_CASH_ID = os.getenv("SHAM_CASH_ID", "bf5b4e0a40d0f9b464b5f90baccf2cbd")
    SHAM_CASH_NAME = os.getenv("SHAM_CASH_NAME", "علي سليمان سليمان")
    USDT_WALLET_ADDRESS = os.getenv("USDT_WALLET_ADDRESS", "0x7E766C4F7bD07f27fa5ab3Be12685992872960C2")

    # طرق الدفع
    PAYMENT_METHODS = {
        "syriatel": {
            "name": "سيريتل كاش",
            "emoji": "📱",
            "auto_enabled": False
        },
        "mtn": {
            "name": "إم تي إن كاش",
            "emoji": "📱",
            "auto_enabled": False
        },
        "sham": {
            "name": "شام كاش",
            "emoji": "💳",
            "auto_enabled": False
        },
        "usdt": {
            "name": "USDT",
            "emoji": "💰",
            "auto_enabled": False
        }
    }

    # معلومات الدعم
    SUPPORT_PHONE = os.getenv("SUPPORT_PHONE", "+963912345678")
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@ichancy.com")
    SUPPORT_TELEGRAM = os.getenv("SUPPORT_TELEGRAM", "@ichancy_support")

    # إعدادات التسجيل
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/bot.log")

    # التحقق من صحة الإعدادات
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("❌ BOT_TOKEN غير موجود. تأكد من ملف .env")
        if not cls.ADMIN_IDS:
            raise ValueError("❌ ADMIN_IDS غير موجود. يجب تحديد مشرف واحد على الأقل.")
        return True