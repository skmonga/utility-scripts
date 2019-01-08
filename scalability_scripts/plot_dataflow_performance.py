import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.lines import Line2D
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import json

plot_color_dict = {"DEPLOY" : "green", "STOP" : "red", "REBALANCE" : "blue", "APPLICATION" : "darkorange"}

######################### Service Calls time ###########################
service_times = "service_times/scale_experiment.log"
dataflow_num = 1 
deploy_dict = {}
stop_dict = {}
rebalance_dict = {}
start_time = 0 
stop_rebalance_count = 1

stop_times = []
rebalance_times = []

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
        stop_times.append((end_time - start_time)/1000)
      else:
        rebalance_dict[stop_rebalance_count] = (start_time, end_time)
        stop_rebalance_count += 1
        rebalance_times.append((end_time - start_time)/1000)
#######################################################################

'''
######################## Application Latencies ########################
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


#lets count how many pvt networks each dataflow is formed of
dataflow_pvt_nw_count = {}

total_dataflows = 100
total_devices = 100
dataflow_processor_count = 8

dataflow_num = 1
while dataflow_num <= total_dataflows:
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
'''

####################### plotting the service times ####################
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(111)
deploy_avg_times = []
step_size = 10

deploy_data = []
current_window = []
for i in range(1,101):
  if i%step_size == 1:
    #rolling_sum = 0
    current_window = []
  #rolling_sum += deploy_dict[i][1] - deploy_dict[i][0]
  current_window.append((deploy_dict[i][1] - deploy_dict[i][0])/1000)
  if i%step_size == 0:
    #deploy_avg_times.append(rolling_sum/step_size)
    step_number = i/step_size
    deploy_data.append(current_window)



application_window = range(10,110,10)
#ax.plot(application_window, deploy_avg_times, label = "DEPLOY", color = plot_color_dict["DEPLOY"])
red_square = dict(markerfacecolor='g', marker='s')
#medianprops = dict(linewidth=1, color='green')
medianprops = dict(linewidth=2, color='green')
#ax.boxplot(deploy_data,flierprops=red_square, showfliers=False, vert=True, positions = application_window, labels = application_window, widths=2.5, patch_artist=False, medianprops=medianprops)
ax.boxplot(deploy_data,flierprops=red_square, showfliers=False, vert=True, positions = application_window, labels = application_window, widths=2.5, patch_artist=False, medianprops=medianprops)
#ax.plot(application_window, stop_times, label = "STOP", color = plot_color_dict["STOP"], marker='o')
ax.plot(application_window, stop_times, label = "STOP", color = plot_color_dict["STOP"], markeredgecolor=plot_color_dict["STOP"], markerfacecolor='none', marker='o', markersize=10)
#ax.plot(application_window, rebalance_times, label = "REBALANCE", color = plot_color_dict["REBALANCE"], marker='^')
ax.plot(application_window, rebalance_times, label = "REBALANCE", color = plot_color_dict["REBALANCE"], markeredgecolor=plot_color_dict["REBALANCE"], markerfacecolor='none', marker='^', markersize=10)

ax.set_xlim(0,105)
#plt.legend()
plt.xlabel('Number of applications', fontsize=25)
plt.ylabel('Service call latency (secs)', fontsize = 25)
#plt.title('Latency for operations with 100 devices')
plt.grid()
plt.minorticks_on()
#plt.grid(b=True, which='minor')

#ax.yaxis.grid(True, which='major')
#ax.yaxis.grid(True, which='minor')

ax.yaxis.set_ticks(np.arange(0, 80, 10))
y_minorLocator = AutoMinorLocator(5)
ax.yaxis.set_minor_locator(y_minorLocator)
ax.grid(color='dimgrey', which='major', axis='y')
ax.grid(color='darkgrey', which='minor', axis='y')

ax.xaxis.set_tick_params(labelsize=22, which='both')
ax.yaxis.set_tick_params(labelsize=22)

################### plot the median of application latency ###########
ax1 = ax.twinx()
ax1.yaxis.set_tick_params(labelsize=22)
ax1.set_ylabel('Median App Latency (secs)', fontsize=25)
ax1.set_ylim(ymin=0)
#ax1.invert_yaxis()
ax1.yaxis.set_ticks(np.arange(0, 4.0, 0.5))
y1_minorLocator = AutoMinorLocator(5)
ax1.yaxis.set_minor_locator(y1_minorLocator)
ax1.yaxis.set_tick_params(labelsize=22)
#ax1.grid(color='dimgrey', which='major', axis='y')
#ax1.grid(color='darkgrey', which='minor', axis='y')

x_axis = np.arange(10,110,10)
median_latency_window = [845.0, 844.0, 832.0, 839.0, 825.0, 817.0, 844.0, 910.0, 991.0, 1110.0]
median_latency_window = [element/1000 for element in median_latency_window]
'''
median_latency_window = []
for window in dag_windows:
	cur_median = np.median(window[2])
	median_latency_window.append(cur_median)

app_median_latency = open("app_median_latency.txt", "w")
app_median_latency.write(str(median_latency_window) + "\n")
app_median_latency.close()
'''

ax1.plot(x_axis, median_latency_window, label = "APPLICATION", color = plot_color_dict["APPLICATION"], markeredgecolor=plot_color_dict["APPLICATION"], markerfacecolor='none', marker='s', markersize=10)

#try custom legend
#deploy_line = Line2D([0], [0], color = plot_color_dict["DEPLOY"])
deploy_line = Line2D([0], [0], color = plot_color_dict["DEPLOY"], linewidth = 2)
#stop_line = Line2D([0], [0], color = plot_color_dict["STOP"], marker='o')
stop_line = Line2D([0], [0], color = 'none', marker='o', markersize = 10, markeredgecolor = plot_color_dict["STOP"], markerfacecolor = 'none')
#rebalance_line = Line2D([0], [0], color = plot_color_dict["REBALANCE"], marker='^')
rebalance_line = Line2D([0], [0], color = 'none', marker='^', markersize = 10, markeredgecolor = plot_color_dict["REBALANCE"], markerfacecolor = 'none')
application_line = Line2D([0], [0], color = 'none', marker='s', markersize = 10, markeredgecolor = plot_color_dict["APPLICATION"], markerfacecolor = 'none')

lines = [deploy_line, stop_line, rebalance_line, application_line]
labels = ['DEPLOY', 'STOP', 'REBALANCE', 'APP LATENCY']
#lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colors]
plt.legend(lines, labels, loc='upper left', prop={'size': 20})

plt.show()
fig.savefig("Scalability_Service_Latency.pdf", bbox_inches='tight')

###################### memory and cpu for containers ##################

##################### Window creation for analysis ####################
#lets create windows for every 10 dataflows for analysis

'''
dag_windows = []
step_size = 10
for i in range(1,11):
  if i == 1:
    window_start = deploy_dict[i][0]
  else:
    window_start = stop_dict[i-1][1]
  window_end = stop_dict[i][1]
  dag_windows.append([window_start, window_end])
#######################################################################

for w in dag_windows:
  print w
'''

#this will store the cumulative sum of cpu and memory used by all
#container within one window
#window_sums_cpu = []
#window_sums_mem = []
#for i in range(0,10):
#  window_sums_cpu.append([])
#  window_sums_mem.append([])

'''
for filename in os.listdir("container_stats"):
  current_window = 0
  observed_devices = {}
  #when device seen first time, use a default multiplication factor 1(sec)
  first_multiplication = 1000
  with open("container_stats/" + filename) as f:
    for line in f:
      splits = line.split(" ")
      time_msec = int(splits[0]) * 1000
      device_name = splits[1]
      cpu_perc = float(splits[2][:-1])
      mem_perc = float(splits[3].strip()[:-1])
      if time_msec >= dag_windows[current_window][0] and time_msec <= dag_windows[current_window][1]:
        if device_name not in observed_devices:
          window_sums_cpu[current_window].append(cpu_perc * first_multiplication)
          window_sums_mem[current_window].append(mem_perc * first_multiplication)
        else:
          window_sums_cpu[current_window].append(cpu_perc * (time_msec - observed_devices[device_name]))
          window_sums_mem[current_window].append(mem_perc * (time_msec - observed_devices[device_name]))
        observed_devices[device_name] = time_msec
      else:
        current_window += 1
        if current_window >= len(dag_windows):
          break
        else:
          window_sums_cpu[current_window].append(cpu_perc * (time_msec - observed_devices[device_name]))
          window_sums_mem[current_window].append(mem_perc * (time_msec - observed_devices[device_name]))
          observed_devices[device_name] = time_msec
'''

'''
window_sums_cpu = {}
window_sums_mem = {}
# i is the window
for i in range(0,10):
  window_sums_cpu[i] = {}
  window_sums_mem[i] = {}
  # j is the VM
  for j in range(1,11):
    window_sums_cpu[i][j] = []
    window_sums_mem[i][j] = []

container_count_VM = 10
for filename in os.listdir("container_stats"):
  current_window = 0
  last_seen_time = -1
  total_cpu = 0
  total_mem = 0
  vm_num = 0
  with open("container_stats/" + filename) as f:
    for line in f:
      splits = line.split(" ")
      time_msec = int(splits[0]) * 1000
      if last_seen_time == -1:
        last_seen_time = time_msec 
      device_name = splits[1]
      if vm_num == 0:
        if 'Edge' in device_name:
          vm_num = int(device_name.split('-')[1].split('.')[0])
        else:
          vm_num = int(device_name.split('-')[1].split('.')[1])
      cpu_perc = float(splits[2][:-1])
      mem_perc = float(splits[3].strip()[:-1])
      if time_msec >= dag_windows[current_window][0] and time_msec <= dag_windows[current_window][1]:
        if time_msec == last_seen_time:
          total_cpu += cpu_perc
          total_mem += mem_perc
        else:
          window_sums_cpu[current_window][vm_num].append(total_cpu)
          window_sums_mem[current_window][vm_num].append(total_mem)
          total_cpu = cpu_perc
          total_mem = mem_perc
          last_seen_time = time_msec
      else:
        current_window += 1
        if current_window >= len(dag_windows):
          break
        else:
          if total_cpu != 0 or total_mem != 0:
            window_sums_cpu[current_window-1][vm_num].append(total_cpu)
            window_sums_mem[current_window-1][vm_num].append(total_mem)
          total_cpu = cpu_perc
          total_mem = mem_perc
          last_seen_time = time_msec

#computing the total cpu and memory for each window
total_devices = 100
total_cpu_perc = 100
total_mem_perc = 100
'''


'''
window_total_cpu = []
window_total_mem = []
for i in range(0,10):
  window_time = dag_windows[i][1] - dag_windows[i][0]
  window_total_cpu.append(total_devices * total_cpu_perc * window_time)
  window_total_mem.append(total_devices * total_mem_perc * window_time)

#cumulative_total_cpu = 0.0
#cumulative_total_mem = 0.0
#for i in range(0,10):
#  cumulative_total_cpu += window_total_cpu[i]
#  cumulative_total_mem += window_total_mem[i]

#cumulative_sum_cpu = []
#cumulative_sum_mem = []
#for i in range(0,10):
#  cumulative_sum_cpu.append([])
#  cumulative_sum_mem.append([])

#cumulative_sum_cpu[0] = window_sums_cpu[0]
#cumulative_sum_mem[0] = window_sums_mem[0]

#for i in range(1,10):
#  cumulative_sum_cpu[i] = window_sums_cpu[i] + cumulative_sum_cpu[i-1]
#  cumulative_sum_mem[i] = window_sums_mem[i] + cumulative_sum_mem[i-1]
  
#perc_cumulative_cpu = []
#perc_cumulative_mem = []
#for i in range(0,10):
#  perc_cumulative_cpu.append([])
#  perc_cumulative_mem.append([])


for i in range(0,10):
  window_sums_cpu[i] = [(element * 100 /window_total_cpu[i]) for element in window_sums_cpu[i]]
  window_sums_mem[i] = [(element * 100 /window_total_mem[i]) for element in window_sums_mem[i]]

#for i in range(0,10):
#  window_sums_cpu[i] = sum(window_sums_cpu[i][0:len(window_sums_cpu[i])])
#  window_sums_mem[i] = sum(window_sums_mem[i][0:len(window_sums_mem[i])])

#avg_cpu_window = []
#avg_mem_window = []
#for i in range(0,10):
#  avg_cpu_window.append((window_sums_cpu[i] * 100)/ window_total_cpu[i])
#  avg_mem_window.append((window_sums_mem[i] * 100)/ window_total_mem[i])
'''


'''
window_total_cpu = []
window_total_mem = []
#for i in range(0,10):
#  window_total_cpu.append([])
#  window_total_mem.append([])

vm_count = 10
for i in range(0,10):
  #lets find minimum size of a list for each VM
  min_size = 100000
  for j in range(1,11):
    cur_len = len(window_sums_cpu[i][j])
    if cur_len < min_size:
      min_size = cur_len
  #break each of the list into min_size
  for j in range(1,11):
    window_sums_cpu[i][j] = window_sums_cpu[i][j][:min_size]
    window_sums_mem[i][j] = window_sums_mem[i][j][:min_size]
  cur_list_cpu = [None]*(vm_count * min_size)
  cur_list_mem = [None]*(vm_count * min_size)
  for j in range(0,10):
    cur_list_cpu[j::10] = window_sums_cpu[i][j+1]
    cur_list_mem[j::10] = window_sums_mem[i][j+1]
  cumulative_cpu = []
  cumulative_mem = []
  for j in range(0,(vm_count-1)*min_size,10):
    cpu_sum = 0
    mem_sum = 0
    for k in range(j,j+10):
      cpu_sum += cur_list_cpu[k]
      mem_sum += cur_list_mem[k]
    cumulative_cpu.append(cpu_sum/100)
    cumulative_mem.append(mem_sum/100)
  window_total_cpu.append(cumulative_cpu)
  window_total_mem.append(cumulative_mem)
'''


'''
fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)
ax.plot(application_window, avg_cpu_window, label = "CPU %" , color = "green")
ax.plot(application_window, avg_mem_window, label = "Memory %" , color = "blue")
ax.set_xticks(np.arange(10,110,10, dtype=int))

ax.set_xlim(0,105)
plt.legend()
plt.xlabel('Number of applications', fontsize=15)
plt.ylabel('CPU and Memory consumption per window', fontsize = 15)
plt.title('CPU and Memory profile')
plt.grid()
plt.show()
'''

'''
fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)
application_window = range(0,120,10)
#medianprops = dict(linewidth=1, color='green')
medianprops = dict(linewidth=5, color='green')
red_square = dict(markerfacecolor='g', marker='s')
ax.boxplot(window_total_cpu,flierprops=red_square, showfliers=False, vert=True, positions = application_window[1:-1], labels = application_window[1:-1], widths=2.5, patch_artist=False, medianprops=medianprops)

ax.set_xlabel('Application Window', fontsize=25)
ax.set_ylabel('CPU Utilization%', fontsize=25)

ax.set_xlim(xmin=0)
ax.set_ylim(ymin=0,ymax=20)
ax.set_xlim(0,105)
plt.grid()
plt.minorticks_on()
ax.yaxis.set_ticks(np.arange(0, 25, 5))
y_minorLocator = AutoMinorLocator(5)
ax.yaxis.set_minor_locator(y_minorLocator)
ax.grid(color='dimgrey', which='major', axis='y')
ax.grid(color='darkgrey', which='minor', axis='y')

ax.xaxis.set_tick_params(labelsize=22)
ax.yaxis.set_tick_params(labelsize=22)
plt.show()


fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)
application_window = range(0,120,10)
medianprops = dict(linewidth=1, color='green')
red_square = dict(markerfacecolor='g', marker='s')
ax.boxplot(window_total_mem,flierprops=red_square, showfliers=False, vert=True, positions = application_window[1:-1], labels = application_window[1:-1], widths=2.5, patch_artist=False, medianprops=medianprops)

ax.set_xlabel('Application Window', fontsize=25)
ax.set_ylabel('Memory Utilization%', fontsize=25)

ax.set_xlim(xmin=0)
ax.set_ylim(ymin=0)
ax.set_xlim(0,105)
plt.grid()
plt.minorticks_on()
ax.yaxis.set_ticks(np.arange(0, 80, 10))
y_minorLocator = AutoMinorLocator(5)
ax.yaxis.set_minor_locator(y_minorLocator)
ax.grid(color='dimgrey', which='major', axis='y')
ax.grid(color='darkgrey', which='minor', axis='y')

ax.xaxis.set_tick_params(labelsize=22)
ax.yaxis.set_tick_params(labelsize=22)
plt.show()
'''
