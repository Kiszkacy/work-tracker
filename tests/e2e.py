import os
import shutil
import tempfile

import pexpect
import pytest

from work_tracker import __version__

TIMEOUT: int = 15
PROMPT_PREFIX: str = r">>"


def _spawn(data_dir: str, cache_dir: str, args: str = "-suc") -> pexpect.spawn:
    env = os.environ.copy()
    env["WORK_TRACKER_DATA_DIR"] = data_dir
    env["WORK_TRACKER_CACHE_DIR"] = cache_dir
    return pexpect.spawn(
        f"python -m work_tracker.main {args}",
        env=env,
        timeout=TIMEOUT,
        encoding="utf-8",
    )


@pytest.fixture()
def fresh_dir():
    data: str = tempfile.mkdtemp(prefix="wt_e2e_data_")
    cache: str = tempfile.mkdtemp(prefix="wt_e2e_cache_")

    yield data, cache

    shutil.rmtree(data, ignore_errors=True)
    shutil.rmtree(cache, ignore_errors=True)


@pytest.fixture(scope="module")
def initialized_dir():
    data: str = tempfile.mkdtemp(prefix="wt_e2e_data_")
    cache: str = tempfile.mkdtemp(prefix="wt_e2e_cache_")
    proc: pexpect.spawn = _spawn(data, cache)
    proc.expect(PROMPT_PREFIX)

    proc.sendline("PL")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)

    yield data, cache

    shutil.rmtree(data, ignore_errors=True)
    shutil.rmtree(cache, ignore_errors=True)


def test_first_time_launch_shows_welcome_message(fresh_dir):
    data, cache = fresh_dir
    proc = _spawn(data, cache)

    proc.expect("Welcome to")

    proc.sendline("PL")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_first_time_launch_asks_for_country_code(fresh_dir):
    data, cache = fresh_dir
    proc = _spawn(data, cache)

    proc.expect("country code")

    proc.sendline("PL")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_first_time_launch_shows_setup_complete_message(fresh_dir):
    data, cache = fresh_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("PL")

    proc.expect("Everything is set up and ready")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_first_time_launch_shows_version_after_setup(fresh_dir):
    data, cache = fresh_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("PL")

    proc.expect(f"{__version__}")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_first_time_launch_invalid_country_code_shows_error(fresh_dir):
    data, cache = fresh_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("XXXX")

    proc.expect("Invalid country code")

    proc.sendline("PL")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_first_time_launch_keeps_asking_until_valid_country_code(fresh_dir):
    data, cache = fresh_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("XXXX")

    proc.expect("Invalid country code")

    proc.sendline("YYYY")

    proc.expect("Invalid country code")

    proc.sendline("PL")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_first_time_launch_accepts_lowercase_country_code(fresh_dir):
    data, cache = fresh_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("pl")

    proc.expect("Everything is set up and ready")
    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_normal_launch_shows_version(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache)

    proc.expect(f"{__version__}")
    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_normal_launch_shows_prompt_immediately(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_normal_launch_does_not_show_welcome_again(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache)

    proc.expect(f"{__version__}")
    proc.expect(PROMPT_PREFIX)
    assert "Welcome to" not in proc.before

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_normal_launch_does_not_ask_for_country_code_again(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)
    assert "country code" not in proc.before

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_exit_command_closes_the_app(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_keyboard_interrupt_shows_unsafe_exit_message(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendcontrol("c")

    proc.expect("UNSAFE EXIT")

    proc.expect(pexpect.EOF)


def test_unknown_command_shows_error_and_keeps_running(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("thisisnotarealcommand")

    proc.expect("ERROR")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_empty_input_does_not_crash(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_multiple_sequential_commands_work(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("version")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("version")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("version")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_version_flag_prints_version_string_and_exits():
    proc = pexpect.spawn(
        "python -m work_tracker.main -v",
        timeout=TIMEOUT,
        encoding="utf-8",
    )

    proc.expect(pexpect.EOF)
    assert f"work-tracker {__version__}" in proc.before


def test_help_flag_prints_usage_and_exits():
    proc = pexpect.spawn(
        "python -m work_tracker.main --help",
        timeout=TIMEOUT,
        encoding="utf-8",
    )

    proc.expect(pexpect.EOF)
    output: str = proc.before
    assert "usage" in output.lower()
    assert "--help" in output
    assert "-v" in output


def test_skip_update_check_flag_is_accepted(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache, args="-suc")

    proc.expect(PROMPT_PREFIX)

    proc.sendline("exit")

    proc.expect(pexpect.EOF)


def test_prompt_changes_to_day_mode_after_date_input(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("01.01")

    proc.expect(r"\[01\.01\]>>")

    proc.sendline("exit && exit")

    proc.expect(pexpect.EOF)


def test_prompt_changes_to_month_mode_after_month_input(initialized_dir):
    data, cache = initialized_dir
    proc = _spawn(data, cache)

    proc.expect(PROMPT_PREFIX)

    proc.sendline("jan")

    proc.expect(r"\[jan\]>>")

    proc.sendline("exit && exit")

    proc.expect(pexpect.EOF)

