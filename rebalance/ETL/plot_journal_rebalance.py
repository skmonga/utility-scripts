import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,AutoMinorLocator)
from matplotlib.lines import Line2D

input_file = "CITY/Rebalance/3/time_taken.csv"
effective_ip_rate = "CITY/Rebalance/3/effective_input_rate.txt"
effective_op_rate = "CITY/Rebalance/3/effective_output_rate.txt"
effective_ip_count = "CITY/Rebalance/3/effective_input_count.txt"
effective_op_count = "CITY/Rebalance/3/effective_output_count.txt"
rebalance_time = "CITY/Rebalance/3/rebalance_time.txt"
update_rate = "CITY/Rebalance/3/updated_rate.txt"
consumption_time = "CITY/Rebalance/3/consumption_time.txt"
median_latency = "CITY/Rebalance/3/median_latency.txt"
#cloud_consecutive_input_diff = "CITY/Rebalance/3/cloud_consecutive_input_diff.txt"

list_ts = []
list_lat = []

exp_start_time = 1537280566286

#to draw vertical line at the time of rebalance, we keep an array at times of rebalance
#list_config_names = ['Edge', 'EFC(2:0:6)', 'EFC(2:1:5)', 'Cloud', 'Fog_Edge', 'Fog']
list_config_names = ['E*', 'EC', 'EFC', 'C*', 'EF', 'F*']
#list_rebalance_times = [0,1529961549180,1529962832550,1529963212250,1529963844000,1529966035910]
#list_rate_update_times = [1529961932250,1529962232350,1529962532450,1529963543910,1529964235430,1529964535520,1529964835600,1529965135690,1529965435790,1529965735890,1529966384650]

list_rebalance_rates = [20,60,90,110,140,160]
list_update_rates = [30,40,50,70,80,100,120,130,150,170,180,190,200]

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
list_median_start_time = []
#this is the actual latency for the window
list_median_latency = []


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


with open(median_latency , "r") as entry:
	for line in entry:
		splits = line.split(",")
		start_time = int(splits[0])
		window_median_latency = float(splits[1].strip())
		list_median_start_time.append(start_time)
		list_median_latency.append(window_median_latency)

list_median_start_time = [(element - exp_start_time)/1000 for element in list_median_start_time]
list_median_start_time_min = [element/60 for element in list_median_start_time]

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

with open(input_file,'r') as entry:
	for line in entry:
		splits = line.split(",")
		timestamp = int(splits[0])
		latency = (int(splits[1].strip()) - timestamp)
		#if latency > 0:
		list_ts.append(timestamp)
		list_lat.append(latency)

list_ts = [(element - exp_start_time)/1000 for element in list_ts]
dict_ts = {}
list_ts_min = []
for elem in list_ts:
	min_convert = int(elem/60)
	if min_convert not in dict_ts:
		list_ts_min.append(min_convert)
		dict_ts[min_convert] = 1

#print list_ts_min


def get_xposition(start,end):
	diff = end - start
	return start + 0.4 * diff

def getYCoordinateForConfigName(top_y):
	return int(0.5 * top_y) 

#############################################################
############# MEDIAN LATENCY OVER 1 MINUTE ##################
#############################################################
fig,ax = plt.subplots()

ax.set_yscale('log')
#print list_median_latency
ax.plot(list_median_start_time_min, list_median_latency, color='b')

ax.set_xlim(xmin=0)
ax.xaxis.set_ticks(np.arange(0, max(list_ts_min) + 11, 10))
x_minorLocator = AutoMinorLocator(5)
ax.xaxis.set_minor_locator(x_minorLocator)
ax.grid(color='dimgrey', which='major', axis='x')
ax.grid(color='gainsboro', which='minor', axis='x')

ax.grid(color='black', which='major', axis='y')
ax.grid(color='gainsboro', which='minor', axis='y')

i = 0
for i in range(len(list_rebalance_times_min)):
	r_time = list_rebalance_times_min[i]
	if i != 0:
		plt.axvline(x=r_time, color='darkorange', linestyle='dashed', linewidth=2.5)
		#plt.axvline(x=r_time, color='black', linestyle='dashed', linewidth=5)
	x_pos = 0
	y_pos = 40000
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

ax.set_xlabel('Run duration (minutes)', fontsize=25)
ax.set_ylabel('Median Latency (ms) [Log]', fontsize=25)

ax1 = ax.twinx()
ax1.set_ylabel('Input Rate (events/sec)', fontsize=25)

ax1.yaxis.set_ticks(np.arange(0, 210, 20))

last_seen = -1
current_rate = 20
print list_window_times_min
for t in list_window_times_min:
	if t == 0:
		last_seen = 0
		continue
	else:
		x_values = np.arange(last_seen, t+1, 1)
		y_values = np.array([current_rate for i in range(len(x_values))])
		ax1.plot(x_values, y_values, 'g')
		#ax1.plot(x_values, y_values, 'g', linewidth=4)
		#ax1.plot(x_values, y_values, 'g', linewidth=4, linestyle='-.')
		last_seen = t
		current_rate += 10

#plot the last green line
x_values = np.arange(178,188,1)
y_values = np.array([current_rate for i in range(len(x_values))])
ax1.plot(x_values, y_values, 'g')
#ax1.plot(x_values, y_values, 'g', linewidth=4)
#ax1.plot(x_values, y_values, 'g', linewidth=4, linestyle='-.')

#add the legend
#colors = ['blue', 'orange', 'green']
median_line = Line2D([0], [0], color='b')
#median_line = Line2D([0], [0], color='b', linewidth=2.5)
rebalance_line = Line2D([0], [0], color='orange', linewidth=1.5, linestyle='--')
#rebalance_line = Line2D([0], [0], color='black', linewidth=2.5, linestyle='--')
input_rate_line = Line2D([0], [0], color='green')
#input_rate_line = Line2D([0], [0], color='green', linewidth=2.5)
#input_rate_line = Line2D([0], [0], color='green', linewidth=2.5, linestyle='-.')
lines = [median_line, rebalance_line, input_rate_line]
labels = ['median latency', 'rebalance point', 'input rate']
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
#here we have multiple y axes on the right side. To check sample code , refer to 
#https://matplotlib.org/gallery/ticks_and_spines/multiple_yaxis_with_spines.html

