import json
import os
import re
from pathlib import Path

import requests

ICONS_DICT = dict(Switch="<light>", shutter="<rollershutter>", dimmer="<light>", AlarmSensor="<motion>")
TYPE_DICT = dict(Switch="Switch", shutter="Rollershutter", dimmer="Dimmer", AlarmSensor="AlarmSensor")
TAG_DICT = dict(Switch="[\"Lighting\"]", dimmer="[\"Lighting\"]", shutter="[\"Shutter\"]", AlarmSensor="[\"\"]")
GROUPS_DICT = dict(Switch="gLights", shutter="gShutters", dimmer="gLights", AlarmSensor="gSensors")
CHANNEL_DICT = dict(Switch="switch", shutter="shutter", dimmer="brightness", AlarmSensor="alarm")
UNIT_ID = dict(Switch="switch", shutter="shutter", dimmer="dimmer", AlarmSensor="AlarmSensor")

# filename = "c:\\tmp\\units.json"
unit_string = "{:<15} {:<20} {:<30} {:<20} {:<20} {:<20} {:<20}"
thing_string = "Thing {} {} {}"
thing_bridge_string = "Bridge touchwand:bridge:{} [ipAddress=\"{}\", username=\"{}\" , password=\"{}\"] "
channel_string = "channel=\"touchwand:{}:{}:{}:{}\""
login_url = "http://{}/auth/login?user={}&psw={}"
list_units_url = "http://{}/units/listUnits"
Shutter = []
Switches = []
AlarmSensor = []
Wall_Controllers = []
things_shutters = []
things_switches = []
things_wall_controllers = []
things_alarm_sensors = []


def get_units(ip, user, passwd):
    url = login_url.format(ip, user, passwd)
    r = requests.get(url)
    url = list_units_url.format(ip)
    rlist = requests.get(url, cookies=r.cookies)
    return rlist.content


def clean_name(s):
    # Remove invalid characters
    s = re.sub('[^0-9a-zA-Z_]', '', s)
    # Remove leading characters until we find a letter or underscore
    s = re.sub('^[^a-zA-Z_]+', '', s)
    s: str = s.strip()
    return s


if __name__ == '__main__':
    controller_address = input('TouchWand controller IP address : ')
    username = input('username: ')
    password = input('password: ')
    bridgeId = input('bridge Id: ')

    #    controller_address = ''
    #    username = ''
    #    password = ''
    #    bridgeId = ''

    controller_id = controller_address.replace('.', '')

    print('Connecting server {} to get units list '.format(controller_address))
    response = get_units(controller_address, username, password)

    response_filename = "response" + controller_id + ".json"
    response_file = open(response_filename, "w+", encoding='utf8')
    response_file.write(response.decode("utf8"))
    response_file.close()

    data_store = json.loads(response)

    units_filename = "units" + controller_id + ".json"
    print('Creating units json file: ', units_filename)

    json_file = open(units_filename, "w+", encoding='utf8')
    json_file.write(json.dumps(data_store, indent=4, sort_keys=True))
    json_file.close()

    sensors_filename = "sensors_" + controller_id + ".json"
    print('Creating sensors json file: ', sensors_filename)

    sensorsJsonFile = open(sensors_filename, "w+", encoding='utf8')
    sensorsJsonFile.write("[\r\n")
    for unit in data_store:
        if unit["type"] == 'AlarmSensor':
            sensorsJsonFile.write(json.dumps(unit, indent=4, sort_keys=True))
            sensorsJsonFile.write(",\r\n")

    sensorsJsonFile.write("\r\n]")
    sensorsJsonFile.close()

    items_filename = "touchwand" + controller_id + ".items"
    things_filename = "touchwand" + controller_id + ".things"

    thing_bridge = thing_bridge_string.format(bridgeId, controller_address, username, password)

    if Path(items_filename).is_file():
        os.remove(items_filename)

    if Path(things_filename).is_file():
        os.remove(things_filename)

    items_file = open(items_filename, "x", encoding='utf8')
    print('Creating items file: ', items_filename)
    things_file = open(things_filename, "x", encoding='utf8')
    print('Creating things file: ', things_filename)

    unit_counter = 0
    for unit in data_store:
        if unit["type"] in TYPE_DICT:
            unit_counter = unit_counter + 1
            unit_name = "\"" + unit["name"] + "\""
            if unit_name.isascii():
                variable_name = TYPE_DICT[unit["type"]] + "_" + clean_name(unit["name"])
            else:
                variable_name = TYPE_DICT[unit["type"]] + "_" + str(unit_counter)
            group_name = '(' + GROUPS_DICT[unit["type"]] + ')'
            unit_type = TYPE_DICT[unit["type"]]
            icon = ICONS_DICT[unit["type"]]
            unit_tag = TAG_DICT[unit["type"]]
            uid = UNIT_ID[unit["type"]]
            unit_id = unit["id"]
            channel = "{" + channel_string.format(uid, bridgeId, unit_id,
                                                  CHANNEL_DICT[unit["type"]]) + "}"

            item = unit_string.format(unit_type, variable_name, unit_name, icon,
                                      group_name, unit_tag, channel)
            thing = thing_string.format(uid, unit_id, unit_name)
            if unit["type"] == "Switch":
                Switches.append(item)
                things_switches.append(thing)
            if unit["type"] == 'shutter':
                Shutter.append(item)
                things_shutters.append(thing)
            if unit["type"] == 'WallController':
                Wall_Controllers.append(item)
                things_wall_controllers.append(thing)
            if unit["type"] == 'dimmer':
                Switches.append(item)
                things_switches.append(thing)
            if unit["type"] == 'AlarmSensor':
                AlarmSensor.append(item)
                things_alarm_sensors.append(thing)

    items_file.write("/* Shutters */\r\r\r")
    for item in Shutter:
        items_file.write(item)
        items_file.write("\r")

    items_file.write("\r\r\r/* Switches */\r\r\r")
    for item in Switches:
        items_file.write(item)
        items_file.write("\r")

    items_file.write("\r\r\r/* WallControllers */\r\r\r")
    for item in Wall_Controllers:
        items_file.write(item)
        items_file.write("\r")

    items_file.write("\r\r\r/* Alarm Sensors */\r\r\r")
    for item in AlarmSensor:
        items_file.write(item)
        items_file.write("\r")

    items_file.close()

    things_file.write(thing_bridge)
    things_file.write(" {\r")
    for thing in things_switches:
        things_file.write(thing)
        things_file.write("\r")

    for thing in things_shutters:
        things_file.write(thing)
        things_file.write("\r")

    for thing in things_wall_controllers:
        things_file.write(thing)
        things_file.write("\r")

    for thing in things_alarm_sensors:
        things_file.write(thing)
        things_file.write("\r")

    things_file.write("}\r")
    things_file.close()

    print('Done...')
