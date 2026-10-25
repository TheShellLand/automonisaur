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

Before performing any task, select the shared skills directory:

1. If `/SKILLS` exists, use `/SKILLS`.
2. Otherwise, use `/tmp/SKILLS`. If it does not exist, run:

   ```sh
   git clone https://github.com/TheShellLand/SKILLS.git /tmp/SKILLS
   ```

Both paths are absolute and separate from this project. Reuse an existing directory; do not overwrite it or check
for a `.git` folder before running Git commands against it.

Run `git -C <skills-directory> pull --rebase` against the selected directory before searching for or reading skills.
Then read and follow its `AGENTS.md` in addition to this project's instructions. When using `/tmp/SKILLS`, treat
references to `/SKILLS` in the shared instructions as references to `/tmp/SKILLS`, including update and discovery steps.

Update the selected directory and discover and use relevant skills on every task, even if the instructions or skills
were read during an earlier task. If an update changes `AGENTS.md`, read the updated file before continuing.

If cloning or updating fails, report the failure and continue with available local skills unless the failure prevents
completing the task correctly. If the selected directory's `AGENTS.md` is missing, report that and continue using this
project's instructions and available tools.
