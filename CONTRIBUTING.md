# Contributing

## Getting Started

1. Ensure you have at minimum Python 3.9 installed; Python 3.8 and 3.7 are optional for multi-environment tests

   This repo uses [tox](https://tox.readthedocs.io/en/latest/) and by default will try to run tests against all
   supported versions. You can run `tox -e py39` to limit tests to just one environment.

2. Clone and setup environment:

    ```bash
    git clone git@github.com:gooddata/gooddata-python-sdk.git
    cd gooddata-python-sdk
    make dev
    ```

   The `make dev` command will create a new Python 3.9 virtual environment in the `.venv` directory, install all
   third party dependencies into it and setup git hooks.

   Additionally, if you use [direnv](https://direnv.net/) you can run `direnv allow .envrc` to enable automatic
   activation of the virtual environment that was previously created in `.venv`.

   If `direnv` is not your cup of tea, you may want to adopt the PYTHONPATH exports that are done as part of the
   script so that you can run custom Python code using the packages container herein without installing them.

   To make sure you have successfully set up your environment run `make test` in virtualenv in the root of git repo.
   Please note, that `make test` executes tests against all the supported python versions. If you need to specify only
   subset of them, see section [Run tests](#Run tests)

## Coding Conventions

This project uses [flake8](https://flake8.pycqa.org/en/latest/) to ensure basic code sanity and [black](https://github.com/psf/black)
for no-nonsense, consistent formatting.

Both `flake8` and auto-fixing `black` are part of the pre-commit hook that is automatically set up during `make dev`.

You can also run the lint and formatter manually:

-  To run flake8 run: `make lint`
-  To reformat code black run: `make format-fix`

**NOTE** If the pre-commit hook finds and auto-corrects some formatting errors, it will not auto-stage
the updated files and will fail the commit operation. You have to re-drive the commit. This is a well-known and
unlikely-to-change behavior of the [pre-commit](https://github.com/pre-commit/pre-commit/issues/806) package that this repository uses to manage hooks.

The project documents code by docstrings in rst format. Compliance with rst format may be checked by running `make docs`.

One logical change is done in one commit.


## Run tests
Tests use [tox](https://tox.wiki/en/latest/index.html) and [pytest](https://docs.pytest.org/en/6.2.x/contents.html)
libraries. Each project has its own `tox.ini`.
NOTE: Tests are not executed for OpenAPI client projects.

Here are the options how to run the tests:
- run tests for one sub-project - drill down to sub-project's directory
    - use `make test` to trigger tests
  ```bash
  cd gooddata-sdk
  make test
  ```
    - or execute `tox` command with arguments of your choice
  ```bash
  cd gooddata-sdk
  tox -e py39
  ```
- run tests for all non-client projects using `make test` in project root directory

Tests triggered by make can be controlled via these environment variables:
- `RECREATE_ENVS` - set environment variable `RECREATE_ENVS` to 1 and make will add `--recreate` flag, `--recreate`
  flag is not used otherwise
  ```bash
  RECREATE_ENVS=1 make test
  ```
- `TEST_ENVS` - define tox test environments (targets) as comma-separated list, by default all tox default targets are
  executed
  ```bash
  TEST_ENVS=py39,py37 make test
  ```
- `ADD_ARGS` - send additional arguments to pytest tool, useful for pin-pointing just part of tests
  ```bash
  ADD_ARGS="-k http_headers" make test
  ```

### How to update vcrpy tests
Some tests include HTTP call(s) to GD.CN instance. That tests are executed through
[vcrpy](https://vcrpy.readthedocs.io/) so that GD.CN instance is needed either first time or when request is changed.
It has clear benefits:
- ability to run the tests without GD.CN
- request and response snapshot - it makes debugging of HTTP calls simple

But there is one disadvantage. One needs GD.CN instance with the original setup to change tests.
`docker-compose.yaml` in root of the repository is here to help. It starts:
- GD.CN AIO in selected version
- postgres with gooddata-fdw extension
- service which setups GD.CN AIO demo project including PDM, LDM, metrics and insights

When a vcrpy supported test needs to be updated:
- start GD.CN using above `docker-compose.yaml`
- delete original vcrpy cassette
- execute test
- update a newly generated cassette to the git

## Run continuous integration tests
Tests in pull request (PR) are executed using docker. The following is done to make tests environment as close
to reproducible as possible:
- each supported python version has defined python base docker image
- tox version installed to docker is frozen to specific version
- all test dependencies specified in test-requirements.txt should be limited to some version range

Above rules give a chance to execute tests on localhost in the same or very similar environment as used in PR.
Orchestration is driven by `make test-ci`. Target `test-ci` supports the same features as `make test`, see
[Run tests](#Run tests) for details.

NOTE: docker tox tests and localhost tox tests are using the same .tox directory. Virtual environments for both test
types are most likely incompatible due to different base python version. tox is able to recognize it and recreate
venv automatically. So when docker tox tests are executed after localhost tests or vice-versa envs are recreated.

### Examples
- run all tests for all supported python environments
  ```bash
  make test-ci
  ```
- run all tests for all supported python environments and for one project
  ```bash
  cd gooddata-sdk
  make test-ci
  ```
- run all tests containing `http_headers` in name for py39 and py38 for all projects
  ```bash
  TEST_ENVS=py39,py38 ADD_ARGS="-k http_headers" make test-ci
  ```

# How to release new version

* Run `make release VERSION=X.Y.Z`
* Create pull request with the latest commit with bumped versions
* Ask for merge of pull request. Once it is merged:
* Checkout latest master tag it vX.Y.Z
* Push the tag to master branch (`git push --tags`)

# How to generate and maintain OpenAPI clients
Refer to our [OpenAPI client README](./.openapi-generator/README.md)
