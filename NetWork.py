import json
import time

from nle_library.httpHelp.NetWorkBusiness import NetWorkBusiness

username = "13800000000"    # 云平台用户名
passwd = "13800000000"  # 云平台用户密码

network = NetWorkBusiness("api.nlecloud.com", 80)  # 实例化NetWorkBusiness


def SinInCallBack(data: str):
    print(data["ResultObj"]["AccessToken"]) # 打印token
    network.setAccessToken(data["ResultObj"]["AccessToken"])  # 设置token


network.signIn(username, passwd, SinInCallBack)  # 用户登录获取token

# 控制设备
# print(network.control(809363, 'on', 1))

# 获取单个传感器历史数据
# print(network.getDeviceSensorHistoryDatas(827757, "temp"))

# 获取单个传感器实时数据
# print(network.getSensor(872017, "m_temp"))

# 获取设备所有数据
# print(network.getSensorsRealTimeData(771151, 827757))
