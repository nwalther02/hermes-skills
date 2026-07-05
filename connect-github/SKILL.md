---
name: connect-github
description: Use when Codex needs live GitHub access or the user says @github, GitHub, repo, PR, pull request, issue, review comments, checks, CI status, branch PR, labels, reactions, or asks to connect/check GitHub. Call the GitHub app/tool first for repository, issue, pull request, comment, reaction, and status data; fall back to local git/gh only for gaps such as branch discovery, commits, pushes, or Actions logs.
---

# Connect GitHub

## Rule

When task needs GitHub state, call GitHub connector tool before answering. Do not rely on stale local knowledge or web search for PR/issue/status data when GitHub app tools are available.

If GitHub tools are not visible, run tool discovery first:

```text
tool_search: "GitHub repository pull request issue status comments"
```

Then use `mcp__codex_apps__github` tools.

## Fast Start

1. Resolve repo scope.
   - Use user-provided `owner/name`, PR/issue URL, or PR number.
   - If user says current repo/branch, inspect local `git remote -v` and `git branch --show-current`.
   - If still ambiguous, ask for repo.
2. Confirm connector only when useful: `_list_installed_accounts` or `_list_installations`.
3. Fetch structured data through GitHub app.
4. Use local `git`/`gh` only for connector gaps: branch creation, commits, pushes, current-branch PR lookup, Actions log bodies.
5. Summarize target, evidence, and next action.

## Tool Map

Use these connector tools when exposed:

- `_list_installed_accounts`: verify available GitHub app accounts.
- `_list_installations`: inspect app installations/org access.
- `_get_pr_info`: PR metadata, refs, state, status, no diff.
- `_fetch_pr`: PR metadata plus diff/patch.
- `_fetch_pr_comments`: merged timeline of issue comments, review comments, reviews.
- `_get_commit_combined_status`: combined commit status and checks.
- `_add_comment_to_issue`: add top-level PR/issue conversation comment.
- `_update_issue_comment`: edit top-level PR/issue conversation comment.
- `_add_reaction_to_pr_review_comment`: react to inline review comment.
- `_remove_reaction_from_pr_review_comment`: remove reaction from inline review comment.
- `_get_pr_review_comment_reactions`: inspect reactions on inline review comment.

## Routing

- PR/issue summary: connector tools only unless local context needed.
- Review feedback: fetch PR + comments; identify actionable unresolved items.
- CI status: get combined status through connector; use `gh run view` only for Actions logs.
- Publish workflow: local git branch/commit/push, then connector or `gh pr create` for PR creation depending available tools.
- Write action: restate exact repo and target PR/issue/comment before changing GitHub.

## Output

Keep response short. Include repo, PR/issue/status inspected, tool path used, and any fallback to `gh`/local git.
