from functools import wraps

from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request

from extensions import redis_client
from utils import get_current_user


# 自定义装饰器，检查 JWT 是否有效并且是否存在于 Redis 中
def jwt_required_with_redis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 1. 获取当前的 JWT token
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"msg": "Missing Authorization Header"}), 401

        # 2. 验证 JWT 是否有效
        try:
            # 这一步会验证 JWT 的签名和过期时间
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({"msg": f"Invalid or expired token: {str(e)}"}), 401

        # 3. 检查 token 是否在 Redis 中存在
        if not redis_client.get(token):
            return jsonify({"msg": "Invalid or expired token"}), 401

        # 如果 token 在 Redis 中存在，继续执行原始的视图函数
        return func(*args, **kwargs)

    return wrapper


def permission_required(desired_permissions: [int]):
    """
    Takes an ability (a string name of either a role or an ability) and returns the function if the user has that ability
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            user_permissions = 0
            current_user = get_current_user()

            for role in current_user.user_roles:
                user_permissions |= role.role_permissions

            desired_perms = 0
            for desired_permission in desired_permissions:
                desired_perms |= desired_permission

            if user_permissions & desired_perms == desired_perms:  # 必须满足全部的权限
                return func(*args, **kwargs)
            else:
                return jsonify({"msg": "No Permission"}), 403

        return inner

    return wrapper


def role_required(desired_roles: [str]):
    """
    Takes a role (a string name of either a role or an ability) and returns the function if the user has that role
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            current_user = get_current_user()

            for role in current_user.user_roles:
                for desired_role in desired_roles:
                    if desired_role == role.role_name:  # 有一个符合的角色即可
                        return func(*args, **kwargs)
            else:
                return jsonify({"msg": "No Permission"}), 403

        return inner

    return wrapper
