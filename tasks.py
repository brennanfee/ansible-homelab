from invoke import task

"""
To use this script you need to install 'invoke'.  This is best done globally using pip or pipx.

`pipx install invoke`

Afterword, you can execute any of these tasks in the terminal with `inv {task name}`.

To target a particular sceario run `inv {task name} --scenario={scenario name}`

For more info:  https://www.pyinvoke.org
"""

scenarios = [
    "default",
    "full_cicd",
    "bootstrap",
    "common",
    "install_apps",
    "install_fonts",
    "virtualbox_guest",
]


@task()
def lint(ctx):
    ctx.run("./lint")


@task(help={"scenario": "The molecule scenario to use.  Default is the default scenario."})
def test(ctx, scenario="default"):
    ctx.run(f"poetry run molecule test -s {scenario}")


@task(help={"scenario": "The molecule scenario to use.  Default is the default scenario."})
def create(ctx, scenario="default"):
    ctx.run(f"poetry run molecule create -s {scenario}")


@task(help={"scenario": "The molecule scenario to use.  Default is the default scenario."})
def converge(ctx, scenario="default"):
    ctx.run(f"poetry run molecule converge -s {scenario}")


@task(help={"scenario": "The molecule scenario to use.  Default is the default scenario."})
def login(ctx, scenario="default"):
    ctx.run(f"poetry run molecule login -s {scenario}")


@task(help={"scenario": "The molecule scenario to use.  Default is the default scenario."})
def verify(ctx, scenario="default"):
    ctx.run(f"poetry run molecule verify -s {scenario}")


@task(help={"scenario": "The molecule scenario to use.  Default is the default scenario."})
def reset(ctx, scenario="default"):
    ctx.run(f"poetry run molecule reset -s {scenario}")


@task(help={"scenario": "The molecule scenario to use.  Default is the default scenario."})
def destroy(ctx, scenario="default"):
    ctx.run(f"poetry run molecule destroy -s {scenario}")


@task()
def resetAll(ctx):
    for scenario in scenarios:
        ctx.run(f"poetry run molecule reset -s {scenario}")


@task()
def destroyAll(ctx):
    for scenario in scenarios:
        ctx.run(f"poetry run molecule destroy -s {scenario}")


@task()
def list(ctx):
    ctx.run("poetry run molecule list")
