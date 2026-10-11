# Verification evidence

This file separates observed output, student-reported checks and work still to run.
Instructions and expected results are not completed experiments.

## Confirmed before the final delivery increment — 11 October 2026

| Evidence | Result and scope |
|---|---|
| Public API/Docker/CI/Ansible integration | PRs #1–#4 are merged. Main was `5c1aad0437be29a753f651403b6832a19eb8f9a1` when this increment was prepared. |
| Public main CI | [Run 38142160075](https://github.com/Hasan-Kalzi/task-tracking-project-devops/actions/runs/38142160075) succeeded on that exact main: Ruff, pytest, Docker build and HTTP/container recreation/persistence checks. That workflow did not yet include the final Ansible syntax steps. |
| Assistant fresh main snapshot | All 22 Git blob hashes matched the public tree; Linux/Python 3.12.14 Ruff lint/format and 25 tests passed. One upstream TestClient deprecation warning remains. |
| Student-reported infrastructure | [PR #4](https://github.com/Hasan-Kalzi/task-tracking-project-devops/pull/4) checks off isolated Windows tests, controller syntax checks, clean Ubuntu 24.04 VM provisioning, immediate repeat `changed=0`, and Love's review/reproduction. The assistant has inspected the checklist, not the corresponding runtime logs. |
| Version forwarding correction | Final increment adds `APP_VERSION` to deployment's generated `.env`; Compose otherwise selects `dev` and fails the expected release version check. |

The final delivery package is prepared and locally validated; no published release or
successful release-archive deployment is claimed here. Docker is unavailable in the
assistant workspace. Its local packaging fixture validates manifests, checksums and
archive membership using a simulated Docker command, not an actual built image.
Real image build/save and publication must succeed in GitHub Actions.

## Add results before the final report

| Experiment | Record |
|---|---|
| Final PR and fresh-clone gate | Merge commit, passing CI URL, controller/Python/Docker/Compose versions and gate output |
| Successful version delivery | Tag, source commit, Actions URL, release URL, four assets, checksum output and manifest image ID |
| Failure-blocking experiment, if performed | Deliberately failing commit/tag, failed delivery URL, skipped publication and absence of a published release |
| Clean VM and provision repeat | Actual OS/architecture, initial state, first/repeated PLAY RECAP; do not publish credentials or private inventory |
| Release deployment and repeat | Verified archive inputs, both PLAY RECAPs, image ID, health/version and container ID |
| Recreation persistence | Saved task response before recreation, new container ID, same task after recreation |
| Upgrade and rollback | Two tested release versions/IDs, deploy logs, old version restored and saved task retained |
| Student collaboration | Actual reviewer, review/corrections and independent commands/results |
| Final hand-in | Public report path, final 2–3-page PDF, new course PR URL referencing proposal #3088 |

Keep local logs under ignored `evidence/`. Add only selected redacted results or stable
run links to the report/repository. Publication is delivery; application deployment,
image rollback and SQLite backup restoration are separate operations.

