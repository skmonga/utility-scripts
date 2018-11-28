import time
import sys
import requests
import json

args = sys.argv[1:]
master_ip = args[0]
max_dag_count = int(args[1])
step_size = int(args[2])
dag_file = args[3]

#step_size = 2

deployed_dags = []
deployed_count = 0

submit_url = "http://" + master_ip + ":8099/DAG"
stop_url = "http://" + master_ip + ":8099/DAG/stop?uuid="
rebalance_url = "http://" + master_ip + ":8099/DAG/rebalance?uuid="

dag_json = ''
with open(dag_file) as f:
	dag_json = json.load(f)

#check to trigger (stop and rebalance) or not
check_stop_rebalance = False
stop_uuid = ''
rebalance_uuid = ''

while deployed_count < max_dag_count:
	dag_json_str = json.dumps(dag_json)
	dag_json_str = dag_json_str.replace("$random_uuid", str(deployed_count+1)).replace("$dataflow_id", str(deployed_count+1))
	#print dag_json_str
	req = requests.post(url = submit_url, data = dag_json_str)
	resp = req.json()
	dag_uuid = resp["uuid"]
	deployed_dags.append(dag_uuid)
	deployed_count += 1
	time.sleep(60)
	if deployed_count % step_size == 0:
		#time.sleep(5)
		stop_uuid = deployed_dags[0]
		del deployed_dags[0]
		rebalance_uuid = deployed_dags[0]
		check_stop_rebalance = True
	
	if check_stop_rebalance == True:
		req = requests.post(url = stop_url + stop_uuid)
		time.sleep(10)
		req = requests.post(url = rebalance_url + rebalance_uuid)
		check_stop_rebalance = False
		time.sleep(10)
	
	

