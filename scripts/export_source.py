"""Export only tracked project files for an implementation-only source archive."""

import argparse
import subprocess
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    # git's tracked list excludes databases, virtual environments, local inventory and evidence.
    result = subprocess.check_output(["git", "ls-files", "-z", "."], cwd=root)
    files = [root / name.decode() for name in result.split(b"\0") if name]
    if not files:
        raise RuntimeError("Commit or stage the implementation files before exporting")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in files:
            archive.write(file, arcname=str(file.relative_to(root)))
    print(f"Exported {len(files)} tracked implementation files to {args.output}")


if __name__ == "__main__":
    main()
