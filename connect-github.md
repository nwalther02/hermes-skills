---
name: "connect-github"
description: "Use when Claude needs live GitHub access or the user says GitHub, repo, PR, pull request, issue, review comments, checks, CI status, branch PR, labels, reactions, or asks to connect/check GitHub. Call the installed github@claude-plugins-official GitHub MCP/tool first for repository, issue, pull request, comment, reaction, and status data; fall back to local git/gh only for gaps such as branch discovery, commits, pushes, PR creation if needed, or Actions logs."
type: "skill"
parameters:
  - name: task
    description: Optional GitHub task, repository, PR, issue, branch, or status scope.
    required: false
---

# Connect GitHub

## Rule

If task needs GitHub state, call GitHub tool before answering. Do not rely on stale local knowledge or web search for PR, issue, repo, review, or status data when GitHub tool is available.

Use installed `github@claude-plugins-official` MCP/GitHub tool first. If GitHub tool is unavailable or unauthenticated, say so briefly, then use local `gh` only when it can answer the request safely.

## Fast Start

1. Resolve repo scope.
   - Use user-provided `owner/name`, PR/issue URL, or PR/issue number.
   - If user says current repo/branch, inspect local `git remote -v` and `git branch --show-current`.
   - If still ambiguous, ask for repo.
2. Use GitHub tool to fetch structured live data.
3. Use local `git` or `gh` only for gaps: branch creation, commits, pushes, current-branch PR lookup, PR creation when needed, or GitHub Actions log bodies.
4. Summarize target, evidence, and next action.

## GitHub Tool Map

Prefer GitHub tool capabilities for:

- Account/install access checks.
- Repository metadata and orientation.
- PR metadata, refs, state, checks, and status.
- PR diffs or changed files.
- PR/issue comments, review comments, and reviews.
- Issue lookup, labels, assignees, milestones, and state.
- Adding or updating top-level PR/issue comments.
- Adding, removing, or inspecting reactions on review comments.

Use `gh` fallback for:

- Discovering current branch PR from local checkout.
- Creating branches, committing, and pushing local changes.
- Opening a PR if no GitHub tool create flow is exposed.
- Reading full GitHub Actions logs.

## Routing

- PR/issue summary: GitHub tool first; local checkout only if current branch context matters.
- Review feedback: fetch PR plus comments/reviews; identify actionable unresolved items.
- CI status: fetch status/checks through GitHub tool; use `gh run view` only for log bodies.
- Publish workflow: local git branch/commit/push, then GitHub tool or `gh pr create` for PR creation.
- Write action: restate exact repo and target PR/issue/comment before changing GitHub.

## Output

Keep response short. Include repo, PR/issue/status inspected, GitHub tool path used, and any fallback to `gh` or local git.
