"""Tools for the DevBuddy agent.

Each tool is a plain Python function. ADK reads the name, the type hints
and the docstring, and shows them to the model so it knows when to call it.
Both web APIs used here are free and need no API key.
"""
import json
import re
import urllib.error
import urllib.request


def _get_json(url: str, payload: dict | None = None) -> dict:
    """Sends a GET (or a POST when payload is given) and returns the JSON body."""
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json",
                                 "User-Agent": "devbuddy-workshop"})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def get_latest_version(package: str) -> dict:
    """Gets the latest released version of a Python package from PyPI.

    Use this whenever the user asks about a package's version, or whether
    an update exists. Never answer from memory: versions change every week.

    Args:
        package: The package name on PyPI, for example "requests".

    Returns:
        A dict with status "success", the latest version, a summary and the
        required Python version, or status "error" with a message.
    """
    try:
        info = _get_json(f"https://pypi.org/pypi/{package.strip()}/json")["info"]
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"status": "error", "error_message": f"'{package}' is not on PyPI."}
        return {"status": "error", "error_message": f"PyPI returned HTTP {exc.code}."}
    except Exception as exc:  # Return errors as data, not crashes.
        return {"status": "error", "error_message": f"Could not reach PyPI: {exc}"}
    return {
        "status": "success",
        "package": info["name"],
        "latest_version": info["version"],
        "summary": info.get("summary") or "",
        "requires_python": info.get("requires_python") or "not specified",
    }


def check_vulnerabilities(package: str, version: str) -> dict:
    """Checks a Python package version for known security vulnerabilities.

    Uses OSV.dev, Google's open source vulnerability database. Use this
    when the user asks if a version is safe, or before recommending a
    version to keep.

    Args:
        package: The package name on PyPI, for example "requests".
        version: The exact version to check, for example "2.25.0".

    Returns:
        A dict with the number of known vulnerabilities and up to five of
        them (ID and summary), or status "error" with a message.
    """
    try:
        result = _get_json(
            "https://api.osv.dev/v1/query",
            {"package": {"name": package.strip(), "ecosystem": "PyPI"},
             "version": version.strip()},
        )
    except Exception as exc:  # Return errors as data, not crashes.
        return {"status": "error", "error_message": f"Could not reach OSV.dev: {exc}"}
    vulns = result.get("vulns", [])
    return {
        "status": "success",
        "package": package,
        "version": version,
        "vulnerability_count": len(vulns),
        "vulnerabilities": [
            {"id": v["id"], "summary": v.get("summary", "No summary")}
            for v in vulns[:5]
        ],
    }


def compare_versions(current: str, latest: str) -> dict:
    """Compares two version numbers and says what kind of update it is.

    Use this whenever you need to decide if a version is outdated. Never
    compare version numbers yourself: 1.10.0 is newer than 1.9.0.

    Args:
        current: The version the user has, for example "2.9.0".
        latest: The newest version, for example "2.10.1".

    Returns:
        A dict with is_outdated (true or false) and update_type: "major",
        "minor", "patch" or "none".
    """
    def parse(version: str) -> tuple[int, int, int] | None:
        parts = re.findall(r"\d+", version)[:3]
        if not parts:
            return None
        parts += ["0"] * (3 - len(parts))
        return tuple(int(p) for p in parts)

    cur, new = parse(current), parse(latest)
    if cur is None or new is None:
        return {"status": "error", "error_message": "Versions must look like 1.2.3."}
    if cur >= new:
        update_type = "none"
    elif cur[0] < new[0]:
        update_type = "major"
    elif cur[1] < new[1]:
        update_type = "minor"
    else:
        update_type = "patch"
    return {
        "status": "success",
        "current": current,
        "latest": latest,
        "is_outdated": cur < new,
        "update_type": update_type,
    }
