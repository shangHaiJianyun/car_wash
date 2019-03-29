# -*- coding:utf-8 -*-
import json

from flask import request, jsonify

from api import db
from api.common_func.area import AreaM, AreaRateM, NearbyM
from api.common_func.city_code import level_code
from api.common_func.nearby_area import set_nearby
from api.modules.map import map_blu


@map_blu.route('/get_rate', methods=['POST'])
def get_rate():
    # 获取指定坐标后根据中心点坐标确定其所属的区域及价格系数
    # lng:经度  lat:纬度
    lng = float(request.json.get('lng'))
    lat = float(request.json.get('lat'))
    # print(lng, lat)
    # 从数据库中获取所有的坐标数据
    for j in AreaM().get_all():
        # 获取该区域的区域坐标
        i = j.locations
        # 判断指定坐标属于哪个区域
        if (i['lt']['lng'] <= lng <= i['rt']['lng']) and (i['rd']['lat'] <= lat <= i['rt']['lat']):
            rate = AreaRateM().get(j.rate_id)
            # 根据需求返回该坐标所属的价格系数
            level = str(rate['rate_level'])

            rate_level = level_code[str(level)] if level else " "
            data = {
                'rate_name': rate['name'],
                'rate_level': rate_level,
                'area_id': j.id,
                'city': j.city_name,
                'city_code': j.city_code
            }
            return jsonify(data)

    return jsonify({'error': 'please input right axis'})


@map_blu.route('/list_area', methods=['GET'])
def list_area():
    result = AreaM().list_all()
    # res = json.dumps(result)
    return jsonify(result)


@map_blu.route('/map_data', methods=['GET', 'POST'])
def map_data():
    # 判断操作的方式 若是修改数据
    if request.method == 'POST':

        id = request.json.get('id')
        level = request.json.get('level')

        try:
            rate_res = AreaRateM().get_obj(level)
            # print(rate_res['id'])
            rate_id = rate_res['id']
            res = AreaM().get(id)
            res.rate_id = rate_id
            db.session.commit()
            # print(res)
            return jsonify({"area_rate": level_code[str(level)] if level else " "})
        except Exception:
            return jsonify({"msg": "please give right data"})
    else:
        # 地图上显示数据
        result = AreaM().list_all()
        return jsonify(result)


@map_blu.route('/rate', methods=['GET', 'POST'])
def return_rate():
    area_id = request.json.get('area_id')
    try:
        area = AreaM().get(area_id)
        res = AreaRateM().get(area.rate_id)
        area_rate = level_code[str(res['rate_level'])] if res['rate_level'] else " "
    except Exception:
        return jsonify({'erro': 'wrong area_id'})
    return jsonify({'area_rate': area_rate})


@map_blu.route('get_nearby', methods=['GET', 'POST'])
def get_nearby():
    """获取某一区域id或者是中心点坐标 返回附近8个区域的信息"""
    try:
        area_id = request.json.get('area_id')
        res = NearbyM().get_nearby(area_id)['nearby']
    except Exception as e:
        raise e
    return jsonify(res)
