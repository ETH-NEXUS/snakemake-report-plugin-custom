from matplotlib import pyplot as plt
import pandas as pd
from glob import glob
from os import path
import re
from io import BytesIO
import base64
import matplotlib
matplotlib.use("Agg")  # Use Agg backend for rendering plots

from snakemake.io import (regex_from_filepattern,
                          apply_wildcards,
                          Namedlist
                          # glob_wildcards,
                          )
from jinja2 import Environment, FileSystemLoader
import datetime

try:
    from snakemake.logging import logger
except ImportError:
    from snakemake import logger

def render_resource_html(workflow, output_dir, html_filename, template_dir, template_file, embedded):
        if not embedded:
            try:
                (output_dir / "img").mkdir(parents=True, exist_ok=False)
            except FileExistsError:
                logger.error(f'resources report folder "{output_dir}" already exists')
                exit(1)
        benchmark_results = []
        for rule in workflow.rules:
            
            logger.info(rule)
            logger.info(f"Rule name: {rule.name}")
            logger.info(f"Rule input files: {rule.input}")
            logger.info(f"Rule benchmark files: {rule.benchmark}")
            if rule.benchmark is not None:
                rule_benchmark = {"rule_name": rule.name}
                try:
                    fig, axs, infos = create_benchmark_plot(
                        rule.name, rule.benchmark, rule.input
                    )
                except ValueError as e:
                    logger.error(e)
                    continue
                if not embedded:
                    # Save to file
                    img = path.join( "img", f"{rule.name}_benchmark.png")
                    fig.savefig(path.join(output_dir, img))
                else:
                    # get the uri
                    buffer = BytesIO()
                    fig.savefig(buffer, format='png') 
                    buffer.seek(0)
                    # Convert the buffer to a base64 string
                    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                    buffer.close()

                    # Step 4: Create a data URI for the image
                    img= f"data:image/png;base64,{img_base64}"

                
                rule_benchmark["image"] = img
                rule_benchmark["caption"] = "\n".join(
                    [f"* {k}: {v}" for k, v in infos.items()]
                )
                benchmark_results.append(rule_benchmark)
        # Load the Jinja2 template
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_file)
        # Prepare data for the report
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Render the report content
        report_content = template.render(results=benchmark_results, now=now)
        # Write the rendered content to the report file
        report_path = path.join(output_dir, html_filename)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        logger.info(f"Report generated at {report_path}")

def create_benchmark_plot(rule_name, benchmark_file, input_names):
    # rule = "celltype_gsva"
    # wdir = "/cluster/work/drscs/scRNA/08_metacells/02_melanoma"
    resources = {}
    benchmark_regex = re.compile(regex_from_filepattern(benchmark_file))
    # glob benchmark files
    # wildcards=glob_wildcards(benchmark_file) # not that useful
    benchmark_glob = re.sub(r"{.*?}", "*", benchmark_file)
    for bm_file in glob(benchmark_glob):
        # find wildcard values
        logger.debug(bm_file)
        match = benchmark_regex.match(bm_file)
        wildcards = match.groupdict()
        wildcard_string = "; ".join(f"{k}={v}" for k, v in wildcards.items())
        fn = path.basename(bm_file)
        logger.debug(f"{fn}\n Wildcards: {wildcard_string}")
        # check for corresponding input files
        input_files = [
            in_file(Namedlist(fromdict=wildcards)) if callable(in_file) else apply_wildcards(in_file, wildcards) for in_file in input_names 
        ]
        try:
            input_size = sum(path.getsize(in_file) for in_file in input_files)
        except FileExistsError as e:
            logger.error(
                "Cannot find input filed for wildcard "
                f"{wildcard_string}\n{e}"
            )
            input_size = 0
        # read snakemake benchmark file
        stats = pd.read_csv(bm_file, sep="\t")
        resources["_".join(wildcards.values())] = {
            "mem": stats["max_rss"][0],
            "time": stats["s"][0],
            "input_size": input_size,
        }
    if not resources:
        raise ValueError("No matching benchmark files found for "
                         f"{rule_name}:\n{benchmark_file}")
    infos = {"n jobs": len(resources)}
    df = pd.DataFrame.from_dict(resources, orient="index")
    logger.debug(df)
    # Create the scatter plot
    fig, ax1 = plt.subplots()

    # Plot input size vs. memory
    ax1.scatter(
        df["input_size"] / 2**30,
        df["mem"] / 2**10,
        color="blue",
        label="Max RSS",
        marker="o",
    )
    ax1.set_xlabel("Input Size (GB)")
    ax1.set_ylabel("used memory (GB)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    # Create a second y-axis for time
    ax2 = ax1.twinx()
    ax2.scatter(
        df["input_size"] / 2**30,
        df["time"] / 60,
        color="red",
        label="Time (min)",
        marker="x",
    )
    ax2.set_ylabel("Runtime (min)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")
    # Add grid and legend
    ax1.grid(True)
    fig.legend(loc="upper left", bbox_to_anchor=(0.15, 0.85))
    # Set title
    plt.title(rule_name)
    
    # plt.savefig(path.join(out_path, file_path))
    return (fig, [ax1, ax2], infos)
