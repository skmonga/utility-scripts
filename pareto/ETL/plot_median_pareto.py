import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import sys
import numpy as np

dataset = 'CITY'

median_dict = {}
#median_dict['Edge'] = [[30,50,55,60,65,70] , [49,52,64,1622,3971,10863] , 'b']
#median_dict['Fog'] = [[30,40,60,80,100,150,250,500,600,750,1000] , [50,46,43,40,40,40,40,47,35114,54319,58213] , 'g']
#median_dict['Fog_Edge'] = [[60,80,100,120,150,200,210,220,250,300] , [357,363,369,401,1285,2496,6948,10489,7683,60218], 'r']
#median_dict['Cloud'] = [[100,110,120,130,140,150,200,300,400] , [530,581,4508,2390,7373,10347,15096,95385,107768] , 'y']
#median_dict['EFC_2_0_6'] = [[60,70,80,90,100,110,120] , [569,1319,732,1778,1036,2909,10400] , 'm']
#median_dict['EFC_2_1_5'] = [[50,100,110,120,130,140,150] , [622,734,1091,2581,5497,8550,15655] , 'c']
median_dict['E*'] = [[30,50,55,60,65,70] , [49,52,64,1622,3971,10863] , 'b', 'o']
median_dict['EF'] = [[60,80,100,120,150,200,210] , [357,363,369,401,1285,2496,6948], 'r', '^' ]
median_dict['F*'] = [[30,40,60,80,100,150,250,500,600] , [50,46,43,40,40,40,40,47,35114] , 'g', 's']
median_dict['EC'] = [[60,70,80,90,100,110,120] , [569,1319,732,1778,1036,2909,10400] , 'm', 'D']
median_dict['EFC'] = [[50,100,110,120,130] , [622,734,1091,2581,5497] , 'c', 'v']
#median_dict['EFC'] = [[50,100,110,120,130] , [622,734,1091,2581,5497] , 'c', '*']
median_dict['C*'] = [[100,110,120,130,140,150,200,300] , [530,581,3302,2390,7373,10347,15096,95385] , 'y', '+']
#median_dict['C*'] = [[100,110,120,130,140,150,200,300] , [530,581,3302,2390,7373,10347,15096,95385] , 'y', 'p']

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot(111)

ax.set_yscale('log')
ax.set_xscale('log')

median_dict_keys = ['E*', 'EF', 'F*', 'EC', 'EFC', 'C*']
annotate_dict = {}
annotate_dict['E*'] = (20,47)
annotate_dict['EF'] = (140,1110)
annotate_dict['F*'] = (160, 40)
annotate_dict['EC'] = (60,569)
annotate_dict['EFC'] = (90,710)
annotate_dict['C*'] = (110,581)


#for key in median_dict_keys:
#	value = median_dict[key]
#	input_rate_list = value[0]
#	latency_list = value[1]
	#i = 0
	#for rate in input_rate_list:
		#ax.text(effective_rate_list[i],latency_list[i], str(supplied_rate_list[i]),transform=ax.transAxes)
#	ax.annotate(str(annotate_dict[key][0]), (annotate_dict[key][0],annotate_dict[key][1]), color='black',fontsize=20)
	#i += 1

marker_style = dict(color='cornflowerblue', marker='o',
                    markersize=25, markerfacecoloralt='gray', )

for key in median_dict_keys:
	value = median_dict[key]
	if key is 'C*':
		#ax.scatter(value[0], value[1], label = key, c='orange', marker=value[3], linewidths=1, edgecolors='orange', facecolors='none', s=100)
		ax.scatter(value[0], value[1], label = key, c='orange', marker=value[3], linewidths=1, edgecolors='orange', facecolors='none', s=200)
	elif key is 'EFC':
		#ax.scatter(value[0], value[1], label = key, c=None, marker=value[3], linewidths=1, edgecolors='c', facecolors='none', s=100)
		ax.scatter(value[0], value[1], label = key, c=None, marker=value[3], linewidths=1, edgecolors='c', facecolors='none', s=200)
	else:
		#ax.scatter(value[0], value[1], label = key, color = None, marker=value[3], linewidths=1, edgecolors=value[2], facecolors='none', s=100)
		ax.scatter(value[0], value[1], label = key, color = None, marker=value[3], linewidths=1, edgecolors=value[2], facecolors='none', s=200)

plt.xlabel('Input Rate (events/sec) [Log]', fontsize=25)
plt.ylabel('Median Latency (ms) [Log]', fontsize=25)
#plt.title('Median latency variation with rate for ETL City',fontsize=24)
plt.grid()

#minor and major grids
ax.grid(color='dimgrey', which='minor', axis='x', linestyle='-', linewidth=0.1)
ax.grid(color='gainsboro', which='minor', axis='y', linestyle='-')

plt.minorticks_on()

#plt.legend()
#legend solid fill background
legend = plt.legend(frameon = 1, loc='upper left' , prop={'size': 20})
frame = legend.get_frame()
#frame.set_facecolor('grey')

#ax.set_xticks(np.arange(10,210,10))
#ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
#ax.xaxis.set_tick_params(labelsize=25)
#ax.xaxis.set_tick_params(labelsize=22, which='major')
ax.xaxis.set_tick_params(labelsize=22, which='both')
ax.yaxis.set_tick_params(labelsize=22)

ax.set_xticks([20,100], minor=False)
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
#ax.set_xticks([20,30,40,50,300,400,500], minor=True)
#ax.get_xaxis().set_minor_formatter(matplotlib.ticker.ScalarFormatter())
#ax.xaxis.grid(True, which='major')
#ax.xaxis.grid(True, which='minor')

plt.show()

