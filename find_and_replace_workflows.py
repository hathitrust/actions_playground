#!/usr/bin/env python3

"""
Objecting: Update reusable workflow references in multiple git repositories like a massive find and replace
1. Traverses all git repositories under a parent directory.
2. Searches for .github/workflows/*.yml and *.yaml files.
3. Find and replace lines within the workfloew.
4. Displays every proposed change and waits for approval.
5. If approved:
      - checks out main
      - pulls latest changes
      - creates branch, ex: ETT-1378
      - updates files
      - commits changes
      - pushes branch
6. Prints the full path of every modified file.

TODO: Create pull requests...?
"""

import os
import sys
import argparse
from pathlib import Path
import re
import subprocess
parser = argparse.ArgumentParser(
    description="Update reusable workflow references in multiple git repositories.")
parser.add_argument(
    "--root_dir", help="Root directory containing many git repositories", required=True)
parser.add_argument("--branch", help="Branch to create", required=True)
parser.add_argument("--commit-message",
                    default="Updating reusable workflow references", help="Commit message for changes")
parser.add_argument(
    "--find", help="String to find in workflow references")

parser.add_argument(
    "--replace", help="String to replace in workflow references")


args = parser.parse_args()


def is_git_repo(path):
    """
    Determine whether a directory is a git repository.
    """
    return (Path(path) / ".git").exists()


def find_repositories(root_dir):
    """
    Locate repositories directly under the supplied root directory.
    """
    repos = []

    for item in Path(root_dir).iterdir():
        if item.is_dir() and is_git_repo(item):
            repos.append(item)

    return sorted(repos)


def find_workflow_files(repo):
    """
    Locate workflow yaml files.
    """
    workflow_dir = repo / ".github" / "workflows"

    if not workflow_dir.exists():
        return []

    files = []

    files.extend(workflow_dir.rglob("*.yml"))
    files.extend(workflow_dir.rglob("*.yaml"))

    return sorted(files)


def collect_changes(repo, find, replace):
    """
    Scan workflow files and collect proposed replacements.

    Returns:
        [
            {
                "file": Path(...),
                "before": "...",
                "after": "...",
            }
        ]
    """

    changes = []
    for workflow_file in find_workflow_files(repo):
        text = workflow_file.read_text(encoding="utf-8")
        matches = list(re.compile(find).finditer(text))

        if not matches:
            continue

        for match in matches:
            before = match.group(0)
            after = re.sub(
                re.compile(find),
                replace,
                before,
            )

            changes.append(
                {
                    "file": workflow_file,
                    "before": before,
                    "after": after,
                }
            )
    return changes


def apply_changes(repo):
    """
    Apply all workflow modifications within a repository.

    Returns a list of modified file paths.
    #TODO: Check formatting on yaml files after changes are applied. If formatting is off, run a formatter and commit those changes as well.
    """

    modified_files = []

    for workflow_file in find_workflow_files(repo):
        original = workflow_file.read_text(
            encoding="utf-8"
        )

        updated = re.sub(
            re.compile(args.find),
            args.replace,
            original,
        )

        if original == updated:  # If no changes were made, skip writing the file and adding it to the modified files list
            continue

        workflow_file.write_text(
            updated,
            encoding="utf-8"
        )

        modified_files.append(str(workflow_file))

    return modified_files


def run_command(command, cwd):
    """
    Execute a shell command and return stdout.
    Raises RuntimeError on failure.
    """

    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"\nCommand failed:\n"
            f"{' '.join(command)}\n"
            f"Repository: {cwd}\n"
            f"stderr:\n{result.stderr}"
        )

    return result.stdout.strip()


# Git Operations

def git_stash_pull_main(repo):
    """
    Stash any local changes, checkout main, pull latest.
    """

    run_command(
        ["git", "stash"],
        repo,
    )

    run_command(
        ["git", "checkout", "main"],
        repo,
    )

    run_command(
        ["git", "pull", "origin", "main"],
        repo,
    )


def prepare_repository(repo):
    """
    Checkout main, pull latest, create feature branch.
    """

    # Check if branch already exists locally or remotely
    existing_branches = run_command(
        ["git", "branch", "--list", args.branch],
        repo,
    )
    if existing_branches:
        print(
            f"\nBranch '{args.branch}' already exists in repository: {repo}.")
        return
    else:
        pass

    print(f"\nPreparing repository: {repo}")

    run_command(
        ["git", "checkout", "main"],
        repo,
    )

    run_command(
        ["git", "pull", "origin", "main"],
        repo,
    )

    # Delete existing local branch for a clean start. Making this operation re-runable
    # try:
    #     run_command(
    #         ["git", "branch", "-D", args.branch],
    #         repo,
    #     )
    # except RuntimeError:
    #     pass

    run_command(
        ["git", "checkout", "-b", args.branch],
        repo,
    )


def view_diff(repo):
    """
    Check for differences in the repository.
    """

    diff = run_command(
        ["git", "diff", "--color=always"],
        repo,
    )
    print(f"\nDifferences in repository {repo}:\n{diff}\n")
    return True


def cleanup_repository(repo):
    """
    Cleanup repository by checking out main and deleting the feature branch.
    """

    print(f"\nCleaning up repository: {repo}")

    run_command(
        ["git", "checkout", "main"],
        repo,
    )

    run_command(
        ["git", "reset", "--hard"],
        repo,
    )

    try:
        run_command(
            ["git", "branch", "-D", args.branch],
            repo,
        )
    except RuntimeError:
        pass


def commit_and_push(repo):
    """
    Commit changes to the branch.
    git status --porcelain = show me the status in a simple format that is easy to parse
    """

    status = run_command(
        ["git", "status", "--porcelain"],
        repo,
    )

    if not status:
        print("No changes detected.")
        return

    run_command(
        ["git", "add", "."],
        repo,
    )

    run_command(
        ["git", "commit", "-m", args.commit_message],
        repo,
    )

    run_command(
        [
            "git",
            "push",
            "--set-upstream",
            "origin",
            args.branch,
        ],
        repo,
    )

# Main


def main():
    repos = find_repositories(args.root_dir)
    if not repos:
        print(f"No git repositories found in {args.root_dir}")
        sys.exit(1)

    proposed_changes = {}  # {repo: changes} mapping

    print("\nScanning repositories for proposed changes...")
    print("--------------------------------------------------\n")

    # Opportunity to collect multiple changes across repositories before applying them, so that the user can review all changes at once.
    replacements = []

    # First pair can still come from CLI or remove this all together.
    if args.find and args.replace:
        replacements.append({
            "find": args.find,
            "replace": args.replace,
        })

    # Allow additional replacements
    while True:
        find = input("Find (leave blank to finish): ").strip()
        if not find:
            break

        replace = input("Replace with: ")

        replacements.append({
            "find": find,
            "replace": replace,
        })

    # Step 1: Collect the changes across all repositories and display them for review
    for repo in repos:
        # Stash any local changes, checkout main, pull latest
        git_stash_pull_main(repo)
        repo_changes = []  # List to hold changes for the current repository
        for replacement in replacements:
            find = replacement["find"]
            replace = replacement["replace"]
            changes = collect_changes(repo, find, replace)

            # Add changes to the list for the current repository
            repo_changes.extend(changes)
        if repo_changes:  # Only add to proposed_changes if there are changes for this repository
            proposed_changes[repo] = repo_changes
            print(f"\nFound changes in {repo}")
            for change in repo_changes:
                print(f"File: {change['file']}")
                print(f"    Before: {change['before']}")
                print(f"    After:  {change['after']}")

    if not proposed_changes:
        print("\nNo proposed changes found.")
        sys.exit(0)

    reponse = input(
        "\nDo you want to apply these changes or abort? (y/n): ")
    if reponse.lower() != 'y':
        print("Not applying changes.")
        sys.exit(0)

    # Step 2: Apply the changes
    for repo in proposed_changes.keys():
        try:
            prepare_repository(repo)
            # TODO: Augment so that it also takes in the find and replace arguments, so that it can apply multiple replacements in one go.
            modified_files = apply_changes(repo)
            view_diff(repo)
        except RuntimeError as e:
            print(f"Error processing repository {repo}: {e}")
        # break  # Remove this break to process all repositories
        response = input(
            f"\nDo you want to commit and push changes for repository {repo}? (y/n): ")
        if response.lower() != 'y':
            print(f"Not committing and pushing changes for repository: {repo}")
            continue
        print("\nApplying changes...")
        for repo in proposed_changes.keys():
            try:
                if not modified_files:
                    print(f"No changes applied for repository: {repo}")
                    continue

                print(f"Modified files in {repo}:")
                for file in modified_files:
                    print(f"{file}")
                commit_and_push(repo)
                print(f"Changes applied and pushed for repository: {repo}")
            except RuntimeError as e:
                print(f"Error processing repository {repo}: {e}")
            break  # Remove this break to process all repositories

    print("Done. All changes have been applied and pushed.")


if __name__ == "__main__":
    main()
