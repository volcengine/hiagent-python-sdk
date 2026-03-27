"""Setup configuration for cli-anything-hiagent package."""

from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cli-anything-hiagent",
    version="0.1.0",
    author="Hiagent",
    author_email="noreply@anthropic.com",
    description="Command-line interface for HiAgent Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.volcengine.com/product/hiagent",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Shells",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
        "pydantic>=2.0.0",
        "hiagent-api>=0.1.0,<3.0.0",
        "hiagent-components>=0.1.0,<3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-hiagent=cli_anything.hiagent_sdk.hiagent_cli:cli",
        ],
    },
    package_data={
        "cli_anything.hiagent_sdk": ["skills/*.md"],
    },
    include_package_data=True,
    zip_safe=False,
)
