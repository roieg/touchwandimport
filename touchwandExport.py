
import json


export_filename = "wsupdates.json"

if __name__ == '__main__':

	filename = input('filename : ')	
#	filename = 'log.json'

	if filename:
		with open(filename, 'r', encoding='utf8') as file:
			data_store = json.load(file)				
				
	jsonfile = open(export_filename,"w+", encoding='utf8')
	jsonfile.write("[\r\n")
	for unit in data_store:		
		if unit["type"] == "UNIT_CHANGED":
			if unit["unit"]['type'] == "AlarmSensor":
				print(unit["unit"])
				jsonfile.write(json.dumps(unit["unit"]))
				jsonfile.write('\r\n,')

	jsonfile.write("]")		 
	jsonfile.close()
