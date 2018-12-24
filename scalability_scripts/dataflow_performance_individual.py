import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import json
import numpy as np

########################### Device UUID & Related #######################
pvt_nw_map = "device_nw_uuid_mapping/device_grouping_private_network.json"
#creating a dict with key as device_uuid and value is a tuple
#of device_name and private network it was part of
device_dict = {}

exp_start_time = 1543353011098

pvt_nw_json = {}
with open(pvt_nw_map) as f:
  pvt_nw_json = json.load(f)

for pvt_nw in pvt_nw_json:
  items = pvt_nw_json[pvt_nw]
  for item in items:
    device_name = item[0]
    device_uuid = item[1]
    device_dict[device_uuid] = (device_name, pvt_nw)
########################################################################

######################### Service Calls time ###########################
service_times = "service_times/scale_experiment.log"
dataflow_num = 1
deploy_dict = {}
stop_dict = {}
rebalance_dict = {}
start_time = 0
stop_rebalance_count = 1
with open(service_times) as f:
  for line in f:
    splits = line.split(",")
    op_type = splits[0]
    op_time = int(splits[2])
    status = splits[3].strip()
    if status == "START":
      start_time = op_time
    else:
      end_time = op_time
      if op_type == "DEPLOY":
        deploy_dict[dataflow_num] = (start_time, end_time)
        dataflow_num += 1
      elif op_type == "STOP":
        stop_dict[stop_rebalance_count] = (start_time, end_time)
      else:
        rebalance_dict[stop_rebalance_count] = (start_time, end_time)
        stop_rebalance_count += 1
#######################################################################

##################### Window creation for analysis ####################
#lets create windows for every 10 dataflows for analysis
dag_windows = []
step_size = 10
for i in range(1,11):
  if i == 1:
    window_start = deploy_dict[i][1]
  else:
    window_start = stop_dict[i-1][1]
  window_end = stop_dict[i][1]
  dag_windows.append([window_start, window_end])
#######################################################################

################# Contribution of dataflow to windows #################
'''
window_times = []
for i in range(1,11):
  window_times.append([])
'''

#lets count how many pvt networks each dataflow is formed of
dataflow_pvt_nw_count = {}

total_dataflows = 100
total_devices = 100
dataflow_processor_count = 8

########## COUNT OF OUTPUT IN EACH WINDOW FROM THAT WINDOW ############
op_count_per_window = {}
for i in range(1,11):
  op_count_per_window[i] = 0

progress_mark = open("current_dataflow.txt", "w")
#######################################################################
########### WINDOW SIZE FOR LATENCY FOR EVERY TEN #####################
#######################################################################
window_size = 10
#key is dataflow_num and value is a list of entry time and time to process
time_taken_per_dataflow = {}

dataflow_num = 1
while dataflow_num <= total_dataflows:
  progress_mark.write("processing dataflow " + str(dataflow_num) + "\n")
  displacement = ((dataflow_num - 1)/step_size) * dataflow_processor_count
  start_device_uuid = ((dataflow_num - 1) * dataflow_processor_count + 1 + displacement)%(total_devices)
  if start_device_uuid == 0:
    start_device_uuid = total_devices
  end_device_uuid = (start_device_uuid + 6)%(total_devices)
  if end_device_uuid == 0:
    end_device_uuid = total_devices
  networks_dict = {}
  for i in range(0,8):
    device_uuid = (start_device_uuid + i)%(total_devices)
    if device_uuid == 0:
      device_uuid = 100
    nw_name = device_dict[device_uuid][1]
    if nw_name not in networks_dict:
      networks_dict[nw_name] = 1
  
  dataflow_pvt_nw_count[dataflow_num] = len(networks_dict)
  
  start_device = device_dict[start_device_uuid][0]
  end_device = device_dict[end_device_uuid][0]
  
  start_file = "logs/" + start_device + "/exp_logs/exp_0_" + str(dataflow_num) + ".log"
  end_file = "logs/" + end_device + "/exp_logs/exp_6_" + str(dataflow_num) + ".log"
  
  start_dict = {}
  time_taken_per_dataflow[dataflow_num] = [[], []]
  with open(start_file) as f:
    for line in f:
      splits = line.split(",")
      flowfile_id = splits[1]
      process_time = int(splits[2])
      status = splits[3].strip()
      if status == "ENTRY":
        start_dict[flowfile_id] = process_time

  with open(end_file) as f:
    for line in f:
      splits = line.split(",")
      flowfile_id = splits[1]
      process_time = int(splits[2])
      status = splits[3].strip()
      if status == "EXIT":
        time_taken = process_time - start_dict[flowfile_id]
        time_taken_per_dataflow[dataflow_num][0].append((start_dict[flowfile_id] - exp_start_time)/1000)
        time_taken_per_dataflow[dataflow_num][1].append(time_taken)
         
  dataflow_num += 1


#fig = plt.figure(figsize=(10,7))
#ax = fig.add_subplot(111)

start = 1
for start in range(1, 100, 10):
  fig = plt.figure(figsize=(10,7))
  ax = fig.add_subplot(111)
  for i in range(start, start+10):
    dataflow_data = time_taken_per_dataflow[i]
    ax.plot(dataflow_data[0], dataflow_data[1], label = 'dataflow-' + str(i))
    ax.legend()
  plt.xlabel('Relative Timestamp (s)', fontsize = 15)
  plt.ylabel('End-to-End Latency (ms)', fontsize = 15)
  plt.title('Latency distribution for dataflows ' + str(start) + '-' + str(start+9))
  plt.show() 


#num_output_windows = []
#for i in range(1,11):
#  num_output_windows.append(op_count_per_window[i])

#plt.ylim(bottom = 40000, top = 60000)
#ax.set_yscale("log")
#ax.plot(windows, num_output_windows)
#plt.xlabel('Current Window', fontsize=20)
#plt.ylabel('Output count in window from dags in the same window', fontsize=10)
#plt.title('Distribution of output count in a window contributed by dags in the same window', fontsize = 12)
#plt.show()
