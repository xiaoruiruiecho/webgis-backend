import json

import requests

import config
import pandas as pd
import pymysql
from datetime import datetime
from flask_jwt_extended import get_jwt_identity
from models.user import User


def get_current_user() -> User:
    try:
        # 获取 JWT 中存储的当前用户身份信息 (用户ID)
        user_id = int(get_jwt_identity())
        return User.query.get(user_id)
    except Exception as e:
        raise ValueError("用户未登录") from e


def upload_weather_data(path: str, region_id: int):
    df = pd.read_excel(path)

    weather_date_list = list(df['采集时间'])

    weather_temperature_list = list(df['空气温度'])
    weather_humidity_list = list(df['空气湿度'])
    weather_illumination_list = list(df['光照'])
    weather_wind_speed_list = list(df['风速'])
    weather_wind_direction_list = list(df['风向'])
    weather_atmospheric_pressure_list = list(df['气压'])
    weather_precipitation_list = list(df['降雨量'])
    weather_CO2_list = list(df['二氧化碳'])
    weather_N_list = list(df['氮'])
    weather_P_list = list(df['磷'])
    weather_K_list = list(df['钾'])

    # 连接数据库
    connect = pymysql.Connect(
        host=config.HOST,
        port=int(config.PORT),
        user=config.USERNAME,
        passwd=config.PASSWORD,
        db=config.DATABASE,
        charset=config.CHARSET
    )

    # 获取游标
    cursor = connect.cursor()

    # 插入数据
    for i in range(len(weather_date_list)):
        if i % 1000 == 0:
            print("正在插入第 " + str(i) + " 条 Weather 数据......")

        date = datetime.strptime(weather_date_list[i], '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

        temperature = float(weather_temperature_list[i])
        humidity = float(weather_humidity_list[i])
        illumination = float(weather_illumination_list[i])
        wind_speed = float(weather_wind_speed_list[i])
        wind_direction = float(weather_wind_direction_list[i])
        atmospheric_pressure = float(weather_atmospheric_pressure_list[i])
        precipitation = float(weather_precipitation_list[i])
        CO2 = float(weather_CO2_list[i])
        N = float(weather_N_list[i])
        P = float(weather_P_list[i])
        K = float(weather_K_list[i])

        sql = (
                "INSERT INTO weather(region_id, weather_date, weather_temperature, weather_humidity, " +
                "weather_illumination, weather_wind_speed, weather_wind_direction, weather_atmospheric_pressure, "
                "weather_precipitation, weather_CO2, weather_N, weather_P, weather_K) " +
                "VALUES ('%d', '%s', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f')")

        data = (
            region_id, date, temperature, humidity, illumination, wind_speed, wind_direction, atmospheric_pressure,
            precipitation, CO2, N, P, K)

        cursor.execute(sql % data)
        connect.commit()

    connect.close()


def upload_soil_data(path: str):
    df = pd.read_excel(path)

    soil_date_list = list(df['采集时间'])

    soil_temperature_list1 = list(df['土壤温度1'])
    soil_water_list1 = list(df['土壤含水量1'])
    soil_conductivity_list1 = list(df['电导率1'])
    soil_PH_list1 = list(df['土壤PH1'])
    soil_salt_list1 = list(df['土壤盐分1'])

    soil_temperature_list2 = list(df['土壤温度2'])
    soil_water_list2 = list(df['土壤含水量2'])
    soil_conductivity_list2 = list(df['电导率2'])
    soil_PH_list2 = list(df['土壤PH2'])
    soil_salt_list2 = list(df['土壤盐分2'])

    soil_temperature_list3 = list(df['土壤温度3'])
    soil_water_list3 = list(df['土壤含水量3'])
    soil_conductivity_list3 = list(df['电导率3'])
    soil_PH_list3 = list(df['土壤PH3'])
    soil_salt_list3 = list(df['土壤盐分3'])

    soil_temperature_list4 = list(df['土壤温度4'])
    soil_water_list4 = list(df['土壤含水量4'])
    soil_conductivity_list4 = list(df['电导率4'])
    soil_PH_list4 = list(df['土壤PH4'])
    soil_salt_list4 = list(df['土壤盐分4'])

    # 连接数据库
    connect = pymysql.Connect(
        host=config.HOST,
        port=int(config.PORT),
        user=config.USERNAME,
        passwd=config.PASSWORD,
        db=config.DATABASE,
        charset=config.CHARSET
    )

    # 获取游标
    cursor = connect.cursor()

    # 插入数据
    for i in range(len(soil_date_list)):
        if i % 1000 == 0:
            print("正在插入第 " + str(i) + " 条 Soil 数据......")

        soil_date = datetime.strptime(soil_date_list[i], '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

        soil_temperature1 = float(soil_temperature_list1[i])
        soil_water1 = float(soil_water_list1[i])
        soil_conductivity1 = float(soil_conductivity_list1[i])
        soil_PH1 = float(soil_PH_list1[i])
        soil_salt1 = float(soil_salt_list1[i])

        soil_temperature2 = float(soil_temperature_list2[i])
        soil_water2 = float(soil_water_list2[i])
        soil_conductivity2 = float(soil_conductivity_list2[i])
        soil_PH2 = float(soil_PH_list2[i])
        soil_salt2 = float(soil_salt_list2[i])

        soil_temperature3 = float(soil_temperature_list3[i])
        soil_water3 = float(soil_water_list3[i])
        soil_conductivity3 = float(soil_conductivity_list3[i])
        soil_PH3 = float(soil_PH_list3[i])
        soil_salt3 = float(soil_salt_list3[i])

        soil_temperature4 = float(soil_temperature_list4[i])
        soil_water4 = float(soil_water_list4[i])
        soil_conductivity4 = float(soil_conductivity_list4[i])
        soil_PH4 = float(soil_PH_list4[i])
        soil_salt4 = float(soil_salt_list4[i])

        sql = (
                "INSERT INTO soil(device_id, soil_date, soil_temperature, soil_water, " +
                "soil_conductivity, soil_PH, soil_salt) " +
                "VALUES ('%d', '%s', '%f', '%f', '%f', '%f', '%f')")

        data1 = (
            1, soil_date, soil_temperature1, soil_water1, soil_conductivity1, soil_PH1, soil_salt1)
        data2 = (
            2, soil_date, soil_temperature2, soil_water2, soil_conductivity2, soil_PH2, soil_salt2)
        data3 = (
            3, soil_date, soil_temperature3, soil_water3, soil_conductivity3, soil_PH3, soil_salt3)
        data4 = (
            4, soil_date, soil_temperature4, soil_water4, soil_conductivity4, soil_PH4, soil_salt4)

        cursor.execute(sql % data1)
        cursor.execute(sql % data2)
        cursor.execute(sql % data3)
        cursor.execute(sql % data4)
        connect.commit()

    connect.close()


def upload_information_data(path: str, url: str):
    # requests.post中的data参数
    # 默认会将传入的Python字典
    # 转为x-www-form-urlencoded格式。
    #
    # 然而，x-www-form-urlencoded的值要求是一个简单的字符串或标量，
    # 复杂的嵌套数据（如JSON对象或数组）需要先转成字符串。
    # 因此需要用json.dumps将Python的对象序列化为JSON字符串。
    #
    # 如果直接传递字典而不使用json.dumps，
    # requests会尝试对嵌套的对象进行不正确的编码，
    # 导致服务器接收到的数据格式不符合预期。

    df = pd.read_excel(path)

    column0 = df.columns[0]
    assert column0.lower() == 'objectid'

    updates = [{'attributes': row.to_dict()} for (index, row) in df.iterrows()]

    url += '/applyEdits'

    params = {
        'f': 'json'
    }

    data = {
        "updates": json.dumps(updates)
    }

    response = requests.post(url=url, params=params, data=data)

    if not response.status_code or response.status_code != 200:
        raise Exception(response.text)
