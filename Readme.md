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
this one. To remedy this situation, you will need to do the following:

TODO: replace <github_subtree_repo> with real repo url

```cmd
git clone <offending_repo>
cd <offending_repo>
git remote add github_subtree <github_subtree_repo>
git fetch github_subtree

git checkout -b subtree_branch github_subtree/main
git checkout -b <subtree_fix_branch>

git rm -r .github/
git read-tree --prefix=.github/ -u subtree_branch
```

Next, un-stage any files that are found in the offending repo's ignore list. 
You can find this in <mu_common_github>/.azurepipelines/scripts/repo_list.yaml>

```cmd
git commit
git push
```

Complete the PR with a rebase & FF.
