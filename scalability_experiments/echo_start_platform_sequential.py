import json
import paramiko
import sys
import time
import numpy as np
import multiprocessing
from multiprocessing import Process

args = sys.argv[1:]
echo_rd_ip = args[0]
echo_kafka_ip = args[1]

device_info = json.load(open("deployment_output.json"))
container_vm_info = json.load(open("vm_config.json"))["container_VM"]

#populate two files
#one contains the uuid of devices within the same pvt nw
#other contains equivalent of echo's networkvisibility
pvt_nw_devices = open("device_grouping_private_network.txt", "w")
nw_visibility = open("networkvisibility.csv", "w")


num_devices = len(device_info)
nw_visibility_matrix = np.zeros((num_devices, num_devices), dtype=int)
np.fill_diagonal(nw_visibility_matrix, 1)

#fixing the device order here so that we visit 
#devices in the same order while starting the
#platform services on them
nw_device_dict = {}
device_info_list = []
current_device_uuid = 1
for device in device_info:
	device_info_list.append(device)
	device_pvt_nw_dict = device_info[device]["private_networks"]
	device_pvt_nw = next(iter(device_pvt_nw_dict))
	if device_pvt_nw not in nw_device_dict:
		nw_device_dict[device_pvt_nw] = []
	for dev in nw_device_dict[device_pvt_nw]:
		device_id = dev[1]
		nw_visibility_matrix[device_id - 1][current_device_uuid - 1] = 1
		nw_visibility_matrix[current_device_uuid - 1][device_id - 1] = 1
	nw_device_dict[device_pvt_nw].append((device,current_device_uuid))
	current_device_uuid += 1

pvt_nw_devices.write(str(nw_device_dict))
pvt_nw_devices.write("\n")

print nw_device_dict

for i in range(num_devices):
	current_row = ''
	for j in range(num_devices):
		current_row += str(nw_visibility_matrix[i][j])
		if j != num_devices-1:
			current_row += ","
	nw_visibility.write(current_row)
	nw_visibility.write("\n")
	
command_start_platform = "sudo docker exec -id {0} python /app/echo_platform_service/bootstrap.py {1} {2} {2} {3} 60 /app/echo_platform_service/usage.log &"

device_to_uuid_dict = {}
device_uuid = 1

def process_nw(nw_name):
	list_tuples = nw_device_dict[nw_name]
	device_to_uuid_dict = {}
	device_to_uuid_file = open("device_to_uuid_mapping_" + nw_name + ".txt" , "w")
	for tup in list_tuples:
		device = tup[0]
		current_uuid = str(tup[1])
	        host_vm = device_info[device]["host_vm_name"]
        	host_vm_info = container_vm_info[host_vm]
        	host_vm_ip = host_vm_info["hostname_ip"]
        	host_vm_user = host_vm_info["user"]
        	host_vm_key_path = host_vm_info["key_path"]
        	key = paramiko.RSAKey.from_private_key_file(host_vm_key_path)
        	client = paramiko.SSHClient()
        	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        	client.connect(hostname = host_vm_ip, username = host_vm_user, pkey = key)
		stdin , stdout, stderr = client.exec_command(command_start_platform.format(device, str(current_uuid), echo_rd_ip, echo_kafka_ip))
		print stderr.read()+"\n"
		print stdout.read()+"\n"
		client.close()
		device_to_uuid_dict[device] = current_uuid
	device_to_uuid_file.write(json.dumps(device_to_uuid_dict))
		

for pvt_nw in nw_device_dict:
	p = Process(target=process_nw, args=(pvt_nw,))
	p.start()

#for device in device_info_list:
#	host_vm = device_info[device]["host_vm_name"]
#	host_vm_info = container_vm_info[host_vm]
#	host_vm_ip = host_vm_info["hostname_ip"]
#	host_vm_user = host_vm_info["user"]
#	host_vm_key_path = host_vm_info["key_path"]
#	key = paramiko.RSAKey.from_private_key_file(host_vm_key_path)
#	client = paramiko.SSHClient()
#	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#	client.connect(hostname = host_vm_ip, username = host_vm_user, pkey = key)
#	stdin , stdout, stderr = client.exec_command(command_start_platform.format(device, str(device_uuid), echo_rd_ip, echo_kafka_ip))
	#time.sleep(60)
	#print stderr.read()+"\n"
	#print stdout.read()+"\n"
	#for line in stdout.read().splitlines():
	#	print(line)
#	client.close()
#	device_to_uuid_dict[device] = str(device_uuid)
#	device_uuid += 1

#device_to_uuid_file = open("device_to_uuid_mapping.txt", "w")
#device_to_uuid_file.write(json.dumps(device_to_uuid_dict))

print "Done my job of starting processes, going to sleep now"
time.sleep(1200)

