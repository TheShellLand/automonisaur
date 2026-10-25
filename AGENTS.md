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

1. If `/SKILLS` exists, run `git -C /SKILLS pull --rebase` before searching for or reading skills and before doing the task.
   This is required for every task, including commit requests, even when the skill files are already available
   locally or were read during an earlier task. Local availability does not establish that the skills are current.
   Do not skip the command to save time or because the task seems possible with cached instructions.
   If the command fails, report the failure; do not claim the update succeeded. Continue using local skills unless
   the failure prevents completing the task correctly.
2. Recursively search the current directory for `SKILL.md` files. Also search `/SKILLS` recursively if that directory
   exists.
3. Use the skills' frontmatter names and descriptions to identify skills relevant to the task.
4. Read and follow the applicable skills before proceeding. Resolve their relative references from the directory
   containing the skill's `SKILL.md`.

Load only relevant skills and supporting references. If no skill applies, proceed with the task using the project's
instructions and available tools.

Best: `/SKILLS` exists, so run `git -C /SKILLS pull --rebase`, then discover and read the applicable skill, then do the task.
Avoid: read an existing local skill and skip the pull because its contents seem sufficient to complete the request.

Before preparing or making a Git commit, find and read the `write-git-commit-messages` skill in the locations above, if
available.

## Terminal Command Rules

- Run Bash scripts with `bash /path/to/script.sh`, not `./script.sh` or a bare script path. For POSIX shell
  scripts, use `sh /path/to/script.sh`. Use the script's required interpreter explicitly, including in Git editor
  commands. Do not rely on executable permissions or shebang execution, or use `chmod +x` as a workaround.
- Keep each terminal execution call on one line.
- Never use literal `\n` sequences or escaped newlines to separate commands.
- Use `&&` when the next command requires the previous command to succeed.
- Use `;` only when commands should run independently.
- For multiline scripts or content, use a file-writing tool, then execute the saved file.
