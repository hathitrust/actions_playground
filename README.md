# actions_playground
This repo is used to test out new or breaking changes to any actions workflow without disrupting the current configurations or packages that are deployed.


# Using the Python script
Objective: Update reusable workflow references in multiple git repositories like a massive find and replace
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

```bash
python3 find_and_replace_workdlows.py --root_dir ../ --branch ETT-1378 --find "hathitrust/github_actions/build@v1" --replace "hathitrust/github_actions/build@v2"
```
