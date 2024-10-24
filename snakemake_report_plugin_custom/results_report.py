from jinja2 import Environment, FileSystemLoader
import datetime
from os import path
import pathlib
import shutil
import pandas as pd
import yaml
import markdown
import snakemake

try:
    from snakemake.logging import logger
except ImportError:
    from snakemake import logger

from snakemake.report import FileRecord
# TODO: how to control the order of entries?
# TODO: add additional text for categories and subcategories

# monkey patching of the snakemake FileRecord class that gets passed to respective templates as variables

def render_file_record(self):
    # render as markdown
    rendered=[] 
    logger.debug(f"render {self.path} as {self.render_settings.get("type", "unknown")}")
    if self.render_settings.get("type") == "image":
        # html
        # rendered.append(f'<img src="{ file.path }" alt="{ file }">') 
        # md
        rendered.append(f'![{self.path.name}]({self.path})')
    elif self.render_settings.get("type") == "table":
        sep=self.render_settings.get("sep",{}).get("suffix",',')
        df=pd.read_table(self.path, sep=sep)
        rendered.append(df.head().to_markdown()) # or to_html()
    if self.render_settings.get("show_link", True):
        logger.debug(f"render  {self.path} as link")
        #rendered.append(f'<li><a href="{ file.path }">{ file.path }</a></li>')
        rendered.append(f'[{self.path}]({self.path})')
    if self.caption and self.render_settings.get("show_caption", True):
        rendered.append(self.caption)
    return("\n".join(rendered))
    

def set_render_settings(self, params):
    suffix=self.path.suffix[1:]
    if suffix in params.get("table", {}).get("suffix", ('csv', "tsv")):
        p={"type":"table", **self.default_render_params["table"], **params.get("table", {})}
    elif suffix in params.get('image', {}).get("suffix", ("png", "jpg")):
        p={"type":"image",**self.default_render_params["image"], **params.get("image", {})}
    else:
        p={**self.default_render_params["other"], **params.get("other", {})}
    self.render_settings=p
    

FileRecord.default_render_params={"table":{"sep":{"cnv":",","tsv":"\t"},"show_link": True}, "image":{"width":None, "height":None, "show_link": False}, "other":{"show_link":True}}
FileRecord.__str__=render_file_record
FileRecord.set_render_settings = set_render_settings


def render_results_html(results,workflow_description, snakemake_config, report_config, output_dir, template_dir, template_file, embedded=False):
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        logger.error(f'result report folder "{output_dir}" already exists')
        exit(1)
    embedded=embedded or report_config.get("embedded", False)
    if embedded:
        raise NotImplementedError("Embeded result report not implemented yet")
    
    # Load the Jinja2 template
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file["main"])

    # Prepare data for the report
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result_file_list = copy_result_files(results, output_dir)
    description_file=report_config.get("description")
    if description_file:
        logger.debug(f"Custom workflow description from {description_file}")
        class Snakemake:
            config=snakemake_config
        workflow_description=render_template(env, description_file, snakemake=Snakemake, categories=results, files={})

    # load user defined section order
    toc=report_config.get("result_sections", {})
    
    if toc:
        logger.debug("Found user defined section order and settings")    
        logger.debug(toc)
        for section in toc:
            if toc[section] is None:
                toc[section]={}
            subsections=toc[section].get("subsections", {})
            for subsec in subsections:
                if subsections[subsec] is None:
                    subsections[subsec]={}
    default_section_template=env.get_template(template_file["section"])
    default_subsection_template=env.get_template(template_file["subsection"])

    category_order={cat:i+1 for i,cat in enumerate(toc)}
    category_order["Other"]=0

    for category, subcat_dict in results.items():     
        category.sort_key=category_order.get(category.name, len(category_order) + 1)
        cat_settings=toc.get(category.name, {})
        subcategory_order={cat:i+1 for i,cat in enumerate(cat_settings.get("subsections", {}))}
        subcategory_order["Other"]=0

        for subcat, result_list in subcat_dict.items():            
            subcat_settings=cat_settings.get("subsections", {}).get(subcat.name, {})
            subcat.sort_key=subcategory_order.get(subcat.name, len(subcategory_order) + 1)
            for file in result_list:        
                file.set_render_settings(report_config)
                logger.debug(f'{file.path.name}: {file.render_settings}')            
            try:
                subsection_template=load_template(env, subcat_settings["template"])
            except (KeyError, FileNotFoundError):
                subsection_template=default_subsection_template
            subcat.rendered=subsection_template.render(subcategory=subcat, files=result_list)
        try:
            section_template=load_template(env, cat_settings["template"])
        except (KeyError, FileNotFoundError):
            section_template=default_section_template
        category.rendered=section_template.render(category=category, subcategories=dict(sorted(subcat_dict.items(), key=lambda x:(x[0].sort_key, x[0].name))), has_other=any(subcat.is_other for subcat in subcat_dict.keys()))
    
    
    # Render the report content
    report_content = template.render(
        title=report_config.get("title", "Result Report"), 
        results=dict(sorted(results.items(), key=lambda x:(x[0].sort_key, x[0].name))),
        now=now,
        workflow_description=workflow_description,
        categories=results
    )

    # Write the rendered content to the report file
    report_path = path.join(output_dir, "results.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(markdown.markdown(report_content, extensions=['extra']))
    report_path = path.join(output_dir, "results.md")
    with open(report_path, "w", encoding="utf-8") as f:    
        f.write(report_content)

def copy_result_files(results, output_dir):
    coppied=[]
    for categories in results.values():
        for subcat in categories.values():
            for file in subcat:
                # logger.debug(file)                
                target = pathlib.Path(path.join(output_dir, file.path))
                logger.debug(f'copy {file.path} to {target.parent}')
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(file.path, target, follow_symlinks=True)
                coppied.append(target)
    return coppied


def load_template(env, template_path):
    try:
        with open(template_path, 'r') as file:
            template_string = file.read()
    except FileNotFoundError:
        logger.error(f"Template at path {template_path} not found. Use Default template.")
        raise
    logger.debug(f"loaded template from {template_path}")
    return env.from_string(template_string)

def render_template(env, template_path,**kwargs):
    template=load_template(env, template_path)
    rendered_output = template.render(**kwargs)
    return rendered_output