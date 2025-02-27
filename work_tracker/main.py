from work_tracker._work_tracker import WorkTracker
from work_tracker import __version__

import sys


def main():
    args: list[str] = sys.argv[1:]

    if "-h" in args or "--help" in args:
        print("WorkTracker: A tool to track your work hours and manage your schedule.")
        print("To run the app, simply execute: work-tracker")
        print("Usage: work-tracker [OPTION]")
        print("  -h, --help                 Show this help message")
        print("  -v, --version              Show the current version of WorkTracker")
        print("  -suc, --skip-update-check  Skip the update check on startup")
        sys.exit(0)

    if "-v" in args or "--version" in args:
        print(f"WorkTracker version installed: {__version__}")
        sys.exit(0)

    skip_update_check: bool = "-suc" in args or "--skip-update-check" in args

    tracker: WorkTracker = WorkTracker()
    tracker.initialize(check_is_new_version_available=not skip_update_check)
    tracker.start()


if __name__ == '__main__':
    main()
