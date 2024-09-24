from flask import Flask, render_template, redirect, url_for, request
import hashlib
import os
import requests

app = Flask(__name__)
app.debug = True

def get_unique_id():
    try:
        # Generate a unique ID based on the user's IP address and User-Agent (browser info)
        user_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'unknown')
        
        # Combine IP and User-Agent and hash it to generate a unique identifier
        unique_string = user_ip + user_agent
        return hashlib.sha256(unique_string.encode()).hexdigest()
    except Exception as e:
        return f"Error generating unique ID: {e}"

def check_permission(unique_key, user_ip):
    try:
        response = requests.get("https://pastebin.com/raw/3h2v25aR")
        if response.status_code == 200:
            data = response.text
            permission_list = [line.strip() for line in data.split("\n") if line.strip()]
            
            # Check if both unique_key and user_ip are in the permission list
            for entry in permission_list:
                if unique_key in entry and user_ip in entry:
                    return True  # Approved
            return False  # Not approved yet
        else:
            return False  # Failed to fetch permissions list
    except Exception as e:
        return f"Error checking permission: {e}"

@app.route('/')
def index():
    unique_key = get_unique_id()  # Generate unique key for the user
    user_ip = request.remote_addr  # Get user IP
    return render_template('index.html', unique_key=unique_key, user_ip=user_ip)

@app.route('/check_approval/<unique_key>/<user_ip>', methods=['GET'])
def check_approval(unique_key, user_ip):
    if check_permission(unique_key, user_ip):
        return redirect(url_for('approved'))  # Redirect to approval page
    else:
        return render_template('not_approved.html', unique_key=unique_key, user_ip=user_ip)  # Stay on approval check

@app.route('/approved')
def approved():
    return render_template('approved.html')  # Show approved page

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=port, debug=True)
