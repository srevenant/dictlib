import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name = 'dictlib',
  packages = ['dictlib'],
  version = '1.1.3',
  description = 'Dictionary Library including good deep merge and dictionary as objects',
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  author = 'Brandon Gillespie',
  author_email = 'bjg-pypi@cold.org',
  url = 'https://github.com/srevenant/dictlib', 
  keywords = ['dict', 'union', 'object', 'dig', 'dug'],
  classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
  ],
)

