# Report for Basic Snakemake Workflow

Report generated on: 2024-10-30 17:54:38
## Workflow Description
### Overview


This Snakemake workflow demonstrates a basic data analysis pipeline for generating random datasets, 
plotting individual samples, and aggregating the data to create a summary table and plot. 
The pipeline is designed to test Snakemake's reporting functionality and showcases the use of the `report()` 
function of output files to include results in a final HTML report.

### Workflow Steps
1. **Data Generation**: 
   For each of the three samples, random data is generated using a normal distribution. 
   The size of the data points is defined by the parameter `n = 100`.
   The generated data is saved as CSV files.

2. **Data Visualization**: 
   Each sample's data is visualized in a plot. 
   The plots show the relationship between the x-values (which are sequential integers) and the y-values 
   (randomly generated following a normal distribution). 
   These plots are included in the report under the category "Data Visualization".

3. **Data Aggregation**: 
   All generated data files are aggregated into a single summary file. 
   The summary contains the mean values of the data points across all samples. 
   A corresponding plot visualizes the aggregated results. Both the summary file 
   and the plot are included in the report under the category "Aggregation".


### Configuration
The workflow is configured to generate 100 datapoints for 3 samples.

## Results


## Aggregation




|   x |         y |
|----:|----------:|
|   1 |  0.131469 |
|   2 |  0.593698 |
|   3 | -0.230604 |
|   4 | -0.473003 |
|   5 | 0.0590795 |
|   6 |  0.444733 |
|   7 | -0.152784 |
|   8 | -0.845227 |
|   9 |  0.506302 |
|  10 | -0.511828 |
[results/summary.csv](results/summary.csv)
<p>These are the first random numbers for aggregated samples</p>


<img src="results/summary.png" alt="summary.png" width="512">
<p>This is the lineplot for sample aggregated samples</p>






## sample2




<img src="results/plots/sample2.png" alt="sample2.png" width="512">
<p>This is the lineplot for sample sample2</p>






## sample3




<img src="results/plots/sample3.png" alt="sample3.png" width="512">
<p>This is the lineplot for sample sample3</p>




