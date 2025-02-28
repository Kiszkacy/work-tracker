import pexpect


def test_launch():
    work_tracker = pexpect.spawn("python -m work_tracker.main -suc")
    # first-time prompt
    work_tracker.expect(">>")
    work_tracker.sendline("pl")
    work_tracker.expect(">>")
    work_tracker.sendline("no")
    # successful launch, test help command
    work_tracker.expect(">>")
    work_tracker.sendline("help")
    work_tracker.expect(">>")
    work_tracker.sendline("exit")
    work_tracker.expect_exact(pexpect.EOF)

