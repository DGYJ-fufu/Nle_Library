import json
import threading
import time
import logging

# DataBus
from nle_library.databus.DataBusFactory import DataBusFactory  #
from nle_library.common.DataObserver import DataObserver, ObResult  #
from nle_library.device.GenericConnector import GenericConnector  #

# 各设备工具
from nle_library.device.ModbusTcpDev import ModbusTcpDev
from nle_library.device.NLAllInOneSensor import NLAllInOneSensor
from nle_library.device.RFID import RFID
from nle_library.device.ModbusDev import ModbusDev
from nle_library.device.Zigbee import Zigbee
from nle_library.device.CenterGateway import CenterGateway


class RGB:
    """RGB灯条类"""

    def __init__(self, mode, address, port):

        # 创建DataBus
        if mode == "TCP":
            self.DataBus = DataBusFactory.newSocketDataBus(address, port)
        else:
            self.DataBus = DataBusFactory.newSerialDataBus(address, port)

        # 实例化GenericConnector并建立连接
        self.enericConnector = GenericConnector(self.DataBus)

        time.sleep(1)  # 稍作延时

        # self.ctrlAllRGB(255, 255, 255)  # 控制RGB颜色

    def ctrlAllRGB(self, th1Value, th2Value, th3Value):
        """控制RGB颜色"""
        self.genericConnector.controlRGB(th1Value, th2Value, th3Value, 254, None)
        print("RGB控制发送完成！")

    def ctrlOneRGB(self, thCode, thValue):
        """控制单通道颜色"""
        self.genericConnectorn.controlRGBOne(thCode, thValue, 254, None)
        print("RGB控制发送完成！")


class UHF:
    """RFID类"""

    def __init__(self, mode, address, port):

        # 实例化工具类
        self.rfid = RFID()

        # 创建DataBus
        if mode == "TCP":
            self.DataBus = DataBusFactory.newSocketDataBus(address, port)
        else:
            self.DataBus = DataBusFactory.newSerialDataBus(address, port)

        # 实例化GenericConnector并建立连接
        self.genericConnector = GenericConnector(self.DataBus)

        time.sleep(1)  # 稍作延时

        while True:
            self.readEPC()
            time.sleep(1)

    def readEPC(self):
        """读取单个EPC"""

        def readEPC_callBack(data, status):
            print(f"EPC:{self.rfid.decodeReadSingleEpcFrame(data)}")

        self.genericConnector.readSingleEpc(readEPC_callBack)


class AllinOne:
    """多合一类"""

    def __init__(self, mode, address, port, SN):

        # 实例化多合一工具类,用于获取多合一数据
        self.AllInOneSensor = NLAllInOneSensor()

        # 设置从机地址
        self.SN = SN

        # 创建DataBus
        if mode == "TCP":
            self.DataBus = DataBusFactory.newSocketDataBus(address, port)
        else:
            self.DataBus = DataBusFactory.newSerialDataBus(address, port)

        # 实例化GenericConnector并建立连接
        self.genericConnector = GenericConnector(self.DataBus)

        time.sleep(1)  # 稍作延时

        while True:
            try:
                self.readTempHumiValue()
                time.sleep(0.5)
            except Exception:
                pass

    def readAirQualityValue(self):
        """读取多合一空气质量"""

        def readAirQualityValue_callBack(data, status):
            print(f"多合一空气质量:{self.AllInOneSensor.getAirQualityValue(data)}")

        self.genericConnector.sendAllInOneAirQuality(self.SN, readAirQualityValue_callBack)

    def readBodyValue(self):
        """读取多合一人体"""

        def readBodyValue_callBack(data, status):
            print(f"多合一人体:{self.AllInOneSensor.getBodyValue(data)}")

        self.genericConnector.sendAllInOneBody(self.SN, readBodyValue_callBack)

    def readPM25Value(self):
        def readPM25Value_callBack(data, status):
            print(f"多合一PM2.5:{self.AllInOneSensor.getPM25Value(data)}")

        """读取多合一PM2.5"""
        self.genericConnector.sendAllInOnePM25(self.SN, readPM25Value_callBack)

    def readPressureValue(self):
        """读取多合一大气压"""

        def readPressureValue_callBack(data, status):
            print(f"多合一大气压:{self.AllInOneSensor.getPressureValue(data)}")

        self.genericConnector.sendAllInOnePressure(self.SN, readPressureValue_callBack)

    def readTempHumiValue(self):
        """读取多合一温湿度"""

        def readTempHumiValue_callBack(data, status):
            data = self.AllInOneSensor.getTempHumiValue(data)
            print(f"多合一温度:{data[0]}")
            print(f"多合一湿度:{data[1]}")

        self.genericConnector.sendAllInOneTempHum(self.SN, readTempHumiValue_callBack)


class Ele:
    """电机类"""

    def __init__(self, mode, address, port, SN):

        # 实例化工具类
        self.modbusDev = ModbusDev()

        # 设置从机地址
        self.SN = SN

        # 创建DataBus
        if mode == "TCP":
            self.DataBus = DataBusFactory.newSocketDataBus(address, port)
        else:
            self.DataBus = DataBusFactory.newSerialDataBus(address, port)

        # 实例化GenericConnector并建立连接
        self.genericConnector = GenericConnector(self.DataBus)

        time.sleep(1)  # 稍作延时

        # self.ctrlEleSpeed(0)
        # self.ctrlEleDirection(0)

    def readEleSpeed(self):
        """读取电机速度"""

        def readEleSpeed_callBack(data, status):
            print(f"电机速度：{self.modbusDev.getMotorCtrlGetSpeed(data)}")

        self.genericConnector.sendEleGetSpeed(self.SN, 1, readEleSpeed_callBack)

    def ctrlEleSpeed(self, SpeedValue):
        """设置电机速度"""
        self.genericConnector.sendEleSetSpeed(self.SN, 1, SpeedValue, None)
        print(f"电机速度设置为:{SpeedValue}")

    def ctrlEleDirection(self, direction):
        """设置电机方向"""
        self.genericConnector.sendEleSetDirection(self.SN, 1, direction, None)
        print(f"电机方向设置为:{direction}")


class LED:
    """LED综合显示屏类"""

    def __init__(self, mode, address, port):

        # 创建DataBus
        if mode == "TCP":
            self.DataBus = DataBusFactory.newSocketDataBus(address, port)
        else:
            self.DataBus = DataBusFactory.newSerialDataBus(address, port)

        # 实例化GenericConnector并建立连接
        self.genericConnector = GenericConnector(self.DataBus)

        time.sleep(1)  # 稍作延时

        self.LEDClear()
        time.sleep(0.5)
        self.LEDShow(43, 22, 16, 1, 'Hello')

    def LEDShow(self, x, y, textSize, textColor, txt):
        """设置LED显示文本"""
        self.genericConnector.sendLedScreenText(1, x, y, textSize, textColor, txt, None)
        print(f"设置文本为{txt}\n字体大小:{textSize}\n字体颜色:{textColor}\n文本位置:{x},{y}")

    def LEDClear(self):
        """清除LED内容"""
        self.genericConnector.sendLedClearScreen(1, None)


class IOT:
    """IOT采集器类"""

    def __init__(self, mode, address, port):

        # 实例化IOT工具类,用于获取IOT数据
        self.modbusTcpDev = ModbusTcpDev()

        # 创建DataBus
        if mode == "TCP":
            self.DataBus = DataBusFactory.newSocketDataBus(address, port)
        else:
            self.DataBus = DataBusFactory.newSerialDataBus(address, port)

        # 实例化GenericConnector并建立连接
        self.genericConnector = GenericConnector(self.DataBus)

        time.sleep(1)  # 稍作延时

        # self.genericConnector.sendTCPSetDoVlue(1, 1, True, None, 0.5)   # 控制DO口

        while True:
            try:
                self.readAI([0, 2])  # 读取AI口
            except Exception:
                pass

    def readDI(self):
        """读取IOT DI口value的函数"""

        def readDI_callBack(data, status):
            data = self.iot.getTCPIOTDigitalInput(data)  # 获取IOT DI口数据
            for i in data:
                print(i)  # 打印IOT DI口数据

        self.genericConnector.sendTCPReadDI(1, readDI_callBack)  # 发送读取IOT DI口数据报文

    def readAI(self, code):
        """读取IOT AI口value的函数"""

        def readAI_callBack(data, status):
            val = self.modbusTcpDev.getTCPIOTAnalogInput(data)  # 获取IOT AI口数据
            if i == 0:
                print(f"温度:{4.375 * val / 1000 - 27.5}")  # 打印IOT AI1口数据
            elif i == 1:
                print(f"湿度:{6.25 * val / 1000 - 25}")  # 打印IOT AI2口数据

        for i in range(len(code)):
            self.genericConnector.sendTCPgetIOTVirtData(1, code[i], readAI_callBack)  # 发送读取IOT AI口数据报文
            time.sleep(1)  # 稍作延时


class Gateway:
    """中心网关类 需要让中心网关的GatewayServer设置为被动请求"""

    def __init__(self, mode, address, port):

        if mode == "TCP":
            self.DataBus = DataBusFactory.newSocketDataBus(address, port)
        else:
            self.DataBus = DataBusFactory.newSerialDataBus(address, port)

        self.genericConnector = GenericConnector(self.DataBus)

        time.sleep(1)

        # while True:
            # self.GatewaySearch("RFID")
            # time.sleep(1)

        # self.GatewayControl("LED", "")        # LED显示文字
        self.GatewayControl("m_fan", 0)  # 开启执行器

    def GatewaySearch(self, apiTag):
        """获取中心网关传感器数值"""

        def GatewaySearch_callBack(data, status):
            self.centerGateway = CenterGateway()
            print(json.loads(data.decode('UTF-8').replace('\\r', ''))["datas"][apiTag])  # 解析中心网关回复的JSON

        self.genericConnector.sendGatewaySearch(apiTag, GatewaySearch_callBack, 0.5)

    def GatewayControl(self, apiTag, value):
        """控制中心网关执行器"""

        def GatewayControl_callBack(data, status):
            if len(data) != 0:
                print("控制成功")

        self.genericConnector.sendGatewayControl(apiTag, None, value, GatewayControl_callBack, 0.5)


class ZigBee:
    """ZigBee类"""

    def __init__(self, mode, address, port):

        # 创建DataBus
        if mode == "TCP":
            self.DataBus = DataBusFactory.newSocketDataBus(address, port)
        else:
            self.DataBus = DataBusFactory.newSerialDataBus(address, port)

        # 实例化GenericConnector并建立连接
        self.genericConnector = GenericConnector(self.DataBus)

        time.sleep(1)  # 稍作延时

        # self.ctrlControl(0x2844, True, True)
        # self.ctrlControl(0x2844, False, False)

        while True:
            self.readZigBeeData()
            time.sleep(1)

    def ctrlControl(self, SN, value1, value2):
        """控制双联继电器"""
        self.genericConnector.zigbeeControl(SN, value1, value2)
        print(f"双联继电器,第一通道设置为{value1},第二通道设置为{value2}")

    def ctrlControlOne(self, SN, thCode, value):
        """控制单联继电器"""
        self.genericConnector.zigbeeControlOne(SN, thCode, value)
        print(f"双联继电器,第{thCode}通道设置为{value}")

    def readZigBeeData(self):
        """获取ZigBee数据"""

        def readZigBeeData_callBack(data, status):
            """ZigBee数据传感器数据处理"""
            zigbee = Zigbee()

            try:
                if zigbee.isReadZigbeeFrame(data):
                    # 获取 Zigbee 节点信息
                    serial, sensor_type = zigbee.getZigbeeNodeInfo(data)

                    if sensor_type == 1:
                        # 获取温湿度值
                        temperature, humidity = zigbee.getTempHumiSensorData(data)
                        print(f"Temperature: {temperature}, Humidity: {humidity}")
                    elif sensor_type == 33:
                        # 获取光照
                        light = zigbee.getLightSensorData(data)
                        print(f"Light: {light}")
                    elif sensor_type == 17:
                        # 获取人体
                        body = zigbee.getBodySensorData(data)
                        print(f"Body: {body}")
                    elif sensor_type == 48:
                        # 获取四输入传感器
                        ch1, ch2, ch3, ch4 = zigbee.getFourInputSensorData(data)
                        print(f"Channel 1: {ch1}, Channel 2: {ch2}, Channel 3: {ch3}, Channel 4: {ch4}")
            except Exception:
                pass

        self.genericConnector.setZigbeeDataListener(readZigBeeData_callBack)


if __name__ == '__main__':
    # UHF_thread = threading.Thread(target=UHF, args=('TCP', '172.18.18.15', 6001))
    # AllinOne_thread = threading.Thread(target=AllinOne, args=('TCP', '172.18.18.15', 6004, 1))
    # iot_thread = threading.Thread(target=IOT, args=('TCP', '172.18.18.19', 502))
    # zigbee_thread = threading.Thread(target=ZigBee, args=('usart', 'COM14', 9600))
    # zigbee_thread = threading.Thread(target=ZigBee, args=('TCP', '172.18.18.15', 6002))
    Gateway_thread = threading.Thread(target=Gateway, args=('TCP', '172.18.21.102', 502))

    # UHF_thread.start()
    # AllinOne_thread.start()
    # iot_thread.start()
    # zigbee_thread.start()
    Gateway_thread.start()
