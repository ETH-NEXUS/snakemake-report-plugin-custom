from dataclasses import dataclass, field
from typing import Optional
from os import path
import yaml



try:
    from snakemake.logging import logger
except ImportError:
    from snakemake import logger

from .resources_report import render_resource_html
from .results_report import render_results_html
from ._utils import print_content, get_vars

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
    config: Optional[Path] = field(
        default=None,
        metadata={
            "help": "Path to the results config yaml",
            "env_var": False,
            "required": False,
        },
    )
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
        self.results_template_files = {what :f"results_{what}.md" for what in ("main", "section", "subsection")} # default template files
        self.resource_template_file = "resources_template.html.jinja2"
        if self.settings.config is not None:
            try:
                with open(self.settings.config, 'r') as config_file:
                    self.settings.config = yaml.safe_load(config_file)
            except FileNotFoundError:
                logger.error(f"specified config file {config_file} not found")
            if self.settings.config is None:
                self.settings.config={}
            if "results" in self.settings.config and self.settings.results is None:
                self.settings.results=Path(self.settings.config["results"].get("path"))
                if self.settings.results is None:
                    logger.warning("reporting config section 'results' found, but no path specified - no results report is generated")
            if "resources" in self.settings.config and self.settings.resources is None:
                self.settings.results=Path(self.settings.config["resources"].get("path"))
                if self.settings.resources is None:
                    logger.warning("reporting config section 'resources' found, but no path specified - no resources report is generated")


        if self.settings.results is None and self.settings.resources is None:
            raise WorkflowError(
                "either specify results or resources report paths in config or with --report-custom-results or --report-custom-resources parameters"
            )
        
        # to get an Idea of what is there:
        print_content(**get_vars(self))



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
        
        # logger.debug("**** config ****\n"+self.configfiles[0].source)
        # Convert JSON string to dictionary
        config_dict=yaml.safe_load(self.configfiles[0].source)

        render_results_html(self.results,self.workflow_description,config_dict,self.settings.config.get("results",{}), output_dir, self.template_dir, self.results_template_files, embedded=False)
        logger.info(f"Result Report generated at {output_dir}")
