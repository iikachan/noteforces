"""
密码修改模块
独立模块，只包含修改密码核心功能
使用方法：在 app.py 中导入并调用 setup_password_change(app, db, User)
"""

from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def json_response(code=0, msg='ok', data=None, status=200):
    """统一 JSON 响应格式"""
    return jsonify({'code': code, 'msg': msg, 'data': data or {}}), status

def setup_password_change(app, db, User):
    """
    在现有 Flask 应用中设置密码修改路由

    参数:
        app: Flask 应用实例
        db: SQLAlchemy 数据库实例
        User: 用户模型类
    """

    @app.route('/user/changePassword', methods=['POST'])
    def change_password():
        """
        修改用户密码接口
        请求格式:
        {
            "oldPassword": "旧密码",
            "newPassword": "新密码"
        }
        """
        try:
            # 获取请求数据
            data = request.get_json(silent=True) or {}
            old_password = data.get('oldPassword')
            new_password = data.get('newPassword')

            # 参数验证
            if not old_password:
                return json_response(4003, '旧密码不能为空', status=400)

            if not new_password:
                return json_response(4003, '新密码不能为空', status=400)

            if len(new_password) < 6:
                return json_response(4003, '新密码长度至少为6位', status=400)

            # 获取当前用户（使用 app.py 中的认证方式）
            auth = request.headers.get('Authorization')
            if not auth or not auth.startswith("Bearer "):
                return json_response(4001, '未登录', status=401)

            token = auth.split(" ", 1)[1]
            user = User.query.filter_by(token=token).first()

            if not user:
                return json_response(4001, '无效的 token', status=401)

            # 验证旧密码
            # 检查是否有 check_password 方法
            if hasattr(user, 'check_password'):
                if not user.check_password(old_password):
                    return json_response(4003, '旧密码错误', status=400)
            else:
                # 使用 Werkzeug 的 check_password_hash
                if not check_password_hash(user.password, old_password):
                    return json_response(4003, '旧密码错误', status=400)

            # 检查新旧密码是否相同
            if old_password == new_password:
                return json_response(4003, '新密码不能与旧密码相同', status=400)

            # 更新密码
            if hasattr(user, 'set_password'):
                user.set_password(new_password)
            else:
                # 使用 Werkzeug 的 generate_password_hash
                user.password = generate_password_hash(new_password)

            # 保存到数据库
            db.session.commit()

            # 记录日志
            logger.info(f'用户 {user.username} (ID: {user.id}) 修改密码成功')

            return json_response(0, '密码修改成功')

        except Exception as e:
            logger.error(f'修改密码时发生错误: {str(e)}')
            db.session.rollback()
            return json_response(5000, '服务器内部错误', status=500)