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

# Skills

Reusable agent skills may be available in the current directory or installed in `/SKILLS`, an absolute directory
separate from the project repository.

Before performing a task:

1. If `/SKILLS` exists, run `git -C /SKILLS pull` to update the skills repository.
2. Recursively search the current directory for `SKILL.md` files. Also search `/SKILLS` recursively if that directory
   exists.
3. Use the skills' frontmatter names and descriptions to identify skills relevant to the task. `/SKILLS/README.md`,
   when present, provides an optional discovery index.
4. Read and follow the applicable skills before proceeding. Resolve their relative references from the directory
   containing the skill's `SKILL.md`.

Load only relevant skills and supporting references. If no skill applies, proceed with the task using the project's
instructions and available tools.

Before preparing or making a Git commit, find and read the `write-git-commit-messages` skill in the locations above, if
available.
