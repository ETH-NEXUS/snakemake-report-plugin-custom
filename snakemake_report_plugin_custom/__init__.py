from dataclasses import dataclass, field
from typing import Optional
from os import path


try:
    from snakemake.logging import logger
except ImportError:
    from snakemake import logger

from .resources_report import render_resource_html
from .results_report import render_results_html

# from snakemake import logger
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
    results: Optional[Path] = field(
        default=None,
        metadata={
            "help": "Path to the results report folder",
            "env_var": False,
            "required": False,
        },
    )
    resources: Optional[Path] = field(
        default=None,
        metadata={
            "help": "Path to the resource usage report folder",
            "env_var": False,
            "required": False,
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
        self.template_dir = path.join(path.dirname(__file__), "templates")
        self.results_template_file = "results_template.html.jinja2"
        self.resource_template_file = "resources_template.html.jinja2"

        if self.settings.results is None and self.settings.resources is None:
            raise WorkflowError(
                "either specify --report-custom-results or --report-custom-resources"
            )



    def render(self):
        if self.settings.results is not None:
            self.render_results_report()
        if self.settings.resources is not None:
            self.render_resources_report()

    def render_resources_report(self):
        output_dir = self.settings.resources
        suffix=output_dir.suffix
        if suffix == "":
            # a path was provided            
            embedded=False
            html_file="resources_index.html"
        elif suffix == ".html":
            embedded=True
            html_file=output_dir.name
            output_dir=output_dir.parent
        else:
            raise NotImplementedError(f"reports of type {suffix} are not supported")
        workflow = vars(self.dag)["workflow"]
        render_resource_html(workflow, output_dir,html_file, self.template_dir, self.resource_template_file,embedded)
        logger.info(f"Resource Report generated at {output_dir}")


    def render_results_report(self):
        # Ensure the output directory does not exist
        output_dir = self.settings.results
        render_results_html(self.results,self.workflow_description, output_dir, self.template_dir, self.results_template_file, embedded=False)
        logger.info(f"Result Report generated at {output_dir}")
