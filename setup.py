"""
Name: setup.py

Description: Package configuration and installation setup for ToolOps.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from setuptools import setup, find_packages


setup(
    name="toolops",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "postgres": ["asyncpg>=0.27.0"],
        "semantic": ["sentence-transformers>=2.2.0", "numpy>=1.24.0"],
        "openai": ["openai>=1.0.0"],
        "otel": ["opentelemetry-api>=1.24.0", "prometheus-client>=0.17.0"],
        "all": [
            "asyncpg>=0.27.0",
            "sentence-transformers>=2.2.0",
            "numpy>=1.24.0",
            "openai>=1.0.0",
            "opentelemetry-api>=1.24.0",
            "prometheus-client>=0.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "toolops=toolops.cli:main",
        ],
    },
    author="Hedi Manai",
    author_email="hedi.manai.pro@gmail.com",
    description="Resilience & Efficiency Layer for AI Agent Tools",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    python_requires=">=3.9",
)