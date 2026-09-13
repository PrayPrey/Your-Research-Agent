from setuptools import setup, find_packages

setup(
    name="h_m1",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "numpy",
        "matplotlib",
        "pandas",
    ],
)
