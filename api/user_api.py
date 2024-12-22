from flask import request
from flask.views import MethodView
from flask_jwt_extended import create_access_token

from decorators import permission_required, role_required, jwt_required_with_redis
from extensions import db, redis_client
from models.region import Precinct
from models.pagebean import PageBean
from models.permission import Permission
from models.result import Result
from models.role import Role
from models.user import User, UserRole
from utils import get_current_user


class SignupApi(MethodView):
    """
    注册
    """

    def post(self):
        """
        用户注册
        """
        params = request.form  # x-www-form-urlencoded

        user_email = params.get('user_email')
        user_name = params.get('user_name')
        user_password = params.get('user_password')
        user_repassword = params.get('user_repassword')

        if not user_email or not user_name or not user_password or not user_repassword:
            return Result.error('参数不足')

        user = User.query.filter_by(user_email=user_email).first()

        if user:
            return Result.error("该用户已注册!")

        user = User(user_email=user_email, user_name=user_name, user_password=user_password)

        try:
            user.commit_add()
        except Exception as e:
            db.session.rollback()
            print(e)
            return Result.error('注册失败')

        return Result.success()


class SigninApi(MethodView):
    """
    登录
    """

    def post(self):
        """
        用户登录
        """
        params = request.json

        user_email = params.get('user_email')
        user_password = params.get('user_password')

        if not user_email or not user_password:
            return Result.error('参数不足')

        user = User.query.filter_by(user_email=user_email).first()
        if not user:
            return Result.error("用户不存在, 请先注册!")

        if user.check_password(user_password):
            token = 'Bearer ' + create_access_token(identity=str(user.user_id))

            redis_client.set(token, token)

            return Result.success(data=token)

        return Result.error('邮箱或密码错误')


class UserInfoApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.USER, Role.MANAGER, Role.ADMINISTRATOR])
    def get(self):
        user = get_current_user()
        data = user.serialize()
        data.pop('user_id')

        return Result.success(data=data)

    @jwt_required_with_redis
    @role_required([Role.USER, Role.MANAGER, Role.ADMINISTRATOR])
    def put(self):
        params = request.json
        user_name = params.get('user_name')
        user_sex = params.get('user_sex')
        user_tel = params.get('user_tel')
        user_address = params.get('user_address')
        user_position = params.get('user_position')

        user = get_current_user()
        user.user_name = user_name
        user.user_sex = user_sex
        user.user_tel = user_tel
        user.user_address = user_address
        user.user_position = user_position

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return Result.error('修改个人信息失败')

        return Result.success()

    @jwt_required_with_redis
    @role_required([Role.USER, Role.MANAGER, Role.ADMINISTRATOR])
    def patch(self):
        params = request.form

        user_old_password = params.get('user_old_password')
        user_new_password = params.get('user_new_password')
        user_re_password = params.get('user_re_password')

        if not user_old_password or not user_new_password or not user_re_password:
            return Result.error('缺少参数')

        user = get_current_user()
        if not user.check_password(user_old_password):
            return Result.error('原密码不正确')

        if user_new_password != user_re_password:
            return Result.error('两次密码不一致')

        user.update_password(user_new_password)

        try:
            db.session.commit()

            token = request.headers.get('Authorization')
            redis_client.delete(token)
        except Exception as e:
            db.session.rollback()
            print(e)
            return Result.error('修改密码失败')

        return Result.success()


class UserApi(MethodView):
    """
    后台用户管理
    """

    @jwt_required_with_redis
    @role_required([Role.ADMINISTRATOR])
    def get(self):
        """
        获取所有用户
        """
        args = request.args
        user_email = args.get('user_email', '')

        if user_email == '':
            users = User.query.order_by(User.user_id).all()
        else:
            users = User.query.filter(User.user_email.like('%' + user_email + '%')).all()

        data = [user.serialize() for user in users]

        return Result.success(data=PageBean.data(data, len(users)))

    @jwt_required_with_redis
    @role_required([Role.ADMINISTRATOR])
    def post(self):
        """
        新增用户
        """
        params = request.json  # x-www-form-urlencoded ?

        user_email = params.get('user_email')
        user_password = params.get('user_password')
        user_repassword = params.get('user_repassword')
        user_roles = [Role.get(role) for role in params.get('user_roles') if role != Role.ADMINISTRATOR]

        if not user_email or not user_password or not user_repassword:
            return Result.error('参数不足')

        user = User.query.filter_by(user_email=user_email).first()

        if user:
            return Result.error("该用户已注册!")

        user = User(user_email=user_email, user_password=user_password, user_name=user_email)

        try:
            user.commit_add(user_roles)
        except Exception as e:
            db.session.rollback()
            print(e)
            return Result.error('注册失败 (注意: 可能是用户注册成功, 角色未分配成功)')

        return Result.success()


class UserRoleApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.ADMINISTRATOR])
    def post(self):
        """
        更改用户角色
        """
        params = request.json

        user_email = params.get('user_email')
        user_roles = [Role.get(role) for role in params.get('user_roles') if role != Role.ADMINISTRATOR]

        user = User.query.filter_by(user_email=user_email).first()
        if not user:
            return Result.error('用户不存在')

        try:
            user.update_roles(user_roles)
        except Exception as e:
            print(e)
            return Result.error('更改角色失败')

        return Result.success()


class UserPrecinctApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.ADMINISTRATOR])
    def get(self):
        user_roles = UserRole.query.filter_by(role_name=Role.MANAGER).all()
        users = [User.query.get(user_role.user_id) for user_role in user_roles]

        data = []
        for user in users:
            precinct = Precinct.query.filter_by(user_id=user.user_id).first()
            data.append(user.serialize() | {'user_precinct': precinct.serialize() if precinct else None})

        return Result.success(data=PageBean.data(data=data, count=len(data)))

    @jwt_required_with_redis
    @role_required([Role.ADMINISTRATOR])
    def post(self):
        params = request.json

        user_id = int(params.get('user_id'))
        precinct_id = int(params.get('precinct_id', -1))

        user_role = UserRole.query.filter_by(user_id=user_id, role_name=Role.MANAGER).first()
        if not user_role:
            return Result.error('请选择管理员进行操作')

        self_precinct = Precinct.query.filter_by(user_id=user_id).first()

        if precinct_id == -1:  # 删除自己管理权限
            if self_precinct:
                self_precinct.user_id = None
        else:  # 分配管理区
            precinct = Precinct.query.get(precinct_id)

            if not precinct:
                return Result.error('请选择正确的管理区')
            elif precinct.user_id is not None:
                return Result.error(
                    '该管理区已有 "' + User.query.get(precinct.user_id).user_name + '" 管理, 请先删除其管理权限')

            if self_precinct:
                self_precinct.user_id = None
            precinct.user_id = user_id

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return Result.error()

        return Result.success()
