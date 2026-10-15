# onboard

A Claude Code skill. It writes a Markdown onboarding lesson plan for a new developer or QA
from a repo and an optional Confluence page or space. The plan is saved outside the repo.

## Requirements

- Python 3 (standard library only) and `git`, for `scripts/check_plan.py`
- Optional: the `confluence` skill at `~/.claude/skills/confluence`. Only Confluence input needs it.

## Install

    git clone <repo-url> ~/src/onboard
    ln -sfn ~/src/onboard ~/.claude/skills/onboard

## Inputs

- Repo path (default: current folder)
- Confluence page or space (optional; needs the `confluence` skill set up)
- Role: `developer` or `qa`
- Time budget (default 5 days)
- Output folder (default `~/.claude/onboarding/<repo-name>/`)

## Use

    /onboard repo ~/code/my-project, role qa, 5 days, Confluence <page URL>
    /onboard next        # tutor mode: teach the next unticked lesson
    /onboard review 3    # teach lesson 3 again; checkboxes do not change

## Check

    python3 scripts/check_plan.py <plan.md> <repo-path>
    source ~/.claude/skills/confluence/scripts/confluence-auth.sh && export CONFLUENCE_AUTH CONFLUENCE_SERVER && python3 scripts/check_plan.py <plan.md> <repo-path>
    python3 -m unittest scripts/test_check_plan.py

The script checks paths, `file:line`, `file:a-b` and `/pages/<id>` Confluence links. It reads
`CONFLUENCE_AUTH` and `CONFLUENCE_SERVER` from the environment.
