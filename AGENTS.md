# AGENTS.md

Source ~/venv/automonisaur/bin/activate before running Python code if it exists.

# Git Tasks when commiting changes

- When executing git commands via shell, ensure multi-line messages are passed with actual line breaks (e.g., using real
  multiline string blocks) rather than literal "\\n" escapes which will be rendered literally in commit logs.

- create a descriptive git commit using git diff
- use this specific format for all commits:

  [component] [Descriptive primary action/sentence]

  [A detailed description or paragraph explaining exactly what was changed and why.]

- use these rules when told to increment code version number:
    - read file setup.py
    - get `version` number
    - version number is formated as: MAJOR.MINOR.PATCH
    - increment PATCH by one
    - get all commits up until the last version number and group commits by `[component]`
    - tag the new commit with the new `version` number
    - use this specific format for commiting a new code version number:

```
{version}

Change log:

{list of grouped commits}
```
