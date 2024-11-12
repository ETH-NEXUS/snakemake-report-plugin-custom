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

### Poetry commands
During development, you can add new dependencies with
```bash
poetry self show
# edit the pyproject.toml file
poetry lock
poetry install
```

### Code checks
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

### release please
Releases are automated with release please, which gets triggered with specially formated commit messages.
For all features, see the githhub readme: https://github.com/googleapis/release-please

git commit messages should follow the scheme that can be parsed by release-please, e.g.:
```
feat: add initial plugin
fix: correct git command
chore: add gitignore and resulting simple_report.html
refactor: update resources_report
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
# default html report
poetry run snakemake -s ../basic_snakemake_workflow/Snakefile --report html_report.html 

# delete old reports and create the report
rm -r results_report  && poetry run snakemake -s ../basic_snakemake_workflow/Snakefile --reporter custom --report-custom-config report_config.yaml

```


## TODO:
* poetry deployment?
* satisfy github action tests
* add functionality to make it useful:
    * add additional text for categories and subcategories
        * additional report/{category_name}.rst files are included if present. 
    * how to control the order of result entries?
        * sort alphabetically: add category prefix (e.g. "01_categoryname") (done)
        * define in report_config.yaml (todo)
    * how to incorporate results (e.g. images) in additional text
        * yaml templates (md or rst) overwrite default (heading + result + caption)
    * how to handle/render tables (.csv files)?
        * specify number of columns to print (default or section specific)
        * in template?
    * how to handle variables? e.g. Software versions, number of de genes
        * parse yaml output of rules?
* make it nice
    * add logo
    * add menu / structure?
    * handle "other" e.g. no category/subcategory 
      * no heading
      * comes first 
* return two htmls, one centered around technicalities, one around results

## Notes:

captions get rendered with:
* snakemake.scripts.Snakemake()
    * input, output, params, wildcards, threads, resources, log, config, rulename, bench_iteration
* categories
* files (list with all result files)


report_config.yaml file
```yaml

results:
  title: "Report for Basic Snakemake Workflow"
  path: results_report/
  # create self contained file (TODO)
  embedded: False
  # if description template is not specified, the template from the snakefile (report directive) is used 
  description: report_template/workflow_overview.md 
  # here you can explicitly define the order of sections, and additional templates
  result_sections:
    "sample1":
      skip: True
    "Data Generation": 
      skip: True # this section will be skipped (with all result files in it)
      template: report_template/data_generation.md
      table: my_specific_table
      subsections:
        Other:
          template: report_template/data_generation_subsection.md
    "Data Visualization":
      template: report_template/data_visualization.md
      image: large
    Aggregation: 
      # default rendering 
      # - header, no text, all result files are concatenated 
    # Categories not listed here are added with default 
    # rendering in alphabetical order
    # to skip a category add:
    # Category_name: skip
    # "[...]": 
    #   template: default
    # References:
    #  template: report_template/references

  # specify default rendering options for    
  render_options: 
    image:
      suffix:
        - "jpg"
        - "png"
      width: 512
      link: False
      presets:
        large:
          width: 1024
    table:
      suffix:
        - "csv"
        - "tsv"
      sep:
        default: "\t"
        csv: ","
      max_row: 10 # fist n rows only
      index: False 
      numalign: "right"
      stralign: "center"
      missingval: "N/A"
      link: False
      presets:
        show_100:
          max_row: 100
        my_specific_table: 
          max_row: 5
          col_select: [0,1] # select a subset of columns
          headers: ["index", "value"] # overwrite column headers
          floatfmt: ".1f"
resources:
  path: resource_report.html

```
category.md templates

```md
## {{name}}
this is text preceding the output which has access to {{vars.ruleX.python_version}}
{{output.render_all()}}
{{output.render_first()}}
{{output.render_wildcard("sample_1")}}
### Conculsions
This is text after the 

```

default template
```md
## {{name}}
{{output.render_all()}}
```