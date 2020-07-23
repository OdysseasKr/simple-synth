import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simplesynth",
    version="0.0.1",
    author="Ody",
    description="A simple-to-use subtractive synthesizer for Python..",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OdysseasKr/simple-synth",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
