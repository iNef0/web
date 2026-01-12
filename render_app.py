# ملف app.py للـ Render
from flask import Flask, redirect, request
import requests
import json

app = Flask(__name__)

# قراءة config
with open('config.json', 'r') as f:
    config = json.load(f)

@app.route('/auth/discord/callback/<endpoint>')
def callback(endpoint):
    code = request.args.get('code')
    
    if not code:
        return redirect("https://discord.com/oauth2/authorize?...")
    
    # استبدال الكود بتوكن
    data = {
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': f"https://your-app.onrender.com/auth/discord/callback/{endpoint}",
        'scope': config['scope']
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    
    if r.status_code == 200:
        # حفظ البيانات
        token_data = r.json()
        
        # هنا يمكنك إرسال البيانات لبوتك عبر WebSocket أو API
        # أو حفظها في قاعدة بيانات
        
        return """
        <h1>✅ Verified Successfully!</h1>
        <p>You can now close this window.</p>
        """
    else:
        return "Error: Verification failed"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
