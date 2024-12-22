from extensions import db
from models.permission import Permission


class Role(db.Model):
    __tablename__ = 'role'

    role_name = db.Column(db.String(64), primary_key=True, nullable=False)
    role_permissions = db.Column(db.Integer, default=0)

    ADMINISTRATOR = 'Administrator'
    MANAGER = 'Manager'
    USER = 'User'

    def serialize(self):
        return {
            'role_name': self.role_name,
            'role_permissions': self.role_permissions,
        }

    # @property 返回单个对象为 property ?
    # @property 返回多个对象为 list<class> ?
    @classmethod
    def administrator(cls):
        return cls.query.get(cls.ADMINISTRATOR)

    @classmethod
    def manager(cls):
        return cls.query.get(cls.MANAGER)

    @classmethod
    def user(cls):
        return cls.query.get(cls.USER)

    @classmethod
    def get(cls, role_name):
        return cls.query.get(role_name)

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.role_permissions += perm
            db.session.commit()  # TODO: useful?

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.role_permissions -= perm
            db.session.commit()  # TODO: useful?

    def reset_permissions(self):
        self.role_permissions = 0
        db.session.commit()

    def has_permission(self, perm):
        return self.role_permissions & perm == perm

    @staticmethod
    def init_static_data():
        roles = {
            'User': [Permission.Perm1, Permission.Perm2, Permission.Perm3],
            'Manager': [Permission.Perm4, Permission.Perm5, Permission.Perm6, Permission.Perm7],
            'Administrator': [Permission.Perm8, Permission.Perm9, Permission.Perm10],
        }

        for role_name in roles:
            role_permissions = 0

            for perm in roles[role_name]:
                role_permissions += perm

            role = Role(role_name=role_name, role_permissions=role_permissions)
            db.session.add(role)

        try:
            db.session.commit()
            print("SUCCESS!!!: models.py -> class Role -> init_static_data()")
        except Exception as e:
            db.session.rollback()
            print("ERROR!!!: models.py -> class Role -> init_static_data()")
            print(e)
