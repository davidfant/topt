from setuptools import setup, find_packages

setup(
  name="topt",
  version="0.0.1",
  author="David Fant",
  author_email="david@fant.io",
  description="A Python library for LLM token optimization",
  long_description=open("README.md", "r").read(),
  long_description_content_type="text/markdown",
  url="https://github.com/davidfant/topt",
  packages=find_packages(),
  python_requires='>=3.6',
  install_requires=[
    "pydantic",
    "json5",
    "yaml",
  ],
  extras_require={
    "test": [
      "pytest",
      "pytest-cov",
    ],
  },
)