"""Package the tested linux/amd64 image and tracked deployment files."""

import argparse
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import tarfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    args = parser.parse_args()
    if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", args.version):
        parser.error("Use an immutable release tag such as v0.1.0")
    if subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=normal", "--", "."], text=True
    ).strip():
        raise RuntimeError("Use a clean committed checkout for release packaging")
    dist = Path("dist")
    if dist.exists():
        raise RuntimeError("dist already exists; use a fresh checkout for each release")
    image = "task-api:" + args.version
    inspected = json.loads(subprocess.check_output(["docker", "image", "inspect", image]))[0]
    labels = inspected["Config"].get("Labels") or {}
    if labels.get("org.opencontainers.image.version") != args.version:
        raise RuntimeError("Image version does not match the release")
    if (inspected["Os"], inspected["Architecture"]) != ("linux", "amd64"):
        raise RuntimeError("The deployment target requires a linux/amd64 image")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", inspected["Id"]):
        raise RuntimeError("Unexpected Docker image ID")
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "compose.yaml", "infra", "docs", "README.md"]
    )
    bundle_files = [Path(name.decode()) for name in tracked.split(b"\0") if name]
    required = {Path("compose.yaml"), Path("infra/deploy.yml"), Path("docs/runbook.md")}
    if not required.issubset(bundle_files):
        raise RuntimeError("Tracked deployment configuration/runbook is missing")
    if Path("infra/inventory.ini") in bundle_files:
        raise RuntimeError("The real inventory must remain untracked")
    dist.mkdir()
    image_file = dist / "image.tar.gz"
    # Save first so gzip cannot hide a failed Docker export.
    raw_image = dist / "image.tar"
    subprocess.run(["docker", "save", "--output", str(raw_image), image], check=True)
    with raw_image.open("rb") as source, gzip.open(image_file, "wb") as output:
        shutil.copyfileobj(source, output)
    raw_image.unlink()
    manifest = {
        "version": args.version,
        "image": image,
        "image_id": inspected["Id"],
        "os": inspected["Os"],
        "architecture": inspected["Architecture"],
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    }
    (dist / "release.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    bundle = dist / f"task-api-{args.version}-deployment.tar.gz"
    with tarfile.open(bundle, "w:gz") as archive:
        for file in sorted(bundle_files):
            archive.add(file, arcname=file.as_posix())
        archive.add(dist / "release.json", arcname="release.json")
    sums = []
    for file in sorted(dist.iterdir()):
        with file.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        sums.append(f"{digest}  {file.name}")
    (dist / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
