# @file subtree_pr_gen.py
# For all provided repos, performs a subtree pull for a specified prefix and
# generates a pull request.
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
    parser = argparse.ArgumentParser(description="Creates a PR in each repo \
        that uses this as a subtree.")
    parser.add_argument('--token', '-T', dest="token",
                        help="the github token credential to use for \
                              authentication.")
    parser.add_argument('--user', '-U', dest="user",
                        help="the name of the user to associate the pull \
                              request with.")
    parser.add_argument('--prefix', '-P', dest="prefix",
                        help="the name of the subdir the subtree is located \
                              at.")
    parser.add_argument('--repos', '-R', dest="repos",
                        help="the path to a yaml file containing a list of \
                              repos. repos must contain name, url, and base")

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

    github_wrapper = Github(token)  # wrapper for communicating with github

    for r in repo_list:
        logging.info(f'Starting subtree update for {r["name"]}.')

        logging.info('Searching for an open PR for updating the subtree.')
        github_repo = github_wrapper.get_repo(
            f'{r["url"].lstrip("https://github.com/").rstrip(".git")}')
        for pull in github_repo.get_pulls(state='open'):
            if pull.title == pr_title:
                logging.info("PR found... closing the PR and deleting the \
                              branch.")
                pull.edit(state='closed', body='Replaced by newer Subtree \
                                                update.')
                ref = github_repo.get_git_ref(f'heads/{head}')
                ref.delete()

        logging.info(f'Cloning {r["name"]}')
        target_repo = Repo.clone_from(
            r["url"], os.path.join(repo_base_path, r["name"]))

        #this_repo = Repo(os.getcwd())
        #this_repo.git.format_patch("-n", "HEAD^", "--stdout", ">", "temp.patch")
        #target_repo.git.checkout('-b', head)
        #target_repo.git.apply("../temp.patch", "--directory=.github")
        #target_repo.git.commit('-m', 'automated update')
        #target_repo.git.push(f'https://{user}:{token}@{r["url"].lstrip("https://")}', head, "--force")

        # This way works if we want to just filter out specific files.
        target_repo.git.remote('add', 'github', 'https://github.com/Javagedes/mu_common_github.git')
        target_repo.git.fetch('github')
        target_repo.git.checkout('-b', head)
        target_repo.git.pull('--strategy', 'subtree', '--squash', 'github', 'main', '--allow-unrelated-histories')
        logging.info(target_repo.git.status())
        for ignore_file in r["ignore"]:
            logging.info(ignore_file)
            target_repo.git.reset("--", ignore_file)

        logging.info(target_repo.git.status())
        target_repo.git.commit('-m', '[.github] update')
        target_repo.git.push(f'https://{user}:{token}@{r["url"].lstrip("https://")}', head, "--force")

        # Create PR
        logging.info(f'Creating the subtree update PR for repo:{r["name"]}')
        github_repo = github_wrapper.get_repo(
            f'{r["url"].lstrip("https:://github.com/").rstrip(".git")}')
        github_repo.create_pull(
            title=pr_title, body=pr_body, head=head, base=r["base"])


if __name__ == "__main__":
    main()
