# Ansible infrastructure

The controller runs Ansible and connects over SSH to a separate target VM.
Use an Ubuntu 24.04 controller with Python 3.12; WSL Ubuntu can be used for local
development. Native Windows cannot run the Ansible controller. Keep a WSL virtual
environment in its Linux home directory, separate from the Windows environment.
WSL is a development option, not an officially supported production controller.

The target is a clean Ubuntu 24.04 **x86_64** VM with SSH, Python 3, a sudo-capable
user and access to the Ubuntu package repositories. Enable the Ubuntu Universe
repository if it is absent: the playbook uses its `docker-compose-v2` package.
The playbook does not create the VM or install its initial SSH/Python access.

## Files and responsibilities

| File | Purpose |
|---|---|
| `infra/inventory.example.ini` | Example SSH host and user; its address is a documentation placeholder |
| `infra/provision.yml` | Check supported OS/architecture, install Docker/Compose, start Docker and create `/opt/task-api` |
| `infra/deploy.yml` | Load an existing release image archive, verify its image ID and start/check Compose |

Copy the example to `infra/inventory.ini` and replace the address/user. The real
inventory is ignored by Git. Verify the VM's SSH host fingerprint against the VM
console before accepting it. Keep host-key checking enabled. Use SSH keys or
Ansible's password prompts; do not place passwords/private keys in tracked files.

## Controller setup and static checks

Run from the repository root on the Linux controller:

```bash
python3.12 -m venv .venv &&
./.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock &&
./.venv/bin/python -m pip check &&
./.venv/bin/ansible-playbook -i infra/inventory.example.ini infra/provision.yml --syntax-check &&
./.venv/bin/ansible-playbook -i infra/inventory.example.ini infra/deploy.yml --syntax-check -e task_api_version=v0.0.0
```

The version above is only a syntax-check input. These commands do not connect to
the example host or demonstrate provisioning/deployment. The development lock
includes Ansible only on non-Windows platforms so native Windows API tests remain
installable. PyYAML is included for YAML tooling and later delivery scripts.

## Provision the real VM

Configure the ignored inventory first. The following commands use SSH keys;
append `--ask-pass` if password SSH is needed (install `sshpass` on the controller).
`--ask-become-pass` prompts for the target user's sudo password.

```bash
./.venv/bin/ansible -i infra/inventory.ini task_api -m ping
mkdir -p evidence
set -o pipefail
./.venv/bin/ansible-playbook -i infra/inventory.ini infra/provision.yml --ask-become-pass | tee evidence/provision-first.log
```

Continue only if that run succeeds. Then repeat the same playbook:

```bash
./.venv/bin/ansible-playbook -i infra/inventory.ini infra/provision.yml --ask-become-pass | tee evidence/provision-repeat.log
```

For an unchanged VM, the immediate repeat should report `changed=0`,
`unreachable=0` and `failed=0`. Record the actual recaps. The apt cache has a
one-hour validity period; later cache refreshes or external host changes can
produce changes. Inspect Docker/Compose versions and that Docker is active on the
VM. Distribution packages track Ubuntu updates; they are not pinned to an exact
Docker version. The provisioning playbook is intended for this dedicated VM.

## Deploy a delivered image in the release increment

Deployment requires the real version, image ID and local image archive from the
verified release manifest. Release packaging/verification is introduced in the
fifth increment. Do not run deployment with the syntax-check version or invented
manifest values.

Once that increment is available, verify its release checksums and manifest, then
run the documented delivery command from its runbook. Deployment copies the
archive, rejects an existing version tag pointing at a different image, loads
the archive without rebuilding, checks the resulting image ID, configures
Compose and verifies storage-aware health and the application version.

The service binds to the VM's loopback interface. Access it using SSH forwarding,
for example `ssh -L 8001:127.0.0.1:8000 USER@VM_IP`, then open
`http://127.0.0.1:8001/docs`. The deployment is a local prototype with synthetic
data; this setup does not provide authentication or TLS.

An unchanged deployment should reuse the loaded image and running container.
That behaviour still needs a repeated real deployment and recorded results.
A failed deployment can leave a partial update; there is no automatic rollback.
The later runbook documents selecting a compatible previous release. Image
rollback does not revert SQLite schema or task data. Keep the named volume and
verify persistence after recreation; never use `down -v` on the real data stack.

## Evidence

Codex checked the prepared third increment on Linux/Python 3.12.14: hash-required
binary installation, dependency consistency, Ruff lint/format, 25 tests and both
Ansible syntax checks passed. One upstream TestClient deprecation warning remains.
Windows-target dependency/wheel validation is recorded in [the AI log](ai-use.md).
Clean-VM provisioning, repeat deployment, rollback and partner reproduction must
be recorded when executed. Syntax checks alone do not establish those results.

Sources: [Ansible controller platforms](https://docs.ansible.com/projects/ansible-core/2.19/os_guide/intro_windows.html),
[Ubuntu Compose package](https://packages.ubuntu.com/noble/docker-compose-v2).
