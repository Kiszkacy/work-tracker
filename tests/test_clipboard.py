from work_tracker.command.clipboard import Clipboard


def test_set_and_get():
    Clipboard.set("key", "value")
    assert Clipboard.get("key") == "value"


def test_get_returns_none_for_missing_key():
    assert Clipboard.get("nonexistent") is None


def test_has_returns_true_when_key_exists():
    Clipboard.set("k", 42)
    assert Clipboard.has("k") is True


def test_has_returns_false_when_key_missing():
    assert Clipboard.has("missing") is False


def test_pop_removes_only_that_key():
    Clipboard.set("a", 1)
    Clipboard.set("b", 2)

    Clipboard.pop("a")

    assert not Clipboard.has("a")
    assert Clipboard.has("b")


def test_pop_missing_key_does_not_raise():
    Clipboard.pop("definitely_not_here")


def test_clear_removes_all_keys():
    Clipboard.set("x", 1)
    Clipboard.set("y", 2)

    Clipboard.clear()

    assert not Clipboard.has("x")
    assert not Clipboard.has("y")


def test_overwrite_existing_key():
    Clipboard.set("k", "first")
    Clipboard.set("k", "second")
    assert Clipboard.get("k") == "second"


def test_stores_arbitrary_types():
    obj = {"nested": [1, 2, 3]}
    Clipboard.set("obj", obj)
    assert Clipboard.get("obj") == {"nested": [1, 2, 3]}
