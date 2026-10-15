# Lesson template

## Lesson N: Form submission to D365

**Goal:** Know how a form gets from the browser to D365.

**Code:** `app/src/Forms/SubmitHandler.php`, `themes/app/src/js/forms/submit.ts`
**Read:** [D365 integration spec](https://example.atlassian.net/wiki/spaces/X/pages/123)
**Why it is built this way:** One line from the decision page
> Warning - Conflict: This page says the form posts directly to D365. The code sends it through a queued job. Trust the code. See Docs to update #2.

**Exercise:** ...

**Check questions:**
1. ...
2. ...

- [ ] Done

Rules:
- Without Confluence, leave out the **Read** and **Why** lines.
- If the code cannot answer a question, write "Ask your lead: ...".
- Code paths are repo-relative, in backticks, and exist. Use `file:line` only for a line that exists.

## Skip for now

- Without Confluence: vendor files, legacy modules, generated files.
- With Confluence: also old meeting notes, retros, archived projects, out-of-date specs.

## Possibly stale

Only with Confluence. Pages not updated after the code they name changed.

- [Local setup](https://example.atlassian.net/wiki/spaces/X/pages/101): last updated 2024-03-02, `composer.json` changed 2025-06-01.

## Ask your lead

- Ask your lead: ...

## Docs to update

Found on 2026-10-15 from the code on `main` at `a1b2c3d`. Code is the source of truth.

| # | Page | Last updated | Page says | Code does | Evidence | Suggested fix |
|---|---|---|---|---|---|---|
| 1 | [Local setup](https://example.atlassian.net/wiki/spaces/X/pages/101) | 2024-03-02 | Use PHP 8.1 | PHP 8.3 is necessary | `composer.json:12` | Change to PHP 8.3 |

Rules:
- Evidence is required: a `file:line` that the check script confirms. No evidence, no conflict.
- The header records the date and the commit.
- Only real conflicts go here. An old page that agrees with the code stays in "Possibly stale".
- Do not edit or comment on Confluence. A person does the update.
- Optional: an Owner column with the page's last editor.
