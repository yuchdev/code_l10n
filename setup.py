# -*- coding: utf-8 -*-
import os
import sys
import pathlib
from setuptools import find_packages, setup
from functools import lru_cache

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

@lru_cache(maxsize=1)
def get_package_info(config_path: str = 'pyproject.toml') -> dict:
    """
    Read the package name and version from the pyproject.toml file.

    :param config_path: Path to the pyproject configuration file
    :return: Dict with keys: name, name_dash, version
    :raises RuntimeError: if project section or required fields are missing
    """
    if tomllib is None:
        raise RuntimeError("tomli or tomllib is required to read pyproject.toml. Install with: pip install tomli")

    config_file = pathlib.Path(config_path)
    if not config_file.exists():
        raise RuntimeError(f"Cannot find {config_path}")

    with open(config_file, 'rb') as f:
        data = tomllib.load(f)

    if 'project' not in data:
        raise RuntimeError(f"Cannot read 'project' section from {config_path}")

    project = data['project']
    name = project.get('name')
    version = project.get('version')

    if not name or not version:
        raise RuntimeError(f"'name' and 'version' must be present in [project] of {config_path}")

    return {
        'name': name,
        'name_dash': name.replace('_', '-'),
        'version': version,
    }

PKG = get_package_info()
VERSION = PKG['version']

# Package-wide wheel filename with underscore
PACKAGE_NAME = PKG['name']

# Name with dash (pip name, URL, S3 bucket)
PACKAGE_NAME_DASH = PKG['name_dash']

# Home dir
HOME = pathlib.Path.home()

# Append package dir to sys.path
PROJECT_DIR = os.path.abspath(str(os.path.join(os.path.dirname(os.path.realpath(__file__)))))
sys.path.append(os.path.abspath(os.path.join(PROJECT_DIR, "src", PACKAGE_NAME)))

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text(encoding='utf8')

# Add possible dependencies here
DEPENDENCIES = []

# Github download link
GITHUB_URL = "https://github.com/yuchdev/{PACKAGE_NAME}"

# Wheel filename, e.g. package_name-1.0.0-py3-none-any.whl
WHEEL_FILE = f"{PACKAGE_NAME}-{VERSION}-py3-none-any.whl"

# Tarball filename, e.g. package_name-1.0.0.tar.gz
TARGET_TARBALL = f"{PACKAGE_NAME}-{VERSION}.tar.gz"

# Github download link
GITHUB_DOWNLOAD = f"{GITHUB_URL}/releases/download/release.{VERSION}/{TARGET_TARBALL}"

# AWS download link
AWS_DOWNLOAD = f"https://{PACKAGE_NAME_DASH}.s3.us-east-1.amazonaws.com/packages/{WHEEL_FILE}"

# PyPI project page
PYPI_URL = f"https://pypi.org/project/{PACKAGE_NAME_DASH}/"

# Issue tracker
ISSUE_TRACKER = "{github_url}/issues".format(github_url=GITHUB_URL)

if __name__ == "__main__":
    setup(
        name=PACKAGE_NAME,
        version=VERSION,
        author="Yurii Cherkasov",
        author_email="strategarius@protonmail.com",
        description="The library scans source trees for comments and docstrings in many programming / config languages; detects parts of those comments/docstrings written in a specific non-English language (e.g. Ukrainian); dranslates those parts via a pluggable translation engine (external API or simple built-in engine).",
        long_description=README,
        long_description_content_type="text/markdown",
        license="MIT",
        url=GITHUB_URL,
        download_url=GITHUB_DOWNLOAD,
        project_urls={
            "Bug Tracker": ISSUE_TRACKER,
        },
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 4 - Beta',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Science/Research",

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate you support Python 3. These classifiers are *not*
            # checked by 'pip install'. See instead 'python_requires' below.
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
        packages=find_packages(where=str(HERE / 'src')),
        package_dir={"": "src"},
        package_data={PACKAGE_NAME: ['defaults/*']},
        python_requires=">=3.9",
        install_requires=DEPENDENCIES,
    )
