# Report for Basic Snakemake Workflow

Report generated on: 2024-11-06 10:30:15
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
|   index |   value |
|--------:|--------:|
|     1.0 |     0.6 |
|     2.0 |     1.6 |
|     3.0 |     0.5 |
|     4.0 |     0.6 |
|     5.0 |    -0.6 |
[results/data/sample1.csv](results/data/sample1.csv)
<p>These are the first random numbers for sample1</p>


### sample2.csv
|   index |   value |
|--------:|--------:|
|     1.0 |     1.0 |
|     2.0 |     0.3 |
|     3.0 |     0.1 |
|     4.0 |     1.4 |
|     5.0 |     0.8 |
[results/data/sample2.csv](results/data/sample2.csv)
<p>These are the first random numbers for sample2</p>


### sample3.csv
|   index |   value |
|--------:|--------:|
|     1.0 |    -1.3 |
|     2.0 |    -1.0 |
|     3.0 |    -0.5 |
|     4.0 |     0.3 |
|     5.0 |    -0.9 |
[results/data/sample3.csv](results/data/sample3.csv)
<p>These are the first random numbers for sample3</p>






## Data Visualization
Here, we visualize the data in a nice way.




<img src="results/plots/sample1.png" alt="sample1.png" width="1024">
<p>This is the lineplot for sample sample1</p>


<img src="results/plots/sample2.png" alt="sample2.png" width="1024">
<p>This is the lineplot for sample sample2</p>


<img src="results/plots/sample3.png" alt="sample3.png" width="1024">
<p>This is the lineplot for sample sample3</p>






## Aggregation




|   x |          y |
|----:|-----------:|
|   1 |  0.0739289 |
|   2 |   0.308444 |
|   3 |  0.0305986 |
|   4 |   0.759747 |
|   5 |  -0.200961 |
|   6 | -0.0744146 |
|   7 |  -0.175992 |
|   8 | -0.0195342 |
|   9 | -0.0149575 |
|  10 |    -0.2201 |
[results/summary.csv](results/summary.csv)
<p>These are the first random numbers for aggregated samples</p>


<img src="results/summary.png" alt="summary.png" width="512">
<p>This is the lineplot for sample aggregated samples</p>




