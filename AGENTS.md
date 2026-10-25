# AGENTS.md

## Python environment

Before running Python code, source `~/venv/automonisaur/bin/activate` if it exists.

## Git commits

- Review `git diff` to write a descriptive commit message explaining what changed and why.
- When passing multiline commit messages through the shell, use actual line breaks rather than literal `\n` escapes.
- Use the following format for regular commits. Version bump commits use the format in the next section.

```text
[component] Descriptive primary action or sentence

A detailed description explaining exactly what changed and why.
```

## Version bumps

When instructed to increment the code version:

1. Read the current `version` in `setup.py`. The format is `MAJOR.MINOR.PATCH`.
2. Increment `PATCH` by one and update `setup.py`.
3. Collect commits since the previous version and group them by `[component]` for the change log.
4. Commit the version bump using the format below.
5. Tag the new commit with the new version number.

```text
{version}

Change log:

{list of grouped commits}
```

# Shared Agent Instructions

Before performing any task, check whether the `/SKILLS` directory and `/SKILLS/AGENTS.md` file exist.
If both exist, read and follow `/SKILLS/AGENTS.md` in addition to this project's instructions.
`/SKILLS` is an absolute path to the shared skills Git repository, separate from this project. Do not check for
a `.git` folder before using it.

When the shared instructions are available, follow them for updating `/SKILLS` and discovering and using relevant skills
on every task,
even if those instructions or skills were read during an earlier task. If updating `/SKILLS` changes its
`AGENTS.md`, read the updated file before continuing.

If either the directory or file is missing, continue using this project's instructions and available tools.
