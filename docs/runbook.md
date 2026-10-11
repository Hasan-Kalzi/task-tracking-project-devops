# Fresh checkout, delivery and VM verification

Commands below are student instructions. Record actual results in
[evidence.md](evidence.md); expected results are not completed experiments.
The public repository is the source of truth.

## 1. Check the final merged project from scratch

After Love reviews/merges the final PR and its CI passes, use a new Linux-home
directory. WSL needs Docker Desktop integration enabled; `docker version` must
show both client and server. Keep its virtual environment separate from Windows.

```bash
git clone https://github.com/Hasan-Kalzi/task-tracking-project-devops.git "$HOME/dd2482-task-api-fresh" &&
cd "$HOME/dd2482-task-api-fresh" &&
"$HOME/.local/bin/uv" venv --python 3.12.14 --managed-python --seed .venv &&
./.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock &&
source .venv/bin/activate &&
docker version &&
bash scripts/checks.sh dev
```

Use a directory that does not already exist. See
[infrastructure setup](infrastructure.md) if uv or the controller prerequisites
are missing. Record `git rev-parse HEAD`, `python --version`,
`docker version` and `docker compose version`. Retain the passing CI URL and
gate output. The gate's disposable Compose stack tests task operations and
persistence after container recreation. It cleans up its own test volume.

## 2. Provision a separate clean target VM

Target: Ubuntu 24.04 x86_64, SSH/Python 3, a sudo-capable user and standard Ubuntu
repositories including Universe. Creating the VM and initial SSH access are
prerequisites. This is separate from the WSL development controller.

From the fresh clone, copy `infra/inventory.example.ini` to ignored
`infra/inventory.ini`, edit the host/user and verify its SSH host fingerprint
against the VM console. Keep host-key checking enabled.

```bash
cp infra/inventory.example.ini infra/inventory.ini
nano infra/inventory.ini
ansible -i infra/inventory.ini task_api -m ping &&
mkdir -p evidence
set -o pipefail
ansible-playbook -i infra/inventory.ini infra/provision.yml --ask-become-pass | tee evidence/provision-first.log
```

Continue only after success, then repeat:

```bash
ansible-playbook -i infra/inventory.ini infra/provision.yml --ask-become-pass | tee evidence/provision-repeat.log
```

If using password SSH, append `--ask-pass` to the Ansible commands; the controller
needs `sshpass`. Do not save credentials in the inventory or repository.
An immediate unchanged provisioning repeat should report `changed=0`,
`unreachable=0`, `failed=0`. Retain the actual recaps and VM OS/architecture,
Docker/Compose versions and active daemon status. A later apt-cache refresh can
legitimately cause changes. PR #4 reports these checks already ran; preserve those
actual logs or repeat on a fresh VM if they are unavailable.

## 3. Deliver v0.1.0

Use the authenticated Windows Git Bash clone after the final merge and passing
fresh gate. Compare its main commit with the fresh-clone commit before tagging.

```bash
git switch main &&
git pull --ff-only origin main &&
git rev-parse HEAD &&
git tag -a v0.1.0 -m "Task API v0.1.0 verified delivery" &&
git push origin v0.1.0
```

Watch **Task API delivery** in GitHub Actions, then confirm the release is public
and has four assets. Record run/release URLs and download all four to the Linux
controller's `$HOME/dd2482-releases/v0.1.0` directory:

`image.tar.gz`, `task-api-v0.1.0-deployment.tar.gz`, `release.json`, `SHA256SUMS`.

The release gate builds once, tests that image and saves it without rebuilding.
It requires Linux/amd64, matching version metadata and a clean committed checkout.
Packaging includes tracked deployment/docs files; local inventory and evidence are excluded.
A failed gate skips publication. An interrupted upload can leave a draft; inspect
the run/draft, fix the cause and use a new version tag. Do not move/reuse tags.

## 4. Verify downloaded assets and deploy

In the Linux controller terminal with its virtual environment activated:

```bash
cd "$HOME/dd2482-releases/v0.1.0" &&
sha256sum -c SHA256SUMS &&
mkdir bundle &&
tar -xzf task-api-v0.1.0-deployment.tar.gz -C bundle &&
cmp release.json bundle/release.json
```

All three checksums must pass. Extract into a new bundle directory, away from
the source checkout. Generate deployment inputs from the verified manifest:

```bash
python - <<'PY'
import json
import re
from pathlib import Path

root = Path.cwd()
manifest = json.loads((root / "release.json").read_text())
assert manifest["version"] == "v0.1.0"
assert manifest["image"] == "task-api:" + manifest["version"]
assert (manifest["os"], manifest["architecture"]) == ("linux", "amd64")
assert re.fullmatch(r"sha256:[0-9a-f]{64}", manifest["image_id"])
inputs = {
    "task_api_version": manifest["version"],
    "task_api_image_id": manifest["image_id"],
    "image_archive": str((root / "image.tar.gz").resolve()),
}
(root / "deployment-vars.json").write_text(json.dumps(inputs, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
PY
```

Confirm the manifest commit matches the source commit of the release tag in GitHub.
Copy the real ignored inventory from the controller checkout, then deploy:

```bash
cd bundle &&
cp "$HOME/dd2482-task-api-fresh/infra/inventory.ini" infra/inventory.ini &&
mkdir -p evidence
set -o pipefail
ansible-playbook -i infra/inventory.ini infra/deploy.yml --ask-become-pass \
  -e @../deployment-vars.json | tee evidence/deploy-first.log
```

After success, repeat the unchanged command:

```bash
ansible-playbook -i infra/inventory.ini infra/deploy.yml --ask-become-pass \
  -e @../deployment-vars.json | tee evidence/deploy-repeat.log
```

The playbook requires the recorded image ID, loads the archive without rebuilding,
writes the selected version into `.env`, starts Compose and verifies health/version.
An unchanged second run should reuse the loaded image and container. Record its
actual recap and inspect unexpected changes. Failed deployment stops; recovery is manual.

## 5. Check runtime persistence

Use a second controller terminal for an SSH tunnel. Enter the actual inventory
user/address; the tunnel stays running until Ctrl+C:

```bash
read -r -p "VM user: " TASK_VM_USER
read -r -p "VM address: " TASK_VM_HOST
ssh -N -o ExitOnForwardFailure=yes -L 8001:127.0.0.1:8000 "${TASK_VM_USER}@${TASK_VM_HOST}"
```

Open `http://127.0.0.1:8001/docs`. Port 8001 avoids the local development port.
In the original activated controller terminal:

```bash
TASK_EVIDENCE_DIR="$HOME/dd2482-project-evidence"
mkdir -p "$TASK_EVIDENCE_DIR"
set -o pipefail
curl --fail --silent --show-error http://127.0.0.1:8001/health | tee "$TASK_EVIDENCE_DIR/health-v0.1.0.json"
curl --fail --silent --show-error -X POST http://127.0.0.1:8001/tasks \
  -H 'Content-Type: application/json' -d '{"title":"Release persistence check"}' \
  > "$TASK_EVIDENCE_DIR/task-created.json" &&
TASK_SAVED_ID="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' "$TASK_EVIDENCE_DIR/task-created.json")" &&
curl --fail --silent --show-error -X PATCH "http://127.0.0.1:8001/tasks/$TASK_SAVED_ID" \
  -H 'Content-Type: application/json' -d '{"completed":true}' \
  > "$TASK_EVIDENCE_DIR/task-completed.json"
```

Enter the same VM identity in this terminal, then force recreation on the target:

```bash
read -r -p "VM user: " TASK_VM_USER
read -r -p "VM address: " TASK_VM_HOST
ssh -t "${TASK_VM_USER}@${TASK_VM_HOST}" \
  'cd /opt/task-api && sudo docker compose -p task-api -f compose.yaml ps -q api && sudo docker compose -p task-api -f compose.yaml up -d --force-recreate --wait --wait-timeout 60 && sudo docker compose -p task-api -f compose.yaml ps -q api'
```

Retain before/after container IDs. After health succeeds, verify the same task:

```bash
curl --fail --silent --show-error "http://127.0.0.1:8001/tasks/$TASK_SAVED_ID" \
  > "$TASK_EVIDENCE_DIR/task-after-recreation.json" &&
python - "$TASK_EVIDENCE_DIR" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
before = json.loads((root / "task-completed.json").read_text())
after = json.loads((root / "task-after-recreation.json").read_text())
assert before == after
assert after["completed"] is True
print("Saved task survives container recreation:", after)
PY
```

Keep the real data volume. `down -v` would destroy it.

## 6. Upgrade and roll back between compatible releases

Retain v0.1.0 assets and deployment inputs. Create another tested tag, `v0.1.1`,
after the first delivery succeeds. It may use the same reviewed source commit:
a new version builds a distinct labelled image, sufficient for an artefact
selection/rollback rehearsal; this does not demonstrate schema migration.

```bash
git switch main &&
git pull --ff-only origin main &&
git tag -a v0.1.1 -m "Task API v0.1.1 rollback rehearsal" &&
git push origin v0.1.1
```

Repeat sections 3–4 for v0.1.1, replacing the version in paths/archive names and
the manifest assertion. Each release gets its own directory and verified inputs.
Check health reports v0.1.1 and the saved task remains.

Then, in the activated Linux controller terminal, apply the **old** inputs:

```bash
cd "$HOME/dd2482-releases/v0.1.0/bundle"
set -o pipefail
ansible-playbook -i infra/inventory.ini infra/deploy.yml --ask-become-pass \
  -e @../deployment-vars.json | tee evidence/rollback-v0.1.0.log
```

Verify health reports v0.1.0 and the same task is still completed. Retain both
release URLs/image IDs, deployment/rollback logs and health/task responses.
Image rollback preserves current SQLite data; it does not reverse schema changes
or restore deleted tasks. There is no automatic rollback.

## 7. Diagnosis and data recovery

On the target, run diagnostics from its deployment directory so Compose reads
the same `.env`:

```bash
cd /opt/task-api
sudo docker compose -p task-api -f compose.yaml ps
sudo docker compose -p task-api -f compose.yaml logs --no-color
```

Distinguish unsupported schema, disk/permissions, wrong image ID, port conflicts
and an application failure before choosing a fix. Reapply verified old release
inputs for a compatible image rollback. For a consistent database backup, stop
the service before copying SQLite:

```bash
cd /opt/task-api &&
sudo docker compose -p task-api -f compose.yaml stop api &&
sudo docker compose -p task-api -f compose.yaml cp api:/data/tasks.db ./tasks-backup.db &&
sudo docker compose -p task-api -f compose.yaml start api
```

Before restoring, stop the service and retain the current DB. Restore the chosen
backup into the volume as `/data/tasks.db` with UID/GID 10001 and mode 0600,
then restart and verify health and known task IDs. Restoration replaces newer data;
review the recovery point first. No backup/restore experiment is claimed here.

## 8. Final report and course hand-in

After actual verification, replace draft notes with measured results and stable
public links. Both students review the implementation/AI log, record responsibilities
and corrections, and finalise/visually check the **2–3-page report**. Include public
source, successful delivery/release, VM access instructions and limitations.
The VM's loopback endpoint is reachable through the documented SSH tunnel; do not
describe it as a public deployed URL. Address the course's deployed-link wording
using the accepted local-VM/delivery proposal and the actual access arrangement.

Follow Carmine's supplied 8 October instruction: open a **new course PR** linking
the completed project and report, referencing accepted proposal
[#3088](https://github.com/KTH/devops-course/pull/3088), before
**11 October 2026, 23:59 Europe/Stockholm**.
Proposal merge and implementation PR merge are separate from final hand-in/grading.
