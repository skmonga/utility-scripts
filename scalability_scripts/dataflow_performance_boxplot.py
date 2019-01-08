import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import json
import numpy as np
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

########################### Device UUID & Related #######################
pvt_nw_map = "device_nw_uuid_mapping/device_grouping_private_network.json"
#creating a dict with key as device_uuid and value is a tuple
#of device_name and private network it was part of
device_dict = {}

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
  dag_windows.append([window_start, window_end, []])
#######################################################################

################# Contribution of dataflow to windows #################
'''
window_times = []
for i in range(1,11):
  window_times.append([])
'''

#lets write the output to a file
output_file = open("time_taken_windowed.txt", "w")

#lets count how many pvt networks each dataflow is formed of
dataflow_pvt_nw_count = {}

total_dataflows = 100
total_devices = 100
dataflow_processor_count = 8

progress_mark = open("current_dataflow.txt", "w")
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
        entry_time = start_dict[flowfile_id]
        for window in dag_windows:
          window_start = window[0]
          window_end = window[1]
          time_taken = window[2]
          if entry_time >= window_start and entry_time <= window_end:
            time_taken.append(process_time - entry_time)
            break
          else:
            continue
      
  dataflow_num += 1

#output_file.write(str(dag_windows))
output_file.close()

#fig = plt.figure(figsize=(10,7))
fig = plt.figure(figsize=(7,9))
ax = fig.add_subplot(111)

#plotting data
data = []
for window in dag_windows:
  current_window_data = window[2]
  data.append(current_window_data)

application_window = range(0,120,10)
#medianprops = dict(linewidth=1, color='green')
medianprops = dict(linewidth=2, color='green')
red_square = dict(markerfacecolor='g', marker='s')
ax.boxplot(data,flierprops=red_square, showfliers=False, vert=True, positions = application_window[1:-1], labels = application_window[1:-1], widths=2.5, patch_artist=False, medianprops=medianprops)

ax.set_xlabel('Application Window', fontsize=25)
ax.set_ylabel('End-to-End Latency (ms)', fontsize=25)

ax.set_xlim(xmin=0)
ax.set_ylim(ymin=0)
ax.set_xlim(0,105)
plt.grid()
plt.minorticks_on()
ax.yaxis.set_ticks(np.arange(0, 3000, 500))
y_minorLocator = AutoMinorLocator(5)
ax.yaxis.set_minor_locator(y_minorLocator)
ax.grid(color='dimgrey', which='major', axis='y')
ax.grid(color='darkgrey', which='minor', axis='y')

ax.xaxis.set_tick_params(labelsize=22)
ax.yaxis.set_tick_params(labelsize=22)

plt.show()
fig.savefig("Scalability_application_latency.pdf", bbox_inches='tight')

