from jinja2 import Environment, FileSystemLoader
import datetime
from os import path
import pathlib
import shutil
try:
    from snakemake.logging import logger
except ImportError:
    from snakemake import logger

def render_results_html(results,workflow_description, output_dir, template_dir, template_file, embedded=False):
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        logger.error(f'result report folder "{output_dir}" already exists')
        exit(1)

    # Load the Jinja2 template
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    # Prepare data for the report
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rendered_results = prepare_results(results, output_dir, embedded)

    # Render the report content
    report_content = template.render(
        results=rendered_results,
        now=now,
        workflow_description=workflow_description,
    )

    # Write the rendered content to the report file
    report_path = path.join(output_dir, "results.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)


def prepare_results(results, output_dir, embedded):
    # Transform results data into a format suitable for the template
    # and copy the files
    # TODO: how to control the order of entries?
    # TODO: add additional text for categories and subcategories
    # TODO: incorporate results (e.g. images) in additional text
    # TODO: how to handle tables?
    # TODO: how to handle variables?
    #       e.g. Software versions, number of de genes, ... (yaml output?)
    if embedded:
        raise NotImplementedError("Embedded result report not implemented yet")

    transformed_results = {}
    for category, subcategories in results.items():
        for subcat in subcategories.values():
            for file in subcat:
                target = pathlib.Path(path.join(output_dir, file.path))
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(file.path, target, follow_symlinks=True)
        transformed_results[category.name] = {
            subcategory.name: [result.path for result in files]
            for subcategory, files in subcategories.items()
        }
    logger.info(transformed_results)
    return transformed_results
