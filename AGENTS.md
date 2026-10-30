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

# Link to AGENTS-SKILLS.md Instructions

At the start of every task, always read [AGENTS-SKILLS.md](AGENTS-SKILLS.md) in this directory and execute its required workflow before proceeding.
