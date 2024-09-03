from dataclasses import dataclass, field
from typing import Optional
from jinja2 import Environment, FileSystemLoader
import os
import datetime


#from snakemake import logger
from snakemake_interface_common.exceptions import WorkflowError  # noqa: F401
from snakemake_interface_report_plugins.reporter import ReporterBase
from snakemake_interface_report_plugins.settings import ReportSettingsBase
from pathlib import Path


# Optional:
# Define additional settings for your reporter.
# They will occur in the Snakemake CLI as --report-<reporter-name>-<param-name>
# Omit this class if you don't need any.
# Make sure that all defined fields are Optional (or bool) and specify a default value
# of None (or False) or anything else that makes sense in your case.

@dataclass
class ReportSettings(ReportSettingsBase):
    path: Optional[Path] = field(
        default=None,
        metadata={
            "help": "Path to the report html file.",
            "env_var": False,
            "required": True,
        },
    )



# Required:
# Implementation of your reporter
class Reporter(ReporterBase):
    def __post_init__(self):
        # initialize additional attributes
        # Do not overwrite the __init__ method as this is kept in control of the base
        # class in order to simplify the update process.
        # See https://github.com/snakemake/snakemake-interface-report-plugins/snakemake_interface_report_plugins/reporter.py # noqa: E501
        # for attributes of the base class.
        # In particular, the settings of above ReportSettings class are accessible via
        # self.settings.
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.template_file = 'report_template.html'

        
        if self.settings.path.suffix != ".html":
            raise WorkflowError("Report file does not end with .html or .zip")
        

    def render(self):
        # Render the report, using attributes of the base class.
        # rulegraph, _, _ = rulegraph_spec(self.dag)

        # just list some text
        print("Custom Report")
        for cat, subcats in self.results.items():
            print(cat.name)
            for subcat, catresults in subcats.items():
                print(f'  - {subcat.name}')
                for res in catresults:
                    print(f'    - {res.path}')
                    
        # Ensure the output directory exists
        output_dir = self.settings.path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load the Jinja2 template
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template_file)

        # Prepare data for the report
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rendered_results = self.prepare_results(self.results)

        # Render the report content
        report_content = template.render(
            results=rendered_results,
            now=now,
            workflow_description=self.workflow_description
        )

        # Write the rendered content to the report file
        report_path = self.settings.path
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Report generated at {report_path}")

    def prepare_results(self, results):
        # Transform results data into a format suitable for the template
        # TODO: how to control the order of entries?
        # TODO: add additional text for categories and subcategories
        # TODO: incorporate results (e.g. images) in additional text
        # TODO: how to handle tables?
        # TODO: how to handle variables? e.g. Software versions, number of de genes, ... (yaml output?)


        transformed_results = {}
        for category, subcategories in results.items():
            transformed_results[category.name] = {
                subcategory.name: [result.path for result in files]
                for subcategory, files in subcategories.items()
            }
        print(transformed_results)
        return transformed_results