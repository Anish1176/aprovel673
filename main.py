from flask import Flask, render_template, redirect, url_for, request
import hashlib
import os
import requests

app = Flask(__name__)

def get_unique_id():
    try:
        # Generate unique ID based on system UID and login
        return hashlib.sha256((str(os.getuid()) + os.getlogin()).encode()).hexdigest()
    except Exception as e:
        return f"Error generating unique ID: {e}"

def get_user_ip():
    return request.remote_addr

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
    user_ip = get_user_ip()  # Get user IP
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
    app.run(host='0.0.0.0', port=3001)
