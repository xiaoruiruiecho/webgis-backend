from datetime import datetime
from extensions import db
from utils import upload_weather_data, upload_soil_data


class Weather(db.Model):
    """
    农场每日天气
    """
    __tablename__ = 'weather'

    region_id = db.Column(db.Integer, db.ForeignKey('region.region_id'), primary_key=True)
    weather_date = db.Column(db.DateTime, primary_key=True)

    weather_temperature = db.Column(db.Float)
    weather_humidity = db.Column(db.Float)  # 空气湿度
    weather_illumination = db.Column(db.Float)  # 光照
    weather_wind_speed = db.Column(db.Float)
    weather_wind_direction = db.Column(db.Float)
    weather_atmospheric_pressure = db.Column(db.Float)  # 气压
    weather_precipitation = db.Column(db.Float)  # 降水量
    weather_CO2 = db.Column(db.Float)
    weather_N = db.Column(db.Float)
    weather_P = db.Column(db.Float)
    weather_K = db.Column(db.Float)

    # other attributes...

    def serialize(self):
        return {
            'region_id': self.region_id,
            'region_name': self.region.region_name,
            'weather_date': self.weather_date.strftime('%Y-%m-%d %H:%M:%S'),
            'weather_temperature': self.weather_temperature,
            'weather_humidity': self.weather_humidity,
            'weather_illumination': self.weather_illumination,
            'weather_wind_speed': self.weather_wind_speed,
            'weather_wind_direction': self.weather_wind_direction,
            'weather_atmospheric_pressure': self.weather_atmospheric_pressure,
            'weather_precipitation': self.weather_precipitation,
            'weather_CO2': self.weather_CO2,
            'weather_N': self.weather_N,
            'weather_P': self.weather_P,
            'weather_K': self.weather_K,
        }

    @staticmethod
    def init_static_data(path: str, region_id: int):
        try:
            upload_weather_data(path, region_id)
        except Exception as e:
            print("ERROR!!!: models.py -> class Weather -> init_static_data()")
            print(e)

        print("SUCCESS!!!: models.py -> class Weather -> init_static_data()")


class Soil(db.Model):
    """
    地块土壤数据
    """
    __tablename__ = 'soil'

    device_id = db.Column(db.Integer, db.ForeignKey('device.device_id'), primary_key=True)
    soil_date = db.Column(db.DateTime, primary_key=True)

    # other attributes...
    soil_temperature = db.Column(db.Float)
    soil_water = db.Column(db.Float)
    soil_conductivity = db.Column(db.Float)
    soil_PH = db.Column(db.Float)
    soil_salt = db.Column(db.Float)

    def serialize(self):
        return {
            'device_id': self.device_id,
            'device_instance': self.device.device_instance,
            'region_id': self.device.region.region_id,
            'region_name': self.device.region.region_name,
            'soil_date': self.soil_date.strftime('%Y-%m-%d %H:%M:%S'),
            'soil_temperature': self.soil_temperature,
            'soil_water': self.soil_water,
            'soil_conductivity': self.soil_conductivity,
            'soil_PH': self.soil_PH,
            'soil_salt': self.soil_salt,
        }

    @staticmethod
    def init_static_data(path: str):
        try:
            upload_soil_data(path)
        except Exception as e:
            print("ERROR!!!: models.py -> class Soil -> init_static_data()")
            print(e)

        print("SUCCESS!!!: models.py -> class Soil -> init_static_data()")


class Service(db.Model):
    """
    农场遥感数据
    """
    __tablename__ = 'service'

    # TODO: service_id or (region_id + service_date) as primary_key
    service_id = db.Column(db.String(256), unique=True)

    region_id = db.Column(db.Integer, db.ForeignKey('region.region_id'), primary_key=True)
    service_date = db.Column(db.Date, primary_key=True)

    year_terrain_url = db.Column(db.String(256))  # 地势
    year_hydrology_url = db.Column(db.String(256))  # 水文

    day_feature_url = db.Column(db.String(256))  # feature layer
    day_growth_url = db.Column(db.String(256))  # tile layer

    def __init__(self, **kwargs):
        super(Service, self).__init__(**kwargs)
        self.set_service_id()

    def set_service_id(self):
        # TODO: assert
        str_region_id = "{:05d}".format(self.region_id)
        self.service_id = datetime.strptime(self.service_date, '%Y-%m-%d').strftime('%Y-%m-%d') + ':' + str_region_id

    def serialize(self):
        return {
            'region_id': self.region_id,
            'region_name': self.region.region_name,
            'service_id': self.service_id,
            'service_date': self.service_date.strftime('%Y-%m-%d'),
            'year_terrain_url': self.year_terrain_url,
            'year_hydrology_url': self.year_hydrology_url,
            'day_feature_url': self.day_feature_url,
            'day_growth_url': self.day_growth_url
        }

    @staticmethod
    def init_static_data():
        # TODO
        datas = [
            (2, '2022-06-11',
             'https://webgis.xiaoruirui.site:6443/arcgis/rest/services/ZSJC/WJQ220611/MapServer'),
            (2, '2022-08-01',
             'https://webgis.xiaoruirui.site:6443/arcgis/rest/services/ZSJC/WJQ220801/MapServer'),
            (2, '2022-08-11',
             'https://webgis.xiaoruirui.site:6443/arcgis/rest/services/ZSJC/WJQ220811/MapServer'),
            (1, '2022-06-11',
             'https://webgis.xiaoruirui.site:6443/arcgis/rest/services/ZSJC/YY220611/MapServer'),
            (1, '2022-08-01',
             'https://webgis.xiaoruirui.site:6443/arcgis/rest/services/ZSJC/YY220801/MapServer'),
            (1, '2022-08-11',
             'https://webgis.xiaoruirui.site:6443/arcgis/rest/services/ZSJC/YY220811/MapServer'),
        ]

        for data in datas:
            service = Service(region_id=data[0], service_date=data[1], day_growth_url=data[2])
            db.session.add(service)

        try:
            db.session.commit()
            print("SUCCESS!!!: models.py -> class Service -> init_static_data()")
        except Exception as e:
            db.session.rollback()
            print("ERROR!!!: models.py -> class Service -> init_static_data()")
            print(e)
