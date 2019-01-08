import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
from matplotlib.lines import Line2D


pi_usage = "CITY/Rebalance/3/logs_edge/cpu_mem_monitor_pi.txt"
fog_usage = "CITY/Rebalance/3/logs_fog/cpu_mem_monitor_fog.txt"
cloud_usage = "CITY/Rebalance/3/logs_cloud/cpu_mem_monitor_cloud.txt"

rebalance_time = "CITY/Rebalance/3/rebalance_time.txt"
update_rate = "CITY/Rebalance/3/updated_rate.txt"

pi_ts = []
pi_cpu = []
pi_mem = []
fog_ts = []
fog_cpu = []
fog_mem = []
cloud_ts = []
cloud_cpu = []
cloud_mem = []

pi_pid = '32114'
fog_pid = '27002'
cloud_pid = '30277'

#we want to plot on x-axis starting from 0 ,so we use the starting time
#of the first message produced in Kafka and subtract the rest of
#timestamps with this one
exp_start_time = 1537280566286

#list_config_names = ['Edge', 'EFC(2:0:6)', 'EFC(2:1:5)', 'Cloud', 'Fog_Edge', 'Fog']
list_config_names = ['E*', 'EC', 'EFC', 'C*', 'EF', 'F*']
list_rebalance_times = []
list_rate_update_times = []

list_rebalance_times.append(0)

with open(rebalance_time, "r") as entry:
	for line in entry:
		splits = line.split(" ")
		time_val = float(splits[len(splits) - 1].strip())
		list_rebalance_times.append(int(time_val * 1000))

list_rebalance_times = [(element - exp_start_time)/1000 for element in list_rebalance_times]
list_rebalance_times_min = [element/60 for element in list_rebalance_times]

with open(update_rate, "r") as entry:
	for line in entry:
		splits = line.split(" ")
		time_val = float(splits[len(splits) - 1].strip())
		list_rate_update_times.append(int(time_val * 1000))

list_rate_update_times = [(element - exp_start_time)/1000 for element in list_rate_update_times]
list_rate_update_times_min = [element/60 for element in list_rate_update_times]

list_window_times_min = list_rebalance_times_min + list_rate_update_times_min
list_window_times_min.sort()

list_ts_min = np.arange(0,189,1)

def get_xposition(start,end):
	diff = end - start
	return start + 0.2 * diff

def make_patch_spines_invisible(ax):
        ax.set_frame_on(True)
        ax.patch.set_visible(False)
        for sp in ax.spines.values():
                sp.set_visible(False)

list_median_pi_window = []
list_median_pi_cpu = []
temp_list = []
current_window = 0
with open(pi_usage) as entry:
	for line in entry:
		splits = line.split()
		pid = splits[1]
		ts = int(((int(splits[0]) * 1000) - exp_start_time)/1000)
		ts_min = ts/60 
		cpu = float(splits[9])
		mem = float(splits[10])
		if pid == pi_pid:
			if ts_min == current_window:
				temp_list.append(cpu)
			else:
				list_median_pi_window.append(current_window)
				list_median_pi_cpu.append(np.median(temp_list))
				current_window = ts_min
				temp_list = []
				temp_list.append(cpu)


list_median_fog_window = []
list_median_fog_cpu = []
temp_list = []
current_window = 0
with open(fog_usage) as entry:
        for line in entry:
                splits = line.split()
		pid = splits[1]
                ts = int(((int(splits[0]) * 1000) - exp_start_time)/1000)
		ts_min = ts/60
                cpu = float(splits[9])
                mem = float(splits[10])
                if pid == fog_pid:
			if ts_min == current_window:
				temp_list.append(cpu)
			else:
				list_median_fog_window.append(current_window)
				list_median_fog_cpu.append(np.median(temp_list))
				current_window = ts_min
				temp_list = []
				temp_list.append(cpu)

list_median_cloud_window = []
list_median_cloud_cpu = []
temp_list = []
current_window = 0
with open(cloud_usage) as entry:
        for line in entry:
                splits = line.split()
		pid = splits[1]
                ts = int(((int(splits[0]) * 1000) - exp_start_time)/1000)
		ts_min = ts/60
                cpu = float(splits[9])
                mem = float(splits[10])
                if pid == cloud_pid:
			if ts_min == current_window:
				temp_list.append(cpu)
			else:
				list_median_cloud_window.append(current_window)
				list_median_cloud_cpu.append(np.median(temp_list))
				current_window = ts_min
				temp_list = []
				temp_list.append(cpu)


###################################
########### CPU Usage #############
###################################
fig,ax = plt.subplots()
#plt.title('CPU Consumption for ETL CITY Rebalance')
#edgecolors for scatter plot, markeredgecolor for plot
#ax.scatter(pi_ts, pi_cpu, marker="o", linewidths=0.5, s=10, facecolors='none', edgecolors='g', label='Edge')
'''
ax.plot(pi_ts, pi_cpu, linewidth=0.5, markerfacecolor='none', markeredgecolor='g', label='Edge')
ax.plot(fog_ts, fog_cpu, linewidth=0.5, markerfacecolor='none', markeredgecolor='b', label='Fog')
ax.plot(cloud_ts, cloud_cpu, linewidth=0.5, markerfacecolor='none', markeredgecolor='r', label='Cloud')
ax.set_xlabel('Timestamp (seconds)')
ax.set_ylabel('Percentage CPU Usage')
ax.tick_params('y', colors='black')
'''


ax.set_xlim(xmin=0)
ax.xaxis.set_ticks(np.arange(0, max(list_ts_min) + 11, 10))
x_minorLocator = AutoMinorLocator(5)
ax.xaxis.set_minor_locator(x_minorLocator)
ax.grid(color='dimgrey', which='major', axis='x')
ax.grid(color='gainsboro', which='minor', axis='x')

ax.set_ylim(ymin=0)
ax.yaxis.set_ticks(np.arange(0, 350, 50))
y_minorLocator = AutoMinorLocator(5)
ax.yaxis.set_minor_locator(y_minorLocator)
ax.yaxis.grid(color='black', which='major')
ax.yaxis.grid(color='gainsboro', which='minor')

ax.plot(list_median_pi_window, list_median_pi_cpu, markerfacecolor='none', color='b')
ax.plot(list_median_fog_window, list_median_fog_cpu, markerfacecolor='none', color='r')
ax.plot(list_median_cloud_window, list_median_cloud_cpu, markerfacecolor='none', color='g')

for i in range(len(list_rebalance_times_min)):
	r_time = list_rebalance_times_min[i]
	if i != 0:
		plt.axvline(x=r_time, color='darkorange', linestyle='dashed', linewidth=2.5)
		#plt.axvline(x=r_time, color='black', linestyle='dashed', linewidth=5)
	x_pos = 0
	y_pos = 250
	if i != len(list_rebalance_times_min) - 1:
		if i == 0:
			x_pos = get_xposition(ax.get_xlim()[0], list_rebalance_times_min[i+1])
		else:
			x_pos = get_xposition(r_time, list_rebalance_times_min[i+1])
	else:
		x_pos = get_xposition(r_time, ax.get_xlim()[1])
	plt.text(x_pos,y_pos,list_config_names[i], color='darkorange',fontsize=20)
	#plt.text(x_pos,y_pos,list_config_names[i], color='black',fontsize=20)

#i = 0
#for update_t in list_rate_update_times:
#  plt.axvline(x=update_t, color='grey', linestyle='dotted', linewidth=0.5)
#  i += 1

rebalance_line = Line2D([0], [0], color='orange', linewidth=1.5, linestyle='--')
#rebalance_line = Line2D([0], [0], color='black', linewidth=5, linestyle='dashed')
edge_line = Line2D([0], [0], color='b')
#edge_line = Line2D([0], [0], color='b', linewidth=2.5)
fog_line = Line2D([0], [0], color='r')
#fog_line = Line2D([0], [0], color='r', linewidth=2.5)
cloud_line = Line2D([0], [0], color='g')
#cloud_line = Line2D([0], [0], color='g', linewidth=2.5)
lines = [rebalance_line, edge_line, fog_line, cloud_line]
labels = ['rebalance point', 'Edge', 'Fog', 'Cloud']
#lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colors]
plt.legend(lines, labels, loc='center right', bbox_to_anchor=(1.0,0.7), prop={'size': 15})

ax.xaxis.set_tick_params(labelsize=15)
ax.yaxis.set_tick_params(labelsize=20)

ax.set_xlabel('Run duration (minutes)', fontsize=25)
ax.set_ylabel('CPU Utilization%', fontsize=25)

plt.show()

###################################
########### Memory Usage ##########
###################################
'''
fig,ax = plt.subplots()
plt.title('Memory Consumption for ETL CITY Rebalance')
ax.plot(pi_ts, pi_mem, linewidth=0.5, markerfacecolor='none', markeredgecolor='g', label='Edge')
ax.plot(fog_ts, fog_mem, linewidth=0.5, markerfacecolor='none', markeredgecolor='b', label='Fog')
ax.plot(cloud_ts,cloud_mem, linewidth=0.5, markerfacecolor='none', markeredgecolor='r', label='Cloud')
ax.set_xlabel('Timestamp (seconds)')
ax.set_ylabel('Percentage Memory Usage')
ax.tick_params('y', colors='black')

#x axis settings
ax.set_xlim(xmin=0)
ax.xaxis.set_ticks(np.arange(0, max(pi_ts) + 1, 1000))
x_minorLocator = AutoMinorLocator(5)
ax.xaxis.set_minor_locator(x_minorLocator)

for i in range(len(list_rebalance_times)):
	r_time = list_rebalance_times[i]
	if i != 0:
		plt.axvline(x=r_time, color='black', linestyle='dashed', linewidth=1.5)
	x_pos = 0
	y_pos = 50
	if i != len(list_rebalance_times) - 1:
		if i == 0:
			x_pos = get_xposition(ax.get_xlim()[0], list_rebalance_times[i+1])
		else:
			x_pos = get_xposition(r_time, list_rebalance_times[i+1])
	else:
		x_pos = get_xposition(r_time, ax.get_xlim()[1])
	plt.text(x_pos,y_pos,list_config_names[i],size='x-small', color='black')

i = 0
for update_t in list_rate_update_times:
  plt.axvline(x=update_t, color='grey', linestyle='dotted', linewidth=0.5)
  i += 1

plt.legend()
plt.show()
'''


