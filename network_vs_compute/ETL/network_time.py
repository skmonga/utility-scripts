import sys
import numpy as np

#This is for a model which involves Edge + either Fog or Cloud
arguments = sys.argv[1:]
dataset = 'CITY'
config = arguments[0]
rate = arguments[1]

edge_entry_file = dataset + "/" + config + "/rate" + rate + "/exp_0.log"
edge_exit_file = dataset + "/" + config + "/rate" + rate + "/exp_6.log"

cloud_entry_file = dataset + "/" + config + "/rate" + rate + "/exp_1.log"
cloud_exit_file = dataset + "/" + config + "/rate" + rate + "/exp_4.log"

makespan_network_latency = open(dataset + "/" + config + "/rate" + rate + "/makespan_network_latency.txt", "w")

edge_entry_time_dict = {}
cloud_entry_time_dict = {}

comp_edge_entry = {}
comp_edge_exit = {}
time_cloud = {}

makespan_dict = {}

with open(edge_entry_file, 'r') as entry:
	for line in entry:
		splits = line.split(",")
		type = splits[3].strip()
		id = splits[0]
		if type == "ENTRY":
			edge_entry_time_dict[id] = int(splits[2])
		else:
			comp_edge_entry[id] = int(splits[2]) - edge_entry_time_dict[id]


time_enter = {}
with open(edge_exit_file, 'r') as entry:
	for line in entry:
		splits = line.split(",")
		type = splits[3].strip()
		id = splits[0]
		if type == "ENTRY":
			time_enter[id] = int(splits[2])
		else:
			comp_edge_exit[id] = int(splits[2]) - time_enter[id]
			makespan_dict[id] = int(splits[2]) - edge_entry_time_dict[id]


with open(cloud_entry_file, 'r') as entry:
	for line in entry:
		splits = line.split(",")
		type = splits[3].strip()
		id = splits[0]
		if type == "ENTRY":
			cloud_entry_time_dict[id] = int(splits[2])


with open(cloud_exit_file, 'r') as entry:
	for line in entry:
		splits = line.split(",")
		type = splits[3].strip()
		id = splits[0]
		if type == "EXIT":
			time_cloud[id] = int(splits[2]) - cloud_entry_time_dict[id]

for key in makespan_dict:
	makespan  = makespan_dict[key]
	compute_edge_entry = comp_edge_entry[key]
	compute_edge_exit = comp_edge_exit[key]
	cloud_time = time_cloud[key]
	network_time = makespan - compute_edge_entry - compute_edge_exit - cloud_time
	makespan_network_latency.write(str(makespan) + "," + str(network_time) + "\n")

makespan_network_latency.close()


nw_latency_file = dataset + "/" + config + "/rate" + rate + "/makespan_network_latency.txt"
nw_perc = []
compute_time = []
with open(nw_latency_file) as entry:
	for line in entry:
		splits = line.split(",")
		makespan = float(splits[0])
		nw_time = float(splits[1].strip())
		compute_time.append(makespan - nw_time)
		nw_time_perc = (nw_time/makespan) * 100
		nw_perc.append(nw_time_perc)

median_compute = np.median(compute_time)
print "The median compute time is : " + str(median_compute) + "\n"

x = [nw_perc]

print str(np.percentile(x, [5], axis=1)) + "\n"
print str(np.percentile(x, [10], axis=1)) + "\n"
nw_error_file = open(dataset + "/" + config + "/rate" + rate + "/network_error.txt", "w")
nw_error_file.write("Minimum percentage time on network : " + str(min(nw_perc)) + "\n")
nw_error_file.write("Maximum percentage time on network : " + str(max(nw_perc)) + "\n")
nw_error_file.write("First Quartile time on network : " + str(np.percentile(x, [25], axis=1)) + "\n")
nw_error_file.write("Median Quartile time on network : " + str(np.percentile(x, [50], axis=1)) + "\n")
nw_error_file.write("Third Quartile time on network : " + str(np.percentile(x, [75], axis=1)) + "\n")


