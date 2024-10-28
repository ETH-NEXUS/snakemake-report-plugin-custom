from jinja2 import Environment, FileSystemLoader
import datetime
from os import path
import pathlib
import shutil
import pandas as pd
import yaml
import markdown
from markdown.extensions.attr_list import AttrListExtension
import snakemake

try:
    from snakemake.logging import logger
except ImportError:
    from snakemake import logger

from snakemake.report import FileRecord


# monkey patching of the snakemake FileRecord class that gets passed to respective templates as variables
HTTP_IMAGE_SETTINGS=("width", "height", "style", "align")
MD_TABLE_SETTINGS = [
    "index",     # Whether to show the DataFrame index (True/False)
    "headers",       # Specify headers; can be "keys" or a list of column names
    "floatfmt",      # Format for floating-point numbers, e.g., ".2f"
    "numalign",      # Alignment for numeric columns ("left", "center", "right")
    "stralign",      # Alignment for string columns ("left", "center", "right")
    "missingval",    # Placeholder for missing values (default is "")
    "colalign"       # Alignment for individual columns, given as a tuple/list of alignments
]

def _render_file_record_default(self):
    return self.show()
    
def _render_file_record(self, **params):
    # render as markdown    
    rendered=[] 
    render_type=self.render_settings.get("type", "unknown")
    params={**self.render_settings,**params}
    logger.debug(f"render {self.path} as {render_type} with settings {params}")
    if not self.render_settings.get("hide", False):
        if self.render_settings.get("type") == "image":
            params.setdefault('alt',self.path.name)
            if any( p in params for p in HTTP_IMAGE_SETTINGS ):        
                settings_list=[f' alt="{ params["alt"] }"'] + \
                    [f' {k}="{ params[k] }"' for k in HTTP_IMAGE_SETTINGS if k in params]
                rendered.append(f'<img src="{ self.path }"{"".join(settings_list)}>') 
            else:
                rendered.append(f'![{params["alt"]}]({self.path})')
        elif self.render_settings.get("type") == "table":        
            sep=self.render_settings.get("sep")
            df=pd.read_table(self.path, sep=sep)
            if "max_row" in params:
                df=df.head(params["max_row"])
            if "col_select" in params:
                try:
                    df=df.iloc[:,params["col_select"]]
                except IndexError as e:
                    logger.error(f'ignoring col_select="{params["col_select"]}" for {self.path.name}: {e}')
            rendered.append(df.to_markdown(**{k:v for k,v in params.items() if k in MD_TABLE_SETTINGS})) # or to_html()
    if self.render_settings.get("show_link", True):
        #rendered.append(f'<li><a href="{ file.path }">{ file.path }</a></li>')
        rendered.append(f'[{self.path}]({self.path})')
    if self.caption and self.render_settings.get("show_caption", True):
        rendered.append(self.caption)
    return("\n".join(rendered))
    

def set_default_render_settings(self, suffix_params):
    # overwrite the class attribute with instance specific defaults
    suffix=self.path.suffix[1:]
    if suffix in suffix_params.get("table", ('csv', "tsv")):
        p={"type":"table", **self.default_render_settings["table"]}
        p["sep"]=p["sep"].get(suffix,",")
    elif suffix in suffix_params.get('image',("png", "jpg")):
        p={"type":"image", **self.default_render_settings["image"]}
    else:
        p={"type":"other", **self.default_render_settings["other"]}
    self.render_settings=p
    

def set_render_settings(self, params, presets):
    # overwrite general settings with specific settings    
    # logger.debug(f"setting rendering options for {self.path.name}: {self.render_settings} <- {params}")
    render_type=self.render_settings["type"]
    params=params.get(render_type, {})
    if not params:
        params={ **presets.get(render_type, {}).get("default", {}), **self.render_settings}
        logger.debug(f"using default preset for {render_type}: {params}")
    elif isinstance(params, str):
        try:
            params=presets[render_type][params]
        except KeyError:
            logger.error(f'no preset "{params}" for files of type "{render_type}"')
            params={}
    # logger.debug(f"setting rendering options for {self.path.name}: {self.render_settings} <- {params}")
    p={**self.render_settings, **params}
    if render_type=="table":
        if isinstance(p["sep"], dict):
            suffix=self.path.suffix[1:]
            p["sep"]=p["sep"].get(suffix,",")
    logger.debug(f"rendering options for {self.path.name}: {p}")
    self.render_settings=p
    
# redering function
FileRecord.show=_render_file_record
FileRecord.__str__=_render_file_record_default
# default render settings
FileRecord.default_render_settings={"table":{"sep":{"cnv":",","tsv":"\t"},"show_link": True}, "image":{"show_link": False}, "other":{"show_link":True}}
# overwrite general settings with specific settings
FileRecord.set_render_settings = set_render_settings
FileRecord.set_default_render_settings = set_default_render_settings


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
    # load user defined rendering options and presets
    default_settings_config=report_config.get("render_options")
    render_presets={}
    default_suffix_params={render_type:params.get("suffix", []) for render_type,params in default_settings_config.items()}
    for render_type in default_settings_config:
        presets=default_settings_config[render_type].pop("presets",{})
        render_presets.setdefault(render_type, {})
        render_presets[render_type]["default"]=default_settings_config[render_type]
        for ps_name, ps_vals in presets.items():
            render_presets[render_type][ps_name]={**default_settings_config[render_type], **ps_vals}
        
    for k,v in default_settings_config.items():
        logger.debug(f"default settings for {k}: {v}")

    for k,v in render_presets.items():
        for ps_k, ps_v in v.items():
            logger.debug(f"preset settings for {k} {ps_k}: {ps_v}")


    for category, subcat_dict in results.items():     
        category.sort_key=category_order.get(category.name, len(category_order) + 1)
        cat_settings={k:v for k,v in toc.get(category.name, {}).items() if k != 'subsections'}
        cat_suffix_params={render_type:params.get("suffix", []) for render_type,params in cat_settings.items() if isinstance(params, dict)}
        subcategory_order={cat:i+1 for i,cat in enumerate(cat_settings.get("subsections", {}))}
        subcategory_order["Other"]=0
        for subcat, result_list in subcat_dict.items():            
            subcat_settings=toc.get(category.name).get("subsections", {}).get(subcat.name, {})
            subcat.sort_key=subcategory_order.get(subcat.name, len(subcategory_order) + 1)
            subcat_suffix_params={render_type:params.get("suffix", []) for render_type,params in subcat_settings.items() if isinstance(params, dict)}
            suffix_params={**default_suffix_params, **cat_suffix_params, **subcat_suffix_params}
            for file in result_list:        
                file.set_default_render_settings(suffix_params) # set default settings
                file.set_render_settings(cat_settings, render_presets) # set category settings
                file.set_render_settings(subcat_settings, render_presets) # set subcategory settings
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