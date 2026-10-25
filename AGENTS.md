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
