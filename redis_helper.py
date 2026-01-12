# إضافة في بداية app.py
import os
from flask import Flask, request
import requests
import json
import redis

# الاتصال بـ Redis (قاعدة بيانات مشتركة)
try:
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        password=os.environ.get('REDIS_PASSWORD'),
        decode_responses=True
    )
    # اختبار الاتصال
    r.ping()
    USE_REDIS = True
except:
    USE_REDIS = False

# دالة حفظ البيانات
def save_user_data(user_data):
    if USE_REDIS:
        r.hset('users', user_data['id'], json.dumps(user_data))
    else:
        # حفظ في ملف (قديم)
        try:
            with open('data.json', 'r') as f:
                data = json.load(f)
        except:
            data = {'users': {}}
        data['users'][user_data['id']] = user_data
        with open('data.json', 'w') as f:
            json.dump(data, f)

# دالة جلب البيانات
def get_user_data():
    if USE_REDIS:
        users = r.hgetall('users')
        return {'users': {k: json.loads(v) for k, v in users.items()}}
    else:
        try:
            with open('data.json', 'r') as f:
                return json.load(f)
        except:
            return {'users': {}}
