#!/usr/bin/env bash
# Run from the repository root with the Linux virtual environment activated.
set -euo pipefail
task_version="${1:-dev}"
if [[ "$task_version" != dev && ! "$task_version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Use dev or vMAJOR.MINOR.PATCH" >&2
  exit 1
fi
task_image="task-api:${task_version}"
mkdir -p evidence
python -m pip check
python -m ruff check app tests scripts
python -m ruff format --check app tests scripts
python -m pytest -q --junitxml=evidence/pytest.xml
ansible-playbook -i infra/inventory.example.ini infra/provision.yml --syntax-check
ansible-playbook -i infra/inventory.example.ini infra/deploy.yml --syntax-check \
  -e task_api_version=v0.0.0
docker compose -f compose.yaml config --quiet
docker build --platform linux/amd64 --build-arg "APP_VERSION=${task_version}" \
  -t "${task_image}" .
python scripts/container_check.py --image "${task_image}" --version "${task_version}"
