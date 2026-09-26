#!/usr/bin/env python3
"""
blast_radius.py — external release-impact signal.

Looks up public registry information as a proxy for how much external reach
a package may have before publishing a new version.

This is NOT an internal code-dependency graph and is NOT a complete risk
assessment.

Usage:
    python blast_radius.py <package_name> <npm|pypi>

Prints a human-readable summary. If the registry cannot be reached, exits
with a clear message so the agent can honestly report that the signal is
unknown rather than guessing.
"""

import sys
import json
import urllib.request
import urllib.error


def npm_downloads(package_name):
    # npm public download-count API; no authentication required.
    url = f"https://api.npmjs.org/downloads/point/last-week/{package_name}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.load(resp)
    return data.get("downloads")


def pypi_info(package_name):
    # PyPI JSON API exposes package metadata.
    # It does not expose live download counts through this endpoint.
    url = f"https://pypi.org/pypi/{package_name}/json"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.load(resp)

    releases = data.get("releases", {})

    return {
        "version_count": len(releases),
        "latest_version": data.get("info", {}).get("version"),
    }


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in ("npm", "pypi"):
        print(
            "Usage: python blast_radius.py <package_name> <npm|pypi>",
            file=sys.stderr,
        )
        sys.exit(1)

    package_name, registry = sys.argv[1], sys.argv[2]

    try:
        if registry == "npm":
            downloads = npm_downloads(package_name)

            if downloads is None:
                print(
                    f"Could not determine weekly downloads for "
                    f"'{package_name}' on npm."
                )
            else:
                print(
                    f"'{package_name}' had {downloads:,} downloads on npm "
                    f"in the last week — that's the rough external "
                    f"release-impact signal."
                )

        else:
            info = pypi_info(package_name)

            print(
                f"'{package_name}' has {info['version_count']} published "
                f"versions on PyPI (latest: {info['latest_version']}). "
                f"PyPI's public API does not expose live download counts, "
                f"so treat this as a partial external signal, not a full "
                f"blast-radius figure."
            )

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(
                f"'{package_name}' was not found on {registry} — "
                f"cannot assess external release impact."
            )
        else:
            print(
                f"Could not reach {registry} registry (HTTP {e.code}) — "
                f"external release impact unknown."
            )

    except Exception as e:
        print(
            f"Could not reach {registry} registry ({e}) — "
            f"external release impact unknown."
        )


if __name__ == "__main__":
    main()
