import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D

#rates = [6,18,30]
#latency = [10273,5480,10843]
#label =['Edge','Fog','Cloud']

rates_city = [30,45,65,75,85,150,190]
rates_fit = [20,45,65,75,90,165,180]

latency_city = [2698,3575,4729,7399,8202,11464,12225]
latency_fit = [2349,5794,4664,6578,8537,11384,12567]

labels = ['Edge','6_Edges','Fog','EFC(2:3:3)','EFC(2:1:5)','EFC(2:0:6','Cloud']
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

legend_elem =  [Line2D([0], [0], marker='o', color='w', label='City',markerfacecolor='g', markersize=10),
                Line2D([0], [0], marker='D', color='w', label='Fit',markerfacecolor='g', markersize=10)]

fig1=plt.figure(figsize=(10,7))
ax1 = fig1.add_subplot(111)

for i in range(len(rates_city)):
	ax1.scatter(rates_city[i],latency_city[i],marker = "o", label = labels[i], color = colors[i])
	ax1.scatter(rates_fit[i],latency_fit[i],marker = "D", color = colors[i])

#ax1.scatter(rates_city,latency_city,marker = "o", label = labels, color = colors)
#ax1.scatter(rates_fit,latency_fit,marker = "D", color = colors)
    
plt.xlabel('Input Rate (msg/sec)', fontsize=20)
plt.ylabel('Latency (ms)', fontsize=20)
plt.title('Pareto Plot for ETL',fontsize=24)
plt.grid()
plt.minorticks_on()

#create a legend for the configuration, we are labelling when doing scatter plot for city dataset
legend_configuration = plt.legend()

#multiple calls to legend won't succeed and only the last call will take effect , so add manually
# Add the legend manually to the current Axes.
ax = plt.gca().add_artist(legend_configuration)

#the second legend can now be added for the labels itself i.e. circle for city and diamond for fit
ax1.legend(handles = legend_elem, loc = "lower right")

pp = PdfPages('/home/skmonga/dreamlab_iisc/echo_experiments/exp_rates/Pareto/Combined_Pareto_ETL.pdf')

pp.savefig(fig1, bbox_inches='tight')
pp.close()


plt.show()
