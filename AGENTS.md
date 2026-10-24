# AGENTS.md

Source ~/venv/automonisaur/bin/activate before running Python code if it exists.

# Git Tasks when commiting changes

- create a descriptive git commit using git diff 
- use this specific format for all commits:

  [component] [Descriptive primary action/sentence]

  [A detailed description or paragraph explaining exactly what was changed and why.]

- use these rules when told to increment code version number:
  - read file setup.py
  - get `version` number
  - version number is formated as: MAJOR.MINOR.PATCH

- use this specific format for commiting a new code version number: 
```
{increment PATCH by one}

Change log:

{get all commits up until the last version number and group commits by [component]}
```
