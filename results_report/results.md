# Report for Basic Snakemake Workflow

Report generated on: 2024-10-24 18:45:00
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


## Data Generation
This is some custom introduction text for the data generation section.




### sample1.csv
|    |   x |          y |
|---:|----:|-----------:|
|  0 |   1 | -0.703586  |
|  1 |   2 | -0.0975687 |
|  2 |   3 | -0.307086  |
|  3 |   4 | -1.63426   |
|  4 |   5 |  0.27029   |
[results/data/sample1.csv](results/data/sample1.csv)
<p>These are the first random numbers for sample1</p>


### sample2.csv
|    |   x |         y |
|---:|----:|----------:|
|  0 |   1 |  0.900229 |
|  1 |   2 |  1.63412  |
|  2 |   3 |  0.141262 |
|  3 |   4 |  1.48179  |
|  4 |   5 | -1.05023  |
[results/data/sample2.csv](results/data/sample2.csv)
<p>These are the first random numbers for sample2</p>


### sample3.csv
|    |   x |         y |
|---:|----:|----------:|
|  0 |   1 |  0.197764 |
|  1 |   2 |  0.244541 |
|  2 |   3 | -0.525987 |
|  3 |   4 | -1.26653  |
|  4 |   5 |  0.957179 |
[results/data/sample3.csv](results/data/sample3.csv)
<p>These are the first random numbers for sample3</p>






## Data Visualization
Here, we visualize the data in a nice way.




![sample1.png](results/plots/sample1.png)
<p>This is the lineplot for sample sample1</p>


![sample2.png](results/plots/sample2.png)
<p>This is the lineplot for sample sample2</p>


![sample3.png](results/plots/sample3.png)
<p>This is the lineplot for sample sample3</p>






## Aggregation




|    |   x |          y |
|---:|----:|-----------:|
|  0 |   1 |  0.131469  |
|  1 |   2 |  0.593698  |
|  2 |   3 | -0.230604  |
|  3 |   4 | -0.473003  |
|  4 |   5 |  0.0590795 |
[results/summary.csv](results/summary.csv)
<p>These are the first random numbers for aggregated samples</p>


![summary.png](results/summary.png)
<p>This is the lineplot for sample aggregated samples</p>




