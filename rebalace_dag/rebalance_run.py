#for numbering of processors , we will be following the convention of starting at 1 and incrementing by 1 on the next processor

import sys
import csv
import json
import urllib2,urllib
import re
import time

arguments = sys.argv[1:]
rate = int(arguments[0])
config_file = arguments[1]
json_file = arguments[2]
rd_ip = arguments[3]
rd_port = arguments[4]
master_ip = arguments[5]
master_port = arguments[6]
stream_file = arguments[7]

#some assumptions will be made for example each device which runs the platform service will be creating logs in same directory as well as
#at the time of rebalance , we will be moving the logs of the current running configuration (which will be overridden once rebalance is done)
#to a predefined location, so these assumptions should be true before running this experiment. The json file which we will be reading will 
#use these location only.
current_logs_dir = '/rebalance_logs/'
logs_backup_dir = '/rebalance_' #here we will adding the config name which we read from config_file
configs = []
echo_json = ''
num_processors = 0
stream_json = ''

with open(config_file,'r') as csvfile:
	reader = csv.reader(csvfile, delimiter = ',')
	for row in reader:
		configs.append(row)


with open(json_file,'r') as json_data:
	echo_json = json.load(json_data)
	num_processors = len(echo_json["processors"])


with open(stream_file,'r') as stream_data:
	stream_json = json.load(stream_data)

rd_base_url = 'http://' + rd_ip + ':' + rd_port + '/cat' 


dict_id_ip = {}
edge_devices = []
fog_devices = []
cloud_devices = []
processor_to_device = {}

def getCurrentDevicesWithIp():
	response = urllib2.urlopen(rd_base_url)
	data = json.load(response)
	try:
		items = data["items"]
	except KeyError as e:
		print "There are no devices in the RD, Exiting"
		exit()
	#this contains list of tuples containing id and ip of device
	global dict_id_ip
	dict_id_ip = {}
	global edge_devices
	edge_devices = []
	global fog_devices
	fog_devices = []
	global cloud_devices
	cloud_devices = []
	for item in items:
		href = item["href"]
		ip_match = re.search("/device/ip/(.*)", href)
		if ip_match is None:
			pass
		else:
			device_id = ip_match.group(1)
			item_metadata = item["item-metadata"]
			for metadata in item_metadata:
				if metadata["rel"] == "IP":
					device_ip = metadata["val"]
					#assumption - edge have ip from 10.24.24.100 to 10.24.24.110, fog have 10.24.24.114 or above
					# else it is cloud
					private_ip_match = re.search("10\.24\.24\.(.*)", device_ip)
					if private_ip_match is None:
						cloud_devices.append(device_id)
					else:
						last_val = int(private_ip_match.group(1))
						if last_val <= 110:
							edge_devices.append(device_id)
						else:
							fog_devices.append(device_id)
					dict_id_ip[device_id] = device_ip




def sendStreamToRD(device_id, processor_id):
	req_url = rd_base_url + '?href=/device/input_stream/' + device_id + '/' + processor_id
	global stream_json
	stream_json["item-metadata"][2]["val"] = processor_id
	stream_json["item-metadata"][3]["val"] = device_id
	stream_json["href"] = '/device/input_stream/' + device_id + '/' + processor_id
	headers = {'Content-Type' : 'text/plain'}
	req = urllib2.Request(req_url, json.dumps(stream_json), headers)
	response = urllib2.urlopen(req)
	if response.getcode() != 200:
		print "Error while registering stream, Exiting"
		exit()


def deleteStreamFromRD():
	global processor_to_device
	for key in processor_to_device.keys():
		url = rd_base_url + '?href=/device/input_stream/' + processor_to_device[key] + '/' + key
		request = urllib2.Request(url, data=None)
		request.get_method = lambda: 'DELETE'
		response = urllib2.urlopen(request)
		if response.getcode() != 200:
			print "Error while deleting stream, Exiting"
	processor_to_device = {}


			
def registerStreamsWithRD(device_list,current_config):
	if current_config == 'Edge' or current_config == 'Fog':
		device_id = device_list[0]
		for i in range(num_processors):
			sendStreamToRD(device_id,str(i+1))
			processor_to_device[str(i+1)] = device_id
	elif current_config == 'Cloud':
		edge_device = device_list[0]
		cloud_device = device_list[1]
		sendStreamToRD(edge_device,'1')
		processor_to_device['1'] = edge_device
		sendStreamToRD(edge_device,'7')
		processor_to_device['7'] = edge_device	
		for i in range(2,7):
			sendStreamToRD(cloud_device, str(i))
			processor_to_device[str(i)] = cloud_device
		sendStreamToRD(cloud_device, '8')
		processor_to_device['8'] = cloud_device
	else:
		config_match = re.search("EFC\((.*):(.*):(.*)\)",current_config[1])
		if config_match is None:
			print "Incorrect configuration provided, Exiting"
			exit()
		edge_no = config_match.group(1)
		fog_no = config_match.group(2)
		cloud_no = config_match.group(3)
		for i in range(0,int(edge_no)):
			sendStreamToRD(device_list[0],str(i+1))
			processor_to_device[str(i+1)] = device_list[0]
		for i in range(int(edge_no), int(edge_no) + int(fog_no)):
			sendStreamToRD(device_list[1],str(i+1))
			processor_to_device[str(i+1)] = device_list[1]
		for i in range(int(edge_no) + int(fog_no),6):
			sendStreamToRD(device_list[2],str(i+1))
			processor_to_device[str(i+1)] = device_list[2]

		sendStreamToRD(device_list[0],'7')
		processor_to_device['7'] = device_list[0]

		sendStreamToRD(device_list[2],'8')
		processor_to_device['8'] = device_list[2]


def getProcessorToDeviceMappingUtil(current_config):
	device_list = []
	if current_config == 'Edge':
		if len(edge_devices) == 0:
			print "No edge devices present, Exiting"
			exit()
		else:
			device_list.append(edge_devices[0])
			registerStreamsWithRD(device_list,current_config)
	elif current_config == 'Fog':
		if len(fog_devices) == 0:
			print "No fog devices present, Exiting"
			exit()
		else:
			device_list.append(fog_devices[0])
			registerStreamsWithRD(device_list,current_config)
	elif current_config == 'Cloud':
		if len(edge_devices) == 0 or len(cloud_devices) == 0:
			print "No edge/cloud devices present, Exiting"
			exit()
		else:
			device_list.append(edge_devices[0])
			device_list.append(cloud_devices[0])
			registerStreamsWithRD(device_list,current_config)
	else:
		if len(edge_devices) == 0 or len(fog_devices) == 0 or len(cloud_devices) == 0:
			print "No edge/fog/cloud devices present, Exiting"
			exit()
		else:
			device_list.append(edge_devices[0])
			device_list.append(fog_devices[0])
			device_list.append(cloud_devices[0])
			registerStreamsWithRD(device_list,current_config)


			
def getProcessorToDeviceMapping(index):
	if index == 0:
		#running the first rate
		current_config = configs[0][1]
		getProcessorToDeviceMappingUtil(current_config)
	else:
		deleteStreamFromRD()
		current_config = configs[index][1]
		getProcessorToDeviceMappingUtil(current_config)

		

app_uuid = ''
dag_submission_url = 'http://' + master_ip + ':' + master_port + '/DAG'
getCurrentDevicesWithIp()  #populate the devices
getProcessorToDeviceMapping(0)   #populate the streams for the first rate
stable_rate = int(configs[0][0])
#deploy the dag
headers = {'Content-Type' : 'application/json'}
req = urllib2.Request(dag_submission_url, json.dumps(echo_json), headers)
response = urllib2.urlopen(req)
if response.getcode() != 200:
	print "Error while deploying dag, Exiting"
	exit()
else:
	data = json.load(response)
	global app_uuid
	app_uuid = data["uuid"]

dag_rebalance_url = dag_submission_url + '/rebalance?uuid=' + app_uuid
index = 0  #index of current config

while True:
	#sleep time , let the dag run for 5 minutes
	time.sleep(150)
	global rate
	rate += 10
	global stable_rate
	if rate > stable_rate:
		index += 1
		if index < len(configs):
			stable_rate = int(configs[index][0])
			getCurrentDevicesWithIp()
			getProcessorToDeviceMapping(index)
			req = urllib2.Request(dag_rebalance_url, data=None)
			req.get_method = lambda: 'POST'
			response = urllib2.urlopen(req)
			if response.getcode() != 200:
				print "Error while rebalancing, Exiting"
				exit()
			else:
				print "Successfully rebalanced"
		else:
			break


deleteStreamFromRD()

