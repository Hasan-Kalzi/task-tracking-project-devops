# Failed checks prevented delivery on 17 October 2026

This controlled experiment fulfils the failure-blocking demonstration in the
[accepted project proposal #3088](https://github.com/KTH/devops-course/pull/3088).

## Exact source and observed run

- Source commit: [f0db00bff239e5daefbd67a96fbb243e2dc02d89](https://github.com/Hasan-Kalzi/task-tracking-project-devops/commit/f0db00bff239e5daefbd67a96fbb243e2dc02d89)
- Tag at verification: v0.1.2
- Branch: evidence/failure-blocking-20261017
- Workflow: [Task API delivery, run 39058760546](https://github.com/Hasan-Kalzi/task-tracking-project-devops/actions/runs/39058760546)
- Job: deliver, 117472135078
- [Deliberately failing test](https://github.com/Hasan-Kalzi/task-tracking-project-devops/blob/f0db00bff239e5daefbd67a96fbb243e2dc02d89/tests/test_release_gate_failure.py)
- [Release workflow](https://github.com/Hasan-Kalzi/task-tracking-project-devops/blob/f0db00bff239e5daefbd67a96fbb243e2dc02d89/.github/workflows/release.yml)
- [Gate script](https://github.com/Hasan-Kalzi/task-tracking-project-devops/blob/f0db00bff239e5daefbd67a96fbb243e2dc02d89/scripts/checks.sh)
- [Selected original job output](failure-blocking-20261017-output.txt)
- [Recorded job conclusions](failure-blocking-20261017-run.json)

Only tests/test_release_gate_failure.py was added to the main snapshot for this
experiment. The test deliberately compares unequal strings. The branch remains
unmerged; the normal application and release code were not changed.

## Observed result

| Check or step | Result |
| --- | --- |
| Locked tooling installation | Success |
| Ruff lint | Passed |
| Ruff formatting | 8 files already formatted |
| Pytest | 1 failed, 25 passed, 1 upstream warning |
| Gate delivery on lint, tests, IaC and container checks | Failure |
| Package the exact tested image | Skipped |
| Publish the completed delivery | Skipped |
| Retain test evidence | Success |
| Release API query for v0.1.2 on 17 October | HTTP 404 Not Found |

The assertion failure was
tests/test_release_gate_failure.py::test_release_gate_negative_control.
The gate process exited with code 1. Because scripts/checks.sh stops on errors,
it did not reach the subsequent Docker build, and the workflow skipped its
packaging and publication steps. No v0.1.2 release was created by this run.

The workflow retained the task-api-release-results artifact (ID 12110093060),
including its failing JUnit test result. The committed output excerpt and job
conclusions preserve the essential result independently of artifact retention.

## Scope and experiment restart

This verifies the configured pytest failure path. It does not exhaustively test
every possible pipeline failure or prove that a person could not publish a release
manually.

The user restarted the experiment once. An earlier run used commit
73e0a1b47b63ff6953a493c031de86fe294f34f9; its experiment branch and tag were deleted,
then v0.1.2 was recreated for the run recorded here. That earlier run also skipped
publication. To avoid ambiguity, this record identifies the final full commit SHA
and workflow run ID rather than relying on the tag alone. The v0.1.0 and v0.1.1
release tags remain unchanged. Retain the current experiment branch/tag and do
not reuse or move tags in further experiments.
