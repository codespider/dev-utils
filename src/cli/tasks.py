import os

from invoke import Program
from invoke import task, Collection


@task
def py_lint(c):
    lint_config = os.getenv("LINT_CFG")
    if lint_config:
        c.run(f"poetry run flake8 --config {lint_config}")
        c.run(f"poetry run mypy --config-file {lint_config} scripts src")
    else:
        c.run("poetry run flake8")
        c.run("poetry run mypy")
@task
def test(c):
    c.run(f"poetry run pytest")

@task
def git_clean(c):
    c.run("git fetch --prune")

    branches = []
    try:
        gone_branches = c.run("git branch -vv  | grep  gone", hide='out')
        gone_branches = [b.strip().split(' ')[0] for b in gone_branches.stdout.strip().split('\n')]
        branches.extend(gone_branches)
    except:
        print("No Gone branches")

    try:
        branches_without_origin = c.run("git branch -vv  | grep  -v origin", hide='out')
        branches_without_origin = [b.strip().split(' ')[0] for b in branches_without_origin.stdout.strip().split('\n')]
        branches.extend(branches_without_origin)
    except:
        print("No branches without origin")

    for branch in branches:
        print(f"Deleting branch: {branch}")
        c.run(f"git branch -D {branch}")


if __name__ == '__main__':
    current_module = __import__(__name__)
    program = Program(namespace=Collection.from_module(current_module), version='0.1.0')
    program.run('git-clean git-clean')
