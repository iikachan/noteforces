from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    return jsonify({'message': 'Login successful'}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

# 自动化测试
def run_tests():
    print('Running automated tests...')
    client = app.test_client()

    # 清空数据库测试
    with app.app_context():
        db.drop_all()
        db.create_all()

    cases = []

    cases.append({
        'name': 'register-success',
        'method': 'post',
        'path': '/register',
        'json': {'username': 'alice', 'password': 'password123'},
        'expected_status': 201
    })

    cases.append({
        'name': 'register-duplicate',
        'method': 'post',
        'path': '/register',
        'json': {'username': 'alice', 'password': 'password123'},
        'expected_status': 400
    })

    cases.append({
        'name': 'register-missing',
        'method': 'post',
        'path': '/register',
        'json': {'username': 'bob'},
        'expected_status': 400
    })

    cases.append({
        'name': 'login-success',
        'method': 'post',
        'path': '/login',
        'json': {'username': 'alice', 'password': 'password123'},
        'expected_status': 200
    })

    cases.append({
        'name': 'login-wrong-pass',
        'method': 'post',
        'path': '/login',
        'json': {'username': 'alice', 'password': 'wrong'},
        'expected_status': 401
    })

    cases.append({
        'name': 'login-no-user',
        'method': 'post',
        'path': '/login',
        'json': {'username': 'charlie', 'password': 'x'},
        'expected_status': 401
    })

    cases.append({
        'name': 'health',
        'method': 'get',
        'path': '/health',
        'json': None,
        'expected_status': 200
    })

    all_passed = True
    for c in cases:
        if c['method'] == 'post':
            res = client.post(c['path'], json=c['json'])
        else:
            res = client.get(c['path'])

        status = res.status_code
        ok = status == c['expected_status']
        all_passed = all_passed and ok
        print(f"{c['name']}: expected {c['expected_status']}, got {status} -> {'PASS' if ok else 'FAIL'}")
        try:
            print('  response:', res.get_json())
        except Exception:
            print('  response: <non-json>')

    print("\nAll tests passed." if all_passed else "\nSome tests failed.")

# 导入密码修改模块并设置路由
from password_change import setup_password_change
setup_password_change(app, db, User)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        run_tests()
    else:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
