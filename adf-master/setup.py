import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="adf-mcp",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="ADF检验MCP工具 - 时间序列平稳性检验",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/adf-mcp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastmcp>=2.12.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "statsmodels>=0.13.0",
        "tqdm>=4.67.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0",
            "isort>=5.0",
            "mypy>=0.950",
        ],
    },
)
