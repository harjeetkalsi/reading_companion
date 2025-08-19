import core.nlp.explain_terms as et_mod
import core.nlp.question_gen as qg_mod
import core.nlp.simplify as sim_mod

import types
import pytest 

class DummyChoice:
    def __init__(self, content):
        self.message = types.SimpleNamespace(content=content)

class DummyResp:
    def __init__(self, content):
        self.choices = [DummyChoice(content)]

# explain_terms 

def test_explain_terms_happy_path(monkeypatch):
    def fake_create(*args, **kwargs):
        # shape checks
        assert kwargs["model"] == "gpt-3.5-turbo"
        msgs = kwargs["messages"]
        assert msgs[0]["role"] == "system"
        assert "explains academic or technical vocab" in msgs[0]["content"].lower()
        assert "Pick out the techincal words" in msgs[1]["content"]
        return DummyResp("Term1 — simple def\nTerm2 — simple def")
    monkeypatch.setattr(et_mod.client.chat.completions, "create", fake_create)

    out = et_mod.explain_terms("Some technical paragraph.")
    assert "Term1" in out

def test_explain_terms_error_is_caught(monkeypatch):
    class Boom(Exception): pass
    def fake_create(*a, **k): raise Boom("API down")
    monkeypatch.setattr(et_mod.client.chat.completions, "create", fake_create)

    out = et_mod.explain_terms("text")
    assert out.startswith("⚠️ Error:")

# question_gen

def test_question_gen_calls_api(monkeypatch):
    def fake_create(*a, **k):
        msgs = k["messages"]
        assert "Generate 3 comprehension questions" in msgs[1]["content"]
        return DummyResp("Q1?\nQ2?\nQ3?")
    monkeypatch.setattr(qg_mod.client.chat.completions, "create", fake_create)

    out = qg_mod.question_gen("paragraph")
    assert "Q1?" in out and "Q3?" in out

# question_answers

def test_question_answers_calls_api(monkeypatch):
    def fake_create(*a, **k):
        msgs = k["messages"]
        assert "now give them the answers" in msgs[1]["content"].lower()
        return DummyResp("A1\nA2\nA3")
    monkeypatch.setattr(qg_mod.client.chat.completions, "create", fake_create)

    out = qg_mod.question_answers("Q1?\nQ2?\nQ3?")
    assert "A1" in out

# simplify_text 

def test_simplify_text_calls_api(monkeypatch):
    def fake_create(*a, **k):
        assert k["max_tokens"] == 400
        assert "Simplify the following text" in k["messages"][1]["content"]
        return DummyResp("Simplified output.")
    monkeypatch.setattr(sim_mod.client.chat.completions, "create", fake_create)

    out = sim_mod.simplify_text("Hard paragraph")
    assert "Simplified output." == out    