# api_routes.py
from flask import Flask
from api.region_api import RegionApi, CropApi, PrecinctApi, DeviceApi
from api.information_api import WeatherApi, WeatherPredictApi, ServiceApi, SoilApi, ExportWeatherApi, ExportSoilApi, \
    InformationApi
from api.user_api import SigninApi, SignupApi, UserApi, UserRoleApi, UserInfoApi, UserPrecinctApi


def register_routes(app: Flask):
    signup_view = SignupApi.as_view('signup_api')
    app.add_url_rule('/api/signup', view_func=signup_view, methods=['POST'])

    signin_view = SigninApi.as_view('signin_api')
    app.add_url_rule('/api/signin', view_func=signin_view, methods=['POST'])

    user_info_view = UserInfoApi.as_view('user_info_api')
    app.add_url_rule('/api/user_info', view_func=user_info_view, methods=['GET', 'PUT', 'PATCH'])

    user_view = UserApi.as_view('user_api')
    app.add_url_rule('/api/user', view_func=user_view, methods=['GET', 'POST'])

    user_role_view = UserRoleApi.as_view('user_role_api')
    app.add_url_rule('/api/user_role', view_func=user_role_view, methods=['POST'])

    user_precinct_view = UserPrecinctApi.as_view('user_precinct_api')
    app.add_url_rule('/api/user_precinct', view_func=user_precinct_view, methods=['GET', 'POST'])


    region_view = RegionApi.as_view('region_api')
    app.add_url_rule('/api/region', view_func=region_view, methods=['GET'])

    crop_view = CropApi.as_view('crop_api')
    app.add_url_rule('/api/crop', view_func=crop_view, methods=['GET'])

    precinct_view = PrecinctApi.as_view('precinct_api')
    app.add_url_rule('/api/precinct', view_func=precinct_view, methods=['GET'])

    device_view = DeviceApi.as_view('device_api')
    app.add_url_rule('/api/device', view_func=device_view, methods=['GET'])


    weather_view = WeatherApi.as_view('weather_api')
    app.add_url_rule('/api/weather', view_func=weather_view, methods=['GET', 'POST'])

    weather_prediction_view = WeatherPredictApi.as_view('weather_prediction_api')
    app.add_url_rule('/api/weather_prediction', view_func=weather_prediction_view, methods=['GET'])

    soil_view = SoilApi.as_view('soil_api')
    app.add_url_rule('/api/soil', view_func=soil_view, methods=['GET', 'POST'])

    information_view = InformationApi.as_view('information_api')
    app.add_url_rule('/api/information', view_func=information_view, methods=['POST'])

    service_view = ServiceApi.as_view('service_api')
    app.add_url_rule('/api/service', view_func=service_view, methods=['GET', 'POST', 'DELETE', 'PUT'])

    export_weather_view = ExportWeatherApi.as_view('export_weather_api')
    app.add_url_rule('/api/export_weather', view_func=export_weather_view, methods=['GET'])

    export_soil_view = ExportSoilApi.as_view('export_soil_api')
    app.add_url_rule('/api/export_soil', view_func=export_soil_view, methods=['GET'])