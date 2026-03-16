# -*- coding: utf-8 -*-
"""
نظام المهام المجدولة والنسخ الاحتياطي
"""

import os
import shutil
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config
from database import session_scope, Backup, User, Transaction
from handlers.jackpot import draw_jackpot

scheduler = None


async def init_scheduler(application):
    """تهيئة المجدول"""
    global scheduler

    scheduler = AsyncIOScheduler()

    # سحب الجاكبوت يومياً الساعة 8 مساءً
    scheduler.add_job(
        lambda: draw_jackpot(application),
        CronTrigger(hour=20, minute=0),
        id="jackpot_draw",
        name="سحب الجاكبوت اليومي"
    )

    # نسخ احتياطي يومياً الساعة 2 صباحاً
    scheduler.add_job(
        lambda: create_backup(application),
        CronTrigger(hour=2, minute=0),
        id="daily_backup",
        name="النسخ الاحتياطي اليومي"
    )

    # تنظيف البيانات القديمة أسبوعياً (يوم الأحد الساعة 3 صباحاً)
    scheduler.add_job(
        lambda: cleanup_old_data(application),
        CronTrigger(day_of_week="sun", hour=3, minute=0),
        id="weekly_cleanup",
        name="تنظيف البيانات القديمة"
    )

    # تحديث إحصائيات المستخدمين كل ساعة
    scheduler.add_job(
        lambda: update_user_stats(application),
        CronTrigger(hour="*", minute=0),
        id="hourly_stats",
        name="تحديث الإحصائيات"
    )

    # تخزين المجدول في application
    application.scheduler = scheduler
    
    print("[INFO] Scheduler initialized successfully")


async def create_backup(application=None):
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)

        # اسم ملف النسخة الاحتياطية
        backup_filename = f"bot_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        # نسخ ملف قاعدة البيانات
        db_path = Config.DATABASE_URL.replace("sqlite:///", "")

        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_path)

            # حجم الملف
            file_size = os.path.getsize(backup_path)

            # تسجيل في قاعدة البيانات
            with session_scope() as session:
                backup = Backup(
                    filename=backup_filename,
                    file_path=backup_path,
                    file_size=file_size,
                    status="success"
                )
                session.add(backup)
                session.commit()

            print(f"[INFO] Backup created: {backup_filename} ({file_size} bytes)")

            # إشعار الإدمن
            if application:
                for admin_id in Config.ADMIN_IDS:
                    try:
                        await application.bot.send_message(
                            chat_id=admin_id,
                            text=f"✅ **تم إنشاء نسخة احتياطية**\n\n"
                                 f"الملف: `{backup_filename}`\n"
                                 f"الحجم: {file_size / 1024:.1f} KB\n"
                                 f"الوقت: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
                        )
                    except Exception as e:
                        print(f"[WARNING] Could not notify admin {admin_id}: {e}")

            # حذف النسخ القديمة (المحتفظ بآخر 7 نسخ)
            await cleanup_old_backups()

        else:
            raise FileNotFoundError(f"Database file not found: {db_path}")

    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Backup failed: {error_msg}")

        # تسجيل الخطأ
        with session_scope() as session:
            backup = Backup(
                filename=f"backup_failed_{timestamp}",
                file_path="",
                file_size=0,
                status="failed",
                error_message=error_msg
            )
            session.add(backup)
            session.commit()

        # إشعار الإدمن بالفشل
        if application:
            for admin_id in Config.ADMIN_IDS:
                try:
                    await application.bot.send_message(
                        chat_id=admin_id,
                        text=f"❌ **فشل إنشاء النسخة الاحتياطية**\n\n"
                             f"الخطأ: {error_msg}\n"
                             f"الوقت: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
                    )
                except Exception:
                    pass


async def cleanup_old_backups():
    """حذف النسخ الاحتياطية القديمة (المحتفظ بآخر 7 نسخ فقط)"""
    try:
        backup_dir = "backups"

        if not os.path.exists(backup_dir):
            return

        # الحصول على قائمة النسخ
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.startswith("bot_backup_") and filename.endswith(".db"):
                path = os.path.join(backup_dir, filename)
                backups.append({
                    "filename": filename,
                    "path": path,
                    "mtime": os.path.getmtime(path)
                })

        # ترتيب حسب التاريخ (الأحدث أولاً)
        backups.sort(key=lambda x: x["mtime"], reverse=True)

        # حذف النسخ القديمة
        deleted_count = 0
        for backup in backups[7:]:  # الاحتفاظ بـ 7 نسخ
            try:
                os.remove(backup["path"])
                deleted_count += 1
                print(f"[INFO] Deleted old backup: {backup['filename']}")
            except Exception as e:
                print(f"[WARNING] Could not delete {backup['filename']}: {e}")

        if deleted_count > 0:
            print(f"[INFO] Cleaned up {deleted_count} old backup(s)")

    except Exception as e:
        print(f"[ERROR] Backup cleanup failed: {e}")


async def cleanup_old_data(application=None):
    """تنظيف البيانات القديمة"""
    try:
        # حذف السجلات القديمة (أقدم من 90 يوم)
        cutoff_date = datetime.utcnow() - timedelta(days=90)

        with session_scope() as session:
            # حذف معاملات مكتملة قديمة
            from database import Transaction
            old_transactions = session.query(Transaction).filter(
                Transaction.created_at < cutoff_date,
                Transaction.status == "completed"
            ).all()

            deleted_count = len(old_transactions)
            for trans in old_transactions:
                session.delete(trans)

            session.commit()

        print(f"[INFO] Cleaned up {deleted_count} old transaction(s)")

        # إشعار الإدمن
        if application:
            for admin_id in Config.ADMIN_IDS:
                try:
                    await application.bot.send_message(
                        chat_id=admin_id,
                        text=f"🧹 **تم تنظيف البيانات القديمة**\n\n"
                             f"• المعاملات المحذوفة: {deleted_count}\n"
                             f"• تاريخ الحذف: قبل {cutoff_date.strftime('%Y-%m-%d')}\n"
                             f"• الوقت: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
                    )
                except Exception:
                    pass

    except Exception as e:
        print(f"[ERROR] Data cleanup failed: {e}")

        if application:
            for admin_id in Config.ADMIN_IDS:
                try:
                    await application.bot.send_message(
                        chat_id=admin_id,
                        text=f"❌ **فشل تنظيف البيانات**\n\nالخطأ: {str(e)}"
                    )
                except Exception:
                    pass


async def update_user_stats(application=None):
    """تحديث إحصائيات المستخدمين"""
    try:
        with session_scope() as session:
            # تحديث عدد الإحالات لكل مستخدم
            users = session.query(User).all()

            updated_count = 0
            for user in users:
                # حساب عدد الإحالات الفعلي
                referral_count = session.query(User).filter(
                    User.referred_by == user.referral_code
                ).count()

                if user.referral_count != referral_count:
                    user.referral_count = referral_count
                    updated_count += 1

            session.commit()

        if updated_count > 0:
            print(f"[INFO] Updated stats for {updated_count} user(s)")

    except Exception as e:
        print(f"[ERROR] Stats update failed: {e}")


# دوال مساعدة للإدارة

async def manual_backup(update, context):
    """إنشاء نسخة احتياطية يدوية (للإدمن)"""
    user_id = update.effective_user.id

    if user_id not in Config.ADMIN_IDS:
        await update.message.reply_text("❌ ليس لديك صلاحية.")
        return

    await update.message.reply_text("🔄 جاري إنشاء النسخة الاحتياطية...")
    await create_backup(context.application)
    await update.message.reply_text("✅ تم إنشاء النسخة الاحتياطية!")


async def list_backups(update, context):
    """عرض قائمة النسخ الاحتياطية (للإدمن)"""
    user_id = update.effective_user.id

    if user_id not in Config.ADMIN_IDS:
        await update.message.reply_text("❌ ليس لديك صلاحية.")
        return

    with session_scope() as session:
        backups = session.query(Backup).order_by(
            Backup.created_at.desc()
        ).limit(10).all()

    if not backups:
        await update.message.reply_text("لا توجد نسخ احتياطية.")
        return

    text = "📦 **النسخ الاحتياطية:**\n\n"

    for backup in backups:
        status = "✅" if backup.status == "success" else "❌"
        size_mb = backup.file_size / (1024 * 1024)
        text += (
            f"{status} `{backup.filename}`\n"
            f"   الحجم: {size_mb:.2f} MB\n"
            f"   التاريخ: {backup.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        )

    await update.message.reply_text(text, parse_mode="Markdown")


async def restore_backup(update, context):
    """استعادة نسخة احتياطية (للإدمن) - تحذير: خطرة"""
    user_id = update.effective_user.id

    if user_id not in Config.ADMIN_IDS:
        await update.message.reply_text("❌ ليس لديك صلاحية.")
        return

    await update.message.reply_text(
        "⚠️ **تحذير!**\n\n"
        "استعادة النسخة الاحتياطية ستستبدل قاعدة البيانات الحالية.\n"
        "استخدم الأمر: `/restorebackup FILENAME`\n\n"
        "**لا يمكن التراجع عن هذه العملية!**"
    )


def shutdown_scheduler():
    """إيقاف المجدول"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        print("[INFO] Scheduler shut down")
