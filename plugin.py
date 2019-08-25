#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Basic Python Plugin Example
#
# Author: Xorfor
#
"""
<plugin key="xfr_pws" name="PWS" author="Xorfor" version="1.0.0">
    <params>
        <param field="Port" label="Port" width="30px" required="true" default="5000"/>
        <param field="Mode6" label="Debug" width="100px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz


class BasePlugin:
    #
    __UNUSED = 0
    __USED = 1
    #
# Devices
    __UNIT_TMP1 = 1
    __UNIT_TMP2 = 14
    __UNIT_THB1 = 2
    __UNIT_HUM1 = 3
    __UNIT_HUM2 = 15
    __UNIT_WND1 = 4
    __UNIT_TPHM = 5
    __UNIT_RAIN = 6
    __UNIT_SOLR = 7
    __UNIT_UVID = 8
    __UNIT_UVAT = 16
    __UNIT_DEWP = 9
    __UNIT_WND2 = 10
    __UNIT_CHLL = 11
    __UNIT_WND3 = 12
    __UNIT_GUST = 13
    __UNIT_SWTP = 20

    __UNITS = [
        # id, name, type, subtype, options, used
        [__UNIT_TMP1, "Temperature (indoor)", 80, 5, {}, __USED],
        [__UNIT_TMP2, "Temperature", 80, 5, {}, __USED],
        [__UNIT_DEWP, "Dew point", 80, 5, {}, __USED],
        [__UNIT_CHLL, "Chill", 80, 5, {}, __USED],
        [__UNIT_HUM1, "Humidity", 81, 1, {}, __USED],
        [__UNIT_HUM2, "Humidity (indoor)", 81, 1, {}, __USED],
        [__UNIT_TPHM, "Temp + Hum", 82, 1, {}, __USED],
        [__UNIT_THB1, "THB", 84, 1, {}, __USED],
        [__UNIT_RAIN, "Rain", 85, 1, {}, __USED],
        [__UNIT_WND1, "Wind", 86, 1, {}, __USED],
        [__UNIT_WND2, "Wind", 86, 4, {}, __USED],
        [__UNIT_UVID, "UVI", 87, 1, {}, __USED],
        [__UNIT_UVAT, "UV Alert", 243, 22, {}, __USED],
        [__UNIT_SOLR, "Solar radiation", 243, 2, {}, __USED],
        [__UNIT_WND3, "Wind speed", 243, 31, {"Custom": "0;m/s"}, __USED],
        [__UNIT_GUST, "Gust", 243, 31, {"Custom": "0;m/s"}, __USED],
        [__UNIT_SWTP, "Station", 243, 19, {}, __USED],
    ]

    def __init__(self):
        self.enabled = False
        self.httpServerConn = None
        self.httpServerConns = {}

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect {}={}:{} {}-{}".format(
            Connection.Name,
            Connection.Address,
            Connection.Port,
            Status,
            Description
        )
        )
        Domoticz.Log(str(Connection))
        self.httpServerConns[Connection.Name] = Connection

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect {}".format(Connection.Name))
        # Domoticz.Log("Server Connections:")
        # for x in self.httpServerConns:
        #     Domoticz.Log("--> "+str(x)+"'.")
        if Connection.Name in self.httpServerConns:
            del self.httpServerConns[Connection.Name]

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage {}={}:{} {}".format(
            Connection.Name,
            Connection.Address,
            Connection.Port,
            Data,
        )
        )
        DumpHTTPResponseToLog(Data)
        dataIsValid = False
        # Incoming Requests
        if "Verb" in Data:
            strVerb = Data["Verb"]
            strURL = Data["URL"]
            Domoticz.Log("Request {}".format(strVerb))
            if strVerb == "GET" and strURL.split("?")[0] == "/weatherstation/updateweatherstation.php":
                protocol = "Wunderground"
                strData = strURL.split("?")[1]
                Domoticz.Log("strData: {}".format(strData))
                # Convert URL parameters to dict for generic update of the devices
                data = dict(item.split("=") for item in strData.split("&"))
                Domoticz.Log("data: {}".format(data))
                if len(data) > 0:
                    dataIsValid = True
                    # Get data
                    humidity = int(data.get("humidity"))
                    humiditystatus = humidity2status(humidity)
                    indoorhumidity = int(data.get("indoorhumidity"))
                    indoorhumiditystatus = humidity2status(indoorhumidity)
                    temp = round(temperature_f2iso(
                        float(data.get("tempf"))), 1)
                    indoortemp = round(temperature_f2iso(
                        float(data.get("indoortempf"))), 1)
                    dewpt = round(temperature_f2iso(
                        float(data.get("dewptf"))), 1)
                    windchill = round(temperature_f2iso(
                        float(data.get("windchillf"))), 1)
                    windspeed = round(speed_mph2iso(
                        float(data.get("windspeedmph"))), 1)
                    windgust = round(speed_mph2iso(
                        float(data.get("windgustmph"))), 1)
                    winddir = int(data.get("winddir"))
                    solarradiation = float(data.get("solarradiation"))
                    uv = int(data.get("UV"))
                    softwaretype = data.get("softwaretype")
                    pressure = pressure_inches2iso(float(data.get("baromin")))
                    preciprate = round(distance_inch2iso(
                        float(data.get("rainin"))), 2)
                    preciptotal = round(distance_inch2iso(
                        float(data.get("dailyrainin"))), 1)

            elif strVerb == "POST" and strURL == "/data/report/":
                protocol = "Ecowitt"
                Domoticz.Log("Ecowitt protocol")
                strData = Data["Data"].decode("utf-8")
                data = dict(item.split("=") for item in strData.split("&"))
                Domoticz.Log("data: {}".format(data))
                if len(data) > 0:
                    dataIsValid = True
                    # Get data
                    humidity = int(data.get("humidity"))
                    humiditystatus = humidity2status(humidity)
                    indoorhumidity = int(data.get("humidityin"))
                    indoorhumiditystatus = humidity2status(indoorhumidity)
                    temp = round(temperature_f2iso(
                        float(data.get("tempf"))), 1)
                    indoortemp = round(temperature_f2iso(
                        float(data.get("tempinf"))), 1)
                    windspeed = round(speed_mph2iso(
                        float(data.get("windspeedmph"))), 1)
                    windgust = round(speed_mph2iso(
                        float(data.get("windgustmph"))), 1)
                    winddir = int(data.get("winddir"))
                    pressure = pressure_inches2iso(
                        float(data.get("baromrelin")))
                    preciprate = round(distance_inch2iso(
                        float(data.get("rainratein"))), 2)
                    preciptotal = round(distance_inch2iso(
                        float(data.get("dailyrainin"))), 1)
                    softwaretype = data.get("stationtype")
                    solarradiation = float(data.get("solarradiation"))
                    uv = int(data.get("uv"))
                    # dewpt not reported in Ecowitt
                    dewpt = dew_point(temp, humidity) if data.get("dewptf") is None else round(
                        temperature_f2iso(float(data.get("dewptf"))), 1)
                    # windchill not reported in Ecowitt
                    windchill = wind_chill(temp, windspeed) if data.get("windchillf") is None else round(
                        temperature_f2iso(float(data.get("windchillf"))), 1)
            else:
                Domoticz.Error("Unknown protocol")
                dataIsValid = False
            if dataIsValid:
                Domoticz.Log("Protocol: {}".format(protocol))
                # Update devices
                UpdateDevice(self.__UNIT_TMP1,
                             0,
                             "{}".format(indoortemp),
                             )
                UpdateDevice(self.__UNIT_TMP2,
                             0,
                             "{}".format(temp),
                             )
                UpdateDevice(self.__UNIT_HUM1,
                             int(humidity),
                             humiditystatus,
                             )
                UpdateDevice(self.__UNIT_HUM2,
                             int(indoorhumidity),
                             indoorhumiditystatus,
                             )
                UpdateDevice(self.__UNIT_DEWP,
                             0,
                             "{}".format(dewpt),
                             )
                UpdateDevice(self.__UNIT_CHLL,
                             0,
                             "{}".format(windchill),
                             )
                UpdateDevice(self.__UNIT_TPHM,
                             0,
                             "{};{};{}".format(
                                 temp, humidity, humiditystatus),
                             )
                UpdateDevice(self.__UNIT_WND1,
                             0,
                             "{};{};{};{};{};{}".format(
                                 winddir, bearing2status(winddir), windspeed*10, windgust*10, temp, windchill)
                             )
                UpdateDevice(self.__UNIT_WND2,
                             0,
                             "{};{};{};{};{};{}".format(
                                 winddir, bearing2status(winddir), windspeed*10, windgust*10, temp, windchill)
                             )
                # Custom device, so we have to handle the alternative windspeed units
                windunit = int(Settings["WindUnit"])
                Domoticz.Log("WindUnit: {}".format(windunit))
                UpdateDeviceOptions(
                    self.__UNIT_WND3, Options=speed2options(windunit))
                UpdateDevice(self.__UNIT_WND3,
                             0,
                             "{}".format(speed2unit(windspeed, windunit)),
                             )
                # Custom device, so we have to handle the alternative windspeed units
                UpdateDeviceOptions(
                    self.__UNIT_GUST, Options=speed2options(windunit))
                UpdateDevice(self.__UNIT_GUST,
                             0,
                             "{}".format(speed2unit(windgust, windunit))
                             )
                UpdateDevice(self.__UNIT_GUST,
                             0,
                             "{}".format(windgust),
                             )
                UpdateDevice(self.__UNIT_SOLR,
                             int(solarradiation),
                             str(solarradiation),
                             )
                UpdateDevice(self.__UNIT_UVID,
                             int(uv),
                             "{};{}".format(uv, temp),
                             )
                UpdateDevice(self.__UNIT_UVAT,
                             uv2status(uv),
                             str(uv) + " UVI",
                             )
                UpdateDevice(self.__UNIT_SWTP,
                             0,
                             "{} ({}): {}".format(
                                 Connection.Address, softwaretype, protocol),
                             )
                UpdateDevice(self.__UNIT_THB1,
                             0,
                             "{};{};{};{};{}".format(
                                 temp, humidity, humiditystatus, pressure, pressure2status(pressure))
                             )
                UpdateDevice(self.__UNIT_RAIN,
                             0,
                             "{};{}".format(preciprate*100, preciptotal)
                             )

    def onStart(self):
        Domoticz.Debug("onStart")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        else:
            Domoticz.Debugging(0)
        # DumpConfigToLog()
        # Devices
        if len(Devices) == 0:
            for unit in self.__UNITS:
                Domoticz.Device(Unit=unit[0],
                                Name=unit[1],
                                Type=unit[2],
                                Subtype=unit[3],
                                Options=unit[4],
                                Used=unit[5],
                                ).Create()
        # Connections
        self.httpServerConn = Domoticz.Connection(
            Name="Server",
            Transport="TCP/IP",
            Protocol="HTTP",
            Port=Parameters["Port"]
        )
        self.httpServerConn.Listen()
        Domoticz.Log("Leaving on start")


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions


def LogMessage(Message):
    if Parameters["Mode6"] != "Normal":
        Domoticz.Log(Message)
    elif Parameters["Mode6"] != "Debug":
        Domoticz.Debug(Message)
    else:
        f = open("http.html", "w")
        f.write(Message)
        f.close()


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return


def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Log("!!! HTTP Details ("+str(len(httpDict))+"):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Log("!!! --->'"+x+" ("+str(len(httpDict[x]))+"):")
                for y in httpDict[x]:
                    Domoticz.Log("!!! ------->'" + y + "':'" +
                                 str(httpDict[x][y]) + "'")
            else:
                Domoticz.Log("!!! --->'" + x + "':'" + str(httpDict[x]) + "'")


def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[Unit].TimedOut != TimedOut or AlwaysUpdate:
            Devices[Unit].Update(
                nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug(
                "Update {}: {} - {} - {}".format(Devices[Unit].Name, nValue, sValue, TimedOut))


def UpdateDeviceOptions(Unit, Options={}):
    if Unit in Devices:
        if Devices[Unit].Options != Options:
            Devices[Unit].Update(nValue=Devices[Unit].nValue,
                                 sValue=Devices[Unit].sValue, Options=Options)
            Domoticz.Debug("Device Options update: {}={}".format(
                Devices[Unit].Name, Options))


################################################################################
# Plugin functions
################################################################################
HUMIDITY_NORMAL = 0
HUMIDITY_COMFORTABLE = 1
HUMIDITY_DRY = 2
HUMIDITY_WET = 3


def humidity2status(hlevel):
    if hlevel < 25:
        return HUMIDITY_DRY
    if 25 <= hlevel <= 60:
        return HUMIDITY_COMFORTABLE
    if hlevel > 60:
        return HUMIDITY_WET
    return HUMIDITY_NORMAL


def temperature_f2iso(value):
    """Temperature conversion from Fahrenheit to ISO (Celsius)
    Args:
        value (float): temperature in Fahrenheit
    Returns:
        temperature in Celsius
    """
    return (value - 32) / 1.8


def speed_mph2iso(value):
    """Speed conversion from mp/h to ISO (m/s)
    Args:
        value (float): speed in mp/h
    Returns:
        speed in m/s
    """
    return (value * 0.44704)


def bearing2status(d):
    """
    Based on https://gist.github.com/RobertSudwarts/acf8df23a16afdb5837f
    """
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    count = len(dirs)  # Number of entries in list
    step = 360 / count  # Wind direction is in steps of 22.5 degrees (360/16)
    ix = int((d + (step / 2)) / step)  # Calculate index in the list
    return dirs[ix % count]


BARO_FORECAST_NOINFO = 0
BARO_FORECAST_SUNNY = 1
BARO_FORECAST_PARTLYCLOUDY = 2
BARO_FORECAST_CLOUDY = 3
BARO_FORECAST_RAIN = 4
BARO_FORECASTS = {BARO_FORECAST_NOINFO,
                  BARO_FORECAST_SUNNY,
                  BARO_FORECAST_PARTLYCLOUDY,
                  BARO_FORECAST_CLOUDY,
                  BARO_FORECAST_RAIN,
                  }


def pressure2status(pressure):
    if pressure < 1000:
        return BARO_FORECAST_RAIN
    elif pressure < 1020:
        return BARO_FORECAST_CLOUDY
    elif pressure < 1030:
        return BARO_FORECAST_PARTLYCLOUDY
    else:
        return BARO_FORECAST_SUNNY


def uv2status(value):
    if value < 3:
        return 0
    elif value < 6:
        return 1
    elif value < 8:
        return 2
    elif value < 11:
        return 3
    else:
        return 4


def pressure_inches2iso(value):
    """Pressure conversion from inches Hg to ISO (hPa)
    Args:
        value (float): pressure in inches Hg
    Returns:
        pressure in hPa
    """
    return value * 33.86


def distance_inch2iso(value):
    """Distance conversion from inches to ISO (cm)
    Args:
        value (float): Distance in inches
    Returns:
        Distance in cm
    """
    return value * 2.54


def dew_point(t, h):
    """Calculate dewpoint
    Args:
        t (float): temperature in °C
        h (float): relative humidity in %
    Returns:
        calculated dewpoint in °C
    Ref:
        https://www.ajdesigner.com/phphumidity/dewpoint_equation_dewpoint_temperature.php
    """
    return round((h / 100) ** (1 / 8) * (112 + 0.9 * t) + 0.1 * t - 112, 2)


def wind_chill(t, v):
    """ Windchill temperature is defined only for temperatures at or below 10 °C 
    and wind speeds above 4.8 kilometres per hour.
    Args:
        t: temperature in °C
        v: wind speed in m/s
    Returns:
        calculated windchill temperature in °C
    Ref: 
        https://en.wikipedia.org/wiki/Wind_chill
    """
    # Calculation expects km/h instead of m/s, so
    v = v * 3.6
    if t < 10 and v > 4.8:
        v = v ** 0.16
        return round(13.12 + 0.6215 * t - 11.37 * v + 0.3965 * t * v, 1)
    else:
        return t


WIND_SPEED_MS = 0
WIND_SPEED_KMH = 1
WIND_SPEED_MPH = 2
WIND_SPEED_KNOTS = 3
WIND_SPEED_BEAUFORT = 4
WIND_SPEED_ISO = WIND_SPEED_MS
WIND_SPEEDS = {
    WIND_SPEED_MS,
    WIND_SPEED_KMH,
    WIND_SPEED_MPH,
    WIND_SPEED_KNOTS,
    WIND_SPEED_BEAUFORT,
}


def speed2unit(speed, unit):
    """Convert the windspeed (in m/s) to the given unit
    Args:
        speed: windspeed in m/s
        unit: the new unit for windspeed
    Returns:
        calculated windspeed for the given unit
    """
    if unit in WIND_SPEEDS:
        if unit == WIND_SPEED_ISO:
            return speed
        elif unit == WIND_SPEED_KMH:
            return round(speed * 3.60000000,1 )
        elif unit == WIND_SPEED_MPH:
            return round(speed * 2.23693629,1)
        elif unit == WIND_SPEED_KNOTS:
            return round(speed * 1.94384449,1)
        elif unit == WIND_SPEED_BEAUFORT:
            if 0 <= speed < 0.3:
                return 0
            elif 0.3 <= speed < 1.6:
                return 1
            elif 1.6 <= speed < 3.4:
                return 2
            elif 3.4 <= speed < 5.5:
                return 3
            elif 5.5 <= speed < 8.0:
                return 4
            elif 8.0 <= speed < 10.8:
                return 5
            elif 10.8 <= speed < 13.9:
                return 6
            elif 13.9 <= speed < 17.2:
                return 7
            elif 17.2 <= speed < 20.8:
                return 8
            elif 20.8 <= speed < 24.5:
                return 9
            elif 24.5 <= speed < 28.5:
                return 10
            elif 28.5 <= speed < 32.7:
                return 11
            elif 32.7 <= speed:
                return 12
        else:
            return None
    else:
        return None


def speed2options(unit):
    if unit in WIND_SPEEDS:
        if unit == WIND_SPEED_ISO:
            return {"Custom": "0;m/s"}
        elif unit == WIND_SPEED_KMH:
            return {"Custom": "0;km/h"}
        elif unit == WIND_SPEED_MPH:
            return {"Custom": "0;mph"}
        elif unit == WIND_SPEED_KNOTS:
            return {"Custom": "0;kn"}
        elif unit == WIND_SPEED_BEAUFORT:
            return {"Custom": "0;bf"}
        else:
            return {}
    else:
        return {}
