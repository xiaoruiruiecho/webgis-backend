import pandas as pd
import requests

from datetime import datetime
from decorators import permission_required, role_required, jwt_required_with_redis
from extensions import db
from flask import request, json, send_from_directory
from flask.views import MethodView
from models.region import Region, Precinct, Device
from models.information import Weather, Service, Soil
from models.pagebean import PageBean
from models.result import Result
from models.role import Role
from settings import WEATHER_PREDICT_API_URL
from sqlalchemy import extract
from utils import get_current_user, upload_weather_data, upload_soil_data, upload_information_data


class WeatherApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.USER, Role.MANAGER])
    def get(self):
        args = request.args

        region_name = args.get('region_name', '')
        date_start = args.get('date_start')  # TODO
        date_end = args.get('date_end')

        has_date_range = True if date_start and date_end else False
        region = Region.query.filter_by(region_name=region_name).first()

        if not region:
            return Result.error('天气查询失败, 请传入具体城市')

        region_id = region.region_id

        if has_date_range:
            date_format = '%Y-%m-%d %H:%M:%S'

            date_start = datetime.strptime(date_start, date_format)
            date_end = datetime.strptime(date_end, date_format)

            weathers: [Weather] = Weather.query.filter_by(
                region_id=region_id).filter(
                Weather.weather_date >= date_start, Weather.weather_date <= date_end).order_by(
                Weather.weather_date.desc()).all()[::-1]
        else:
            weathers: [Weather] = Weather.query.filter_by(
                region_id=region_id).order_by(
                Weather.weather_date.desc()).limit(
                10).all()[::-1]

        data = [weather.serialize() for weather in weathers]

        return Result.success(data=PageBean.data(data=data, count=len(data)))

    @jwt_required_with_redis
    @role_required([Role.MANAGER])
    def post(self):
        region_name = request.form.get('region_name')
        file = request.files.get("weather_file")

        if not file:
            return Result.error('请选择文件')

        region = Region.query.filter_by(region_name=region_name).first()
        if not region:
            return Result.error('请选择正确的农场')

        region_id = region.region_id

        filename = file.filename
        path = './uploads/weather/' + filename

        try:
            file.save(path)
        except Exception as e:
            print(e)
            return Result.error('文件上传失败')

        try:
            upload_weather_data(path, region_id)
        except Exception as e:
            print(e)
            return Result.error('数据导入失败')

        return Result.success()


class WeatherPredictApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.USER, Role.MANAGER])
    def get(self):
        args = request.args
        region_name = args.get('region_name')
        predict_days = int(args.get('predict_days', 7))

        if not region_name:
            return Result.error("天气预测失败, 请传入具体城市")

        success, data = WeatherPredictApi.get_prediction(region_name, predict_days)
        if not success:
            return Result.error("查询不到 '" + region_name + "' 的未来天气数据")

        return Result.success(data=PageBean.data(data=data, count=len(data)))

    @staticmethod
    def get_prediction(region_name, predict_days):
        url = WEATHER_PREDICT_API_URL

        # TODO
        region_dict = {
            'YY': '101050401',
            '597': '101050101'
        }

        pred_id = region_dict.get(region_name)
        if not pred_id:
            return False, None

        url = url + pred_id
        response = requests.get(url)

        return True, WeatherPredictApi.process_prediction(region_name, predict_days, response.text)

    @staticmethod
    def process_prediction(region_name, predict_days, text):
        text = json.loads(text)
        region = Region.query.filter_by(region_name=region_name).first()

        if not region:
            raise Exception('该区域不存在于数据库中')

        region_id = region.region_id
        max_len = len(text['data']['forecast'])  # = 15
        predict_days = min(max(predict_days, 1), max_len)

        weathers = []
        for i in range(predict_days):
            weather = {
                'region_id': region_id,
                'region_name': region_name,
                # 日期
                'date': text['data']['forecast'][i]["ymd"],
                # 最高温
                'temperature_max': float(text['data']['forecast'][i]["high"][3:-1]),
                # 最低温
                'temperature_min': float(text['data']['forecast'][i]["low"][3:-1]),
                # 风向风力
                'windy': text['data']['forecast'][i]["fx"] + " " + text['data']['forecast'][i]["fl"],
                # 天气
                'weather': text['data']['forecast'][i]["type"]
            }

            weathers.append(weather)

        return weathers


class SoilApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.USER, Role.MANAGER])
    def get(self):
        args = request.args

        region_name = args.get('region_name')
        soil_count = int(args.get('soil_count', 1))

        region = Region.query.filter_by(region_name=region_name).first()
        if not region:
            return Result.error('请传入具体城市')

        region_id = region.region_id
        devices = Device.query.filter_by(region_id=region_id).all()

        data = []
        for device in devices:
            device_id = device.device_id
            soils = Soil.query.filter_by(device_id=device_id).order_by(Soil.soil_date).limit(soil_count).all()
            data.append(device.serialize() | {'device_soils': [soil.serialize() for soil in soils]})

        return Result.success(data=PageBean.data(data=data, count=len(data)))

    @jwt_required_with_redis
    @role_required([Role.MANAGER])
    def post(self):  # TODO: device_id 如何确定
        file = request.files.get("soil_file")

        if not file:
            return Result.error('请选择文件')

        filename = file.filename
        path = './uploads/soil/' + filename

        try:
            file.save(path)
        except Exception as e:
            print(e)
            return Result.error('文件上传失败')

        try:
            upload_soil_data(path)
        except Exception as e:
            print(e)
            return Result.error('数据导入失败')

        return Result.success()


class InformationApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.MANAGER])
    def post(self):
        file = request.files.get("information_file")
        url = request.form.get('url')

        if not file:
            return Result.error('请选择文件')

        filename = file.filename
        path = './uploads/information/' + filename

        try:
            file.save(path)
        except Exception as e:
            print(e)
            return Result.error('文件上传失败')

        try:
            upload_information_data(path, url)
        except Exception as e:
            print(e)
            return Result.error('数据导入失败')

        return Result.success()


class ServiceApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.MANAGER])
    def get(self):
        args = request.args

        page = int(args.get('page', 1))
        limit = int(args.get('limit', 100))

        user = get_current_user()
        precinct = Precinct.query.filter_by(user_id=user.user_id).first()

        if not precinct:
            return Result.error('当前管理员没有管理区域')

        region = Region.query.get(precinct.region_id)
        region_id = region.region_id

        count = Service.query.filter_by(region_id=region_id).count()
        if not limit:
            limit = count

        services: [Service] = Service.query.filter_by(region_id=region_id).order_by(
            Service.service_date.desc()).offset(
            (page - 1) * limit).limit(limit).all()

        data = [service.serialize() for service in services]

        return Result.success(data=PageBean.data(data=data, count=count))

    @jwt_required_with_redis
    @role_required([Role.MANAGER])
    def post(self):
        params = request.json

        service_date = params.get('service_date')
        year_terrain_url = params.get('year_terrain_url')
        year_hydrology_url = params.get('year_hydrology_url')
        day_feature_url = params.get('day_feature_url')
        day_growth_url = params.get('day_growth_url')

        user = get_current_user()
        precinct = Precinct.query.filter_by(user_id=user.user_id).first()

        if not precinct:
            return Result.error('当前管理员没有管理区域')

        region_id = precinct.region_id
        service = Service(region_id=region_id, service_date=service_date, year_terrain_url=year_terrain_url,
                          year_hydrology_url=year_hydrology_url, day_feature_url=day_feature_url,
                          day_growth_url=day_growth_url)

        try:
            db.session.add(service)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return Result.error('上传服务失败')

        return Result.success()

    @jwt_required_with_redis
    @role_required([Role.MANAGER])
    def delete(self):
        # Delete: 前端用 x-www-form-urlencoded; 后端用 values, 不能用 json
        params = request.values

        service_id = params.get('service_id')
        service = Service.query.filter_by(service_id=service_id).first()

        if not service:
            return Result.error('请传入正确的服务id')

        try:
            db.session.delete(service)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return Result.error('删除服务失败')

        return Result.success()

    @jwt_required_with_redis
    @role_required([Role.MANAGER])
    def put(self):
        params = request.json

        service_id = params.get('service_id')
        service_date = params.get('service_date')
        year_terrain_url = params.get('year_terrain_url')
        year_hydrology_url = params.get('year_hydrology_url')
        day_feature_url = params.get('day_feature_url')
        day_growth_url = params.get('day_growth_url')

        service = Service.query.filter_by(service_id=service_id).first()

        if not service:
            return Result.error('请传入正确的服务id')

        service.service_date = service_date  # TODO: format
        service.year_terrain_url = year_terrain_url
        service.year_hydrology_url = year_hydrology_url
        service.day_feature_url = day_feature_url
        service.day_growth_url = day_growth_url
        service.set_service_id()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return Result.error('修改服务失败')

        return Result.success()


class ExportWeatherApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.MANAGER])
    def get(self):
        args = request.args

        region_name = args.get('region_name')
        weather_year = int(args.get('weather_year', datetime.today().year))

        region = Region.query.filter_by(region_name=region_name).first()

        if not region:
            return Result.error('请选择地区')

        weathers = Weather.query.filter(Weather.region_id == region.region_id,
                                        extract('year', Weather.weather_date) == weather_year).order_by(
            Weather.weather_date).all()

        if len(weathers) == 0:
            return Result.error('没有数据')

        df = pd.DataFrame([weather.serialize() for weather in weathers])
        fileroot = './exports'
        filename = f'{region_name}_{weather_year}_weather_export.xlsx'
        filepath = fileroot + '/' + filename
        df.to_excel(filepath, index=False)

        # download_url = settings.BACKEND_DOMAIN + filepath[1:]

        return send_from_directory(fileroot, filename, as_attachment=True)


class ExportSoilApi(MethodView):
    @jwt_required_with_redis
    @role_required([Role.MANAGER])
    def get(self):
        args = request.args

        region_name = args.get('region_name')
        soil_year = int(args.get('soil_year', datetime.today().year))

        region = Region.query.filter_by(region_name=region_name).first()

        if not region:
            return Result.error('请选择地区')

        device_ids = [device.device_id for device in region.region_devices]  # 提取所有设备ID (在每个农场的设备不多的前提下)

        soils = Soil.query.filter(
            Soil.device_id.in_(device_ids),
            extract('year', Soil.soil_date) == soil_year
        ).order_by(Soil.device_id,
                   Soil.soil_date).all()

        if len(soils) == 0:
            return Result.error('没有数据')

        df = pd.DataFrame([soil.serialize() for soil in soils])
        fileroot = './exports'
        filename = f'{region_name}_{soil_year}_soil_export.xlsx'
        filepath = fileroot + '/' + filename
        df.to_excel(filepath, index=False)

        # download_url = settings.BACKEND_DOMAIN + filepath[1:]

        return send_from_directory(fileroot, filename, as_attachment=True)
