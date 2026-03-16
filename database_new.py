# -*- coding: utf-8 -*-
"""
قاعدة بيانات محسنة مع session_scope
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, contextmanager
from datetime import datetime
import uuid
import os

Base = declarative_base()

class User(Base):
    """جدول المستخدمين"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    balance = Column(Float, default=0.0)
    referral_code = Column(String(20), unique=True)
    referred_by = Column(String(20))
    referral_count = Column(Integer, default=0)
    referral_earnings = Column(Float, default=0.0)
    total_bets = Column(Float, default=0.0)
    total_wins = Column(Float, default=0.0)
    vip_level = Column(String(20), default='beginner')
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    ichancy_username = Column(String(100))  # اسم المستخدم في Ichancy
    ichancy_password = Column(String(255))  # كلمة المرور في Ichancy
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    transactions = relationship("Transaction", back_populates="user")

class Transaction(Base):
    """جدول المعاملات المالية"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    transaction_type = Column(String(30), nullable=False)  # deposit, withdraw, referral, gift
    amount = Column(Float, nullable=False)
    method = Column(String(50))  # syriatel_cash, bank, usdt
    status = Column(String(20), default='pending')  # pending, completed, failed, cancelled
    description = Column(Text)
    admin_notes = Column(Text)
    external_transaction_id = Column(String(100))  # معرف المعاملة الخارجية
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # العلاقات
    user = relationship("User", back_populates="transactions")

class DatabaseManager:
    """مدير قاعدة البيانات المحسن"""
    
    def __init__(self, database_url=None):
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///data/telegram_bot.db")
        
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.func = func
        
    def create_tables(self):
        """إنشاء الجداول"""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """الحصول على جلسة قاعدة البيانات"""
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """Session scope لضمان إغلاق الجلسة"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def generate_referral_code(self):
        """توليد كود إحالة فريد"""
        return str(uuid.uuid4())[:8].upper()
        
    def create_user(self, telegram_id, username=None, first_name=None, last_name=None):
        """إنشاء مستخدم جديد"""
        with self.session_scope() as session:
            # التحقق من وجود المستخدم
            existing_user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
            if existing_user:
                return existing_user
                
            # إنشاء مستخدم جديد
            referral_code = self.generate_referral_code()
            while session.query(User).filter(User.referral_code == referral_code).first():
                referral_code = self.generate_referral_code()
                
            user = User(
                telegram_id=str(telegram_id),
                username=username,
                first_name=first_name,
                last_name=last_name,
                referral_code=referral_code
            )
            session.add(user)
            session.flush()  # للحصول على ID بدون commit
            return user
            
    def get_user(self, telegram_id):
        """الحصول على مستخدم بواسطة telegram_id"""
        with self.session_scope() as session:
            user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
            if user:
                # تحديث آخر نشاط
                user.last_activity = datetime.utcnow()
            return user

# إنشاء نسخة عالمية
db_manager = DatabaseManager()

# دالة مساعدة للاستخدام في الوحدات الأخرى
def session_scope():
    """Session scope عالمي"""
    return db_manager.session_scope()

# تصدير الكائنات المطلوبة
__all__ = [
    'Base', 'User', 'Transaction', 'DatabaseManager', 
    'db_manager', 'session_scope'
]
