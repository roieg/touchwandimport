import json
import re
from pathlib import Path
import os
import requests

ICONS_DICT = dict(Switch="<light>", shutter="<rollershutter>", dimmer="<light>")
TYPE_DICT = dict(Switch="Switch", shutter="Rollershutter", dimmer="Dimmer")
TAG_DICT = dict(Switch="[\"Lighting\"]", dimmer="[\"Lighting\"]", shutter="[\"Shutter\"]")
GROUPS_DICT = dict(Switch="gLights", shutter="gShutters", dimmer="gLights")
CHANNEL_DICT = dict(Switch="switch", shutter="shutter", dimmer="brightness")
UNIT_ID = dict(Switch="switch", shutter="shutter", dimmer="dimmer")

# filename = "c:\\tmp\\units.json"
unit_string = "{:<15} {:<20} {:<30} {:<20} {:<20} {:<20} {:<20}"
thing_string = "Thing {} {} {} [id=\"{}\"]"
thing_bridge_string = "Bridge touchwand:bridge:{} [ipAddress=\"{}\", username=\"{}\" , password=\"{}\"] "
channel_string = "channel=\"touchwand:{}:{}:{}:{}\""
login_url = "http://{}/auth/login?user={}&psw={}"
list_units_url = "http://{}/units/listUnits"
Shutter = []
Switches = []
Wall_Controllers = []
things_shutters = []
things_switches = []
things_wall_controllers = []


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
    controller_address = input("TouchWand controller IP address : ")
    username = input("username: ")
    password = input("password: ")

    # controller_address = "192.168.1.106"
    # username = "techf8dc7a142552"
    # password = "tech"
    response = get_units(controller_address, username, password)
    data_store = json.loads(response)

    #    if filename:
    #        with open(filename, 'r', encoding='utf8') as file:
    #            data_store = json.load(file)

    controller_id = controller_address.replace('.', '')
    items_filename = "touchwand" + controller_id + ".items"
    things_filename = "touchwand" + controller_id + ".things"
    thing_bridge = thing_bridge_string.format(controller_id, controller_address, username, password)

    if Path(items_filename).is_file():
        os.remove(items_filename)

    if Path(things_filename).is_file():
        os.remove(things_filename)

    items_file = open(items_filename, "x", encoding='utf8')
    things_file = open(things_filename, "x", encoding='utf8')

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
            channel = "{" + channel_string.format(uid, controller_id, unit_id,
                                                  CHANNEL_DICT[unit["type"]]) + "}"

            item = unit_string.format(unit_type, variable_name, unit_name, icon,
                                      group_name, unit_tag, channel)
            thing = thing_string.format(uid, unit_id, unit_name, unit_id)
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
    things_file.write("}\r")
    things_file.close()
