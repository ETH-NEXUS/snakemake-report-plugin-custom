
try:
    from snakemake.logging import logger
except ImportError:
    from snakemake import logger

def get_vars(obj):
    if hasattr(obj, "__dict__"):
        return vars(obj)
    return obj


def print_content(**kwargs):
    """
    This function prints the content of the provided arguments
    """
    logger.info("\n- ".join(kwargs.keys()))
    if "configfiles" in kwargs:
        logger.info("\n--- CONFIGFILES ---")
        logger.info(kwargs['configfiles'])

    if "dag" in kwargs:
        dag=kwargs["dag"]
        logger.info("\n--- DAG ---")
        logger.info(dag)
        for k, v in vars(dag).items():
            logger.info(f"{k}: {v}")
        workflow = vars(dag)["workflow"]
        logger.info("\n--- WORKFLOW ---")
        logger.info(workflow)
        logger.info("\n--- RULES ---")

        for rule in workflow.rules:
            logger.info(rule)
            logger.info(f"Rule name: {rule.name}")
            logger.info(f"Rule input files: {rule.input}")
            logger.info(f"Rule output files: {rule.output}")
            logger.info(f"Rule benchmark files: {rule.benchmark}")

    if "jobs" in kwargs:
        logger.info("\n--- JOBS ---")
        for job in kwargs["jobs"]:
            # Convert job object to a dictionary if possible
            logger.info((job))

    if "results" in kwargs:
        logger.info("\n--- RESULTS ---")
        for cat, subcats in kwargs["results"].items():
            logger.info(cat.name)
            for subcat, catresults in subcats.items():
                logger.info(f"  - {subcat.name}")
                for res in catresults:
                    logger.info(f"    - {res.path}")

    if "rule" in kwargs:
        logger.info("\n--- RULES ---")
        rules=kwargs["rules"]
        for rule_name, rule_record in rules.items():
            logger.info(f"Rule: {rule_name}")
            # Convert rule record to dictionary if possible
            logger.info(rule_record)
        for rule in rules.values():
            logger.info(rule)

    # explore what we have:
    for k,value in kwargs.items():
        if k in ["rule", "jobs", "results", "dag", "configfiles"]:
            continue
        logger.info(f"\n--- {k.upper()} ---")
        if isinstance(value, list):
            for item in value:
                logger.info(get_vars(item))
        elif isinstance(value, dict):
            for key, item in value.items():
                logger.info(f"{key}: {get_vars(item)}")
        else:
            logger.info(get_vars(value))