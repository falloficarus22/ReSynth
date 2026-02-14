"""
Setup script for ReSynth
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#")]

# Read version from __init__.py
def get_version():
    version_file = os.path.join(this_directory, 'src', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.1.0'

setup(
    name="resynth",
    version=get_version(),
    author="ReSynth Team",
    author_email="resynth@example.com",
    description="Research Paper Synthesis Agent - Fetch, process, and query academic papers with AI-powered answers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/resynth-ai/resynth",
    project_urls={
        "Bug Tracker": "https://github.com/resynth-ai/resynth/issues",
        "Documentation": "https://github.com/resynth-ai/resynth/blob/main/README.md",
        "Source Code": "https://github.com/resynth-ai/resynth",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "isort>=5.10.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "resynth=resynth.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "resynth": [
            "*.md",
            "*.txt", 
            "*.yml",
            "*.yaml",
            "templates/*",
            "static/*",
        ],
    },
    keywords=[
        "research papers",
        "academic literature",
        "machine learning",
        "natural language processing",
        "question answering",
        "information retrieval",
        "arxiv",
        "pubmed",
        "embeddings",
        "vector database",
        "citation generation",
        "paper synthesis",
    ],
    zip_safe=False,
)
