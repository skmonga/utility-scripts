import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,AutoMinorLocator)
from matplotlib.lines import Line2D

input_file_entry = "Rebalance/4/time_taken_entry.csv"
input_file_exit = "Rebalance/4/time_taken_exit.csv"
consumption_time = "Rebalance/4/consumption_time.txt"
rebalance_time = "Rebalance/4/rebalance_time.txt"
update_rate = "Rebalance/4/updated_rate.txt"

effective_ip_rate_entry = "Rebalance/4/effective_input_rate_entry.txt"
effective_op_rate_entry = "Rebalance/4/effective_output_rate_entry.txt"
effective_ip_count_entry = "Rebalance/4/effective_input_count_entry.txt"
effective_op_count_entry = "Rebalance/4/effective_output_count_entry.txt"
median_latency_entry = "Rebalance/4/median_latency_entry_sort.txt"

effective_ip_rate_exit = "Rebalance/4/effective_input_rate_exit.txt"
effective_op_rate_exit = "Rebalance/4/effective_output_rate_exit.txt"
effective_ip_count_exit = "Rebalance/4/effective_input_count_exit.txt"
effective_op_count_exit = "Rebalance/4/effective_output_count_exit.txt"
median_latency_exit = "Rebalance/4/median_latency_exit_sort.txt"

output_message_per_window_entry = "Rebalance/4/output_message_per_window_entry.txt"
output_message_per_window_exit = "Rebalance/4/output_message_per_window_exit.txt"

exp_start_time = 1537111497219

list_op_entry_window = []
list_op_entry_count = []

list_op_exit_window = []
list_op_exit_count = []

with open(output_message_per_window_entry, "r") as entry:
	for line in entry:
		splits = line.split(",")
		list_op_entry_window.append((int(splits[0]), int(splits[1])))
		list_op_entry_count.append(int(splits[2].strip()))

list_op_entry_window = [((elem[0] - exp_start_time)/1000, (elem[1] - exp_start_time)/1000) for elem in list_op_entry_window]

with open(output_message_per_window_exit, "r") as entry:
	for line in entry:
		splits = line.split(",")
		list_op_exit_window.append((int(splits[0]), int(splits[1])))
		list_op_exit_count.append(int(splits[2].strip()))

list_op_exit_window = [((elem[0] - exp_start_time)/1000, (elem[1] - exp_start_time)/1000) for elem in list_op_exit_window]

#cloud_consecutive_input_diff= "Rebalance/4/cloud_consecutive_input_diff.txt"

list_ts_entry = []
list_lat_entry = []

list_ts_exit = []
list_lat_exit = []


#to draw vertical line at the time of rebalance, we keep an array at times of rebalance
#list_config_names = ['Edge', 'Fog', 'Hybrid_CC_FF', 'Hybrid_FC_FC', 'Cloud']
list_config_names = ['E*', 'F*', 'CCFF', 'FCFC', 'C*']
#list_rebalance_times = [0,1529961549180,1529962832550,1529963212250,1529963844000,1529966035910]
#list_rate_update_times = [1529961932250,1529962232350,1529962532450,1529963543910,1529964235430,1529964535520,1529964835600,1529965135690,1529965435790,1529965735890,1529966384650]

list_rebalance_rates = [3,9,18,24,36]
list_update_rates = [6,12,15,21,27,30,33,39,42,45,48,51,54]

##########################################
####### For cloud only plot ##############
#list_cloud_rebalance_idx = [3]
#list_cloud_update_idx = [6,7]
##########################################

list_rebalance_times = []
list_rate_update_times = []
#no rebalance for edge so placing 0 for it
list_rebalance_times.append(exp_start_time)


#we will be adding a median latency plot for every 1 minute
#this list has start time for a window
list_median_start_time_entry = []
list_median_start_time_exit = []
#this is the actual latency for the window
list_median_latency_entry = []
list_median_latency_exit = []


#adding the difference between consecutive entry data points in Cloud
#list_cloud_entry_time = []
#list_cloud_consecutive_diff = []

#with open(cloud_consecutive_input_diff , "r") as entry:
#	for line in entry:
#		splits = line.split(",")
#		entry_time = int(splits[0])
#		diff_time = int(splits[1].strip())
#		list_cloud_entry_time.append(entry_time)
#		list_cloud_consecutive_diff.append(diff_time)

#print max(list_cloud_consecutive_diff)

#list_cloud_entry_time = [(element - exp_start_time)/1000 for element in list_cloud_entry_time]

temp_list = []
last_seen_time = -1
with open(median_latency_entry , "r") as entry:
	for line in entry:
		splits = line.split(",")
		start_time = int(splits[0])
		window_median_latency = float(splits[1].strip())
		list_median_start_time_entry.append(start_time)
		list_median_latency_entry.append(window_median_latency)

list_median_start_time_entry = [(element - exp_start_time)/1000 for element in list_median_start_time_entry]
list_median_start_time_entry_mins = [element/60 for element in list_median_start_time_entry]

with open(median_latency_exit , "r") as entry:
	for line in entry:
		splits = line.split(",")
		start_time = int(splits[0])
		window_median_latency = float(splits[1].strip())
		list_median_start_time_exit.append(start_time)
		list_median_latency_exit.append(window_median_latency)

list_median_start_time_exit = [(element - exp_start_time)/1000 for element in list_median_start_time_exit]
list_median_start_time_exit_mins = [element/60 for element in list_median_start_time_exit]


with open(rebalance_time, "r") as entry:
	for line in entry:
		splits = line.split(" ")
		time_val = float(splits[len(splits) - 1].strip())
		list_rebalance_times.append(int(time_val * 1000))

list_rebalance_times = [(element - exp_start_time)/1000 for element in list_rebalance_times]
list_rebalance_times_mins = [element/60 for element in list_rebalance_times]

with open(update_rate, "r") as entry:
	for line in entry:
		splits = line.split(" ")
		time_val = float(splits[len(splits) - 1].strip())
		list_rate_update_times.append(int(time_val * 1000))

list_rate_update_times = [(element - exp_start_time)/1000 for element in list_rate_update_times]
list_rate_update_times_mins = [element/60 for element in list_rate_update_times]

list_window_times_mins = list_rebalance_times_mins + list_rate_update_times_mins
list_window_times_mins.sort()

list_entry = []
list_diff = []
with open(consumption_time, 'r') as entry:
	for line in entry:
		splits = line.split(",")
		entry_time = int(splits[0])
		diff_time = int(splits[1].strip())
		list_entry.append(entry_time)
		list_diff.append(diff_time)
		#TODO::Need to handle exp_start_time

def make_patch_spines_invisible(ax):
	ax.set_frame_on(True)
	ax.patch.set_visible(False)
	for sp in ax.spines.values():
		sp.set_visible(False)

with open(input_file_entry,'r') as entry:
	for line in entry:
		splits = line.split(",")
		timestamp = int(splits[0])
		latency = (int(splits[1].strip()) - timestamp)
		#if latency > 0:
		list_ts_entry.append(timestamp)
		list_lat_entry.append(latency)

list_ts_entry = [(element - exp_start_time)/1000 for element in list_ts_entry]
list_ts_entry_mins = [element/60 for element in list_ts_entry]

with open(input_file_exit,'r') as entry:
	for line in entry:
		splits = line.split(",")
		timestamp = int(splits[0])
		latency = (int(splits[1].strip()) - timestamp)
		#if latency > 0:
		list_ts_exit.append(timestamp)
		list_lat_exit.append(latency)

list_ts_exit = [(element - exp_start_time)/1000 for element in list_ts_exit]
list_ts_exit_mins = [element/60 for element in list_ts_exit]


def get_xposition(start,end):
	diff = end - start
	return start + 0.25 * diff

def getYCoordinateForConfigName(top_y):
	return int(0.75 * top_y) 


#############################################################
############# MEDIAN LATENCY OVER 1 MINUTE ##################
#############################################################
fig,ax = plt.subplots()

ax.set_yscale('log')
ax.plot(list_median_start_time_entry_mins, list_median_latency_entry, markerfacecolor='none', color='b')
ax.plot(list_median_start_time_exit_mins, list_median_latency_exit, markerfacecolor='none', color='r')

ax.set_xlim(xmin=0)
ax.xaxis.set_ticks(np.arange(0, max(max(list_ts_entry_mins), max(list_ts_exit_mins)) + 11, 10))
x_minorLocator = AutoMinorLocator(5)
ax.xaxis.set_minor_locator(x_minorLocator)
ax.grid(color='dimgrey', which='major', axis='x')
ax.grid(color='gainsboro', which='minor', axis='x')


ax.grid(color='black', which='major', axis='y')
ax.grid(color='gainsboro', which='minor', axis='y')

i = 0
for i in range(len(list_rebalance_times_mins)):
	r_time = list_rebalance_times_mins[i]
	if i != 0:
		plt.axvline(x=r_time, color='darkorange', linestyle='dashed', linewidth=2.5)
	x_pos = 0
	y_pos = 110000
	if i != len(list_rebalance_times_mins) - 1:
		if i == 0:
			x_pos = get_xposition(ax.get_xlim()[0], list_rebalance_times_mins[i+1])
		else:
			x_pos = get_xposition(r_time, list_rebalance_times_mins[i+1])
	else:
		x_pos = get_xposition(r_time, ax.get_xlim()[1])
	plt.text(x_pos,y_pos,list_config_names[i], color='darkorange',fontsize=20)


#i = 0
#for update_t in list_rate_update_times:
#  plt.axvline(x=update_t, color='grey', linestyle='dotted', linewidth=0.5)
#  i += 1


ax.set_xlabel('Run duration (minutes)', fontsize=25)
ax.set_ylabel('Median Latency (ms) [Log]', fontsize=25)

ax1 = ax.twinx()
ax1.set_ylabel('Input Rate (events/min)', fontsize=25)

ax1.yaxis.set_ticks(np.arange(0, 60, 6))

last_seen = -1
current_rate = 3
#print list_window_times_min
for t in list_window_times_mins:
	if t == 0:
		last_seen = 0
		continue
	else:
		x_values = np.arange(last_seen, t+1, 1)
		y_values = np.array([current_rate for i in range(len(x_values))])
		ax1.plot(x_values, y_values, 'g')
		last_seen = t
		current_rate += 3

#plot the last green line
x_values = np.arange(179,191,1)
y_values = np.array([current_rate for i in range(len(x_values))])
ax1.plot(x_values, y_values, 'g')

#add the legend
#colors = ['blue', 'orange', 'green']
median_line_entry = Line2D([0], [0], color='b')
median_line_exit = Line2D([0], [0], color='r')
rebalance_line = Line2D([0], [0], color='orange', linewidth=1.5, linestyle='--')
input_rate_line = Line2D([0], [0], color='green')
lines = [median_line_entry, median_line_exit, rebalance_line, input_rate_line]
labels = ['median latency entry topic', 'median latency exit topic', 'rebalance point', 'input rate']
#lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='--') for c in colors]
plt.legend(lines, labels, loc='center right', prop={'size': 15})

ax.xaxis.set_tick_params(labelsize=15)
ax.yaxis.set_tick_params(labelsize=20)
ax1.yaxis.set_tick_params(labelsize=20)

plt.show()

##################################################################
######### PLOTTING DIFF BTW CONSECUTIVE ENTRIES IN CLOUD #########
##################################################################
#fig,ax = plt.subplots()

##################################################################
############ REBALANCE & UPDATE TIMES FOR CLOUD ##################
##################################################################
#list_cloud_rebalance_times = [list_rebalance_times[i] for i in list_cloud_rebalance_idx]
#list_cloud_update_times = [list_rate_update_times[i] for i in list_cloud_update_idx]

#ax.set_yscale('log')
#mpl.rc('lines', markeredgewidth=0.1) 
#ax.scatter(list_cloud_entry_time, list_cloud_consecutive_diff,alpha=0.5, marker=".", linewidths=0.5, edgecolors='none')

#ax.xaxis.set_ticks(np.arange(list_cloud_rebalance_times[0], list_cloud_update_times[-1] + 1, 500))
#x_minorLocator = AutoMinorLocator(5)
#ax.xaxis.set_minor_locator(x_minorLocator)
#ax.grid(color='dimgrey', which='major', axis='x', linestyle='-', linewidth=1)
#ax.grid(color='darkgrey', which='minor', axis='x', linestyle='-', linewidth=0.75)

#ax.set_yscale('log')
#ax.set_ylim(ymin=1)

#for i in range(len(list_cloud_rebalance_times)):
#	r_time = list_cloud_rebalance_times[i]
#	if i != 0:
#		plt.axvline(x=r_time, color='black', linestyle='dashed', linewidth=1.5)
#	x_pos = 0
#	y_pos = 100
#	if i != len(list_cloud_rebalance_times) - 1:
#		if i == 0:
#			x_pos = get_xposition(ax.get_xlim()[0], list_rebalance_times[i+1])
#		else:
#			x_pos = get_xposition(r_time, list_rebalance_times[i+1])
#	else:
#		x_pos = get_xposition(r_time, ax.get_xlim()[1])
#	plt.text(x_pos,y_pos,list_config_names[i],size='x-small', color='black')


#i = 0
#for update_t in list_cloud_update_times:
#  plt.axvline(x=update_t, color='grey', linestyle='dotted', linewidth=0.5)
#  i += 1


#plt.xlabel('Timestamp (seconds)', fontsize=20)
#plt.ylabel('Time difference between consecutive input tuples (milliseconds)', fontsize=10)
#plt.title('Difference between consecutive input tuples for Cloud',fontsize=24)
#plt.show()
