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

When asked to bump the version, create a patch release:

1. Read `version` in `setup.py` as `MAJOR.MINOR.PATCH` and identify its matching Git tag.
2. Collect commits from that tag through `HEAD`, excluding the tagged release commit. Group them by their
   `[component]` prefix, preserving component names. Put commits without a prefix under `[Other]`.
3. Increment `PATCH` by one in `setup.py`, leaving `MAJOR` and `MINOR` unchanged.
4. Review the diff and commit only the version change using the message format below. Include each collected
   commit's short hash and a readable summary under its component heading.
5. Tag the new commit with the exact new version, without a `v` prefix.
6. Verify that `setup.py`, the commit message, and the tag agree on the new version, and that the tag points to
   the release commit. Report the version, commit hash, and remaining working-tree changes.

Use actual line breaks in the commit message, preferably with `git commit -F <message-file>`:

```text
{version}

Change log:

[component]
- {short-hash} {commit summary}

[another component]
- {short-hash} {commit summary}
```

# Shared Agent Instructions

## Select the shared skills directory

At the start of every task, select one shared skills directory:

1. If `/SKILLS` exists, use `/SKILLS`.
2. Otherwise, use `/tmp/SKILLS`. If it does not exist, run:

   ```sh
   git clone https://github.com/TheShellLand/SKILLS.git /tmp/SKILLS
   ```

Both paths are absolute and separate from this project. Reuse an existing directory without overwriting it or
checking for a `.git` folder before running Git commands against it. In the steps below, `<skills-directory>` means
the selected path. Treat references to `/SKILLS` in shared instructions as references to that path, including update
and discovery steps.

## Prepare and execute each task

Perform this workflow once per task, even if instructions or skills were read during an earlier task:

1. Run `git -C <skills-directory> pull --rebase` before searching for or reading skills.
2. Read and follow the selected directory's updated `AGENTS.md` in addition to this project's instructions.
3. Recursively discover `SKILL.md` files in both the current project and the selected shared directory.
4. Inspect skill names and descriptions, then read each applicable skill and its required references before
   executing the task. Resolve relative references from the skill's directory.
5. Execute the task using the applicable preparation, execution, and verification requirements. If no skill applies,
   follow the project and shared instructions.
6. Before reporting completion, verify that actual tool calls and results support compliance with those requirements.

## Handle preparation failures

If cloning or updating fails, report the failure and continue with available local skills unless the failure prevents
completing the task correctly. If the selected directory's `AGENTS.md` is missing, report that and continue using
this project's instructions and available tools. Do not silently skip required steps or claim full compliance when
a requirement could not be completed.
