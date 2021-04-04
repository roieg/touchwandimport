import json

export_filename = "wsupdates.json"

if __name__ == '__main__':

    filename = input('filename : ')
    #	filename = 'log.json'

    if filename:
        with open(filename, 'r', encoding='utf8') as file:
            data_store = json.load(file)

    json_file = open(export_filename, "w+", encoding='utf8')
    json_file.write("[\r\n")
    for unit in data_store:
        if unit["type"] == "UNIT_CHANGED":
            if unit["unit"]['type'] == "AlarmSensor":
                print(unit["unit"])
                json_file.write(json.dumps(unit["unit"]))
                json_file.write('\r\n,')

    json_file.write("]")
    json_file.close()
