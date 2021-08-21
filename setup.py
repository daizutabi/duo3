import os
import re
import subprocess
import sys

from setuptools import setup


def get_version(package: str) -> str:
    """Return version of the package."""
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), package, "__init__.py"
    )
    with open(path, "r") as file:
        source = file.read()
    m = re.search(r'__version__ = ["\'](.+)["\']', source)
    if m:
        return m.group(1)
    else:
        return "0.0.0"


def get_packages(package):
    """Return root package and all sub-packages."""
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


long_description = ""


def check():
    def run(command):
        assert subprocess.run(command.split()).returncode == 0
        print(f"'{command}' --- OK")

    run("flake8 duo3")
    run("mypy duo3")
    run("flake8 tests")
    run("mypy tests")


def publish():
    check()
    subprocess.run("python setup.py sdist bdist_wheel".split())
    subprocess.run("twine upload dist/*".split())
    version = get_version("duo3")
    subprocess.run(["git", "tag", "-a", f"v{version}", "-m", f"'Version {version}'"])
    subprocess.run(["git", "push", "origin", "--tags"])
    sys.exit(0)


if sys.argv[-1] == "publish":
    publish()

if sys.argv[-1] == "check":
    check()


setup(
    name="duo3",
    version=get_version("duo3"),
    description="DUO3",
    long_description=long_description,
    url="https://github.com/daizutabi/duo3",
    author="daizutabi",
    author_email="daizutabi@gmail.com",
    license="MIT",
    packages=get_packages("duo3"),
    include_package_data=True,
    install_requires=["kivy"],
    python_requires=">=3.9",
    entry_points={"console_scripts": ["duo3 = duo3.app:main"]},
)
