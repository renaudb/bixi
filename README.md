Bixi API Client
===============

[![PyPI](https://img.shields.io/pypi/v/bixi-sdk.svg)](https://pypi.org/project/bixi-sdk/)
[![License](https://img.shields.io/github/license/renaudb/bixi.svg)](LICENSE)
[![pre-commit](https://github.com/renaudb/bixi/actions/workflows/ci.yml/badge.svg)](https://github.com/renaudb/bixi/actions/workflows/ci.yml)

## Description

Simple Bixi API Client

## Documentation

Full documentation is available at [bixi.readthedocs.io](https://bixi.readthedocs.io/en/latest/).

## Installation

```bash
pip install bixi-sdk
```

## Example

```python
from bixi import Bixi

bixi = Bixi.login("username", "password")
rides = bixi.rides()

for ride in rides:
    print(ride)
```
