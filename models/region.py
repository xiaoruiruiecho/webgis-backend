from extensions import db


class Region(db.Model):
    __tablename__ = 'region'

    region_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region_name = db.Column(db.String(64), unique=True, nullable=False)
    region_lon = db.Column(db.Float, nullable=False)
    region_lat = db.Column(db.Float, nullable=False)

    # 关系引用 (一对多)
    region_fields = db.relationship('Field', backref='region', lazy=True)
    region_precincts = db.relationship('Precinct', backref='region', lazy=True)
    region_devices = db.relationship('Device', backref='region', lazy=True)
    region_weathers = db.relationship('Weather', backref='region', lazy=True)
    region_services = db.relationship('Service', backref='region', lazy=True)

    def serialize(self):
        return {
            'region_id': self.region_id,
            'region_name': self.region_name,
            'region_lonlat': [self.region_lon, self.region_lat]
        }

    @staticmethod
    def init_static_data():
        datas = [
            (1, 'YY', 132.00, 46.83),
            (2, '597', 132.01, 46.82),
        ]

        for data in datas:
            region = Region(region_id=data[0], region_name=data[1], region_lon=data[2], region_lat=data[3])
            db.session.add(region)

        try:
            db.session.commit()
            print("SUCCESS!!!: models.py -> class Region -> init_static_data()")
        except Exception as e:
            db.session.rollback()
            print("ERROR!!!: models.py -> class Region -> init_static_data()")
            print(e)


class Crop(db.Model):
    __tablename__ = 'crop'

    crop_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    crop_name = db.Column(db.String(32), unique=True, nullable=False)

    crop_fields = db.relationship('Field', backref='crop')

    def serialize(self):
        return {
            'crop_id': self.crop_id,
            'crop_name': self.crop_name
        }

    @staticmethod
    def init_static_data():
        datas = [
            (1, '水稻'),
            (2, '大豆'),
            (3, '玉米'),
            (4, '麦类'),
            (5, '花生'),
            (6, '其他'),
        ]

        for data in datas:
            crop = Crop(crop_id=data[0], crop_name=data[1])
            db.session.add(crop)

        try:
            db.session.commit()
            print("SUCCESS!!!: models.py -> class Crop -> init_static_data()")
        except Exception as e:
            db.session.rollback()
            print("ERROR!!!: models.py -> class Crop -> init_static_data()")
            print(e)


class Field(db.Model):
    __tablename__ = 'field'

    region_id = db.Column(db.Integer, db.ForeignKey('region.region_id'))
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.crop_id'))

    field_id = db.Column(db.Integer, primary_key=True)
    field_area = db.Column(db.Float, nullable=False)

    def serialize(self):
        return {
            'region_id': self.region_id,
            'crop_id': self.crop_id,
            'field_id': self.field_id,
            'field_area': self.field_area
        }


class Precinct(db.Model):
    """
    管理区
    """
    __tablename__ = 'precinct'

    precinct_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    region_id = db.Column(db.Integer, db.ForeignKey('region.region_id'))
    # 如果不写 `nullable=True`, 那么 `principal_id` 不能为 `null`
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), unique=True, nullable=True)  # 负责人, 可以为空, 一区一人
    precinct_name = db.Column(db.String(64), unique=True, nullable=False)
    precinct_area = db.Column(db.Float, nullable=False)

    # other attributes...

    def serialize(self):
        return {
            'region_id': self.region_id,
            'region_name': self.region.region_name,
            'user_id': self.user_id,
            'user_name': self.user.user_name,
            'user_email': self.user.user_email,
            'precinct_id': self.precinct_id,
            'precinct_name': self.precinct_name,
            'precinct_area': self.precinct_area
        }

    @staticmethod
    def init_static_data():
        datas = [
            (1, 1, 2, '友谊管理区1', 1000.),
            (2, 1, 3, '友谊管理区2', 2000.),
            (3, 1, 4, '友谊管理区3', 3000.),
            (4, 2, 5, '597管理区1', 3000.),
            (5, 2, 6, '597管理区2', 2000.),
            (6, 2, 7, '597管理区3', 1000.),
        ]

        for data in datas:
            precinct = Precinct(precinct_id=data[0], region_id=data[1], user_id=data[2], precinct_name=data[3],
                                precinct_area=data[4])
            db.session.add(precinct)

        try:
            db.session.commit()
            print("SUCCESS!!!: models.py -> class Precinct -> init_static_data()")
        except Exception as e:
            db.session.rollback()
            print("ERROR!!!: models.py -> class Precinct -> init_static_data()")
            print(e)


class Device(db.Model):
    """
    监测设备
    """
    __tablename__ = 'device'

    region_id = db.Column(db.Integer, db.ForeignKey('region.region_id'))
    device_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    device_instance = db.Column(db.String(64), nullable=False)
    device_type = db.Column(db.String(64), nullable=False)

    device_lon = db.Column(db.Float, nullable=False)
    device_lat = db.Column(db.Float, nullable=False)

    device_abnormality_rate = db.Column(db.Float)  # 异常率

    device_soils = db.relationship('Soil', backref='device', lazy=True)

    # other attributes...

    def serialize(self):
        return {
            'region_id': self.region_id,
            'region_name': self.region.region_name,
            'device_id': self.device_id,
            'device_instance': self.device_instance,
            'device_type': self.device_type,
            'device_lonlat': [self.device_lon, self.device_lat],
            'device_abnormality_rate': self.device_abnormality_rate
        }

    @staticmethod
    def init_static_data():
        datas = [
            (1, 1, 'YY土壤设备1', '土壤监测设备', 132.01, 46.84),
            (2, 1, 'YY土壤设备2', '土壤监测设备', 132.02, 46.85),
            (3, 1, 'YY气象设备1', '气象监测设备', 132.03, 46.86),
            (4, 1, 'YY气象设备2', '气象监测设备', 132.04, 46.87),
        ]

        for data in datas:
            device = Device(device_id=data[0], region_id=data[1], device_instance=data[2], device_type=data[3],
                            device_lon=data[4], device_lat=data[5])
            db.session.add(device)

        try:
            db.session.commit()
            print("SUCCESS!!!: models.py -> class Device -> init_static_data()")
        except Exception as e:
            db.session.rollback()
            print("ERROR!!!: models.py -> class Device -> init_static_data()")
            print(e)
