import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DateCleaning",
    version="2.0.0",
    author="aabushnell",
    author_email="aabushnell@gmail.com",
    description="A package that gets a date and outputs a clear time period",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LongRunGrowth/DateCleaning",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["googletrans",
                      "pytest",
                      "pandas",
                      "pyspellchecker",
                      "requests",
                      "dateparser",
                      "numpy",
                      "nltk",
                      "wheel",
                      "SQLAlchemy",
                      "fuzzywuzzy",
                      "python-Levenshtein",
                      "autocorrect",
                      "shapely",
                      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
