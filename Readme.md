# Read me

This repository is used as a subtree for most Project Mu repositories. It
ensure that for all repositories, the .github/* subdirectory remain uniform.

**If you are updating anything in the .github/ folder from outside the
[Insert Repo here] repository, you are wrong! Go to [Insert Repo link here] to
update the repository**

## Limitations

Any `git subtree pull` generated commit must be merged into the main branch via
a merge commit or a rebase & ff. As Project Mu does not allow merge commits,
then it must be completed via a rebase & ff. **A squash will break future `git
subtree pull` commands**. This is because the git subtree pull works by relying
on the commit message of a previous subtree pull (it contains commit hashes). A
squash changes the commit hash of what is being squashed, so the commit message
no longer matches the commit value.

## Pipeline broken, out of sync?

This typically happens when someone merged the PR via a squash or makes an edit
to a file in the .github/ directory from within a different repository then
this one. to remedy this situation, you will need to:

1. Make a branch in the offending repo
2. delete the .github/ folder
3. commit the change
4. run `git subtree add --prefix .github/ [TODO: add here the repo link]main --squash`
    - Note: This creates 2 commits, a merge commit and the actual commit.
    If you are picky, you can cherry-pick out only the second commit,
    ignoring the merge commit.
5. Submit a PR with the commit to remove the .github/ folder, and the (1 or 2)
commits from the git subtree command
    - Note: This PR must be completed via a REBASE & FF

.
Update