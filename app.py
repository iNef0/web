from flask import Flask, request, redirect, render_template
import requests
import json
import os

app = Flask(__name__)

# قراءة الإعدادات من متغيرات البيئة
config = {
    'client_id': os.environ.get('CLIENT_ID'),
    'client_secret': os.environ.get('CLIENT_SECRET'),
    'token': os.environ.get('BOT_TOKEN'),
    'scope': os.environ.get('SCOPE', 'identify%20guilds.join')
}

@app.route('/')
def index():
    return "Discord Auth Bot is running!"

@app.route('/auth/discord/callback/<endpoint>')
def callback(endpoint):
    code = request.args.get('code')
    
    if not code:
        return """
        <h1>❌ Error</h1>
        <p>No verification code received.</p>
        <a href="javascript:window.close()">Close Window</a>
        """
    
    try:
        # استبدال الكود بتوكن
        data = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': f"https://web-ji8b.onrender.com/auth/discord/callback/{endpoint}",
            'scope': config['scope']
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # جلب بيانات المستخدم
            headers = {'Authorization': f"Bearer {token_data['access_token']}"}
            user_response = requests.get('https://discord.com/api/users/@me', headers=headers)
            user_data = user_response.json()
            
            # حفظ البيانات
            try:
                with open('data.json', 'r') as f:
                    data_file = json.load(f)
            except:
                data_file = {'users': {}}
            
            data_file['users'][str(user_data['id'])] = {
                'username': user_data['username'],
                'discriminator': user_data['discriminator'],
                'avatar': user_data.get('avatar', ''),
                'access_token': token_data['access_token'],
                'refresh_token': token_data['refresh_token']
            }
            
            with open('data.json', 'w') as f:
                json.dump(data_file, f, indent=4)
            
            # محاولة إضافة المستخدم للسيرفر
            if 'guilds.join' in config['scope']:
                headers = {
                    'Authorization': f"Bot {config['token']}",
                    'Content-Type': 'application/json'
                }
                join_data = {'access_token': token_data['access_token']}
                
                # إضافة للسيرفر الرئيسي
                requests.put(f'https://discord.com/api/guilds/{endpoint}/members/{user_data["id"]}', 
                           headers=headers, json=join_data)
            
            return """
            <h1>✅ Verification Successful!</h1>
            <p>You have been verified successfully.</p>
            <p>You can close this window now.</p>
            <script>
                setTimeout(() => window.close(), 3000);
            </script>
            """
        else:
            return f"""
            <h1>❌ Verification Failed</h1>
            <p>Error: {response.text}</p>
            <a href="javascript:window.close()">Close Window</a>
            """
            
    except Exception as e:
        return f"""
        <h1>❌ Server Error</h1>
        <p>Error: {str(e)}</p>
        <a href="javascript:window.close()">Close Window</a>
        """

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
