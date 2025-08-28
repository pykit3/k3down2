# DO NOT EDIT!!! built with `python _building/build_setup.py`
import setuptools

setuptools.setup(
    name="k3down2",
    packages=["k3down2"],
    version="0.1.19",
    license="MIT",
    description="convert markdown segment into easy to transfer media sucha images.",
    long_description="# k3down2\n\n[![Build Status](https://travis-ci.com/pykit3/k3down2.svg?branch=master)](https://travis-ci.com/pykit3/k3down2)\n![Python package](https://github.com/pykit3/k3down2/workflows/Python%20package/badge.svg)\n[![Documentation Status](https://readthedocs.org/projects/k3down2/badge/?version=stable)](https://k3down2.readthedocs.io/en/stable/?badge=stable)\n[![Package](https://img.shields.io/pypi/pyversions/k3down2)](https://pypi.org/project/k3down2)\n\nconvert markdown segment into easy to transfer media sucha images.\n\nk3down2 is a component of [pykit3] project: a python3 toolkit set.\n\n\nk3down2 is utility to convert markdown segment into easy to transfer media sucha images.\nIt depends on:\n\n- pandoc to render markdown snippet to html, such as tables.\n- graphviz to render graphviz to image.\n- google-chrome to render svg/html to png.\n- imagemagick to process images.\n- mmdc to convert mermaid chart to svg. See: https://mermaid-js.github.io/mermaid/#\n\n\n\n\n\n# Install\n\n```\npip install k3down2\n```\n\n# Synopsis\n\n```python\n\n```\n\n#   Author\n\nZhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n#   Copyright and License\n\nThe MIT License (MIT)\n\nCopyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n\n[pykit3]: https://github.com/pykit3",
    long_description_content_type="text/markdown",
    author="Zhang Yanpo",
    author_email="drdr.xp@gmail.com",
    url="https://github.com/pykit3/k3down2",
    keywords=["markdown", "python", "tex"],
    python_requires=">=3.0",
    install_requires=[
        "setuptools",
        "k3ut~=0.1.7",
        "k3proc~=0.2.10",
        "pylatexenc~=2.8",
        "pygments~=2.7.3",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ]
    + [
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
