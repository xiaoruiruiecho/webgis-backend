# commands.py
from extensions import db
from flask.cli import AppGroup
from models.region import Region, Crop, Precinct, Device
from models.role import Role
from models.user import User
from models.information import Service, Weather, Soil


def init_command(app):
    # 创建一个命令组
    cli = AppGroup('init')

    @cli.command('reset')
    def init_reset_data():
        """
        清空并删除所有表
        """
        db.drop_all()

        print('SUCCESS!!!: flask init reset')

    @cli.command('static')
    def init_static_data():
        """
        重建所有表, 初始化静态数据
        """
        db.drop_all()
        db.create_all()

        Role.init_static_data()
        User.init_static_data()

        Region.init_static_data()
        Crop.init_static_data()
        Precinct.init_static_data()
        Device.init_static_data()

        Weather.init_static_data('./static/YY_weather_2023.xls', 1)
        Soil.init_static_data('./static/YY_soil_2023.xls')
        Service.init_static_data()

        print('SUCCESS!!!: flask init static')

    app.cli.add_command(cli)
