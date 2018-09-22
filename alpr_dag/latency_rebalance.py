from __future__ import division
import numpy as np

edge_entrytopic_entry_file = "Rebalance/4/logs_edge/exp_0.log"
edge_exittopic_entry_file = "Rebalance/4/logs_edge/exp_1.log"
edge_exit_file = "Rebalance/4/logs_edge/exp_6.log"

fog_entrytopic_entry_file = "Rebalance/4/logs_fog/exp_0.log"
fog_exittopic_entry_file = "Rebalance/4/logs_fog/exp_1.log"
fog_exit_file = "Rebalance/4/logs_fog/exp_6.log"

output_file_entry = open("Rebalance/4/time_taken_entry.csv", "w")
output_file_exit = open("Rebalance/4/time_taken_exit.csv", "w")

effective_input_rate_entry = open("Rebalance/4/effective_input_rate_entry.txt", "w")
effective_input_count_entry = open("Rebalance/4/effective_input_count_entry.txt", "w")
effective_op_rate_entry = open("Rebalance/4/effective_output_rate_entry.txt", "w")
effective_op_count_entry = open("Rebalance/4/effective_output_count_entry.txt", "w")
median_latency_entry = open("Rebalance/4/median_latency_entry.txt", "w")

effective_input_rate_exit = open("Rebalance/4/effective_input_rate_exit.txt", "w")
effective_input_count_exit = open("Rebalance/4/effective_input_count_exit.txt", "w")
effective_op_rate_exit = open("Rebalance/4/effective_output_rate_exit.txt", "w")
effective_op_count_exit = open("Rebalance/4/effective_output_count_exit.txt", "w")
median_latency_exit = open("Rebalance/4/median_latency_exit.txt", "w")

#this contains the entry time in first processor followed by the time
#between its production and consumption
consumption_time = open("Rebalance/4/consumption_time.txt", "w")

produce_time_entry = "Rebalance/4/produce_time_entry.log"
produce_time_exit = "Rebalance/4/produce_time_exit.log"
consume_time_edge_entry = "Rebalance/4/logs_edge/consume_time_entry.log"
consume_time_edge_exit = "Rebalance/4/logs_edge/consume_time_exit.log"
consume_time_fog_entry = "Rebalance/4/logs_fog/consume_time_entry.log"
consume_time_fog_exit = "Rebalance/4/logs_fog/consume_time_exit.log"

#we need to count the average number of output messages after every 30 messages
#so will be using the producer log along with message tracker log at Kafka
message_tracker = "Rebalance/4/message_tracker.log"
producer_entry_list = []
producer_exit_list = []
output_message_per_window_entry = open("Rebalance/4/output_message_per_window_entry.txt", "w")
output_message_per_window_exit = open("Rebalance/4/output_message_per_window_exit.txt", "w")
output_msg_entry_dict = dict()
output_msg_exit_dict = dict()
consumer_key_to_msgid_entry = dict()
consumer_key_to_msgid_exit = dict()
msg_loss_entry = open("Rebalance/4/msg_loss_entry.txt", "w")
msg_loss_exit = open("Rebalance/4/msg_loss_exit.txt", "w")
output_present_edge_entry_dict_1 = dict()
output_present_edge_exit_dict_1 = dict()
output_present_edge_entry_dict_2 = dict()
output_present_edge_exit_dict_2 = dict()
output_present_fog_entry_dict = dict()
output_present_fog_exit_dict = dict()


#two dictionaries for edge
#Since rebalance places the KafkaConsumer on Fog and then
#Hybrid config places back it on the Edge, we need to maintain
# 2 dict for each entry and exit topic for Edge
#Fog can work with single one
edge_entrytopic_dict_1 = dict()
edge_exittopic_dict_1 = dict()
edge_entrytopic_dict_2 = dict()
edge_exittopic_dict_2 = dict()

fog_entrytopic_dict = dict()
fog_exittopic_dict = dict()

#produce_dict contains mapping of key in Kafka to the time of ACK in Kafka(essentially produce time at broker)
produce_dict_entry = dict()
produce_dict_exit = dict()
#both consume_dict below contains the mapping of flowfile_id to the key in Kafka which will be later
#correlated using the produce_dict
consume_dict_edge_entry_1 = dict()
consume_dict_edge_exit_1 = dict()
consume_dict_edge_entry_2 = dict()
consume_dict_edge_exit_2 = dict()
consume_dict_fog_entry = dict()
consume_dict_fog_exit = dict()

#For calculating median latency for a window of 1 minute
#this is the start time for a window
median_start_time_entry = 0
median_start_time_exit = 0
#the list of latency entries in a window
list_median_latency_entry = []
list_median_latency_exit = []


##################################################################
################ MESSAGE TRACKING AND OUTPUT MESSAGES#############
reverse_consumer_edge_entry_dict_1 = dict()
reverse_consumer_edge_exit_dict_1 = dict()
reverse_consumer_edge_entry_dict_2 = dict()
reverse_consumer_edge_exit_dict_2 = dict()

with open(produce_time_entry,"r") as entry:
	for line in entry:
		splits = line.split(",")
		kafka_key = splits[0]
		producer_entry_list.append(kafka_key)

with open(produce_time_exit,"r") as entry:
	for line in entry:
		splits = line.split(",")
		kafka_key = splits[0]
		producer_exit_list.append(kafka_key)

with open(consume_time_edge_entry,"r") as entry:
	for line in entry:
		splits = line.split(",")
		flowfile_id = splits[0]
		kafka_key = splits[1].strip()
		rate = int(kafka_key.split("-")[0])
		if rate <= 9:
			reverse_consumer_edge_entry_dict_1[kafka_key] = flowfile_id
		else:
			reverse_consumer_edge_entry_dict_2[kafka_key] = flowfile_id
		consumer_key_to_msgid_entry[kafka_key] = flowfile_id

with open(consume_time_fog_entry,"r") as entry:
	for line in entry:
		splits = line.split(",")
		flowfile_id = splits[0]
		kafka_key = splits[1].strip()
		consumer_key_to_msgid_entry[kafka_key] = flowfile_id

with open(consume_time_edge_exit,"r") as entry:
	for line in entry:
		splits = line.split(",")
		flowfile_id = splits[0]
		kafka_key = splits[1].strip()
		rate = int(kafka_key.split("-")[0])
		if rate <= 9:
			reverse_consumer_edge_exit_dict_1[kafka_key] = flowfile_id
		else:
			reverse_consumer_edge_exit_dict_2[kafka_key] = flowfile_id
		consumer_key_to_msgid_exit[kafka_key] = flowfile_id

with open(consume_time_fog_exit,"r") as entry:
	for line in entry:
		splits = line.split(",")
		flowfile_id = splits[0]
		kafka_key = splits[1].strip()
		consumer_key_to_msgid_exit[kafka_key] = flowfile_id

id_last = 0
doneSwap = False
thresholdForSwap = 10
with open(edge_exit_file,"r") as entry:
	for line in entry:
		splits = line.split(",")
		flowfile_id = splits[0]
		type = splits[3].strip()
		if doneSwap:
			if type == 'entry_LICENSE' or type == 'entry_COLOR':
				output_present_edge_entry_dict_2[flowfile_id] = 1
			elif type == 'exit_LICENSE' or type == 'exit_COLOR':
				output_present_edge_exit_dict_2[flowfile_id] = 1
		else:
			if int(flowfile_id) >= id_last:
				if type == 'entry_LICENSE' or type == 'entry_COLOR':
					output_present_edge_entry_dict_1[flowfile_id] = 1
				elif type == 'exit_LICENSE' or type == 'exit_COLOR':
					output_present_edge_exit_dict_1[flowfile_id] = 1
				id_last = int(flowfile_id)
			elif abs(id_last - int(flowfile_id)) < thresholdForSwap:
				if type == 'entry_LICENSE' or type == 'entry_COLOR':
					output_present_edge_entry_dict_1[flowfile_id] = 1
				elif type == 'exit_LICENSE' or type == 'exit_COLOR':
					output_present_edge_exit_dict_1[flowfile_id] = 1
			else:
				doneSwap = True
				if type == 'entry_LICENSE' or type == 'entry_COLOR':
					output_present_edge_entry_dict_2[flowfile_id] = 1
				elif type == 'exit_LICENSE' or type == 'exit_COLOR':
					output_present_edge_exit_dict_2[flowfile_id] = 1


with open(fog_exit_file,"r") as entry:
	for line in entry:
		splits = line.split(",")
		flowfile_id = splits[0]
		type = splits[3].strip()
		if type == 'entry_LICENSE' or type == 'entry_COLOR':
			output_present_fog_entry_dict[flowfile_id] = 1
		elif type == 'exit_LICENSE' or type == 'exit_COLOR':
			output_present_fog_exit_dict[flowfile_id] = 1

			
		
idx = 0
#60 as in message tracker logging, one for entry then one for exit
# and we are doing for 30 message window
output_message_window_list_entry = []
output_message_window_list_exit = []
window_size = 60
running_count_entry = 0
running_count_exit = 0
start_entry = ''
last_entry = ''
start_exit = ''
last_exit = ''
with open(message_tracker,"r") as entry:
	for line in entry:
		img_name = line.strip()
		if 'parking_lot' not in img_name:
			if idx%2 == 0:
				kafka_key = producer_entry_list[idx//2]
				if idx%window_size == 0:
					start_entry = kafka_key
				last_entry = kafka_key
				running_count_entry += 1
				output_msg_entry_dict[kafka_key] = 1
			else:
				kafka_key = producer_exit_list[idx//2]
				if idx%window_size == 1:
					start_exit = kafka_key
				last_exit = kafka_key
				running_count_exit += 1
				output_msg_exit_dict[kafka_key] = 1
		else:
			if idx%2 == 0:
				kafka_key = producer_entry_list[idx//2]
				if idx%window_size == 0:
					start_entry = kafka_key
				last_entry = kafka_key
				output_msg_entry_dict[kafka_key] = 1
			else:
				kafka_key = producer_exit_list[idx//2]
				if idx%window_size == 1:
					start_exit = kafka_key
				last_exit = kafka_key
				output_msg_exit_dict[kafka_key] = 1	
		idx += 1
		if idx%window_size == 0:
			output_message_window_list_entry.append((running_count_entry,start_entry,last_entry))
			output_message_window_list_exit.append((running_count_exit,start_exit,last_exit))
			running_count_entry = 0
			running_count_exit = 0
			



##################################################################



##################################################################
############ PRODUCE AND CONSUME DICT FILLING PART ###############
##################################################################

with open(produce_time_entry,"r") as entry:
	for line in entry:
		splits = line.split(",")
		key_val = splits[0]
		ack_time = splits[1].strip()
		produce_dict_entry[key_val] = ack_time

with open(produce_time_exit,"r") as entry:
	for line in entry:
		splits = line.split(",")
		key_val = splits[0]
		ack_time = splits[1].strip()
		produce_dict_exit[key_val] = ack_time


with open(consume_time_edge_entry,"r") as entry:
	for line in entry:
		splits = line.split(",")
		flowfile_id = splits[0]
		record_key = splits[1].strip()
		rate = int(record_key.split("-")[0])
		if rate <= 9:
			consume_dict_edge_entry_1[flowfile_id] = record_key
		else:
			consume_dict_edge_entry_2[flowfile_id] = record_key

with open(consume_time_edge_exit,"r") as entry:
	for line in entry:
		splits = line.split(",")
		flowfile_id = splits[0]
		record_key = splits[1].strip()
		rate = int(record_key.split("-")[0])
		if rate <= 9:
			consume_dict_edge_exit_1[flowfile_id] = record_key
		else:
			consume_dict_edge_exit_2[flowfile_id] = record_key

with open(consume_time_fog_entry,"r") as entry:
        for line in entry:
                splits = line.split(",")
                flowfile_id = splits[0]
                record_key = splits[1].strip()
                consume_dict_fog_entry[flowfile_id] = record_key

with open(consume_time_fog_exit,"r") as entry:
        for line in entry:
                splits = line.split(",")
                flowfile_id = splits[0]
                record_key = splits[1].strip()
                consume_dict_fog_exit[flowfile_id] = record_key  

##################################################################


#not mandatory for entries in the processor to be perfectly ordered by id
#however subsequent entries won't differ by much , so a threshold can be applied
diff_threshold = 5

#effective input rate must be calculated lets say for a boundary of 10 sec
#note the starting point and use that till next 10 sec to keep a count of entries
#note the last point for that 10 sec duration and plot this duration against 
#number of entries seen in this duration
running_count_entry = 0
running_start_entry = 0
running_end_entry = 0

running_count_exit = 0
running_start_exit = 0
running_end_exit = 0

#a similar setup for effective output rate
running_op_count_entry = 0
running_op_start_entry = 0
running_op_end_entry = 0

running_op_count_exit = 0
running_op_start_exit = 0
running_op_end_exit = 0

#time limit we consider for effective input rate
time_limit = 60000

def updateForEffectiveInputRateEntry(current_ts, rate_file, count_file):
	global running_count_entry
	global running_start_entry
	global running_end_entry
	if running_count_entry == 0:
		running_start_entry = current_ts
		running_end_entry = current_ts
		running_count_entry = 1
	else:
		if current_ts - running_start_entry >= time_limit:
			#write the start,end,number of entries to the file
			if running_count_entry > 1:
				rate_effective = (running_count_entry * 1000 * 60)/(running_end_entry - running_start_entry)
				rate_file.write(str(running_start_entry) + "," + str(running_end_entry) + "," + str(rate_effective))
				rate_file.write("\n")
				count_file.write(str(running_start_entry) + "," + str(running_end_entry) + "," + str(running_count_entry))
				count_file.write("\n")
			running_start_entry = current_ts
			running_end_entry = current_ts
			running_count_entry = 1
		else:
			running_end_entry = current_ts
			running_count_entry += 1

def updateForEffectiveInputRateExit(current_ts, rate_file, count_file):
	global running_count_exit
	global running_start_exit
	global running_end_exit
	if running_count_exit == 0:
		running_start_exit = current_ts
		running_end_exit = current_ts
		running_count_exit = 1
	else:
		if current_ts - running_start_exit >= time_limit:
			#write the start,end,number of entries to the file
			if running_count_exit > 1:
				rate_effective = (running_count_exit * 1000 * 60)/(running_end_exit - running_start_exit)
				rate_file.write(str(running_start_exit) + "," + str(running_end_exit) + "," + str(rate_effective))
				rate_file.write("\n")
				count_file.write(str(running_start_exit) + "," + str(running_end_exit) + "," + str(running_count_exit))
				count_file.write("\n")
			running_start_exit = current_ts
			running_end_exit = current_ts
			running_count_exit = 1
		else:
			running_end_exit = current_ts
			running_count_exit += 1



def updateForEffectiveOutputRateEntry(current_ts, msg_id, entry_dict, rate_file, count_file, median_file):
        global running_op_count_entry
        global running_op_start_entry
        global running_op_end_entry
	global median_start_time_entry
	global list_median_latency_entry
        if running_op_count_entry == 0:
                running_op_start_entry = current_ts
                running_op_end_entry = current_ts
                running_op_count_entry = 1
		median_start_time_entry = current_ts
		list_median_latency_entry = []
        else:
                if current_ts - running_op_start_entry >= time_limit:
                        #write the start,end,number of entries to the file
                        if running_op_count_entry > 1:
                                rate_effective = (running_op_count_entry * 1000 * 60)/(running_op_end_entry - running_op_start_entry)
                                rate_file.write(str(running_op_start_entry) + "," + str(running_op_end_entry) + "," + str(rate_effective))
                                rate_file.write("\n")
				count_file.write(str(running_op_start_entry) + "," + str(running_op_end_entry) + "," + str(running_op_count_entry))
                                count_file.write("\n")
				window_median_latency = np.median(list_median_latency_entry)
				median_file.write(str(median_start_time_entry) + "," + str(window_median_latency))
				median_file.write("\n")

                        running_op_start_entry = current_ts
                        running_op_end_entry = current_ts
                        running_op_count_entry = 1
			median_start_time_entry = current_ts
			list_median_latency_entry = []
                else:
                        running_op_end_entry = current_ts
                        running_op_count_entry += 1

	current_latency = current_ts - int(entry_dict[msg_id])
	list_median_latency_entry.append(current_latency)

def updateForEffectiveOutputRateExit(current_ts, msg_id, entry_dict, rate_file, count_file, median_file):
        global running_op_count_exit
        global running_op_start_exit
        global running_op_end_exit
	global median_start_time_exit
	global list_median_latency_exit
        if running_op_count_exit == 0:
                running_op_start_exit = current_ts
                running_op_end_exit = current_ts
                running_op_count_exit = 1
		median_start_time_exit = current_ts
		list_median_latency_exit = []
        else:
                if current_ts - running_op_start_exit >= time_limit:
                        #write the start,end,number of entries to the file
                        if running_op_count_exit > 1:
                                rate_effective = (running_op_count_exit * 1000 * 60)/(running_op_end_exit - running_op_start_exit)
                                rate_file.write(str(running_op_start_exit) + "," + str(running_op_end_exit) + "," + str(rate_effective))
                                rate_file.write("\n")
				count_file.write(str(running_op_start_exit) + "," + str(running_op_end_exit) + "," + str(running_op_count_exit))
                                count_file.write("\n")
				window_median_latency = np.median(list_median_latency_exit)
				median_file.write(str(median_start_time_exit) + "," + str(window_median_latency))
				median_file.write("\n")

                        running_op_start_exit = current_ts
                        running_op_end_exit = current_ts
                        running_op_count_exit = 1
			median_start_time_exit = current_ts
			list_median_latency_exit = []
                else:
                        running_op_end_exit = current_ts
                        running_op_count_exit += 1

	current_latency = current_ts - int(entry_dict[msg_id])
	list_median_latency_exit.append(current_latency)



##########################################################
################# KAFKA ENTRY TOPIC AT EDGE ##############
##########################################################
swapDone = False
id_last = 0
with open(edge_entrytopic_entry_file, 'r') as entry:
	for line in entry:
		splits = line.split(",")
		type = splits[3].strip()
		id = splits[0]
                if type == "ENTRY":
			if swapDone:
				edge_entrytopic_dict_2[id] = splits[2]
				updateForEffectiveInputRateEntry(int(splits[2]), effective_input_rate_entry, effective_input_count_entry)
			else:
				if int(id) > int(id_last):
					edge_entrytopic_dict_1[id] = splits[2]
					id_last = int(id)
					updateForEffectiveInputRateEntry(int(splits[2]), effective_input_rate_entry, effective_input_count_entry)
				else:
					if abs(int(id_last) - int(id)) < diff_threshold:
						edge_entrytopic_dict_1[id] = splits[2]
						updateForEffectiveInputRateEntry(int(splits[2]), effective_input_rate_entry, effective_input_count_entry)
					else:
						if running_count_entry > 1:
							rate_effective = (running_count_entry * 1000 * 60)/(running_end_entry - running_start_entry)
							effective_input_rate_entry.write(str(running_start_entry) + "," + str(running_end_entry) + "," + str(rate_effective))
							effective_input_rate_entry.write("\n")
							effective_input_count_entry.write(str(running_start_entry) + "," + str(running_end_entry) + "," + str(running_count_entry))
							effective_input_count_entry.write("\n")
						running_start_entry = int(splits[2])
						running_end_entry = int(splits[2])
						running_count_entry = 1
						swapDone = True
						edge_entrytopic_dict_2[id] = splits[2]


if running_count_entry > 1:
	rate_effective = (running_count_entry * 1000 * 60)/(running_end_entry - running_start_entry)
	effective_input_rate_entry.write(str(running_start_entry) + "," + str(running_end_entry) + "," + str(rate_effective))
	effective_input_rate_entry.write("\n")
	effective_input_count_entry.write(str(running_start_entry) + "," + str(running_end_entry) + "," + str(running_count_entry))
	effective_input_count_entry.write("\n")

running_count_entry = 0
running_start_entry = 0
running_end_entry = 0


##########################################################
################# KAFKA EXIT TOPIC AT EDGE ############### 
##########################################################
swapDone = False
id_last = 0
with open(edge_exittopic_entry_file, 'r') as entry:
	for line in entry:
		splits = line.split(",")
		type = splits[3].strip()
		id = splits[0]
                if type == "ENTRY":
			if swapDone:
				edge_exittopic_dict_2[id] = splits[2]
				updateForEffectiveInputRateExit(int(splits[2]), effective_input_rate_exit, effective_input_count_exit)
			else:
				if int(id) > int(id_last):
					edge_exittopic_dict_1[id] = splits[2]
					id_last = int(id)
					updateForEffectiveInputRateExit(int(splits[2]), effective_input_rate_exit, effective_input_count_exit)
				else:
					if abs(int(id_last) - int(id)) < diff_threshold:
						edge_exittopic_dict_1[id] = splits[2]
						updateForEffectiveInputRateExit(int(splits[2]), effective_input_rate_exit, effective_input_count_exit)
					else:
						if running_count_exit > 1:
							rate_effective = (running_count_exit * 1000 * 60)/(running_end_exit - running_start_exit)
							effective_input_rate_exit.write(str(running_start_exit) + "," + str(running_end_exit) + "," + str(rate_effective))
							effective_input_rate_exit.write("\n")
							effective_input_count_exit.write(str(running_start_exit) + "," + str(running_end_exit) + "," + str(running_count_exit))
							effective_input_count_exit.write("\n")
						running_start_exit = int(splits[2])
						running_end_exit = int(splits[2])
						running_count_exit = 1
						swapDone = True
						edge_exittopic_dict_2[id] = splits[2]


if running_count_exit > 1:
	rate_effective = (running_count_exit * 1000 * 60)/(running_end_exit - running_start_exit)
	effective_input_rate_exit.write(str(running_start_exit) + "," + str(running_end_exit) + "," + str(rate_effective))
	effective_input_rate_exit.write("\n")
	effective_input_count_exit.write(str(running_start_exit) + "," + str(running_end_exit) + "," + str(running_count_exit))
	effective_input_count_exit.write("\n")

running_count_exit = 0
running_start_exit = 0
running_end_exit = 0


##########################################################
################# exit point in the pipeline #############
##########################################################
swapDone_entry = False
id_last_entry = 0
swapDone_exit = False
id_last_exit = 0
with open(edge_exit_file,'r') as entry:
	for line in entry:
		splits = line.split(",")
                type = splits[3].strip()
                id = splits[0]
		current_ts = int(splits[2])
                if type == "entry_EXIT":
			if swapDone_entry:
				output_file_entry.write(edge_entrytopic_dict_2[id] + "," + splits[2])
				updateForEffectiveOutputRateEntry(int(splits[2]), id, edge_entrytopic_dict_2, effective_op_rate_entry, effective_op_count_entry, median_latency_entry)
			else:
				if int(id) > int(id_last_entry):
					output_file_entry.write(edge_entrytopic_dict_1[id] + "," + splits[2])
					updateForEffectiveOutputRateEntry(int(splits[2]), id, edge_entrytopic_dict_1, effective_op_rate_entry, effective_op_count_entry, median_latency_entry)
					id_last_entry = int(id)
				else:
					if abs(int(id_last_entry) - int(id)) < diff_threshold:
						output_file_entry.write(edge_entrytopic_dict_1[id] + "," + splits[2])
						updateForEffectiveOutputRateEntry(int(splits[2]), id, edge_entrytopic_dict_1, effective_op_rate_entry, effective_op_count_entry, median_latency_entry)
					else:
						if running_op_count_entry > 1:
							rate_effective = (running_op_count_entry * 1000 * 60)/(running_op_end_entry - running_op_start_entry)
							effective_op_rate_entry.write(str(running_op_start_entry) + "," + str(running_op_end_entry) + "," + str(rate_effective))
							effective_op_rate_entry.write("\n")
							effective_op_count_entry.write(str(running_op_start_entry) + "," + str(running_op_end_entry) + "," + str(running_op_count_entry))
							effective_op_count_entry.write("\n")
							window_median_latency = np.median(list_median_latency_entry)
							median_latency_entry.write(str(median_start_time_entry) + "," + str(window_median_latency))
							median_latency_entry.write("\n")
						running_op_start_entry = current_ts
						running_op_end_entry = current_ts
						running_op_count_entry = 1
						median_start_time_entry = current_ts
						list_median_latency_entry = []
						current_latency = current_ts - int(edge_entrytopic_dict_2[id])
						list_median_latency_entry.append(current_latency)
						swapDone_entry = True
						output_file_entry.write(edge_entrytopic_dict_2[id] + "," + splits[2])
			output_file_entry.write("\n")
		elif type == "exit_EXIT":
			if swapDone_exit:
				output_file_exit.write(edge_exittopic_dict_2[id] + "," + splits[2])
				updateForEffectiveOutputRateExit(int(splits[2]), id, edge_exittopic_dict_2, effective_op_rate_exit, effective_op_count_exit, median_latency_exit)
			else:
				if int(id) > int(id_last_exit):
					output_file_exit.write(edge_exittopic_dict_1[id] + "," + splits[2])
					updateForEffectiveOutputRateExit(int(splits[2]), id, edge_exittopic_dict_1, effective_op_rate_exit, effective_op_count_exit, median_latency_exit)
					id_last_exit = int(id)
				else:
					if abs(int(id_last_exit) - int(id)) < diff_threshold:
						output_file_exit.write(edge_exittopic_dict_1[id] + "," + splits[2])
						updateForEffectiveOutputRateExit(int(splits[2]), id, edge_exittopic_dict_1, effective_op_rate_exit, effective_op_count_exit, median_latency_exit)
					else:
						if running_op_count_exit > 1:
							rate_effective = (running_op_count_exit * 1000 * 60)/(running_op_end_exit - running_op_start_exit)
							effective_op_rate_exit.write(str(running_op_start_exit) + "," + str(running_op_end_exit) + "," + str(rate_effective))
							effective_op_rate_exit.write("\n")
							effective_op_count_exit.write(str(running_op_start_exit) + "," + str(running_op_end_exit) + "," + str(running_op_count_exit))
							effective_op_count_exit.write("\n")
							window_median_latency = np.median(list_median_latency_exit)
							median_latency_exit.write(str(median_start_time_exit) + "," + str(window_median_latency))
							median_latency_exit.write("\n")
						running_op_start_exit = current_ts
						running_op_end_exit = current_ts
						running_op_count_exit = 1
						median_start_time_exit = current_ts
						list_median_latency_exit = []
						current_latency = current_ts - int(edge_exittopic_dict_2[id])
						list_median_latency_exit.append(current_latency)
						swapDone_exit = True
						output_file_exit.write(edge_exittopic_dict_2[id] + "," + splits[2])
			output_file_exit.write("\n")


if running_op_count_entry > 1:
        rate_effective = (running_op_count_entry * 1000 * 60)/(running_op_end_entry - running_op_start_entry)
        effective_op_rate_entry.write(str(running_op_start_entry) + "," + str(running_op_end_entry) + "," + str(rate_effective))
        effective_op_rate_entry.write("\n")
	effective_op_count_entry.write(str(running_op_start_entry) + "," + str(running_op_end_entry) + "," + str(running_op_count_entry))
        effective_op_count_entry.write("\n")
	window_median_latency = np.median(list_median_latency_entry)
	median_latency_entry.write(str(median_start_time_entry) + "," + str(window_median_latency))
	median_latency_entry.write("\n")

if running_op_count_exit > 1:
        rate_effective = (running_op_count_exit * 1000 * 60)/(running_op_end_exit - running_op_start_exit)
        effective_op_rate_exit.write(str(running_op_start_exit) + "," + str(running_op_end_exit) + "," + str(rate_effective))
        effective_op_rate_exit.write("\n")
	effective_op_count_exit.write(str(running_op_start_exit) + "," + str(running_op_end_exit) + "," + str(running_op_count_exit))
        effective_op_count_exit.write("\n")
	window_median_latency = np.median(list_median_latency_exit)
	median_latency_exit.write(str(median_start_time_exit) + "," + str(window_median_latency))
	median_latency_exit.write("\n")

running_op_count_entry = 0
running_op_start_entry = 0
running_op_end_entry = 0

running_op_count_exit = 0
running_op_start_exit = 0
running_op_end_exit = 0

#####################################################
############## KAFKA ENTRY TOPIC ####################
#####################################################
with open(fog_entrytopic_entry_file,'r') as entry:
	for line in entry:
		splits = line.split(",")
                type = splits[3].strip()
                id = splits[0]
                if type == "ENTRY":
			fog_entrytopic_dict[id] = splits[2]
			updateForEffectiveInputRateEntry(int(splits[2]), effective_input_rate_entry, effective_input_count_entry)


if running_count_entry > 1:
	rate_effective = (running_count_entry * 1000 * 60)/(running_end_entry - running_start_entry)
	effective_input_rate_entry.write(str(running_start_entry) + "," + str(running_end_entry) + "," + str(rate_effective))
	effective_input_rate_entry.write("\n")
	effective_input_count_entry.write(str(running_start_entry) + "," + str(running_end_entry) + "," + str(running_count_entry))
	effective_input_count_entry.write("\n")

running_count_entry = 0
running_start_entry = 0
running_end_entry = 0

#####################################################
############## KAFKA EXIT TOPIC #####################
#####################################################
with open(fog_exittopic_entry_file,'r') as entry:
	for line in entry:
		splits = line.split(",")
                type = splits[3].strip()
                id = splits[0]
                if type == "ENTRY":
			fog_exittopic_dict[id] = splits[2]
			updateForEffectiveInputRateExit(int(splits[2]), effective_input_rate_exit, effective_input_count_exit)


if running_count_exit > 1:
	rate_effective = (running_count_exit * 1000 * 60)/(running_end_exit - running_start_exit)
	effective_input_rate_exit.write(str(running_start_exit) + "," + str(running_end_exit) + "," + str(rate_effective))
	effective_input_rate_exit.write("\n")
	effective_input_count_exit.write(str(running_start_exit) + "," + str(running_end_exit) + "," + str(running_count_exit))
	effective_input_count_exit.write("\n")

running_count_exit = 0
running_start_exit = 0
running_end_exit = 0
			

#####################################################
############## exit point in the pipeline ###########
#####################################################
with open(fog_exit_file,'r') as entry:
	for line in entry:
        	splits = line.split(",")
              	type = splits[3].strip()
                id = splits[0]
                if type == "entry_EXIT":
                        output_file_entry.write(fog_entrytopic_dict[id] + "," + splits[2])
			output_file_entry.write("\n")
			updateForEffectiveOutputRateEntry(int(splits[2]), id, fog_entrytopic_dict, effective_op_rate_entry, effective_op_count_entry, median_latency_entry)
		elif type == "exit_EXIT":
                        output_file_exit.write(fog_exittopic_dict[id] + "," + splits[2])
			output_file_exit.write("\n")
			updateForEffectiveOutputRateExit(int(splits[2]), id, fog_exittopic_dict, effective_op_rate_exit, effective_op_count_exit, median_latency_exit)


if running_op_count_entry > 1:
        rate_effective = (running_op_count_entry * 1000 * 60)/(running_op_end_entry - running_op_start_entry)
        effective_op_rate_entry.write(str(running_op_start_entry) + "," + str(running_op_end_entry) + "," + str(rate_effective))
        effective_op_rate_entry.write("\n")
	effective_op_count_entry.write(str(running_op_start_entry) + "," + str(running_op_end_entry) + "," + str(running_op_count_entry))
        effective_op_count_entry.write("\n")
	window_median_latency = np.median(list_median_latency_entry)
	median_latency_entry.write(str(median_start_time_entry) + "," + str(window_median_latency))
	median_latency_entry.write("\n")

if running_op_count_exit > 1:
        rate_effective = (running_op_count_exit * 1000 * 60)/(running_op_end_exit - running_op_start_exit)
        effective_op_rate_exit.write(str(running_op_start_exit) + "," + str(running_op_end_exit) + "," + str(rate_effective))
        effective_op_rate_exit.write("\n")
	effective_op_count_exit.write(str(running_op_start_exit) + "," + str(running_op_end_exit) + "," + str(running_op_count_exit))
        effective_op_count_exit.write("\n")
	window_median_latency = np.median(list_median_latency_exit)
	median_latency_exit.write(str(median_start_time_exit) + "," + str(window_median_latency))
	median_latency_exit.write("\n")

running_op_count_entry = 0
running_op_start_entry = 0
running_op_end_entry = 0

running_op_count_exit = 0
running_op_start_exit = 0
running_op_end_exit = 0



output_file_entry.close()
output_file_exit.close()

effective_input_rate_entry.close()
effective_op_rate_entry.close()
median_latency_entry.close()

effective_input_rate_exit.close()
effective_op_rate_exit.close()
median_latency_exit.close()

#now writing to consumption file to compare difference between
#production and consumption times

def writeDiffBtwProduceConsume(flowfile_entry_dict, consume_time_dict, produce_dict):
	for key in flowfile_entry_dict:
       		try:
			consume_time = flowfile_entry_dict[key]
		except KeyError:
			continue
		try:
        		record_key = consume_time_dict[key]
		except KeyError:
			continue
		try:
        		ack_time = produce_dict[record_key]
		except KeyError:
			continue
        	diff_time = int(consume_time) - int(ack_time)
        	consumption_time.write(consume_time + "," + str(diff_time))
        	consumption_time.write("\n")
	
writeDiffBtwProduceConsume(edge_entrytopic_dict_1, consume_dict_edge_entry_1, produce_dict_entry)
writeDiffBtwProduceConsume(edge_exittopic_dict_1, consume_dict_edge_exit_1, produce_dict_exit)
writeDiffBtwProduceConsume(edge_entrytopic_dict_2, consume_dict_edge_entry_2, produce_dict_entry)
writeDiffBtwProduceConsume(edge_exittopic_dict_2, consume_dict_edge_exit_2, produce_dict_exit)
writeDiffBtwProduceConsume(fog_entrytopic_dict, consume_dict_fog_entry, produce_dict_entry)
writeDiffBtwProduceConsume(fog_exittopic_dict, consume_dict_fog_exit, produce_dict_exit)

consumption_time.close()

#####################################################################
#################### CALCULATING MESSAGE LOSS #######################
#output_present_edge_entry_dict_1, output_present_edge_entry_dict_2,
#output_present_fog_entry_dict - these contain flowfile_id at the end
#match these with the consumed message i.e. consume_dict_edge_entry_1,
#consume_dict_edge_entry_2, consume_dict_fog_entry 
#####################################################################
def keepLossyMessage(output_dict, consume_dict):
	for key in output_dict:
		del consume_dict[key]
	print consume_dict

keepLossyMessage(output_present_edge_entry_dict_1, consume_dict_edge_entry_1)
keepLossyMessage(output_present_edge_exit_dict_1, consume_dict_edge_exit_1)
keepLossyMessage(output_present_edge_entry_dict_2, consume_dict_edge_entry_2)
keepLossyMessage(output_present_edge_exit_dict_2, consume_dict_edge_exit_2)
keepLossyMessage(output_present_fog_entry_dict, consume_dict_fog_entry)
keepLossyMessage(output_present_fog_exit_dict, consume_dict_fog_exit)

def writeLostMessageToFile(file_name, consume_dict):
	for key in consume_dict:
		file_name.write(key + "," + consume_dict[key])
		file_name.write("\n")

writeLostMessageToFile(msg_loss_entry, consume_dict_edge_entry_1)
writeLostMessageToFile(msg_loss_entry, consume_dict_edge_entry_2)
writeLostMessageToFile(msg_loss_entry, consume_dict_fog_entry)
writeLostMessageToFile(msg_loss_exit, consume_dict_edge_exit_1)
writeLostMessageToFile(msg_loss_exit, consume_dict_edge_exit_2)
writeLostMessageToFile(msg_loss_exit, consume_dict_fog_exit)

msg_loss_entry.close()
msg_loss_exit.close()

###################################################################
############### MESSAGE OUTPUT EVERY 30 INPUT MESSAGE #############
#output_message_window_list_entry, output_message_window_list_exit
#3-tuple each containing count and start kafka_key and end kafka_key
#look for these keys in the reverse consumer dicts (only for edge)
# reverse_consumer_edge_entry_dict_1 and _2 to find the actual
# consumer of the message if edge in phase 1 or phase 2 or the fog.
#  Once thats done, look for the flowfile_id from reverse dict
# consumer_key_to_msgid_entry and consumer_key_to_msgid_exit to find 
# the flowfile_id and then look at the entry time in the corresponding
# entry dict of the correct consumer
#from the flowfile_id, get the time when message was consumed from
# edge_entrytopic_dict_1, edge_entrytopic_dict_2, fog_entrytopic_dict
#write these to output_message_per_window_entry and 
# output_message_per_window_exit
###################################################################
for elem in output_message_window_list_entry:
	count = elem[0]
	start_key = elem[1]
	last_key = elem[2]
	start_msg_id = ''
	last_msg_id = ''
	start_ts = ''
	last_ts = ''
	if start_key in reverse_consumer_edge_entry_dict_1:
		start_msg_id = reverse_consumer_edge_entry_dict_1[start_key]
		start_ts = edge_entrytopic_dict_1[start_msg_id]
	elif start_key in reverse_consumer_edge_entry_dict_2:
		start_msg_id = reverse_consumer_edge_entry_dict_2[start_key]
		start_ts = edge_entrytopic_dict_2[start_msg_id]
	else:
		start_msg_id = consumer_key_to_msgid_entry[start_key]
		start_ts = fog_entrytopic_dict[start_msg_id]
	
	if last_key in reverse_consumer_edge_entry_dict_1:
		last_msg_id = reverse_consumer_edge_entry_dict_1[last_key]
		last_ts = edge_entrytopic_dict_1[last_msg_id]
	elif last_key in reverse_consumer_edge_entry_dict_2:
		last_msg_id = reverse_consumer_edge_entry_dict_2[last_key]
		last_ts = edge_entrytopic_dict_2[last_msg_id]
	else:
		last_msg_id = consumer_key_to_msgid_entry[last_key]
		last_ts = fog_entrytopic_dict[last_msg_id]
	
	output_message_per_window_entry.write(start_ts + "," + last_ts + "," + str(count))
	output_message_per_window_entry.write("\n")

output_message_per_window_entry.close()


for elem in output_message_window_list_exit:
	count = elem[0]
	start_key = elem[1]
	last_key = elem[2]
	start_msg_id = ''
	last_msg_id = ''
	start_ts = ''
	last_ts = ''
	if start_key in reverse_consumer_edge_exit_dict_1:
		start_msg_id = reverse_consumer_edge_exit_dict_1[start_key]
		start_ts = edge_exittopic_dict_1[start_msg_id]
	elif start_key in reverse_consumer_edge_exit_dict_2:
		start_msg_id = reverse_consumer_edge_exit_dict_2[start_key]
		start_ts = edge_exittopic_dict_2[start_msg_id]
	else:
		start_msg_id = consumer_key_to_msgid_exit[start_key]
		start_ts = fog_exittopic_dict[start_msg_id]
	
	if last_key in reverse_consumer_edge_exit_dict_1:
		last_msg_id = reverse_consumer_edge_exit_dict_1[last_key]
		last_ts = edge_exittopic_dict_1[last_msg_id]
	elif last_key in reverse_consumer_edge_exit_dict_2:
		last_msg_id = reverse_consumer_edge_exit_dict_2[last_key]
		last_ts = edge_exittopic_dict_2[last_msg_id]
	else:
		last_msg_id = consumer_key_to_msgid_exit[last_key]
		last_ts = fog_exittopic_dict[last_msg_id]
	
	output_message_per_window_exit.write(start_ts + "," + last_ts + "," + str(count))
	output_message_per_window_exit.write("\n")

output_message_per_window_exit.close()
