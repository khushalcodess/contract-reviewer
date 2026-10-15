from types import SimpleNamespace

from src import llm


def _fake_client(reply, calls):
    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=reply))],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5),
        )
    completions = SimpleNamespace(create=create)
    return SimpleNamespace(chat=SimpleNamespace(completions=completions))


def test_second_identical_call_uses_cache(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(llm, "CACHE_DIR", tmp_path / "c")
    monkeypatch.setattr(llm, "LOG_PATH", tmp_path / "log.jsonl")
    monkeypatch.setattr(llm, "_get_client", lambda: _fake_client("hi", calls))

    assert llm.complete("sys", "user") == "hi"
    assert llm.complete("sys", "user") == "hi"
    assert len(calls) == 1


def test_different_prompt_is_not_cached(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(llm, "CACHE_DIR", tmp_path / "c")
    monkeypatch.setattr(llm, "LOG_PATH", tmp_path / "log.jsonl")
    monkeypatch.setattr(llm, "_get_client", lambda: _fake_client("hi", calls))

    llm.complete("sys", "user one")
    llm.complete("sys", "user two")
    assert len(calls) == 2


def test_empty_reply_is_not_cached(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(llm, "CACHE_DIR", tmp_path / "c")
    monkeypatch.setattr(llm, "LOG_PATH", tmp_path / "log.jsonl")
    monkeypatch.setattr(llm, "_get_client", lambda: _fake_client("", calls))

    llm.complete("sys", "user")
    llm.complete("sys", "user")
    assert len(calls) == 2