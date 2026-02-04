from pathlib import Path

from setuptools import find_packages, setup

_readme = Path(__file__).parent / "README.md"
setup(
    name="ecoscore-sdk",
    version="0.1.0",
    description="Python client for the Product Sustainability & Impact Assessment API (sustainability, CO2, water, CBAM).",
    long_description=_readme.read_text(encoding="utf-8") if _readme.exists() else "",
    long_description_content_type="text/markdown",
    author="EcoScore",
    url="https://github.com/autozbudoucnosti/ecoscore-sdk",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["httpx>=0.26.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
    ],
    keywords="sustainability carbon co2 cbam e-commerce api client",
)
