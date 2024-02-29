import re

import click
import toml


@click.group()
def cli():
    """Base command group."""


def get_config_parameter(path: str):
    """Prints config parameter from pyproject.toml file."""

    data = toml.load("pyproject.toml")

    for key in path.split("."):
        data = data.get(key, {})

    return data


@cli.command("print")
@click.argument("path")
def print_config_parameter(path: str):
    """Prints config parameter from pyproject.toml file."""

    print(get_config_parameter(path=path))


@cli.command("version")
@click.argument("path")
def print_version(path: str):
    """Prints version from pyproject.toml file."""

    py_version_pattern = r"py3(?P<minor>[0-9]+)"
    py_version_replace = r"3.\g<minor>"

    version = get_config_parameter(path)

    result = ""

    if isinstance(version, list):
        result = [re.sub(py_version_pattern, py_version_replace, item) for item in version]
    elif isinstance(version, str):
        if version.startswith("^"):
            version = version[1:]

        result = re.sub(py_version_pattern, py_version_replace, version)

    print(result)


def main():
    cli()


if __name__ == "__main__":
    main()
