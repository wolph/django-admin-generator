Contributing
============

Help is greatly appreciated, just please remember to clone the **development**
branch and to run `tox` before creating pull requests.

Travis tests for `flake8` support and test coverage so it's always good to
check those before creating a pull request.

Development branch:
https://github.com/WoLpH/django-admin-generator/tree/development

A simple trick to speed up your tox runs is to use detox, it runs all tox
processes in parallel.

```
pip install tox detox
detox
```

## Automatic formatting

Pull requests apply Ruff fixes before the lint check. With the autofix.ci
app installed for this repository, those fixes are committed to the pull
request branch, including forks. Findings Ruff cannot fix still fail CI.
The CI lint job checks committed files on pushes. The separate autofix.ci
workflow also runs on pushes to develop and master and can commit fixes.

Apply the same fixes locally with:

```console
uvx --with tox-uv tox -e ruff-fix
```
