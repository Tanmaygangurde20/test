from flask import Flask, render_template, request, render_template_string
import random
import os
import pickle
import base64

app = Flask(__name__)
user_count, bot_count = 0, 0
name = None
imgs = ['Rock.jpg', 'Paper.jpg', 'Scissors.jpg']

# ==========================================
# VULNERABLE SECRETS (Scanner should flag)
# ==========================================
AWS_SECRET_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
DATABASE_PASSWORD = "super_secret_admin_password_123!"


# ==========================================
# ORIGINAL GAME ROUTES
# ==========================================
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    global name
    msg = f"Hello👋 {name}, Choose your Next Move ⏩!"
    if request.form.get('username'):
        name = request.form.get('username')
        msg=f"Hello👋, {name}! Choose Your Move ✅!"
    return render_template('index.html', msg=msg, name=name, imgs=imgs)

@app.route('/game', methods=['POST'])
def game():
    global user_count, bot_count, name
    ind = int(request.form.get('ind'))
    sel_img = []
    sel_img.append(imgs[ind])
    sel_img.append(random.choice(imgs))
    msg = "Hello👋!"
    if sel_img[0] == sel_img[1]:
        msg = "Draw 😐, Retry 🔄️"
    elif (sel_img[0] == 'Paper.jpg' and sel_img[1] == 'Rock.jpg') or (sel_img[0] == 'Rock.jpg' and sel_img[1] == 'Scissors.jpg') or (sel_img[0] == 'Scissors.jpg' and sel_img[1] == 'Paper.jpg'):
        user_count += 1
        msg = f"{name}🫅 Win!"
    elif (sel_img[0] == 'Paper.jpg' and sel_img[1] =='Scissors.jpg') or (sel_img[0] == 'Rock.jpg' and sel_img[1] == 'Paper.jpg') or (sel_img[0] == 'Scissors.jpg' and sel_img[1] == 'Rock.jpg'):
        bot_count += 1
        msg = "Bot🤖 Win!"
    else:
        msg = "Undefined"
        
    win_msg = None
    if user_count >= 3 or bot_count >= 3:
        if user_count >= 3:
            win_msg = f"Congratulations🎉 {name}, You are the Winner🫅!"
        else:
            win_msg = f"Better Luck Next time🤝 {name}, Bot🤖 Wins!"
            
        tu_cnt, tb_cnt = user_count, bot_count
        user_count, bot_count = 0, 0
        return render_template('index.html', win_msg=win_msg, name=name, tu_cnt=tu_cnt, tb_cnt=tb_cnt, msg=f"{win_msg}", sel_img=None, imgs=None)
        
    return render_template('index.html', msg=msg, sel_img=sel_img, user_count=user_count, bot_count=bot_count, name=name, imgs=None)


# ==========================================
# VULNERABLE ROUTES FOR SCANNER TESTING
# ==========================================
@app.route('/hello_test')
def hello_test():
    # VULNERABILITY 1: Server-Side Template Injection (SSTI) / XSS
    user_input = request.args.get('name', 'Guest')
    template = f"<h1>Hello {user_input}!</h1>"
    return render_template_string(template)

@app.route('/ping_test')
def ping_test():
    # VULNERABILITY 2: OS Command Injection
    target_ip = request.args.get('ip', '127.0.0.1')
    os.system(f"ping -c 1 {target_ip}")
    return f"Ping command executed for {target_ip}"

@app.route('/load_state')
def load_state():
    # VULNERABILITY 3: Insecure Deserialization
    state_data = request.args.get('state')
    if state_data:
        decoded_data = base64.b64decode(state_data)
        obj = pickle.loads(decoded_data) 
        return "State loaded successfully!"
    return "No state provided."

@app.route('/db_connect')
def db_connect():
    # VULNERABILITY 4: Exposing Hardcoded Secrets
    return f"Connected to DB using password: {DATABASE_PASSWORD}"

if __name__ == '__main__':
    app.run(debug=True)
