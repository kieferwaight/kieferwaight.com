# GitLab publishing boundary

GitLab merge requests are the approval boundary for changes to this site. A content branch may create authored Markdown, assets, diagrams, and related tests; it cannot publish them.

## Flow

1. Create a short-lived branch such as `content/topic` or `refresh/archive-record`.
2. Push the branch to GitLab and open a merge request using the Content template.
3. GitLab validates the merge-request pipeline without R2 or GitHub publishing credentials.
4. A reviewer approves the rendered artifact and evidence, then merges the MR to protected GitLab `main`.
5. The protected `main` pipeline synchronizes R2 assets and PDFs, then mirrors that exact commit to GitHub `main`.
6. The existing GitHub Pages workflow builds and deploys the mirrored commit.

Do not push directly to GitHub `main`. GitHub is the static-hosting target; GitLab owns the review and publishing decision.

## Local issue workflow

The issue board is the work queue. The local Taskfile creates a content branch from the public issue title, runs the full quality suite, then opens a prefilled GitLab merge-request form. It does not merge or deploy.

```sh
# Start a branch such as content/1-zigair-page from gitlab/main.
task issue:start ISSUE=1

# Use refresh or fix when the branch type better describes the work.
ISSUE_BRANCH_KIND=fix task issue:start ISSUE=3

# Validate, commit, push the branch, and open a form prefilled with Closes #1.
task issue:submit ISSUE=1

# Print the issue and MR URLs for the current issue branch.
task issue:status ISSUE=1
```

The helper reads a public GitLab issue title without API credentials. If the issue is private or unavailable, provide the title explicitly: `ISSUE_TITLE="ZigAir Page" task issue:start ISSUE=1`.

During the initial migration, `issue:start` refuses to create a branch while GitLab `main` is behind GitHub `main`. Merge the publishing-boundary MR first; afterward GitLab becomes the branch source for every issue workflow.

## Required project settings

Configure these settings in GitLab before merging this change:

- Protect `main`; allow merges only for the designated maintainer and disallow direct pushes.
- Require one approval from the designated maintainer, disallow author approval, require successful pipelines, and require all discussions to be resolved.
- Mark `R2_BUCKET`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, and `GITHUB_MIRROR_TOKEN` as masked and protected variables.
- Use a fine-grained GitHub token for `GITHUB_MIRROR_TOKEN` with repository contents write access only. It is used only by the protected `mirror_to_github` job.
- Configure GitHub `main` so only the GitLab publisher can push. GitHub Pages continues to deploy when that mirror push reaches `main`.

`GITHUB_MIRROR_TOKEN` is intentionally required by the protected main pipeline. If it is absent, the publish job fails before GitHub is changed.

## Agent and Gemini policy

Agents may create content branches, run local checks, push branches, open merge requests, and respond to review comments. They may not approve or merge merge requests, edit protected-branch settings, access publishing variables, or deploy.

Gemini CLI may draft or review locally with repository instructions as its scope. Keep it outside the protected publishing jobs. An advisory GitLab review job may be added later only with a secretless workload-identity design or a separately isolated reviewer service; never expose a Gemini credential to arbitrary merge-request code.
