import click
from subprocess import call
import sys
from virl.api import VIRLServer
from virl.helpers import (
    store_sim_info,
    get_cml_client,
    safe_join_existing_lab_by_title,
    safe_join_existing_lab,
    check_lab_cache,
    cache_lab,
    set_current_lab,
)


# This may need to become a helper
def check_lab_cache_server(lab_id, client):
    """
    check if a lab exists in either the cache or the server.
    if on server and not in cache, cache the lab.
    """
    ret = None

    if not check_lab_cache(lab_id):
        lab_obj = safe_join_existing_lab(lab_id, client)
        if lab_obj:
            cache_lab(lab_obj)
            ret = lab_id
    else:
        ret = lab_id

    return ret


@click.command()
@click.argument("lab", required=False)
@click.option("--id", required=False, help="An existing CML lab ID to start (lab-name is ignored)")
@click.option("--lab-name", "-n", required=False, help="An existing CML lab name to start")
def use(lab, id, lab_name):
    """
    use lab launched elsewhere
    """
    server = VIRLServer()
    client = get_cml_client(server)
    lab_id = None

    if not lab and not id and not lab_name:
        exit(call([sys.argv[0], "use", "--help"]))

    if id:
        lab_id = check_lab_cache_server(id, client)

    # Prefer --lab-name over positional argument
    if lab_name:
        lab = lab_name

    if not id and lab:
        lab_obj = safe_join_existing_lab_by_title(lab, client)
        if lab_obj:
            # Make sure this lab is cached.
            lab_id = check_lab_cache_server(lab_obj.id, client)

    if lab_id:
        set_current_lab(lab_id)
    else:
        click.secho("Unable to find lab in the cache or on the server", fg="red")


@click.command()
@click.argument("sim")
def use1(sim):
    """
    use virl simulation launched elsewhere
    """
    store_sim_info(sim, env="default")  # 'topology-2lkx2'
    click.secho("Now using VIRL simulation {}".format(sim))
