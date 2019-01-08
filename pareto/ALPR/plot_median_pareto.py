import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import sys
import numpy as np

arguments = sys.argv[1:]
is_log_scale = arguments[0]

dataset = 'ALPR'

median_dict = {}
#median_dict['Edge'] = [[1,2,5,6,8,10] , [7650,7313,7361,7645,35180,72803] , 'b']
#median_dict['Fog_Edge'] = [[1,5,10,15,16,18,20,25,30] , [4064,3991,3918,3945,3974,4192,8397,93100,114463] , 'g']
#median_dict['Fog'] = [[1,5,10,15,16,18,20,25,30] , [3816,3773,3851,3809,3801,3799,6180,64887,61657] , 'black']
#median_dict['Hybrid_CC_FF'] = [[1,5,10,15,16,18,20,25,30,35] , [6462,3940,4148,3969,4038,4106,6362,11062,10670,10765] , 'r']
#median_dict['Hybrid_CF_CF'] = [[5,10,15,16,18,20,25] , [5652,5815,6235,6485,6574,8300,67725] , 'c']
#median_dict['Hybrid_FC_FC'] = [[5,10,15,16,18,20,25,30,35,40,45] , [7061,6486,6716,6734,5940,7242,6975,8349,9576,47302,77382] , 'm']
#median_dict['Cloud'] = [[1,5,10,15,20,25,30,35,40,45,60] , [9791,9045,7578,8055,6734,7240,8242,9089,7751,8749,15049] , 'y']

median_dict['E*'] = [[1,2,5,6,8] , [7650,7313,7361,7645,35180] , 'b', 'o']
median_dict['EF'] = [[1,5,10,15,16,18,20,25] , [4064,3991,3918,3945,3974,4192,8397,93100], 'r', '^']
median_dict['F*'] = [[1,5,10,15,16,18,20,25] , [3816,3773,3851,3809,3801,3799,6180,64887], 'g', 's']
median_dict['FCFC'] = [[5,10,15,16,18,20,25,30,35,40] , [7061,6486,6716,6734,5940,7242,6975,8349,9576,47302] , 'm', 'D']
median_dict['CFCF'] = [[5,10,15,16,18,20,25] , [5652,5815,6235,6485,6574,8300,67725] , 'c', 'v']
#median_dict['CFCF'] = [[5,10,15,16,18,20,25] , [5652,5815,6235,6485,6574,8300,67725] , 'c', '*']
median_dict['CCFF'] = [[1,5,10,15,16,18,20,25,30] , [6462,3940,4148,3969,4038,4106,6362,11062,10670] , 'k' , 'x']
median_dict['C*'] = [[1,5,10,15,20,25,30,35,40,45,60] , [9791,9045,7578,8055,6734,7240,8242,9089,7751,8749,15049] , 'y', "+"]
#median_dict['C*'] = [[1,5,10,15,20,25,30,35,40,45,60] , [9791,9045,7578,8055,6734,7240,8242,9089,7751,8749,15049] , 'y', "p"]

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)

#using log scale on latency axis
if is_log_scale == 'True':
	ax.set_yscale('log')

median_dict_keys = ['E*', 'EF', 'F*', 'FCFC', 'CFCF', 'CCFF', 'C*']
annotate_dict = {}
annotate_dict['E*'] = (3,7340)
#annotate_dict['EF'] = (150,1285)
annotate_dict['F*'] = (9, 3851)
annotate_dict['CCFF'] = (18,4106)
annotate_dict['FCFC'] = (24,6975)
annotate_dict['C*'] = (36,9089)


#for key in median_dict:
#	value = median_dict[key]
#	ax.scatter(value[0], value[1], label = key, color = value[2], marker="o", linewidths=0.1, edgecolors='none')

#for key in median_dict_keys:
#	if key not in annotate_dict:
#		continue
#	value = median_dict[key]
#	input_rate_list = value[0]
#	latency_list = value[1]
	#i = 0
	#for rate in input_rate_list:
		#ax.text(effective_rate_list[i],latency_list[i], str(supplied_rate_list[i]),transform=ax.transAxes)
#	ax.annotate(str(annotate_dict[key][0]), (annotate_dict[key][0],annotate_dict[key][1]), color='black',fontsize=20)
	#i += 1

for key in median_dict_keys:
	value = median_dict[key]
	if key is 'CCFF':
		#ax.scatter(value[0], value[1], label = key, c='tab:brown', marker=value[3], linewidths=1, edgecolors='tab:brown', facecolors='none', s=100)
		ax.scatter(value[0], value[1], label = key, c='tab:brown', marker=value[3], linewidths=1, edgecolors='tab:brown', facecolors='none', s=200)
	elif key is 'C*':
		#ax.scatter(value[0], value[1], label = key, c='orange', marker=value[3], linewidths=1, edgecolors='orange', facecolors='none', s=100)
		ax.scatter(value[0], value[1], label = key, c='orange', marker=value[3], linewidths=1, edgecolors='orange', facecolors='none', s=200)
	else:
		#ax.scatter(value[0], value[1], label = key, color = None, marker=value[3], linewidths=1, edgecolors=value[2], facecolors='none', s=100)
		ax.scatter(value[0], value[1], label = key, color = None, marker=value[3], linewidths=1, edgecolors=value[2], facecolors='none', s=200)

plt.xlabel('Input Rate (events/min)', fontsize=25)
plt.ylabel('Median Latency (ms) [Log]', fontsize=25)
#plt.title('Median rates for ALPR',fontsize=24)
plt.grid()

#minor and major grids
ax.grid(color='dimgrey', which='minor', axis='x', linestyle='-', linewidth=0.1)
ax.grid(color='gainsboro', which='minor', axis='y', linestyle='-')

#plt.minorticks_on()
#plt.legend()
#legend solid fill background
legend = plt.legend(frameon = 1, loc='upper left' , prop={'size': 15})
frame = legend.get_frame()
#frame.set_facecolor('grey')


#if is_log_scale == 'False':
#	pp = PdfPages('/home/skmonga/dreamlab_iisc/echo_experiments/azure_experiments/'+dataset+'/Pareto_Latency_ALPR.pdf')
#else:
#	pp = PdfPages('/home/skmonga/dreamlab_iisc/echo_experiments/azure_experiments/'+dataset+'/Pareto_Latency_ALPR_log.pdf')

#pp.savefig(fig, bbox_inches='tight')
#pp.close()

#ax.set_xticks(np.arange(0,63,3))
#ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.xaxis.set_tick_params(labelsize=22)
ax.yaxis.set_tick_params(labelsize=22)

ax.set_xticks(np.arange(12,72,12), minor=False)
ax.set_xticks(np.arange(0,63,3), minor=True)
ax.xaxis.grid(True, which='major')
ax.xaxis.grid(True, which='minor')

plt.show()
	
