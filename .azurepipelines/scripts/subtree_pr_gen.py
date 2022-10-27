# @file subtree_pr_gen.py
# For all provided repos, performs a subtree pull for a specified prefix and generates a pull request.
#
##
# Copyright (c) Microsoft Corporation
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
##
from github import Github
from git import Repo
import argparse
import os
import yaml
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO)

def parse_args():
    parser = argparse.ArgumentParser(description="Creates a PR in each repo that uses this as a subtree.")
    parser.add_argument('--token', '-T', dest="token",
        help = "the github token credential to use for authentication.")
    parser.add_argument('--user', '-U', dest="user",
        help = "the name of the user to associate the pull request with.")
    parser.add_argument('--prefix', '-P', dest="prefix", 
        help = "the name of the subdir the subtree is located at.")
    parser.add_argument('--repos', '-R', dest="repos",
        help = "the path to a yaml file containing a list of repos. repos must contain name, url, and base")

    args = parser.parse_args()
    return args

def parse_yaml(path):
    try:
        with open(path) as f:
            yaml_dict = yaml.load(f, Loader=yaml.SafeLoader) 
    except Exception:
        logging.error(f'Failed to locate and parse {path}')
        raise

    return yaml_dict["repos"]

def main():
    setup_logging()
    args = parse_args()
    
    token = args.token
    user = args.user
    prefix = args.prefix
    repo_list = parse_yaml(args.repos)
    
    pr_title = f'Update {prefix} subtree'
    
    pr_body = f'''
## MUST COMPLETE PR WITH A REBASE&FF

## Description

Update {prefix} subtree

## How this was tested

Automatically generated PR
'''

    # Note - we re-use the same branch name. This way if the previous PR has
    # not yet been merged, it is simple to locate and delete the branch.
    head = 'subtree/github/update'
    repo_base_path = os.path.join(os.getcwd(), 'src')
    os.makedirs(repo_base_path, exist_ok=True)

    github_wrapper = Github(token) # wrapper for communicating with github

    for repo in repo_list:
        logging.info(f'Starting subtree update for {repo["name"]}.')
        
        logging.info(f'Searching for an open PR for updating the subtree.')
        github_repo = github_wrapper.get_repo(f'{repo["url"].lstrip("https:://github.com/").rstrip(".git")}')
        for pull in github_repo.get_pulls(state='open'):
            if pull.title == pr_title:
                logging.info("PR found... closing the PR and deleting the branch.")
                pull.edit(state='closed', body='Replaced by newer Subtree update.')
                ref = github_repo.get_git_ref(f'heads/{head}')
                ref.delete()

        logging.info(f'Cloning {repo["name"]}')
        r = Repo.clone_from(repo["url"], os.path.join(repo_base_path, repo["name"]))

        # This process is more complex then it should to be. The subtree pull 
        # command creates a merge commit on top of the subtree pull commit;
        # however,a REBASE&FF cannot be performed on a PR if a merge commit 
        # is present. This is an issue because a REBASE&FF MUST be performed as
        # we don't allow merge commits, and a squash changes commit hashes and 
        # breaks future subtree commands.
        #
        # To get around this, we perform the pull on a temporary branch and
        # cherry-pick the second commit hash into the branch the PR will be 
        # creating for. (The first commit is the merge commit and the second is
        # the subtree pull commit).
        logging.info('Performing the subtree pull')
        r.git.checkout('-b', 'temp')
        r.git.subtree('pull', '--prefix', '.github/', 'https://github.com/Javagedes/mu_common_github', 'main', '--squash')
        hash = r.git.log('-n', '1', '--skip=1', '--pretty=format:%H')
        
        r.git.checkout(repo['base'])
        r.git.checkout('-b', head)
        r.git.cherry_pick(hash)

        # Push the commit
        logging.info('Pushing the Subtree pull commit to branch: {head}')
        r.git.push(f'https://{user}:{token}@{repo["url"].lstrip("https://")}', head, "--force")

        # Create PR
        logging.info(f'Creating the subtree update PR for repo: {repo["name"]}')
        github_repo = github_wrapper.get_repo(f'{repo["url"].lstrip("https:://github.com/").rstrip(".git")}')
        github_repo.create_pull(title=pr_title, body = pr_body, head = head, base = repo["base"])

if __name__ == "__main__":
    main()