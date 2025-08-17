from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jobsim",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A discrete event simulation system for job execution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jobsim",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/jobsim/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: System :: Distributed Computing",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    # No external dependencies - all modules are from Python standard library
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "jobsim=jobsim.jobsim:main",
            "jobgen=jobsim.jobgen:main",
            "sim-config=jobsim.sim_config:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
