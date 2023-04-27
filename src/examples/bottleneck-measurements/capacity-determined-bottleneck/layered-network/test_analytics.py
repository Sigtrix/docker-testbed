import pandas as pd
import matplotlib.pyplot as plt

# read csv into a pandas dataframe
df = pd.read_csv('test_results.csv')

bottlneck_bw_values = []
mean_bandwidth_list = []
median_bandwidth_list = []
var_bandwidth_list = []
weighted_mean_bandwidth_list = []
bottleneck_list = []

# loop through the dataframe, taking n samples at a time
for bandwidth, group in df.groupby('Bandwidth'):
    window_size = len(group)
    # calculate the mean and variance of bandwidth for the window
    mean_bandwidth = group['Bottleneck_BW'].mean()
    var_bandwidth = group['Bottleneck_BW'].var()
    median_bandwidth = group['Bottleneck_BW'].median()

    # calculate the weighted mean bandwidth
    weighted_mean_bandwidth = (group['Bottleneck_BW'] * group['Conf_Level']).sum() / group['Conf_Level'].sum()

    # calculate the bottleneck predicted max number of times
    bottleneck_value = group['Bottleneck'].value_counts().idxmax()

    # add the metrics in a list
    mean_bandwidth_list.append(mean_bandwidth)
    var_bandwidth_list.append(var_bandwidth)
    median_bandwidth_list.append(median_bandwidth)
    weighted_mean_bandwidth_list.append(weighted_mean_bandwidth)
    bottleneck_list.append(bottleneck_value)
    bottlneck_bw_values.append(bandwidth)

# print the list of mean bandwidths
print(f"Real bw values = {bottlneck_bw_values}")
print(f"mean_bandwidth = {mean_bandwidth_list}")
print(f"median_bandwidth = {median_bandwidth_list}")
print(f"variance = {var_bandwidth_list}")
print(f"weighted mean = {weighted_mean_bandwidth_list}")
print(f"bottleneck predictions = {bottleneck_list}")

# plot weighted bandwidth test results
plt.figure(1)
plt.scatter(bottlneck_bw_values, median_bandwidth_list, c='blue', label = 'Median BW')
plt.scatter(bottlneck_bw_values, weighted_mean_bandwidth_list, c='orange', label = 'Weighted_Mean BW')
plt.legend()
plt.axline((0, 0), slope=1, c='black', linestyle='--')
plt.xlabel('Bandwidth values configured with tc')
plt.ylabel('Measured bandwidth on detected bottlneck with pathneck')
plt.title(f'Bandwidth [Mbits/sec] comparison')
plt.savefig('pathneck-weighted_bandwidth-measurements')
plt.show()

plt.figure(2)
plt.plot(bottlneck_bw_values, var_bandwidth_list)
plt.title("Variance Vs Bandwidth")
plt.savefig('Variance_Vs_Bandwidth')
plt.show()