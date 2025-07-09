from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="dragonwind",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Comprehensive Simulation Platform for China's Renewable Energy Production Capacity and Net Zero Pathways",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dragonwind",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords=[
        "renewable energy",
        "energy transition",
        "climate change",
        "simulation",
        "china",
        "net zero",
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/dragonwind/issues",
        "Source": "https://github.com/yourusername/dragonwind",
    },
)
