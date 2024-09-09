from dataclasses import dataclass, field
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from os import path
import datetime
import shutil

try:
    from snakemake.logging import logger
except ImportError:
    from snakemake import logger
from .resources_report import create_benchmark_plot

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

    def explore_content(self):
        def get_vars(obj):
            if hasattr(item, "__dict__"):
                return vars(obj)
            return obj

        # explore what we have:
        for attr in dir(self):
            if attr.startswith("_"):
                continue
            logger.info(f'\n{attr}\n{"="*len(attr)}')
            value = getattr(self, attr, None)
            if isinstance(value, list):
                for item in value:
                    logger.info(get_vars(item))
            elif isinstance(value, dict):
                for key, item in value.items():
                    logger.info(f"{key}: {get_vars(item)}")
            else:
                logger.info(get_vars(value))

    def print_content(self):
        logger.info("My Fancy Report")
        logger.info("\n--- CONFIGFILES ---")
        logger.info(self.configfiles)

        logger.info("\n--- DAG ---")
        logger.info(self.dag)
        for k, v in vars(self.dag).items():
            logger.info(f"{k}: {v}")
        workflow = vars(self.dag)["workflow"]

        logger.info("\n--- WORKFLOW ---")
        logger.info(workflow)

        logger.info("\n--- RULES ---")

        for rule in workflow.rules:
            logger.info(rule)
            logger.info(f"Rule name: {rule.name}")
            logger.info(f"Rule input files: {rule.input}")
            logger.info(f"Rule output files: {rule.output}")
            logger.info(f"Rule benchmark files: {rule.benchmark}")

        logger.info("\n--- JOBS ---")
        for job in self.jobs:
            # Convert job object to a dictionary if possible
            logger.info((job))

        logger.info("\n--- RESULTS ---")
        for cat, subcats in self.results.items():
            logger.info(cat.name)
            for subcat, catresults in subcats.items():
                logger.info(f"  - {subcat.name}")
                for res in catresults:
                    logger.info(f"    - {res.path}")

        logger.info("\n--- RULES ---")
        for rule_name, rule_record in self.rules.items():
            logger.info(f"Rule: {rule_name}")
            # Convert rule record to dictionary if possible
            logger.info(rule_record)

        for rule in self.rules.values():
            logger.info(rule)

        logger.info("\n--- SETTINGS ---")
        # Convert settings object to a dictionary if possible
        logger.info(vars(self.settings))

        logger.info("\n--- WORKFLOW DESCRIPTION ---")
        # logger.info(self.workflow_description)

        logger.info("\n--- TEMPLATE DIRECTORY ---")
        logger.info(self.template_dir)

        logger.info("\n--- TEMPLATE FILE ---")
        logger.info(self.results_template_file)

    def render(self):
        if self.settings.results is not None:
            self.render_results_report()
        if self.settings.resources is not None:
            self.render_resources_report()

    def render_resources_report(self):
        output_dir = self.settings.resources
        try:
            (output_dir / "img").mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            logger.error(f'resources report folder "{output_dir}" already exists')
            exit(1)
        workflow = vars(self.dag)["workflow"]
        benchmark_results = []
        for rule in workflow.rules:

            logger.info(rule)
            logger.info(f"Rule name: {rule.name}")
            logger.info(f"Rule input files: {rule.input}")
            logger.info(f"Rule benchmark files: {rule.benchmark}")
            if rule.benchmark is not None:
                rule_benchmark = {"rule_name": rule.name}
                try:
                    file, infos = create_benchmark_plot(
                        rule.name, rule.benchmark, rule.input, output_dir
                    )
                except ValueError as e:
                    logger.error(e)
                    continue
                rule_benchmark["image_path"] = file
                rule_benchmark["caption"] = "\n".join(
                    [f"* {k}: {v}" for k, v in infos.items()]
                )
                benchmark_results.append(rule_benchmark)
        # Load the Jinja2 template
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.resource_template_file)
        # Prepare data for the report
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Render the report content
        report_content = template.render(results=benchmark_results, now=now)
        # Write the rendered content to the report file
        report_path = path.join(output_dir, "resources_index.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        logger.info(f"Report generated at {report_path}")

    def render_results_report(self):
        # Ensure the output directory does not exist
        output_dir = self.settings.results
        try:
            output_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            logger.error(f'result report folder "{output_dir}" already exists')
            exit(1)

        # Load the Jinja2 template
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.results_template_file)

        # Prepare data for the report
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rendered_results = self.prepare_results(self.results, output_dir)

        # Render the report content
        report_content = template.render(
            results=rendered_results,
            now=now,
            workflow_description=self.workflow_description,
        )

        # Write the rendered content to the report file
        report_path = path.join(output_dir, "results.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        logger.info(f"Report generated at {report_path}")

    def prepare_results(self, results, output_dir):
        # Transform results data into a format suitable for the template
        # and copy the files
        # TODO: how to control the order of entries?
        # TODO: add additional text for categories and subcategories
        # TODO: incorporate results (e.g. images) in additional text
        # TODO: how to handle tables?
        # TODO: how to handle variables?
        #       e.g. Software versions, number of de genes, ... (yaml output?)

        transformed_results = {}
        for category, subcategories in results.items():
            for subcat in subcategories.values():
                for file in subcat:
                    target = Path(path.join(output_dir, file.path))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(file.path, target, follow_symlinks=True)
            transformed_results[category.name] = {
                subcategory.name: [result.path for result in files]
                for subcategory, files in subcategories.items()
            }
        logger.info(transformed_results)
        return transformed_results
