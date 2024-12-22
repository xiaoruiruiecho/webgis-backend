import settings
from extensions import db
from models.role import Role
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(32), unique=True, nullable=False)
    user_name = db.Column(db.String(32), nullable=False)
    user_password = db.Column(db.String(512), nullable=False)

    user_tel = db.Column(db.String(32))
    user_sex = db.Column(db.String(32))
    user_address = db.Column(db.String(128))
    user_position = db.Column(db.String(128))

    # 关系引用 (一对一)
    precinct = db.relationship('Precinct', backref='user')

    @property
    def user_roles(self) -> [Role]:
        user_roles = UserRole.query.filter_by(user_id=self.user_id).all()
        return [Role.query.get(user_role.role_name) for user_role in user_roles]

    def serialize(self):
        return {
            'user_id': self.user_id,
            'user_email': self.user_email,
            'user_name': self.user_name,
            'user_tel': self.user_tel,
            'user_sex': self.user_sex,
            'user_address': self.user_address,
            'user_position': self.user_position,
            'user_roles': [user_role.role_name for user_role in self.user_roles]
        }

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.encrypt_password()

    def encrypt_password(self):
        self.user_password = generate_password_hash(self.user_password)

    def check_password(self, password):
        return check_password_hash(self.user_password, password)

    def update_password(self, password):
        self.user_password = generate_password_hash(password)

    def commit_add(self, roles: [Role] = None):
        db.session.add(self)
        db.session.commit()

        if roles:
            self.add_roles(roles)
        else:
            if self.user_email in settings.ADMINISTRATOR_EMAILS:
                self.add_roles([Role.administrator()])
            elif self.user_email in settings.MANAGER_EMAILS:
                self.add_roles([Role.manager(), Role.user()])
            else:
                self.add_roles([Role.user()])

    def reset_roles(self):
        user_roles = UserRole.query.filter_by(user_id=self.user_id).all()
        for user_role in user_roles:
            db.session.delete(user_role)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def add_roles(self, roles: [Role]):
        for role in roles:
            user_role = UserRole(user_id=self.user_id, role_name=role.role_name)
            db.session.add(user_role)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # TODO: 但是 user 并未删除 ?
            raise e

    def update_roles(self, roles: [Role]):
        try:
            self.reset_roles()
            self.add_roles(roles)
        except Exception as e:
            raise e

    @staticmethod
    def init_static_data():
        datas = [
            (1, 'admin@163.com', '超级管理员', 'webgis'),
            (2, 'yy_manager1@163.com', '友谊管理员1', 'yy1'),
            (3, 'yy_manager2@163.com', '友谊管理员2', 'yy2'),
            (4, 'yy_manager3@163.com', '友谊管理员3', 'yy3'),
            (5, '597_manager1@163.com', '597管理员1', '5971'),
            (6, '597_manager2@163.com', '597管理员2', '5972'),
            (7, '597_manager3@163.com', '597管理员3', '5973'),
            (8, 'user1@163.com', 'user1', 'user1'),
            (9, 'user2@163.com', 'user2', 'user2'),
            (10, 'user3@163.com', 'user3', 'user3'),
        ]

        try:
            for data in datas:
                user = User(user_id=data[0], user_email=data[1], user_name=data[2], user_password=data[3])
                user.commit_add()

            print("SUCCESS!!!: models.py -> class User -> init_static_data()")
        except Exception as e:
            db.session.rollback()
            print("ERROR!!!: models.py -> class User -> init_static_data()")
            print(e)


class UserRole(db.Model):
    __tablename__ = 'user_role'

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    role_name = db.Column(db.String(64), db.ForeignKey('role.role_name'), primary_key=True)

    def serialize(self):
        return {
            'user_id': self.user_id,
            'role_name': self.role_name
        }
