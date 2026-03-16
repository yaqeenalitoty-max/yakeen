# -*- coding: utf-8 -*-
"""
لوحات المفاتيح (الأزرار) - نسخة كاملة
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu():
    """القائمة الرئيسية"""
    keyboard = [
        [InlineKeyboardButton("👤 حسابي", callback_data="my_account")],
        [InlineKeyboardButton("💰 شحن رصيد", callback_data="deposit"),
         InlineKeyboardButton("💸 سحب رصيد", callback_data="withdraw")],
        # عمليات بين محفظة البوت وحساب Ichancy
        [InlineKeyboardButton("💳 شحن حساب Ichancy", callback_data="wallet_to_ichancy"),
         InlineKeyboardButton("🏧 سحب من Ichancy", callback_data="ichancy_to_wallet")],
        [InlineKeyboardButton("👥 نظام الإحالات", callback_data="referral"),
         InlineKeyboardButton("🎁 إهداء رصيد", callback_data="gift_start")],
        [InlineKeyboardButton("🎟️ كود هدية", callback_data="redeem_code"),
         InlineKeyboardButton("⭐ VIP", callback_data="vip_status")],
        [InlineKeyboardButton("🎰 الجاكبوت", callback_data="jackpot"),
         InlineKeyboardButton("🎲 سجل الرهانات", callback_data="my_bets")],
        [InlineKeyboardButton("🎮 الألعاب", callback_data="games"),
         InlineKeyboardButton("📩 تواصل معنا", callback_data="contact")],
        [InlineKeyboardButton("🆕 إنشاء حساب Ichancy", callback_data="ichancy_register"),
         InlineKeyboardButton("👑 لوحة المشرف", callback_data="admin_panel")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_button():
    """زر الرجوع للقائمة الرئيسية"""
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]])


def get_payment_methods():
    """طرق الدفع"""
    keyboard = [
        [InlineKeyboardButton("📱 سيريتل كاش", callback_data="method_syriatel")],
        [InlineKeyboardButton("📱 إم تي إن كاش", callback_data="method_mtn")],
        [InlineKeyboardButton("💳 شام كاش", callback_data="method_sham")],
        [InlineKeyboardButton("💰 USDT", callback_data="method_usdt")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_panel_keyboard(counts):
    """لوحة المشرف"""
    keyboard = [
        [InlineKeyboardButton(f"📋 طلبات شحن ({counts['charges']})", callback_data="admin_charges")],
        [InlineKeyboardButton(f"📋 طلبات سحب ({counts['withdrawals']})", callback_data="admin_withdrawals")],
        [InlineKeyboardButton(f"📨 رسائل ({counts['messages']})", callback_data="admin_messages")],
        [InlineKeyboardButton("📊 إحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def contact_keyboard():
    """قائمة التواصل"""
    keyboard = [
        [InlineKeyboardButton("📩 رسالة للإدارة", callback_data="message_admin")],
        [InlineKeyboardButton("❓ الأسئلة الشائعة", callback_data="faq")],
        [InlineKeyboardButton("📞 معلومات الاتصال", callback_data="support_info")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)