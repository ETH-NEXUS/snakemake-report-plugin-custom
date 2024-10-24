## Workflow Description
### Overview


This Snakemake workflow demonstrates a basic data analysis pipeline for generating random datasets, 
plotting individual samples, and aggregating the data to create a summary table and plot. 
The pipeline is designed to test Snakemake's reporting functionality and showcases the use of the `report()` 
function of output files to include results in a final HTML report.

### Workflow Steps
1. **Data Generation**: 
   For each of the three samples, random data is generated using a normal distribution. 
   The size of the data points is defined by the parameter `n = {{ snakemake.config["generate_data"]["n"] }}`.
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
The workflow is configured to generate {{ snakemake.config["generate_data"]["n"] }} datapoints for {{  snakemake.config["samples"] | length }} samples.
