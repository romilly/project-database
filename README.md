# project-database

A Python meta-project to create and maintain a database of my projects.

Goal: make it easier for me to
- find relevant projects
- to keep track of where projects are installed
- see which projects are synced on GitHub
- see which projects are on GitHub but not stored locally.

It will use sql-alchemy + SQLite to start with, and use AI on polwarth.

I'd also like to build a modern web interface.

I'll be building it with help from Claude code.

## Installation

```bash
pip install -e .
```

## Development

```bash
pip install -e .[test]
pytest
```