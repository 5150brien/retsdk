import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="retsdk",
    version="1.0.0",
    author="Devlin O'Brien",
    author_email="dobrien@my.ccsu.edu",
    license="MIT",
    keywords="rets real estate",
    description="Python SDK for the real estate transaction standard (RETS)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/5150brien/retsdk",
    packages=setuptools.find_packages(),
    python_requires=">=3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
