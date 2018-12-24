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
#keeping the interesting windows(61-70,71-80,81-90,91-100) for analysis
interest_window_dict = {}
#lets create separate dict for each window of interest
window_phase_7_dict = {}
window_phase_8_dict = {}
window_phase_9_dict = {}
window_phase_10_dict = {}

dag_windows = []
step_size = 10
for i in range(1,11):
  if i == 1:
    window_start = deploy_dict[i][1]
  else:
    window_start = stop_dict[i-1][1]
  window_end = stop_dict[i][1]
  dag_windows.append([window_start, window_end])
  if i >= 7:
    interest_window_dict[i] = (window_start, window_end)
#######################################################################

################# Contribution of dataflow to windows #################
'''
window_times = []
for i in range(1,11):
  window_times.append([])
'''

#lets count how many pvt networks each dataflow is formed of
dataflow_pvt_nw_count = {}
#lets count the number of edge cuts each dataflow has
edge_cuts_count = {}

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
#edges_dict = {0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 4:7}
edges_dag = ([0,1,2,3,4,5,4], [1,2,3,4,5,6,7])

nw_to_vm_map = {"violet_private_1" : "AEP_12", "violet_private_2" : "AEP_3", "violet_private_3": "AEP_5", "violet_private_4": "AEP_9", "violet_private_5": "AEP_4", "violet_private_6": "AEP_8", "violet_private_7": "AEP_10", "violet_private_8": "AEP_11", "violet_private_9": "AEP_6", "violet_private_10": "AEP_1"}

#we need a 2D matrix of 10 X 10 for edge cuts between VM's
#lets first number the VM's
vm_index_map = {"AEP_1" : 0, "AEP_3" : 1, "AEP_4" : 2, "AEP_5" : 3, "AEP_6" : 4, "AEP_8" : 5, "AEP_9" : 6, "AEP_10" : 7, "AEP_11" : 8, "AEP_12" : 9}


#lets track edge cuts before the interesting windows and then do for
#each window of interest
vm_to_vm_edge_cuts = np.zeros(shape = (10,10), dtype = int)
vm_to_vm_edge_cuts_window_7 = np.zeros(shape = (1,1), dtype = int)
vm_to_vm_edge_cuts_total_window_7 = np.zeros(shape = (1,1), dtype = int)
vm_to_vm_edge_cuts_window_8 = np.zeros(shape = (1,1), dtype = int)
vm_to_vm_edge_cuts_total_window_8 = np.zeros(shape = (1,1), dtype = int)
vm_to_vm_edge_cuts_window_9 = np.zeros(shape = (1,1), dtype = int)
vm_to_vm_edge_cuts_total_window_9 = np.zeros(shape = (1,1), dtype = int)
vm_to_vm_edge_cuts_window_10 = np.zeros(shape = (1,1), dtype = int)
vm_to_vm_edge_cuts_total_window_10 = np.zeros(shape = (1,1), dtype = int)

#lets keep a minimum entry time to only track windows of interest
minimum_entry_time = interest_window_dict[7][0]

#to calculate standard error for each dataflow across the windows of
#interest, store the processing time for the very first input of each
#dataflow for every window
window_phase_7_first_dict = {}
window_phase_8_first_dict = {}
window_phase_9_first_dict = {}
window_phase_10_first_dict = {}

#structures necessary to accumulate the standard error for each
#dataflow for every window of interest
window_phase_7_error_dict = {}
window_phase_8_error_dict = {}
window_phase_9_error_dict = {}
window_phase_10_error_dict = {}

#lets track where are the edgecuts for each dataflow
#in the dict, key is the dataflow_num and value is a another dict
#consisting of sourceVM-targetVM as the key and value being the 
#number of edge cuts between them. The key will always have the VM
#with lower index as the source
edge_cuts_per_dataflow = {}

#lets track the placement of every dag so that we know which
#VM's are used for a dag. Additionally write to a file the 
#specific placement of each processor in the dag to a VM.
dataflow_placement = open("dataflow_placement.txt", "w")
placement_per_dataflow = {}

#lets track the number of tasks per VM
tasks_per_VM = {}
for i in range(0,8):
  tasks_per_VM[i] = np.zeros(shape=(1,10), dtype=int)

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

  edge_cuts_dataflow = 0
  processor_vm_placement = {}
  placement_per_dataflow[dataflow_num] = np.zeros(shape=(1,10), dtype=int)

  #for key in edges_dict:
  for i in range(len(edges_dag[0])):
    key = edges_dag[0][i]
    from_device_uuid = (start_device_uuid + key)%(total_devices)
    if from_device_uuid == 0:
      from_device_uuid = total_devices
    from_nw = device_dict[from_device_uuid][1]
    #to_device_uuid = (start_device_uuid + edges_dict[key])%(total_devices)
    to_device_uuid = (start_device_uuid + edges_dag[1][i])%(total_devices)
    if to_device_uuid == 0:
      to_device_uuid = total_devices
    to_nw = device_dict[to_device_uuid][1]

    if key not in processor_vm_placement:
      vm_name = nw_to_vm_map[from_nw]
      processor_vm_placement[key] = vm_name
      placement_per_dataflow[dataflow_num][0,vm_index_map[vm_name]] += 1
      tasks_per_VM[key][0,vm_index_map[vm_name]] += 1
    if edges_dag[1][i] not in processor_vm_placement:
      vm_name = nw_to_vm_map[to_nw]
      processor_vm_placement[edges_dag[1][i]] = vm_name
      placement_per_dataflow[dataflow_num][0,vm_index_map[vm_name]] += 1
      tasks_per_VM[edges_dag[1][i]][0,vm_index_map[vm_name]] += 1

    if from_nw == to_nw:
      pass
    else:
      edge_cuts_dataflow += 1
      from_vm = nw_to_vm_map[from_nw]
      to_vm = nw_to_vm_map[to_nw]
      if dataflow_num not in edge_cuts_per_dataflow:
        edge_cuts_per_dataflow[dataflow_num] = {}
      from_index = vm_index_map[from_vm]
      to_index = vm_index_map[to_vm]
      dict_key = ''
      if from_index < to_index:
        dict_key = from_vm + "-" + to_vm
      else:
        dict_key = to_vm + "-" + from_vm
      if dict_key not in edge_cuts_per_dataflow[dataflow_num]:
        edge_cuts_per_dataflow[dataflow_num][dict_key] = 0
      edge_cuts_per_dataflow[dataflow_num][dict_key] += 1
      if dataflow_num <= 60:
        vm_to_vm_edge_cuts[vm_index_map[from_vm]][vm_index_map[to_vm]] += 1
        vm_to_vm_edge_cuts[vm_index_map[to_vm]][vm_index_map[from_vm]] += 1
      elif dataflow_num >= 61 and dataflow_num <= 70:
        if not vm_to_vm_edge_cuts_window_7.any():
          vm_to_vm_edge_cuts_window_7 = np.empty_like(vm_to_vm_edge_cuts)
          vm_to_vm_edge_cuts_total_window_7 = np.empty_like(vm_to_vm_edge_cuts)
          vm_to_vm_edge_cuts_total_window_7[:] = vm_to_vm_edge_cuts
        vm_to_vm_edge_cuts_window_7[vm_index_map[from_vm]][vm_index_map[to_vm]] += 1
        vm_to_vm_edge_cuts_window_7[vm_index_map[to_vm]][vm_index_map[from_vm]] += 1
        vm_to_vm_edge_cuts_total_window_7[vm_index_map[from_vm]][vm_index_map[to_vm]] += 1
        vm_to_vm_edge_cuts_total_window_7[vm_index_map[to_vm]][vm_index_map[from_vm]] += 1
      elif dataflow_num >= 71 and dataflow_num <= 80:
        if not vm_to_vm_edge_cuts_window_8.any():
          vm_to_vm_edge_cuts_window_8 = np.empty_like(vm_to_vm_edge_cuts)
          vm_to_vm_edge_cuts_total_window_8 = np.empty_like(vm_to_vm_edge_cuts)
          vm_to_vm_edge_cuts_total_window_8[:] = vm_to_vm_edge_cuts_total_window_7
        vm_to_vm_edge_cuts_window_8[vm_index_map[from_vm]][vm_index_map[to_vm]] += 1
        vm_to_vm_edge_cuts_window_8[vm_index_map[to_vm]][vm_index_map[from_vm]] += 1
        vm_to_vm_edge_cuts_total_window_8[vm_index_map[from_vm]][vm_index_map[to_vm]] += 1
        vm_to_vm_edge_cuts_total_window_8[vm_index_map[to_vm]][vm_index_map[from_vm]] += 1
      elif dataflow_num >= 81 and dataflow_num <= 90:
        if not vm_to_vm_edge_cuts_window_9.any():
          vm_to_vm_edge_cuts_window_9 = np.empty_like(vm_to_vm_edge_cuts)
          vm_to_vm_edge_cuts_total_window_9 = np.empty_like(vm_to_vm_edge_cuts)
          vm_to_vm_edge_cuts_total_window_9[:] = vm_to_vm_edge_cuts_total_window_8
        vm_to_vm_edge_cuts_window_9[vm_index_map[from_vm]][vm_index_map[to_vm]] += 1
        vm_to_vm_edge_cuts_window_9[vm_index_map[to_vm]][vm_index_map[from_vm]] += 1
        vm_to_vm_edge_cuts_total_window_9[vm_index_map[from_vm]][vm_index_map[to_vm]] += 1
        vm_to_vm_edge_cuts_total_window_9[vm_index_map[to_vm]][vm_index_map[from_vm]] += 1
      elif dataflow_num >= 91 and dataflow_num <= 100: 
        if not vm_to_vm_edge_cuts_window_10.any():
          vm_to_vm_edge_cuts_window_10 = np.empty_like(vm_to_vm_edge_cuts)
          vm_to_vm_edge_cuts_total_window_10 = np.empty_like(vm_to_vm_edge_cuts)
          vm_to_vm_edge_cuts_total_window_10[:] = vm_to_vm_edge_cuts_total_window_9
        vm_to_vm_edge_cuts_window_10[vm_index_map[from_vm]][vm_index_map[to_vm]] += 1
        vm_to_vm_edge_cuts_window_10[vm_index_map[to_vm]][vm_index_map[from_vm]] += 1
        vm_to_vm_edge_cuts_total_window_10[vm_index_map[from_vm]][vm_index_map[to_vm]] += 1
        vm_to_vm_edge_cuts_total_window_10[vm_index_map[to_vm]][vm_index_map[from_vm]] += 1      
       
  dataflow_pvt_nw_count[dataflow_num] = len(networks_dict)
  edge_cuts_count[dataflow_num] = edge_cuts_dataflow
 
  #lets write the placement of the dag in the file
  placement_str = str(dataflow_num) + " : "
  dict_keys = processor_vm_placement.keys()
  dict_keys.sort()
  for key in dict_keys:
    placement_str += str(key) + "->" + processor_vm_placement[key] + "  "
  placement_str += "\n"
  dataflow_placement.write(placement_str)
 
  start_device = device_dict[start_device_uuid][0]
  end_device = device_dict[end_device_uuid][0]
  
  start_file = "logs/" + start_device + "/exp_logs/exp_0_" + str(dataflow_num) + ".log"
  end_file = "logs/" + end_device + "/exp_logs/exp_6_" + str(dataflow_num) + ".log"
  
  start_dict = {}
  time_taken_per_dataflow[dataflow_num] = [[], []]
  #count_window_7 = 0
  #count_window_8 = 0
  #count_window_9 = 0
  #count_window_10 = 0

  '''
  with open(start_file) as f:
    for line in f:
      splits = line.split(",")
      flowfile_id = splits[1]
      process_time = int(splits[2])
      status = splits[3].strip()
      if status == "ENTRY" and process_time >= minimum_entry_time:
        start_dict[flowfile_id] = process_time

  with open(end_file) as f:
    for line in f:
      splits = line.split(",")
      flowfile_id = splits[1]
      process_time = int(splits[2])
      status = splits[3].strip()
      if status == "EXIT" and flowfile_id in start_dict:
        entry_time = start_dict[flowfile_id]
        time_taken = process_time - entry_time
        if entry_time >= interest_window_dict[7][0] and entry_time <= interest_window_dict[7][1]:
          if dataflow_num not in window_phase_7_dict:
            window_phase_7_dict[dataflow_num] = []
            #window_phase_7_first_dict[dataflow_num] = time_taken
            #window_phase_7_error_dict[dataflow_num] = 0
          window_phase_7_dict[dataflow_num].append(time_taken)
          #window_phase_7_error_dict[dataflow_num] += (window_phase_7_first_dict[dataflow_num] - time_taken)
          #count_window_7 += 1
        elif entry_time >= interest_window_dict[8][0] and entry_time <= interest_window_dict[8][1]:
          if dataflow_num not in window_phase_8_dict:
            window_phase_8_dict[dataflow_num] = []
            #window_phase_8_first_dict[dataflow_num] = time_taken
            #window_phase_8_error_dict[dataflow_num] = 0
          window_phase_8_dict[dataflow_num].append(time_taken)
          #window_phase_8_error_dict[dataflow_num] += (window_phase_8_first_dict[dataflow_num] - time_taken)
          #count_window_8 += 1
        elif entry_time >= interest_window_dict[9][0] and entry_time <= interest_window_dict[9][1]:
          if dataflow_num not in window_phase_9_dict:
            window_phase_9_dict[dataflow_num] = []
            #window_phase_9_first_dict[dataflow_num] = time_taken
            #window_phase_9_error_dict[dataflow_num] = 0
          window_phase_9_dict[dataflow_num].append(time_taken)
          #window_phase_9_error_dict[dataflow_num] += (window_phase_9_first_dict[dataflow_num] - time_taken)
          #count_window_9 += 1
        elif entry_time >= interest_window_dict[10][0] and entry_time <= interest_window_dict[10][1]:
          if dataflow_num not in window_phase_10_dict:
            window_phase_10_dict[dataflow_num] = []
            #window_phase_10_first_dict[dataflow_num] = time_taken
            #window_phase_10_error_dict[dataflow_num] = 0
          window_phase_10_dict[dataflow_num].append(time_taken)
          #window_phase_10_error_dict[dataflow_num] += (window_phase_10_first_dict[dataflow_num] - time_taken)
          #count_window_10 += 1
  
#  if dataflow_num in window_phase_7_error_dict:
#    window_phase_7_error_dict[dataflow_num] = window_phase_7_error_dict[dataflow_num]/(count_window_7 * window_phase_7_first_dict[dataflow_num] * 1.0)

#  if dataflow_num in window_phase_8_error_dict:
#    window_phase_8_error_dict[dataflow_num] = window_phase_8_error_dict[dataflow_num]/(count_window_8 * window_phase_8_first_dict[dataflow_num] * 1.0)

#  if dataflow_num in window_phase_9_error_dict:
#    window_phase_9_error_dict[dataflow_num] = window_phase_9_error_dict[dataflow_num]/(count_window_9 * window_phase_9_first_dict[dataflow_num] * 1.0)

#  if dataflow_num in window_phase_10_error_dict:
#    window_phase_10_error_dict[dataflow_num] = window_phase_10_error_dict[dataflow_num]/(count_window_10 * window_phase_10_first_dict[dataflow_num] * 1.0)

  '''
  dataflow_num += 1

'''
fig, ax = plt.subplots(2, 2)
#lets calculate the median latency for each dag for interesting windows
median_phase_7_dict = {}
median_phase_8_dict = {}
median_phase_9_dict = {}
median_phase_10_dict = {}

count = 1
for key in window_phase_7_dict:
  data = window_phase_7_dict[key]
  data_median = np.median(data)
  median_phase_7_dict[key] = data_median
  if count == 1 and (key-1)/50 == 0 and ((key-1)/25)%2 == 0:
    ax[(key-1)/50,((key-1)/25)%2].plot(key, data_median, label = '61-70', color = 'red', marker = 'o', linewidth = 2)
    count += 1
  else:
    ax[(key-1)/50,((key-1)/25)%2].plot(key, data_median, color = 'red', marker = 'o', linewidth = 2)

count = 1
for key in window_phase_8_dict:
  data = window_phase_8_dict[key]
  data_median = np.median(data)
  median_phase_8_dict[key] = data_median
  if count == 1 and (key-1)/50 == 0 and ((key-1)/25)%2 == 0:
    ax[(key-1)/50,((key-1)/25)%2].plot(key, data_median, label = '71-80', color = 'blue', marker = 'o', linewidth = 2)
    count += 1
  else:
    ax[(key-1)/50,((key-1)/25)%2].plot(key, data_median, color = 'blue', marker = 'o', linewidth = 2)

count = 1
for key in window_phase_9_dict:
  data = window_phase_9_dict[key]
  data_median = np.median(data)
  median_phase_9_dict[key] = data_median
  if count == 1 and (key-1)/50 == 0 and ((key-1)/25)%2 == 0:
    ax[(key-1)/50,((key-1)/25)%2].plot(key, data_median, label = '81-90', color = 'green', marker = 'o', linewidth = 2)
    count += 1
  else:
    ax[(key-1)/50,((key-1)/25)%2].plot(key, data_median, color = 'green', marker = 'o', linewidth = 2)

count = 1
for key in window_phase_10_dict:
  data = window_phase_10_dict[key]
  data_median = np.median(data)
  median_phase_10_dict[key] = data_median
  if count == 1 and (key-1)/50 == 0 and ((key-1)/25)%2 == 0:
    ax[(key-1)/50,((key-1)/25)%2].plot(key, data_median, label = '91-100', color = 'black', marker = 'o', linewidth = 2)
    count += 1
  else:
    ax[(key-1)/50,((key-1)/25)%2].plot(key, data_median, color = 'black', marker = 'o', linewidth = 2)

#write to file the median latencies for interesting windows
dag_median_latency = open("dag_median_latency.csv", "w")
list_7 = median_phase_7_dict.keys()
list_7.sort()
for key in list_7:
  val_7 = median_phase_7_dict[key]
  val_8 = ''
  val_9 = ''
  val_10 = ''
  if key in median_phase_8_dict:
    val_8 = median_phase_8_dict[key]
  if key in median_phase_9_dict:
    val_9 = median_phase_9_dict[key]
  if key in median_phase_10_dict:
    val_10 = median_phase_10_dict[key]
  edge_cuts = edge_cuts_count[key]
  dag_median_latency.write(str(key) + "," + str(val_7) + "," + str(val_8) + "," + str(val_9) + "," + str(val_10) + "," + str(edge_cuts) + "\n")

for i in range(71,81):
  val_7 = ''
  val_8 = median_phase_8_dict[i]
  val_9 = median_phase_9_dict[i]
  val_10 = median_phase_10_dict[i]
  edge_cuts = edge_cuts_count[i]
  dag_median_latency.write(str(i) + "," + str(val_7) + "," + str(val_8) + "," + str(val_9) + "," + str(val_10) + "," + str(edge_cuts) + "\n")

for i in range(81,91):
  val_7 = ''
  val_8 = ''
  val_9 = median_phase_9_dict[i]
  val_10 = median_phase_10_dict[i]
  edge_cuts = edge_cuts_count[i]
  dag_median_latency.write(str(i) + "," + str(val_7) + "," + str(val_8) + "," + str(val_9) + "," + str(val_10) + "," + str(edge_cuts) + "\n")

for i in range(91,101):
  val_7 = ''
  val_8 = ''
  val_9 = ''
  val_10 = median_phase_10_dict[i]
  edge_cuts = edge_cuts_count[i]
  dag_median_latency.write(str(i) + "," + str(val_7) + "," + str(val_8) + "," + str(val_9) + "," + str(val_10) + "," + str(edge_cuts) + "\n")


ax[0,0].legend()
ax[0,1].legend()
ax[1,0].legend()
ax[1,1].legend()

#xticks define
#x_axis_ticks = np.linspace(1,100, 100)
ax[0,0].set_xticks(np.linspace(1,25,25))
ax[0,1].set_xticks(np.linspace(26,50,25))
ax[1,0].set_xticks(np.linspace(51,75,25))
ax[1,1].set_xticks(np.linspace(76,100,25))

ax[0,0].set_xlabel('Application Number', fontsize = 10)
ax[0,0].set_ylabel('Median Latency (ms)', fontsize = 10)

ax[0,1].set_xlabel('Application Number', fontsize = 10)
ax[0,1].set_ylabel('Median Latency (ms)', fontsize = 10)

ax[1,0].set_xlabel('Application Number', fontsize = 10)
ax[1,0].set_ylabel('Median Latency (ms)', fontsize = 10)

ax[1,1].set_xlabel('Application Number', fontsize = 10)
ax[1,1].set_ylabel('Median Latency (ms)', fontsize = 10)

#ax_0_0_1 = ax[0,0].twinx()
#for i in range(1,26):
#  ax_0_0_1.plot(i, edge_cuts_count[i], color = 'cyan', marker = 'o', linewidth = 2)
#ax_0_0_1.set_ylabel("Number of Edge Cuts", fontsize = 10)

#ax_0_1_1 = ax[0,1].twinx()
#for i in range(26,51):
#  ax_0_1_1.plot(i, edge_cuts_count[i], color = 'cyan', marker = 'o', linewidth = 2)
#ax_0_1_1.set_ylabel("Number of Edge Cuts", fontsize = 10)

#ax_1_0_1 = ax[1,0].twinx()
#for i in range(51,76):
#  ax_1_0_1.plot(i, edge_cuts_count[i], color = 'cyan', marker = 'o', linewidth = 2)
#ax_1_0_1.set_ylabel("Number of Edge Cuts", fontsize = 10)

#ax_1_1_1 = ax[1,1].twinx()
#for i in range(76,101):
#  ax_1_1_1.plot(i, edge_cuts_count[i], color = 'cyan', marker = 'o', linewidth = 2)
#ax_1_1_1.set_ylabel("Number of Edge Cuts", fontsize = 10)

plt.show() 

'''
#lets do the analysis for the edge cuts between VM's
#lets do it for the interesting windows

edge_cuts_vms_61_70 = open("edge_cuts_vms_61_70.csv", "w")

window_7_70_edge_cuts = np.zeros(shape = (10,10), dtype = int)
for i in range(7,71):
  edge_cut_dict = {}
  if i in edge_cuts_per_dataflow:
    edge_cut_dict = edge_cuts_per_dataflow[i]
  for key in edge_cut_dict:
    splits = key.split("-")
    vm_1 = splits[0]
    vm_2 = splits[1].strip()
    window_7_70_edge_cuts[vm_index_map[vm_1]][vm_index_map[vm_2]] += edge_cut_dict[key]
    window_7_70_edge_cuts[vm_index_map[vm_2]][vm_index_map[vm_1]] += edge_cut_dict[key]

#lets write the edge cuts data for window 61-70 in the file
for i in range(0,10):
  placement_str = ''
  for j in range(0,10):
    placement_str += str(window_7_70_edge_cuts[i][j]) + ","
  edge_cuts_vms_61_70.write(placement_str + "\n")
    

edge_cuts_vms_71_80 = open("edge_cuts_vms_71_80.csv", "w")

window_8_80_edge_cuts = np.empty_like(window_7_70_edge_cuts)
window_8_80_edge_cuts[:] = window_7_70_edge_cuts
#remove for 7, then add for 71-80
remove_dict = edge_cuts_per_dataflow[7]
for key in remove_dict:
  splits = key.split("-")
  vm_1 = splits[0]
  vm_2 = splits[1].strip()
  window_8_80_edge_cuts[vm_index_map[vm_1]][vm_index_map[vm_2]] -= remove_dict[key]
  window_8_80_edge_cuts[vm_index_map[vm_2]][vm_index_map[vm_1]] -= remove_dict[key]

for i in range(71,81):
  edge_cut_dict = {}
  if i in edge_cuts_per_dataflow:
    edge_cut_dict = edge_cuts_per_dataflow[i]
  for key in edge_cut_dict:
    splits = key.split("-")
    vm_1 = splits[0]
    vm_2 = splits[1].strip()
    window_8_80_edge_cuts[vm_index_map[vm_1]][vm_index_map[vm_2]] += edge_cut_dict[key]
    window_8_80_edge_cuts[vm_index_map[vm_2]][vm_index_map[vm_1]] += edge_cut_dict[key]

#lets write the edge cuts data for window 71-80 in the file
for i in range(0,10):
  placement_str = ''
  for j in range(0,10):
    placement_str += str(window_8_80_edge_cuts[i][j]) + ","
  edge_cuts_vms_71_80.write(placement_str + "\n")


edge_cuts_vms_81_90 = open("edge_cuts_vms_81_90.csv", "w")

window_9_90_edge_cuts = np.empty_like(window_8_80_edge_cuts)
window_9_90_edge_cuts[:] = window_8_80_edge_cuts
#remove for 8, then add for 81-90
remove_dict = edge_cuts_per_dataflow[8]
for key in remove_dict:
  splits = key.split("-")
  vm_1 = splits[0]
  vm_2 = splits[1].strip()
  window_9_90_edge_cuts[vm_index_map[vm_1]][vm_index_map[vm_2]] -= remove_dict[key]
  window_9_90_edge_cuts[vm_index_map[vm_2]][vm_index_map[vm_1]] -= remove_dict[key]

for i in range(81,91):
  edge_cut_dict = {}
  if i in edge_cuts_per_dataflow:
    edge_cut_dict = edge_cuts_per_dataflow[i]
  for key in edge_cut_dict:
    splits = key.split("-")
    vm_1 = splits[0]
    vm_2 = splits[1].strip()
    window_9_90_edge_cuts[vm_index_map[vm_1]][vm_index_map[vm_2]] += edge_cut_dict[key]
    window_9_90_edge_cuts[vm_index_map[vm_2]][vm_index_map[vm_1]] += edge_cut_dict[key]

#lets write the edge cuts data for window 81-90 in the file
for i in range(0,10):
  placement_str = ''
  for j in range(0,10):
    placement_str += str(window_9_90_edge_cuts[i][j]) + ","
  edge_cuts_vms_81_90.write(placement_str + "\n")


edge_cuts_vms_91_100 = open("edge_cuts_vms_91_100.csv", "w")

window_10_100_edge_cuts = np.empty_like(window_9_90_edge_cuts)
window_10_100_edge_cuts[:] = window_9_90_edge_cuts
#remove for 9, then add for 91-100
remove_dict = edge_cuts_per_dataflow[9]
for key in remove_dict:
  splits = key.split("-")
  vm_1 = splits[0]
  vm_2 = splits[1].strip()
  window_10_100_edge_cuts[vm_index_map[vm_1]][vm_index_map[vm_2]] -= remove_dict[key]
  window_10_100_edge_cuts[vm_index_map[vm_2]][vm_index_map[vm_1]] -= remove_dict[key]

for i in range(91,101):
  edge_cut_dict = {}
  if i in edge_cuts_per_dataflow:
    edge_cut_dict = edge_cuts_per_dataflow[i]
  for key in edge_cut_dict:
    splits = key.split("-")
    vm_1 = splits[0]
    vm_2 = splits[1].strip()
    window_10_100_edge_cuts[vm_index_map[vm_1]][vm_index_map[vm_2]] += edge_cut_dict[key]
    window_10_100_edge_cuts[vm_index_map[vm_2]][vm_index_map[vm_1]] += edge_cut_dict[key]

#lets write the edge cuts data for window 81-90 in the file
for i in range(0,10):
  placement_str = ''
  for j in range(0,10):
    placement_str += str(window_10_100_edge_cuts[i][j]) + ","
  edge_cuts_vms_91_100.write(placement_str + "\n")


vm_names = ["AEP_1", "AEP_3", "AEP_4", "AEP_5", "AEP_6", "AEP_8", "AEP_9", "AEP_10", "AEP_11", "AEP_12"]

'''
fig, ax = plt.subplots(2, 2)
#61-70
ax[0,0].imshow(window_7_70_edge_cuts)
ax[0,0].set_xticks(np.arange(len(vm_names)))
ax[0,0].set_yticks(np.arange(len(vm_names)))
ax[0,0].set_xticklabels(vm_names)
ax[0,0].set_yticklabels(vm_names)
plt.setp(ax[0,0].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
#plt.setp(ax[0,0].get_yticklabels(), rotation=45, ha="right", rotation_mode="anchor")

for i in range(len(vm_names)):
  for j in range(len(vm_names)):
    text = ax[0,0].text(i, j, window_7_70_edge_cuts[i, j], ha="center", va="center", color="w")

ax[0,0].set_title("EdgeCuts between VM's for window 61-70")

#71-80
ax[0,1].imshow(window_8_80_edge_cuts)
ax[0,1].set_xticks(np.arange(len(vm_names)))
ax[0,1].set_yticks(np.arange(len(vm_names)))
ax[0,1].set_xticklabels(vm_names)
ax[0,1].set_yticklabels(vm_names)
plt.setp(ax[0,1].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
#plt.setp(ax[0,1].get_yticklabels(), rotation=45, ha="right", rotation_mode="anchor")

for i in range(len(vm_names)):
  for j in range(len(vm_names)):
    text = ax[0,1].text(i, j, window_8_80_edge_cuts[i, j], ha="center", va="center", color="w")

ax[0,1].set_title("EdgeCuts between VM's for window 71-80")

#81-90
ax[1,0].imshow(window_9_90_edge_cuts)
ax[1,0].set_xticks(np.arange(len(vm_names)))
ax[1,0].set_yticks(np.arange(len(vm_names)))
ax[1,0].set_xticklabels(vm_names)
ax[1,0].set_yticklabels(vm_names)
plt.setp(ax[1,0].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
#plt.setp(ax[1,0].get_yticklabels())

for i in range(len(vm_names)):
  for j in range(len(vm_names)):
    text = ax[1,0].text(i, j, window_9_90_edge_cuts[i, j], ha="center", va="center", color="w")

ax[1,0].set_title("EdgeCuts between VM's for window 81-90")

#91-100
ax[1,1].imshow(window_10_100_edge_cuts)
ax[1,1].set_xticks(np.arange(len(vm_names)))
ax[1,1].set_yticks(np.arange(len(vm_names)))
ax[1,1].set_xticklabels(vm_names)
ax[1,1].set_yticklabels(vm_names)
plt.setp(ax[1,1].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
#plt.setp(ax[1,1].get_yticklabels())

for i in range(len(vm_names)):
  for j in range(len(vm_names)):
    text = ax[1,1].text(i, j, window_10_100_edge_cuts[i, j], ha="center", va="center", color="w")

ax[1,1].set_title("EdgeCuts between VM's for window 91-100")

fig.tight_layout()
plt.show()


fig, ax = plt.subplots(2, 2)

vm_names = ["AEP_1", "AEP_3", "AEP_4", "AEP_5", "AEP_6", "AEP_8", "AEP_9", "AEP_10", "AEP_11", "AEP_12"]

task_distribution_per_application = open("task_distribution_per_application_per_VM.csv", "w")
#write to the file first
for i in range(1,101):
  current_array = placement_per_dataflow[i]
  placement_str = ''
  for j in range(0,10):
    placement_str += str(current_array[0,j]) + ","
  task_distribution_per_application.write(placement_str + "\n")

#1-25 subplot, start with 1 and then concatenate upto 25
array_1 = placement_per_dataflow[1]
for i in range(2,26):
  array_1 = np.concatenate((array_1, placement_per_dataflow[i]), axis=0)

ax[0,0].imshow(array_1, extent=[-1,25,10,-1])
ax[0,0].set_xticks(np.arange(0,25))
ax[0,0].set_yticks(np.arange(len(vm_names)))
#ax[0,0].set_ylim(ymin = -1, ymax=10)
ax[0,0].set_xticklabels([str(i) for i in range(1,26)])
ax[0,0].set_yticklabels(vm_names)
plt.setp(ax[0,0].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize=7)

for i in range(0,25):
  for j in range(len(vm_names)):
    ax[0,0].text(i, j, array_1[i, j], ha="center", va="center", color="w")

ax[0,0].set_title("Task Distribution for applications 1-25")
ax[0,0].set_xlabel('Application Number', fontsize = 10) 
ax[0,0].set_ylabel('VM', fontsize = 10)

#26-50 subplot, start with 26 and then concatenate upto 50
array_2 = placement_per_dataflow[26]
for i in range(27,51):
  array_2 = np.concatenate((array_2, placement_per_dataflow[i]), axis=0)

ax[0,1].imshow(array_2, extent=[-1,25,10,-1])
ax[0,1].set_xticks(np.arange(0,25))
ax[0,1].set_yticks(np.arange(len(vm_names)))
ax[0,1].set_xticklabels([str(i) for i in range(26,51)])
ax[0,1].set_yticklabels(vm_names)
plt.setp(ax[0,1].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize=7)

for i in range(0,25):
  for j in range(len(vm_names)):
    ax[0,1].text(i, j, array_2[i, j], ha="center", va="center", color="w")

ax[0,1].set_title("Task Distribution for applications 26-50")
ax[0,1].set_xlabel('Application Number', fontsize = 10) 
ax[0,1].set_ylabel('VM', fontsize = 10)

#51-75 subplot, start with 51 and then concatenate upto 75
array_3 = placement_per_dataflow[51]
for i in range(52,76):
  array_3 = np.concatenate((array_3, placement_per_dataflow[i]), axis=0)

ax[1,0].imshow(array_3, extent=[-1,25,10,-1])
ax[1,0].set_xticks(np.arange(0,25))
ax[1,0].set_yticks(np.arange(len(vm_names)))
ax[1,0].set_xticklabels([str(i) for i in range(51,76)])
ax[1,0].set_yticklabels(vm_names)
plt.setp(ax[1,0].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize=7)

for i in range(0,25):
  for j in range(len(vm_names)):
    ax[1,0].text(i, j, array_3[i, j], ha="center", va="center", color="w")

ax[1,0].set_title("Task Distribution for applications 51-75")
ax[1,0].set_xlabel('Application Number', fontsize = 10) 
ax[1,0].set_ylabel('VM', fontsize = 10)

#76-100 subplot, start with 76 and then concatenate upto 100
array_4 = placement_per_dataflow[76]
for i in range(77,101):
  array_4 = np.concatenate((array_4, placement_per_dataflow[i]), axis=0)

ax[1,1].imshow(array_4, extent=[-1,25,10,-1])
ax[1,1].set_xticks(np.arange(0,25))
ax[1,1].set_yticks(np.arange(len(vm_names)))
ax[1,1].set_xticklabels([str(i) for i in range(76,101)])
ax[1,1].set_yticklabels(vm_names)
plt.setp(ax[1,1].get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize=7)

for i in range(0,25):
  for j in range(len(vm_names)):
    ax[1,1].text(i, j, array_4[i, j], ha="center", va="center", color="w")

ax[1,1].set_title("Task Distribution for applications 76-100")
ax[1,1].set_xlabel('Application Number', fontsize = 10)
ax[1,1].set_ylabel('VM', fontsize = 10)

fig.tight_layout()
plt.show()

#lets plot the distribution of tasks on the VM's
task_names = ["KafkaConsumer", "SenML", "RBI", "Join", "Annotate", "CSVSenML", "KafkaProducer", "MySQLInsert"]

#concatenate the distribution of each task in a single 2D matrix
tasks_VM_array = tasks_per_VM[0]
for i in range(1,8):
  tasks_VM_array = np.concatenate((tasks_VM_array, tasks_per_VM[i]), axis=0)

#write the overall task distribution to a csv file
overall_task_dist = open("overall_task_dist_per_VM.csv", "w")
for i in range(0,10):
  placement_str = ''
  for j in range(0,8):
    placement_str += str(tasks_per_VM[j][0,i]) + ","
  overall_task_dist.write(placement_str + "\n")


fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)

ax.imshow(tasks_VM_array, extent=[-1,8,10,-1])
ax.set_xticks(np.arange(0,8))
ax.set_yticks(np.arange(len(vm_names)))
ax.set_xticklabels(task_names)
ax.set_yticklabels(vm_names)
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize=7)

for i in range(len(task_names)):
  for j in range(len(vm_names)):
    ax.text(i, j, tasks_VM_array[i, j], ha="center", va="center", color="w")

fig.tight_layout()
plt.show()
'''
