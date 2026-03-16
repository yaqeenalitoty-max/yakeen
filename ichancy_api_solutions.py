# -*- coding: utf-8 -*-
"""
حلول مشاكل API Ichancy
"""

import requests
from config import Config

def test_ichancy_endpoints():
    """اختبار جميع الـ endpoints الممكنة"""
    
    # تسجيل الدخول
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    login_data = {
        'username': Config.ICHANCY_AGENT_USERNAME,
        'password': Config.ICHANCY_AGENT_PASSWORD
    }
    
    session = requests.Session()
    session.headers.update(headers)
    response = session.post(f'{Config.ICHANCY_API_BASE}/User/signIn', json=login_data)
    
    if response.status_code != 200:
        print("❌ فشل تسجيل الدخول")
        return
    
    print("✅ تم تسجيل الدخول بنجاح")
    
    # قائمة الـ endpoints الممكنة
    endpoints = [
        # لجلب اللاعبين
        ('/Agent/players', 'GET'),
        ('/Agent/player/list', 'GET'),
        ('/Agent/players/list', 'GET'),
        ('/Player/list', 'GET'),
        ('/Player/listByAgent', 'GET'),
        ('/Agent/getPlayers', 'POST'),
        ('/Agent/playerList', 'POST'),
        
        # للبحث عن لاعب
        ('/Player/search', 'POST', {'username': 'Reemafree'}),
        ('/Agent/searchPlayer', 'POST', {'search': 'Reemafree'}),
        ('/Player/getPlayerByLogin', 'GET', {'login': 'Reemafree'}),
        ('/Player/getPlayerInfo', 'POST', {'username': 'Reemafree'}),
        
        # لإيداع الرصيد
        ('/Agent/deposit', 'POST', {'playerId': 1, 'amount': 10}),
        ('/Agent/addBalance', 'POST', {'playerId': 1, 'amount': 10}),
        ('/Agent/creditPlayer', 'POST', {'playerId': 1, 'amount': 10}),
        ('/Agent/depositToPlayer', 'POST', {'playerId': 1, 'amount': 10}),
        ('/Agent/depositToPlayerByUsername', 'POST', {'username': 'Reemafree', 'amount': 10}),
        ('/Player/updateBalance', 'POST', {'playerId': 1, 'amount': 10, 'type': 'deposit'}),
        ('/Transaction/create', 'POST', {'type': 'deposit', 'playerId': 1, 'amount': 10}),
    ]
    
    working_endpoints = []
    
    for endpoint_info in endpoints:
        if len(endpoint_info) == 2:
            endpoint, method = endpoint_info
            data = None
        else:
            endpoint, method, data = endpoint_info
        
        try:
            if method == 'GET':
                if data:
                    resp = session.get(f'{Config.ICHANCY_API_BASE}{endpoint}', params=data)
                else:
                    resp = session.get(f'{Config.ICHANCY_API_BASE}{endpoint}')
            else:
                resp = session.post(f'{Config.ICHANCY_API_BASE}{endpoint}', json=data)
            
            # التحقق من الاستجابة
            if resp.status_code == 200:
                response_text = resp.text
                if 'result' in response_text and response_text.count('null') < 3 and len(response_text) > 50:
                    working_endpoints.append((endpoint, method, response_text[:200]))
                    print(f"✅ {method} {endpoint}: {response_text[:100]}...")
        except Exception as e:
            pass
    
    print(f"\n🎯 تم العثور على {len(working_endpoints)} endpoint يعمل:")
    for endpoint, method, response in working_endpoints:
        print(f"  - {method} {endpoint}")
    
    return working_endpoints

def alternative_deposit_solution(username, amount):
    """حل بديل لإيداع الرصيد باستخدام Selenium"""
    print(f"""
🔧 حل بديل مقترح لإيداع الرصيد:

1. استخدام Selenium للوصول إلى https://agents.ichancy.com/players/players
2. تسجيل الدخول تلقائياً
3. البحث عن اللاعب: {username}
4. إيداع المبلغ: {amount}
5. تأكيد العملية

المميزات:
- ✅ يعمل مثل الإنسان تماماً
- ✅ يتجاوز مشاكل API
- ✅ يمكنه التعامل مع واجهة الويب المعقدة

العيوب:
- ❌ أبطأ من API
- ❌ يحتاج إلى تثبيت Selenium و WebDriver
""")

def manual_solution():
    """حل يدوي مؤقت"""
    print(f"""
📋 الحل اليدوي المؤقت:

1. عند موافقة الأدمن على الإيداع:
   - يتم إضافة الرصيد في البوت ✅
   - يتم إشعار المستخدم ✅
   - يتم إشعار الأدمن بفشل الإيداع في Ichancy ⚠️

2. يقوم الأدمن يدوياً:
   - الدخول إلى https://agents.ichancy.com/players/players
   - البحث عن اسم المستخدم
   - إيداع الرصيد يدوياً

3. يمكن إضافة زر "إيداع يدوي" في لوحة الأدمن لتسهيل العملية
""")

if __name__ == "__main__":
    print("🔍 اختبار endpoints Ichancy API...")
    test_ichancy_endpoints()
    print("\n" + "="*50)
    alternative_deposit_solution("Reemafree", 10)
    print("\n" + "="*50)
    manual_solution()
