# -*- coding: utf-8 -*-
# @Time    : 19-1-2 下午3:29


# 与Area模型相关的数据库操作存储位置
import json
import os
import random
import sys
from urllib import request

import requests

from api.common_func.city_code import city_codes, level_code
from api.models.models import Area, row2dict, db, Area_rate, NearbyArea


class AreaM(object):
    def get_all(self):
        areas = Area.query.all()
        return areas

    def list_all(self):
        areas = Area.query.all()
        json_list = []
        for i in areas:
            json_dict = {}
            json_dict["area_id"] = i.id
            # json_dict["rate_id"] = i.rate_id
            json_dict["cen_loc"] = i.locations['cen']
            json_dict["locations"] = i.locations
            level = AreaRateM().get(i.rate_id)['rate_level']
            # print(level)
            sur = i.surrounds['surrounds'][0]['title'] if i.surrounds['surrounds'] else " "
            # print(sur)
            rate_level = level_code[str(level)] if level else " "
            json_dict["level"] = level
            json_dict["surrounds"] = sur
            json_dict["area_rate"] = rate_level
            json_dict["business"] = i.business
            json_dict["address"] = i.address
            json_dict['active'] = i.active
            json_list.append(json_dict)

        return json_list

    def get(self, id):
        res = Area.query.get(id)

        if res:
            return row2dict(res)
        else:
            return None

    def get_obj(self, id):
        res = Area.query.get(id)
        if res:
            return res
        else:
            return None

    def get_active_obj(self):
        res = Area.query.filter(Area.active == 1)
        return res

    def add_new(self, **args):
        new_co = Area(**args)
        db.session.add(new_co)
        db.session.commit()
        return self.get(new_co.id)

    def update(self, id, param):
        # print id, param
        Area.query.filter(Area.id == id).update(param)
        db.session.commit()
        return 'success'

    def delete(self, id):
        tmp = Area.query.filter(Area.id == id)
        db.session.delete(tmp.one())
        db.session.commit()
        return 'success'

    def get_area(self, name):
        res = Area.query.filter(Area.city_name == name)
        return res

    @staticmethod
    def set_area():
        temp = os.getcwd()
        with open(temp + '/models/mapAll.json', encoding='utf-8') as f:
            # with open(temp + '/api/models/mapAll.json', encoding='utf-8') as f:
            res = json.load(f)
            # print(res)
            f.close()
        for i in res:
            # lng:经度,lat:纬度
            # 区域坐标：
            locations = {
                'cen': i['cen'],
                'lt': i['lt'],
                'ld': i['ld'],
                'rt': i['rt'],
                'rd': i['rd']
            }
            # 周边建筑群：
            surs = {
                'surrounds': i['detail']['surroundingPois']
            }
            count = len(surs['surrounds'])
            business = i['detail']['business']
            city_name = i['detail']['addressComponents']['city']
            address = i['detail']['address']
            if city_name:
                city_code = city_codes[city_name] if city_name else ""
            else:
                city_name = ' '
                city_code = ' '
            # 将数据存储在数据库中
            areas = AreaM()
            if count < 1:
                areas.add_new(city_name=city_name, city_code=city_code, locations=locations, surrounds=surs,
                              sur_count=count, business=business, address=address, rate_id=2)
            else:
                areas.add_new(city_name=city_name, city_code=city_code, locations=locations, surrounds=surs,
                              sur_count=count, address=address, business=business, rate_id=1)

        return 'set data successfully!'

    @staticmethod
    def update_area_description():
        areas = AreaM().get_all()
        for i in areas:
            lng, lat = i.locations['cen']['lng'], i.locations['cen']['lat']
            loc = '{0},{1}'.format(lng, lat)
            # location_url = "http://api.map.baidu.com/geocoder/v2/?callback=renderReverse&location=35.658651,139.745415" \
            #       "&output=json&pois=1&latest_admin=1&ak=您的ak //GET请求"

            res = requests.get(
                url="https://restapi.amap.com/v3/geocode/regeo",
                params={
                    "key": "1307e088b2362d9d10bb5a3a26a4c29e",
                    "output": "json",
                    "location": loc,
                    "radius": 1000
                }
            )
            result = res.json()['regeocode']['formatted_address']
            if result:
                param = {"area_description": result}
                AreaM().update(i.id, param)
                # print('update successfully.')
            else:
                param = {"area_description": i.city_name}
                AreaM().update(i.id, param)


class AreaRateM(object):
    def list_all(self):
        pass

    def get(self, id):
        res = Area_rate.query.filter(Area_rate.id == id).one_or_none()
        return row2dict(res)

    def add_new(self, **args):
        new_co = Area_rate(**args)
        db.session.add(new_co)
        db.session.commit()
        return self.get(new_co.id)

    def get_obj(self, level):
        res = Area_rate.query.filter(
            Area_rate.rate_level == level).one_or_none()
        return row2dict(res)


class NearbyM(object):
    def list_all(self):
        nearby = NearbyArea.query.all()
        return nearby

    def get(self, id):
        res = NearbyArea.query.filter(NearbyArea.id == id).one_or_none()
        return row2dict(res)

    def get_nearby(self, area_id):
        res = NearbyArea.query.filter(
            NearbyArea.area_id == area_id).one_or_none()
        return row2dict(res)

    def add_new(self, **args):
        new_co = NearbyArea(**args)
        db.session.add(new_co)
        db.session.commit()
        return self.get(new_co.id)


def gen_loc(area_id):
    """
    根据区域id随机生成该区域的坐标，并获取地址名称
    :param area_id: 区域id
    """
    res = AreaM().get(area_id)
    if res:
        lt_lat = res['locations']['lt']['lat']
        ld_lat = res['locations']['ld']['lat']
        ld_lng = res['locations']['ld']['lng']
        rd_lng = res['locations']['rd']['lng']
        gen_lat = round(random.uniform(ld_lat, lt_lat), 6)
        gen_lng = round(random.uniform(ld_lng, rd_lng), 6)
        loc = '{0},{1}'.format(gen_lat, gen_lng)
        loc_name = gen_locname(loc)
        return loc, loc_name
    else:
        return None


def gen_locname(loc):
    """
    根据百度地图api获取地址名称
    :param loc: (lat,lng)
    """
    ak = '1mGq6bdr1Ys05haNBw755UGc4tAEDsEe'
    res = requests.get(
        url="https://api.map.baidu.com/reverse_geocoding/v3/?ak=" + ak,
        params={
            "output": "json",
            "location": loc,
            "coordtype": "wgs84ll"
        }
    ).json()
    return res.get('result')['formatted_address']


class HandlePois(object):
    """
        运用高德地图api获取相关指标确定不同区域的定性
    """

    def __init__(self):
        self.key = ''

    def car_wash_pois(self, location, radius):
        '''洗车店附近的poi'''

        url = 'https://restapi.amap.com/v3/place/around?key=%s&types=010500' % self.key
        res = requests.get(
            url=url,
            params={
                "location": location,
                "output": "json",
                "radius": radius,
                "page": 1,
                "extensions": "all",
                "offset": 20
            }
        ).json()
        return res['pois']

    def restaurant_pois(self, location, radius):
        '''餐馆附近的poi'''
        # url = 'https://restapi.amap.com/v3/place/around?key=%s' \
        #            '&location=%s&keywords=&types=%s&radius=3000&offset=20&page=1&extensions=all' \
        #            % (self.key, location, types)
        url = 'https://restapi.amap.com/v3/place/around?key=%s&types=050100' % self.key
        res = requests.get(
            url=url,
            params={
                "location": location,
                "output": "json",
                "radius": radius,
                "page": 1,
                "extensions": "all",
                "offset": 20
            }
        ).json()
        return res['pois']

    def area_carwash_pois(self):
        areas = AreaM().list_all()
        car_cost = {}
        for i in areas:
            cen_loc = i['cen_loc']
            pois = self.car_wash_pois(cen_loc, 3000)
            cost = []
            for j in pois:
                c = j['biz_ext']['cost']
                cost.append(c)
            car_cost[i['area_id']] = cost
        return car_cost

    def area_restaurant_pois(self):
        areas = AreaM().list_all()
        restaurant_cost = {}
        for i in areas:
            cen_loc = i['cen_loc']
            pois = self.car_wash_pois(cen_loc, 3000)
            cost = []
            for j in pois:
                c = j['biz_ext']['cost']
                cost.append(c)
            restaurant_cost[i['area_id']] = cost
        return restaurant_cost
