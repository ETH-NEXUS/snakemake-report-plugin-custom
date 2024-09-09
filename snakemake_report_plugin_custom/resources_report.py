from matplotlib import pyplot as plt
import pandas as pd
from glob import glob
from os import path
import re
import matplotlib

matplotlib.use("Agg")  # Use Agg backend for rendering plots
try:
    from snakemake.logging import logger
except ImportError:
    from snakemake import logger


def substitute_wildcards(filename, wildcards):
    # Find all wildcards in the pattern using regex
    found_wildcards = re.findall(r"{(\w+)}", filename)
    # Filter the wildcards to those present in the pattern
    substitutions = {k: v for k, v in wildcards.items() if k in found_wildcards}
    # Perform the substitution
    return filename.format(**substitutions)


# todo: this would be cool in a custom report


def create_benchmark_plot(rule_name, benchmark_file, input_names, out_path):
    # rule = "celltype_gsva"
    # wdir = "/cluster/work/drscs/scRNA/08_metacells/02_melanoma"
    resources = {}
    benchmark_pattern = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", benchmark_file)
    benchmark_re = re.compile(benchmark_pattern)
    benchmark_glob = re.sub(r"{\w+}", "*", benchmark_file)
    # glob benchmark files
    for bm_file in glob(benchmark_glob):
        # find wildcard values
        match = benchmark_re.match(bm_file)
        wildcards = match.groupdict()
        wildcard_string = "; ".join(f"{k}={v}" for k, v in wildcards.items())
        fn = path.basename(bm_file)
        logger.debug(f"{fn}\n Wildcards: {wildcards}")
        # check for corresponding input files
        input_files = [
            substitute_wildcards(in_file, wildcards) for in_file in input_names
        ]
        try:
            input_size = sum(path.getsize(in_file) for in_file in input_files)
        except FileExistsError as e:
            logger.error(
                "Cannot find input filed for wildcard "
                f"{wildcard_string}\n{e.message}"
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
    # Save to file
    file_path = path.join("img", f"{rule_name}_benchmark.png")

    plt.savefig(path.join(out_path, file_path))
    return (file_path, infos)
