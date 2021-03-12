import time
import random
import base64
import datetime
import calendar
import traceback
import configparser
import urllib.parse

import requests

BASE_URL = "https://xiaobei.yinghuaonline.com/prod-api"
PUB_HEADERS = {
    'Host': 'xiaobei.yinghuaonline.com',
    'User-Agent': 'iPad8,3(iOS/14.4) Uninview(Uninview/1.0.0) Weex/0.26.0 1668x2388',
    'Accept-Language': 'zh-cn',
    'Accept': '*/*'
}


def get_locations(filename: str, config: str) -> dict:
    cf = configparser.ConfigParser()
    cf.read(filename, encoding="utf-8")
    return {
        "lon": [int(cf.get(config, "lon_a")), int(cf.get(config, "lon_b"))],
        "lat": [int(cf.get(config, "lat_a")), int(cf.get(config, "lat_b"))],
        "accuracy": int(cf.get(config, "accuracy")),
        "coordinates": cf.get(config, "coordinates")
    }


def user_config(filename: str) -> list:
    cf = configparser.ConfigParser()
    cf.read(filename, encoding="utf-8")
    return [cf.get("user", "location"), cf.get("user", "username"), cf.get("user", "password")]


def login(username: str, password: str, is_base64: bool = False) -> str:
    print("Start to login")
    if not is_base64:
        password = base64.b64encode(password.encode("utf-8")).decode("utf-8")
    captcha_data = requests.get(f"{BASE_URL}/captchaImage", headers=PUB_HEADERS).json()
    print(f"Captcha uuid: {captcha_data['uuid']}")
    login_data = {
        "username": username,
        "password": password,
        "code": captcha_data["showCode"],
        "uuid": captcha_data["uuid"]
    }
    token_data = requests.post(f"{BASE_URL}/login", headers=PUB_HEADERS, json=login_data).json()
    if "token" not in token_data:
        raise RuntimeError(f"Login failed: {token_data}")
    token = token_data["token"]
    header = PUB_HEADERS.copy()
    header.update(dict(Authorization=f"Bearer {token}"))
    user_data = requests.get(f"{BASE_URL}/getInfo", headers=header).json()
    print(f"Login at: {user_data['user']['userId']}[{user_data['user']['nickName']}]")
    return token


def generate_location(config: dict):
    lon = list(str(random.randint(*config["lon"])))
    lat = list(str(random.randint(*config["lat"])))
    lon.insert(-config["accuracy"], ".")
    lat.insert(-config["accuracy"], ".")
    lon = "".join(lon)
    lat = "".join(lat)
    return config["coordinates"], ",".join([lon, lat])


def do_sign(token: str, locat_data: dict, force_sign: bool = False, disable_notice: bool = False):
    header = PUB_HEADERS.copy()
    header.update(dict(Authorization=f"Bearer {token}"))
    # Check first
    now_date = datetime.date.today()
    range_month = calendar.monthrange(now_date.year, now_date.month)[1]
    query_date = {
        "params": {
            "beginCreateTime": datetime.date(year=now_date.year, month=now_date.month, day=1).strftime("%Y-%m-%d"),
            "endCreateTime": datetime.date(year=now_date.year, month=now_date.month, day=range_month).strftime(
                "%Y-%m-%d")
        }
    }
    query_str = urllib.parse.urlencode(query_date)
    check_list = requests.get(f"{BASE_URL}/student/health/list?{query_str}", headers=header).json()
    print(f"Month[{now_date.year}-{now_date.month}]: {len(check_list['rows'])} record(s)")
    last_log_time = time.strptime(check_list["rows"][-1]["createTime"], "%Y-%m-%d %H:%M:%S")
    if last_log_time.tm_mday == now_date.day:
        print(f"Warning: Signed in today({check_list['rows'][-1]['createTime']})")
        if force_sign:
            print("FORCE SIGN enabled")
        else:
            if disable_notice:
                print(">>>The operation was cancelled<<<")
                return
            else:
                while True:
                    i = input("Will force sign, continue?(y/N)>>> ")
                    if i.lower() == "y":
                        print("FORCE SIGN enabled by user")
                        break
                    elif i.lower() == "n":
                        print(">>>The operation was cancelled by user<<<")
                        return
    locat = generate_location(locat_data)
    temperature = str(random.randint(364, 368) / 10)
    sign_data = {
        "location": locat[1],
        "dangerousRegion": "2",
        "goOutRemark": "",
        "dangerousRegionRemark": "",
        "remark": "",
        "goOut": "1",
        "familySituation": "1",
        "temperature": temperature,
        "healthState": "1",
        "coordinates": locat[0],
        "contactSituation": "2"
    }
    print(f"Start to sign: {sign_data}")
    res = requests.post(f"{BASE_URL}/student/health", headers=header, json=sign_data).json()
    if res["code"] == 200:
        print(">>>Sign success<<<")
    else:
        print(">>>Sign failed<<<")
        raise RuntimeError(f"Sign failed: {res}")


if __name__ == '__main__':
    try:
        location, username, password = user_config("user.conf")
        token = login(username, password)
        do_sign(token, get_locations("location.conf", location))
    except Exception as err:
        traceback.print_exc()
    finally:
        time.sleep(5)  # Wait
