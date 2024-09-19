from jinja2 import Environment, FileSystemLoader
import datetime
from os import path
import pathlib
import shutil
import pandas as pd
import yaml
import markdown

try:
    from snakemake.logging import logger
except ImportError:
    from snakemake import logger


# TODO: how to control the order of entries?
# TODO: add additional text for categories and subcategories

def render_results_html(results,workflow_description, config_dict, output_dir, template_dir, template_file, embedded=False):
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
    copy_result_files(results, output_dir)

    if embedded:
        raise NotImplementedError("Embedded result report not implemented yet")
    for categories in results.values():
        # how to add custom descriptions here?
        for subcat in categories.values():
            for file in subcat:        
                file.rendered=render_result(file, config_dict)
    # Render the report content
    report_content = template.render(
        results=dict(sorted(results.items())),
        now=now,
        workflow_description=workflow_description,
        categories=categories
    )

    # Write the rendered content to the report file
    report_path = path.join(output_dir, "results.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

def copy_result_files(results, output_dir):
    for categories in results.values():
        for subcat in categories.values():
            for file in subcat:
                # logger.debug(file)
                
                target = pathlib.Path(path.join(output_dir, file.path))
                logger.debug(f'copy {file.path} to {target.parent}')
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(file.path, target, follow_symlinks=True)


def render_result(file, config_dict):
    # Transform results data into a format suitable for the template
    # and copy the files
    # TODO: incorporate results (e.g. images) in additional text
    # TODO: how to handle tables?
    # TODO: how to handle variables?
    #       e.g. Software versions, number of de genes, ... (yaml output?)
    html=[] 
    as_link=True
    suffix=file.path.suffix[1:]
    report_config=config_dict.get("report")
    # logger.debug(f"{file.path} is a {suffix} file")
    if suffix in report_config.get("image", {}).get("suffix", []):
        # logger.debug(f"render {suffix} {fil.pathe} as image")
        html.append(f'<img src="{ file.path }" alt="{ file }">')
        as_link=report_config["image"].get("link", False)
    elif suffix in report_config.get("table", {}).get("suffix", []):
        # logger.debug(f"render {file.path} as table")
        sep_dict=report_config["table"].get("sep", {})
        sep=sep_dict.get(suffix,sep_dict.get("default", "\t"))
        df=pd.read_table(file.path, sep=sep)
        html.append(df.head().to_html())
        as_link=report_config["table"].get("link", False)
    elif suffix in report_config.get("yaml", {}).get("suffix", []):
        pass  
    if as_link:
        # logger.debug(f"render {file.path} as link")
        html.append(f'<li><a href="{ file.path }">{ file.path }</a></li>')

    if file.caption is not None:
        html.append(file.caption)
    return("\n".join(html))