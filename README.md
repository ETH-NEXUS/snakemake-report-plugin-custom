# Snakmake custom report
Since Snakemake 8.5 seems to implement a report plugin interface to customize report (#2700). 
https://github.com/snakemake/snakemake-interface-report-plugins
Its been merged to main branch in Feb 2024
This could be a handy solution for automated custom reports. 
However this feature is not documented. 

A plugin is a python module that provides the required functionality to create the report.
There is a poetry plugin to create templates for these plugins:
https://github.com/snakemake/poetry-snakemake-plugin

This example modifies this skeleton to create a minimal html report. 

## Setup
To set up the dev env, we need to install poetry and the SnakeMake plugin
```bash
# set up poetry
curl -sSL https://install.python-poetry.org | python -
#add to PATH
echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.zshrc 
# Install poetry plugin via
poetry self add poetry-snakemake-plugin
```
Next the plugin is initialized
```bash
# Create a new poetry project with poetry new snakemake-report-plugin-<reporter-name>
# e.g. if the reporter is called "custom", like in this example here, the command would be
poetry new snakemake-report-plugin-custom
cd snakemake-report-plugin-custom
# Scaffold the project as a snakemake report plugin
poetry scaffold-snakemake-report-plugin
```
## Development
Next, edit the scaffolded code according to your needs
In particular, the ReportSettings and Reporter classes in `__init__.py` need to be implemented.
Then publish the resulting plugin into a GitHub repository. The scaffold command also 
creates GitHub actions workflows that will immediately start to check and test
the plugin.

During development, you can add new dependencies with
```bash
# edit the pyproject.toml file
poetry lock
poetry install
```
Run the checks done in github actions
```bash
# formatting
poetry run black .
poetry run black --check .
# linting
poetry run flake8
# tests are not set up right now ...
poetry run coverage run -m pytest tests/tests.py
poetry run coverage report -m

```



## Create the report
To test the feature, you can use the basic_snakemake_workflow
```bash
# clone the example workflow
git clone git@github.com:ETH-NEXUS/basic_snakemake_workflow.git ../basic_snakemake_workflow
# copy the config (and potentially adjust it)
cp -r ../basic_snakemake_workflow/config .
# run snakemake to create results
poetry run snakemake -s ../basic_snakemake_workflow/Snakefile
# create the report
poetry run snakemake -s ../basic_snakemake_workflow/Snakefile --reporter custom --report-custom-path simple_report.html
```


## TODO:
* test installation without poetry (github, PyPI)
* poetry deployment?
* satisfy github action tests
* add functionality to make it useful:
    * add additional text for categories and subcategories
        * additional report/{category_name}.rst files are included if present. 
    * how to control the order of result entries?
        * category prefix (e.g. "01_categoryname")
    * how to incorporate results (e.g. images) in additional text
    * how to handle/render tables (.csv files)?
        * specify number of columns to print?
    * how to handle variables? e.g. Software versions, number of de genes
        * parse yaml output
* make it nice
    * add logo
    * add menu / structure?
* return two htmls, one centered around technicalities, one around results

