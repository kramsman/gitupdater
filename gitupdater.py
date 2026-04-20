## run gitupdater to make sure bekutils and bekgoogle utility libraries are updated
#import sys
#import os
#sys.path.append(os.path.expanduser("~/Dropbox/Postcard Files/"))
#if True:
#    import gitupdater



import subprocess
import urllib.request
import json
import os
import sys
import importlib.util
import importlib.metadata

_config_path = os.path.join(os.getcwd(), "gitupdater_packages.json")
if os.path.exists(_config_path):
    with open(_config_path) as _f:
        GITHUB_PACKAGES = [(_p["url"], _p["module"]) for _p in json.load(_f)]
else:
    GITHUB_PACKAGES = [
        ("git+https://github.com/kramsman/uvbekutils.git", "uvbekutils"),
        ("git+https://github.com/kramsman/bekgoogle.git", "bekgoogle"),
    ]

UPDATER_FILE = os.path.join(os.getcwd(), "gitupdater.json")


def get_latest_commit(github_url):
    """Return the latest commit SHA on the default branch."""
    repo_path = github_url.replace("git+https://github.com/", "").replace(".git", "")
    api_url = f"https://api.github.com/repos/{repo_path}/commits/HEAD"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Python"})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        return data["sha"]


def get_last_updated(github_url):
    repo_path = github_url.replace("git+https://github.com/", "").replace(".git", "")
    api_url = f"https://api.github.com/repos/{repo_path}"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Python"})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        return data["updated_at"]


def package_installed(module_name):
    """Check existence without importing (avoids caching old version in sys.modules)."""
    return importlib.util.find_spec(module_name) is not None


def get_installed_commit(module_name):
    """Return the installed git commit SHA from the package's direct_url.json, or None."""
    try:
        dist = importlib.metadata.distribution(module_name)
        direct_url_path = dist.locate_file("direct_url.json")
        if os.path.exists(direct_url_path):
            with open(direct_url_path) as f:
                data = json.load(f)
            return data.get("vcs_info", {}).get("commit_id")
    except Exception:
        pass
    return None


# Load saved timestamps
stamps = {}
if os.path.exists(UPDATER_FILE):
    with open(UPDATER_FILE) as f:
        stamps = json.load(f)

updated = False
for url, module in GITHUB_PACKAGES:
    last_updated = get_last_updated(url)
    latest_commit = get_latest_commit(url)
    installed_commit = get_installed_commit(module)

    if not package_installed(module):
        print(f"{module} not installed, installing...")
        subprocess.run(["uv", "pip", "install", "--reinstall", url], check=True)
        stamps[url] = last_updated
        updated = True
    elif stamps.get(url) != last_updated or (latest_commit and installed_commit and latest_commit != installed_commit):
        print(f"Update found, reinstalling {module}...")
        subprocess.run(["uv", "pip", "install", "--reinstall", url], check=True)
        stamps[url] = last_updated
        updated = True
    else:
        print(f"{module} is up to date")

# Save updated timestamps
with open(UPDATER_FILE, "w") as f:
    json.dump(stamps, f)

if updated:
    print()
    print("** Libraries were updated. Please re-run the script to use the latest version.")
    print()
    sys.exit(0)
