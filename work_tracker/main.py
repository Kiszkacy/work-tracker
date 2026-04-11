import argparse

from work_tracker import __version__
from work_tracker._work_tracker import WorkTracker


def main():
    parser = argparse.ArgumentParser(
        prog="work-tracker",
        description="A tool to track your work hours and manage your schedule.",
        epilog="To start the app, simply run work-tracker with no arguments.",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=40),
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-suc", "--skip-update-check", action="store_true", help="skip the update check on startup")

    args = parser.parse_args()

    tracker: WorkTracker = WorkTracker()
    tracker.initialize(check_is_new_version_available=not args.skip_update_check)
    tracker.start()


if __name__ == '__main__':
    main()
