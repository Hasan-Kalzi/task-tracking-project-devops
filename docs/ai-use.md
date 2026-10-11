# AI assistance — implementation increments

Historical entries begin on 9 October 2026; latest preparation: 11 October 2026.
Date of initial implementation: 9 October 2026. Tool: ChatGPT Work. Requester: Hasan Kalzi.

AI helped the students guiding them to generate the initial FastAPI/SQLite API, pytest tests and Ruff configuration. It helped and gave instructions
generating hash-locked dependencies with uv and prepared this separate first-increment
package. The development lock for this increment includes
only runtime packages, HTTP test tooling, pytest and Ruff; Ansible is deferred to the
infrastructure increment.

The first increment was checked by AI on Linux/Python 3.12.14: 25 tests passed
and Ruff lint/format checks passed. One upstream TestClient deprecation warning was reported.
Hasan's Windows execution is recorded below; detailed code review remains pending. No Docker,
CI/CD, remote deployment, partner execution or final course pass is claimed for this public increment.

## Windows dependency correction — 9 October 2026

Hasan attempted installation on Windows/Python 3.12.10. The original Linux-generated
development lock omitted pytest's conditional Windows dependency, colorama, so pip's
hash-required installation stopped before Ruff and pytest were installed. AI regenerated
both locks with uv's universal resolution for Python 3.12, preserving package versions and
including pinned, hashed colorama only on Windows.

AI verified a fresh hash-required installation on Linux/Python 3.12.14, Ruff lint and
format checks, and 25 passing tests (one upstream deprecation warning). A separate Windows
resolution matched all 24 packages; their Windows-compatible wheels, hashes and conditional
dependency metadata were checked. This is dependency verification from Linux, not execution
of the application or tests on Windows. Hasan's subsequent execution is recorded below.

## Student-reported Windows execution — 9 October 2026

Hasan supplied terminal output showing successful binary/hash-required installation of the
corrected development lock, Ruff lint passing, four files already formatted and 25 tests
passing with one upstream deprecation warning in 4.34 seconds. `.gitignore` correctly matched
`.venv/` and `data/`.

The activation command failed because `.venv/Scripts/activate` was missing. Package paths
in the test output point to the global Python 3.12 installation, so this run is not evidence
of successful installation or testing inside the project virtual environment. AI supplied
commands to create `.venv` and use its Python executable explicitly; that isolated rerun
remains pending. The transcript does not establish completed code review or Love's execution.

## Docker/Compose increment — 9 October 2026

AI prepared Dockerfile, `.dockerignore`, runtime/build Compose files and the
standard-library container check from the existing AI-assisted private baseline, plus
updated README and this log for `feature/docker-compose`. This is the second planned
public increment. At preparation time public PR #1 is open and requests Love's review;
the new branch should be created from main after that PR is merged.

All five container files exactly match the baseline that passed private GitHub CI on
`65103a0f59b94b7ea2f31cd48068880f495c875b`:
https://github.com/Hasan-Kalzi/KTH-DD2482-Devops/actions/runs/37928004590 . That run verified
Compose configuration, image build, health/version, task operations and named-volume
persistence after forced container recreation. This is private-baseline evidence, not a
claim that the second public increment has run in CI or on Hasan's Docker Desktop.

AI verified the combined API/second-increment export on Linux/Python 3.12.14: Ruff lint
and formatting passed for app/tests/scripts, and 25 tests passed with one upstream
TestClient deprecation warning. Compose YAML was parsed and its declared service/volume
relationships checked; Docker is unavailable in the assistant's current environment.
Local Docker Desktop build/container execution and Love's review remain to be recorded.

## Ansible infrastructure increment — 10 October 2026

AI checked public progress: API PR #1 is merged (9 October at 22:53 Stockholm);
Docker PR #2 is open at `90a1c3b7`, with Love requested as reviewer and no submitted
review at preparation time. No new local Docker output was supplied. The third
branch should start from main after PR #2 is merged.

AI helped preparing the three unchanged Ansible provisioning/deployment/inventory files
from the existing private baseline, added controller/provisioning documentation,
and extended development inputs/lock with Ansible and PyYAML. Ansible and its
controller dependencies are conditional on non-Windows platforms so native
Windows API/test installs remain supported. Linux/WSL needs a separate Linux
virtual environment; the deployment target is a separate Ubuntu 24.04 x86_64 VM.

Hasan checked the combined API/Docker/third export on Linux/Python 3.12.14:
fresh hash-required binary installation, pip dependency consistency, Ruff lint and
format checks, 25 tests and both Ansible syntax checks passed. One upstream
TestClient deprecation warning remains. A separate Windows resolution matched all
25 applicable package pins; 25 Windows-compatible wheel hashes and conditional
dependency closure were verified from Linux. Ansible is excluded and colorama
included on Windows. This is not Windows application/test execution.

AI helped complete branch/check/provision/commit/PR
guide for Hasan's manual public integration. No assistant writes to the public
repository were made. Deployment commands must use real verified release inputs,
introduced in the fifth increment; syntax-check values are not release evidence.

## Restored CI contribution record

The following entry was introduced in Love's CI PR #3 and omitted by the subsequent
Ansible documentation replacement. It is restored without changing its authorship claim.

## Docker integration test mismatch during CI workflow - 11 October 2026

When implementing the Docker integration test for the CI workflow, it initially failed because there was a mismatch between the expected `APP_VERSION` and the actual version. Love used ChatGPT to debug the issue by first inspecting the CI logs and then trace how the version environment variable was passed through the `container_check.py` and `compose.yaml` files. It was discovered that the test's `--version` argument wasn't being forwarded to the running container properly, therefore defaulting to `dev`.

## WSL controller correction — 11 October 2026

Hasan supplied output showing Ubuntu lacked `python3.12-venv`, then successfully installed
uv and managed Python 3.12.14. His next command failed because the planned Linux project
directory did not exist. AI supplied a fresh-clone/Linux-home controller workflow and
explicit environment executables. Installing an interpreter alone is not controller or
VM execution evidence. PR #4 later reports those checks and provisioning were completed.

## Final release-delivery preparation — 11 October 2026

Request: after the merges, prepare the final push and verify the project from scratch.
AI checked live public PRs #3/#4 and exact main `5c1aad0`, preserved Love's CI,
Compose and container-check changes. It adds the
tag delivery workflow, gate/packaging/source-export scripts. CI additionally validates Ansible/Compose; official checkout v5 and
setup-python v6 action revisions and Python 3.12.14 are pinned.

Local verification uses Linux/Python 3.12.14 for hash-locked tooling, Ruff, 25 tests,
both Ansible syntax checks and static workflow/template checks. Packaging/export is
checked in a disposable Git fixture with a simulated Docker CLI, including checksums,
tracked-only archive contents and rejection of invalid/mismatched inputs. This fixture
does not prove Docker build/save, GitHub publication or VM deployment; these require
the actual Actions and student runtime results.

PR #4's checklist reports isolated Windows/controller/VM checks, immediate provisioning
repeat and Love review/reproduction. Its actual logs/environment details have not been
inspected by AI. A new release delivery run, fresh merged clone, release deployment,
repeat deployment, compatible-version rollback and final 2–3-page report remain to run.
