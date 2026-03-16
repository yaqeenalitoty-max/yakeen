#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
البوت الرئيسي - Ichancy Bot - نسخة كاملة ومستقرة
"""

import logging
import warnings
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from telegram.warnings import PTBUserWarning

# تجاهل تحذيرات PTBUserWarning
warnings.filterwarnings("ignore", category=PTBUserWarning, module="telegram")

from config import Config
from database import init_db
from scheduler import init_scheduler, shutdown_scheduler
from handlers.user import start, balance, help_command, cancel, my_account
from handlers.admin import (
    admin_panel, admin_users_list, admin_ban_user, admin_unban_user,
    admin_add_balance, admin_deduct_balance, admin_stats, admin_broadcast,
    admin_charges_list, admin_approve_charge, admin_reject_charge
)
from handlers.payment import (
    deposit_handler,
    withdraw_handler,
    process_amount,
    process_transaction_id,
    withdraw_address_received,
    withdraw_amount_received,
)
from handlers.referral import referral_system
from handlers.contact import contact_menu, message_admin
from handlers.games import games_menu
from handlers.ichancy import (
    ichancy_register_start, ichancy_register_username, ichancy_register_password
)
from handlers.ichancy_new import (
    wallet_to_ichancy_start,
    ichancy_to_wallet_start,
    handle_wallet_amount,
)
from handlers.gifts import gift_start, gift_cancel, gift_amount, gift_recipient, gift_confirm, gift_history
from handlers.gift_codes import redeem_code_start, redeem_code
from handlers.vip import vip_status, vip_levels, claim_vip_bonus
from handlers.jackpot import jackpot_info, join_jackpot, my_jackpot_stats
from handlers.bets import my_bets, game_stats, process_link_ichancy
from keyboards import get_main_menu, get_back_button, get_payment_methods
from utils import setup_logging, error_handler

# إعداد التسجيل
logger = setup_logging()

# حالات المحادثة
(
    AMOUNT_INPUT,
    TRANSACTION_ID_INPUT,
    WITHDRAW_ADDRESS_INPUT,
    WITHDRAW_AMOUNT_INPUT,
    GIFT_AMOUNT,
    GIFT_RECIPIENT,
    GIFT_CONFIRM,
    CODE_INPUT,
    ADMIN_MESSAGE_INPUT,
    REGISTER_USERNAME,
    REGISTER_PASSWORD,
) = range(11)


async def post_init(application: Application):
    """بعد تهيئة البوت - إعداد الأوامر والمجدول"""
    commands = [
        BotCommand("start", "بدء استخدام البوت"),
        BotCommand("menu", "القائمة الرئيسية"),
        BotCommand("balance", "عرض الرصيد"),
        BotCommand("help", "المساعدة"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("تم إعداد أوامر البوت")
    
    # بدء المجدول
    await init_scheduler(application)
    application.scheduler.start()
    logger.info("تم بدء المجدول")


async def menu_command(update: Update, context):
    """عرض القائمة الرئيسية"""
    await update.message.reply_text("القائمة الرئيسية", reply_markup=get_main_menu())


async def button_handler(update: Update, context):
    """معالج الأزرار الرئيسي"""
    query = update.callback_query
    data = query.data
    
    try:
        # محاولة الإجابة على الاستعلام مع تجاهل الأخطاء
        try:
            await query.answer()
        except Exception as e:
            print(f"[WARNING] Could not answer callback query: {e}")
        
        if data == "main_menu":
            await query.edit_message_text(
                "🏠 **القائمة الرئيسية**",
                reply_markup=get_main_menu(),
                parse_mode="Markdown"
            )
        elif data == "my_account":
            await my_account(update, context)
        elif data == "deposit":
            context.user_data["operation"] = "deposit"
            await query.edit_message_text(
                "💰 **اختر طريقة الشحن:**",
                reply_markup=get_payment_methods(),
                parse_mode="Markdown"
            )
        elif data == "withdraw":
            context.user_data["operation"] = "withdraw"
            await query.edit_message_text(
                "💸 **اختر طريقة السحب:**",
                reply_markup=get_payment_methods(),
                parse_mode="Markdown"
            )
        elif data.startswith("method_"):
            method = data.replace("method_", "")
            context.user_data["method"] = method
            operation = context.user_data.get("operation")
            if operation == "deposit":
                await query.edit_message_text(
                    f"💰 أرسل المبلغ الذي تريد شحنه (الحد الأدنى {Config.MIN_DEPOSIT} - الأقصى {Config.MAX_DEPOSIT}):",
                    reply_markup=get_back_button()
                )
                return AMOUNT_INPUT
            elif operation == "withdraw":
                await query.edit_message_text(
                    f"💰 أرسل المبلغ الذي تريد سحبه (الحد الأدنى {Config.MIN_WITHDRAWAL} - الأقصى {Config.MAX_WITHDRAWAL}):",
                    reply_markup=get_back_button()
                )
                return AMOUNT_INPUT
        elif data == "referral":
            await referral_system(update, context)
        elif data == "contact":
            await contact_menu(update, context)
        elif data == "games":
            await games_menu(update, context)
        elif data == "ichancy_register":
            # يتم التعامل معه بواسطة ConversationHandler منفصل
            pass
        elif data == "wallet_to_ichancy":
            await wallet_to_ichancy_start(update, context)
        elif data == "ichancy_to_wallet":
            await ichancy_to_wallet_start(update, context)
        elif data == "admin_panel":
            await admin_panel(update, context)
        elif data == "admin_charges":
            await admin_charges_list(update, context)
        elif data.startswith("approve_charge_"):
            await admin_approve_charge(update, context)
        elif data.startswith("reject_charge_"):
            await admin_reject_charge(update, context)
        elif data == "admin_users":
            await admin_users_list(update, context)
        elif data == "admin_stats":
            await admin_stats(update, context)
        elif data == "jackpot":
            await jackpot_info(update, context)
        elif data == "join_jackpot":
            await join_jackpot(update, context)
        elif data == "my_jackpot_stats":
            await my_jackpot_stats(update, context)
        elif data == "vip_status":
            await vip_status(update, context)
        elif data == "vip_levels":
            await vip_levels(update, context)
        elif data == "claim_vip_bonus":
            await claim_vip_bonus(update, context)
        elif data == "my_bets":
            await my_bets(update, context)
        elif data == "game_stats":
            await game_stats(update, context)
        elif data == "link_ichancy":
            await process_link_ichancy(update, context)
        elif data == "full_stats":
            await game_stats(update, context)
        elif data == "gift_cancel":
            await gift_cancel(update, context)
        elif data == "gift_start":
            await gift_start(update, context)
        elif data == "redeem_code":
            await redeem_code_start(update, context)
        else:
            await query.edit_message_text("هذه الميزة قيد التطوير.", reply_markup=get_back_button())
    
    except Exception as e:
        print(f"[ERROR] Error in button_handler: {e}")
        try:
            await query.edit_message_text("حدث خطأ، يرجى المحاولة مرة أخرى.", reply_markup=get_main_menu())
        except:
            pass


def main():
    """تشغيل البوت"""
    Config.validate()
    init_db()

    application = Application.builder().token(Config.BOT_TOKEN).post_init(post_init).build()

    # أوامر عامة
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("balance", balance))
    # أوامر إدارة الهدايا والأكواد
    application.add_handler(CommandHandler("gift", gift_history))
    application.add_handler(CommandHandler("gifthistory", gift_history))
    application.add_handler(CommandHandler("redeem", redeem_code_start))

    # أوامر الإدمن
    application.add_handler(CommandHandler("ban", admin_ban_user))
    application.add_handler(CommandHandler("unban", admin_unban_user))
    application.add_handler(CommandHandler("addbalance", admin_add_balance))
    application.add_handler(CommandHandler("deductbalance", admin_deduct_balance))
    application.add_handler(CommandHandler("broadcast", admin_broadcast))
    application.add_handler(CommandHandler("adminstats", admin_stats))

    # أوامر VIP والرهانات
    application.add_handler(CommandHandler("vip", vip_status))
    application.add_handler(CommandHandler("bets", my_bets))
    application.add_handler(CommandHandler("jackpot", jackpot_info))

    # محادثة الدفع الموحدة (إيداع + سحب)
    payment_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^method_.*$")],
        states={
            AMOUNT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_amount)],
            TRANSACTION_ID_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_transaction_id)],
            WITHDRAW_ADDRESS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_address_received)],
            WITHDRAW_AMOUNT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_amount_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )
    application.add_handler(payment_conv)

    # محادثة الإهداء
    gift_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(gift_start, pattern="^gift_start$")],
        states={
            GIFT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, gift_amount)],
            GIFT_RECIPIENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, gift_recipient)],
            GIFT_CONFIRM: [CallbackQueryHandler(gift_confirm)],
        },
        fallbacks=[CommandHandler("cancel", gift_cancel)],
        per_message=False,
    )
    application.add_handler(gift_conv)

    # محادثة أكواد الهدايا
    gift_code_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(redeem_code_start, pattern="^redeem_code$")],
        states={
            CODE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, redeem_code)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )
    application.add_handler(gift_code_conv)

    # محادثة إنشاء حساب Ichancy
    ichancy_register_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ichancy_register_start, pattern="^ichancy_register$")],
        states={
            REGISTER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ichancy_register_username)],
            REGISTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ichancy_register_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )
    application.add_handler(ichancy_register_conv)

    # معالج الأزرار الرئيسي
    application.add_handler(CallbackQueryHandler(button_handler))

    # معالج الرسائل النصية العادية
    async def handle_unknown_message(update: Update, context):
        # التحقق أولاً من رسائل المحفظة
        if context.user_data.get("wallet_flow"):
            await handle_wallet_amount(update, context)
            return
        
        await update.message.reply_text("استخدم الأزرار للتنقل:", reply_markup=get_main_menu())
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown_message))

    # معالج الأخطاء
    application.add_error_handler(error_handler)

    logger.info("بدء تشغيل البوت...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
