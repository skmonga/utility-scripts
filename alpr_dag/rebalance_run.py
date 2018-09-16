#for numbering of processors , we will be following the convention of starting at 1 and incrementing by 1 on the next processor

import sys
import csv
import json
import urllib2,urllib
import re
import time
from httplib import BadStatusLine
import os
import signal
import subprocess

arguments = sys.argv[1:]
rate = int(arguments[0])
config_file = arguments[1]
json_file = arguments[2]
rd_ip = arguments[3]
rd_port = arguments[4]
master_ip = arguments[5]
master_port = arguments[6]
stream_file = arguments[7]

#we are logging rebalance time in a file named rebalance_time.txt
rebalance_time = open('rebalance_time.txt', 'w')
#we are logging the time at which rate change happens in the same config in file named updated_rate.txt
updated_rate = open('updated_rate.txt', 'w')

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

#this will start the publish message process on the broker machine
execCommand = "sshpass -p linux ssh root@10.24.24.113 'export JAVA_HOME=/usr/lib64/jvm/jre-1.8.0-openjdk/ && cd /root/kafka_producer_client && java -jar Trial1-0.0.1-SNAPSHOT-ALPR-jar-with-dependencies.jar /root/cars_markus/ 10.24.24.113:9092 {0}'"

#this will kill the publishing process on the broker machine
killCommand = 'sshpass -p linux ssh root@10.24.24.113 \'ps ax|grep Trial1-0.0.1-SNAPSHOT-ALPR-jar-with-dependencies|awk "{print $1}"|head -1|awk "{print \$1}"|xargs kill -9\''

#this will check if there is any publish process is running or not
checkCommand = 'sshpass -p linux ssh root@10.24.24.113 \'ps ax|grep [T]rial1-0.0.1-SNAPSHOT-ALPR-jar-with-dependencies|head -1|awk "{print $1}"\''

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
					#change - edge in 10.24.50.0/24	
					#assumption - edge have ip from 10.24.24.100 to 10.24.24.110, fog have 10.24.24.114 or above
					# else it is cloud
					private_ip_match = re.search("10\.24\.(.*)\.(.*)", device_ip)
					if private_ip_match is None:
						cloud_devices.append(device_id)
					else:
						last_val = int(private_ip_match.group(2))
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
		for i in range(1,3):
			sendStreamToRD(edge_device,str(i))
			processor_to_device[str(i)] = edge_device
		for i in range(7,11):
			sendStreamToRD(edge_device,str(i))
			processor_to_device[str(i)] = edge_device
		for i in range(3,7):
			sendStreamToRD(cloud_device, str(i))
			processor_to_device[str(i)] = cloud_device
	elif current_config == 'Hybrid_CC_FF':
		edge_device = device_list[0]
		fog_device = device_list[1]
		cloud_device = device_list[2]
		for i in range(1,3):
			sendStreamToRD(edge_device,str(i))
			processor_to_device[str(i)] = edge_device
		for i in range(7,11):
			sendStreamToRD(edge_device,str(i))
			processor_to_device[str(i)] = edge_device
		for i in range(3,5):
			sendStreamToRD(cloud_device,str(i))
			processor_to_device[str(i)] = cloud_device
		for i in range(5,7):
			sendStreamToRD(fog_device,str(i))
			processor_to_device[str(i)] = fog_device
	elif current_config == 'Hybrid_FC_FC':
		edge_device = device_list[0]
		fog_device = device_list[1]
		cloud_device = device_list[2]
		for i in range(1,3):
			sendStreamToRD(edge_device,str(i))
			processor_to_device[str(i)] = edge_device
		for i in range(7,11):
			sendStreamToRD(edge_device,str(i))
			processor_to_device[str(i)] = edge_device
		for i in range(4,7,2):
			sendStreamToRD(cloud_device,str(i))
			processor_to_device[str(i)] = cloud_device
		for i in range(3,6,2):
			sendStreamToRD(fog_device,str(i))
			processor_to_device[str(i)] = fog_device	
	else:
		print 'This looks like an invalid configuration'

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

#start publishing in Kafka at the given starting rate
proc = subprocess.Popen(execCommand.format(str(rate)), stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid, bufsize=0)
time.sleep(2)
os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

while True:
	#sleep for some time, then check if there is any publish process running 
	# if a publish process is running , then let it continue since we are dealing with 
	# a fixed number of input message for each rate (rate * constant)
	# if no publish process is running, then we should create a new process with 
	# updated rate for publish process
	time.sleep(5)
	proc1 = subprocess.Popen(checkCommand, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid, bufsize=0)
	time.sleep(2)
	os.killpg(os.getpgid(proc1.pid), signal.SIGTERM)
	
	global rate
	startNewProcess = True
	while True:
		line = proc1.stdout.readline()
		#print line
		if line != '':
			if 'java' in line:
				print "There is a publish process running"
				startNewProcess = False
				break
			else:
				print "********This is not a publish process********"
				#rate += 3
		else:
			break
	proc1.communicate()
	global stable_rate
	if startNewProcess == True:
		rate += 3
		if rate > stable_rate:
			index += 1
			if index < len(configs):
				print "Running in the next configuration , rate is %d, configure this in Kafka" % (rate,)
				rebalance_time.write("Rebalance time for rate : " + str(rate) + " is " + str(time.time()))
				rebalance_time.write("\n")
				try:
					stable_rate = int(configs[index][0])
					getCurrentDevicesWithIp()
					getProcessorToDeviceMapping(index)
					req = urllib2.Request(dag_rebalance_url, data=None)
					req.get_method = lambda: 'POST'
					#just before we are making request for rebalance, submitting the next higher rate in Kafka
					proc = subprocess.Popen(execCommand.format(str(rate)), stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid, bufsize=0)
					time.sleep(2)
					os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
				
					response = urllib2.urlopen(req)
					if response.getcode() != 200:
						print "Error while rebalancing, Exiting"
						exit()
					else:
						print "Successfully rebalanced"
				except BadStatusLine as error:
					print "Error occurred : " , error
			else:
				break
		else:
			print "Running at the next rate in the same configuration , rate is %d , configure this in Kafka" % (rate,)
			#just before we are making request for rebalance, submitting the next higher rate in Kafka
			proc = subprocess.Popen(execCommand.format(str(rate)), stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid, bufsize=0)
			time.sleep(2)
			os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
		
			updated_rate.write("Shifting to new rate : " + str(rate) + " at time " + str(time.time()))
			updated_rate.write("\n")

rebalance_time.close()
updated_rate.close()
deleteStreamFromRD()

