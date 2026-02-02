import reading_companion.core.nlp.explain_terms as et_mod
import reading_companion.core.nlp.question_gen as qg_mod
import reading_companion.core.nlp.simplify as sim_mod
from reading_companion.core.nlp.openai_client import set_client

import types

class DummyChoice:
    def __init__(self, content): self.message = types.SimpleNamespace(content=content)
class DummyResp:
    def __init__(self, content): self.choices = [DummyChoice(content)]
class DummyCompletions:
    def create(self, **kwargs): return DummyResp("DUMMY")
class DummyChat:
    def __init__(self): self.completions = DummyCompletions()
class DummyClient:
    def __init__(self): self.chat = DummyChat()



def test_simplify_text_uses_client_injection(monkeypatch):
    set_client(DummyClient())  # inject fake
    from reading_companion.core.nlp.simplify import simplify_text
    out = simplify_text("Hello world")
    assert "DUMMY" in out
    
# explain_terms 

def test_explain_terms_happy_path(monkeypatch):
    class VerifyCompletions(DummyCompletions):
        def create(self, **kwargs):
            assert kwargs["model"] == "gpt-5-nano"
            msgs = kwargs["messages"]
            assert msgs[0]["role"] == "system"
            assert "explain" in msgs[0]["content"].lower()
            assert "Pick out all the scientific words" in msgs[1]["content"]
            return DummyResp("Term1 — simple def\nTerm2 — simple def")

    class VerifyChat(DummyChat):
        def __init__(self): self.completions = VerifyCompletions()

    monkeypatch.setattr(et_mod, "get_client", lambda: types.SimpleNamespace(chat=VerifyChat()))
    out = et_mod.explain_terms("Some technical paragraph.")
    assert "Term1" in out

def test_explain_terms_error_is_caught(monkeypatch):
    class Boom(Exception): 
        pass
    class ErrorCompletions(DummyCompletions):
        def create(self, *a, **k): raise Boom("API down")
    class ErrorChat(DummyChat):
        def __init__(self): self.completions = ErrorCompletions()

    monkeypatch.setattr(et_mod, "get_client", lambda: types.SimpleNamespace(chat=ErrorChat()))
    out = et_mod.explain_terms("x")
    assert "⚠️ Error:" in out  

# question_gen

def test_question_gen_calls_api(monkeypatch):
    class VerifyCompletions(DummyCompletions):
        def create(self, **k):
            msgs = k["messages"]
            assert "Generate 3 comprehension questions" in msgs[1]["content"]
            return DummyResp("Q1?\nQ2?\nQ3?")
    class VerifyChat(DummyChat):
        def __init__(self): self.completions = VerifyCompletions()

    monkeypatch.setattr(qg_mod, "get_client", lambda: types.SimpleNamespace(chat=VerifyChat()))
    out = qg_mod.question_gen("para")
    assert "Q1?" in out

# question_answers

def test_question_answers_calls_api(monkeypatch):
    class VerifyCompletions(DummyCompletions):
        def create(self, **k):
            assert "answers" in k["messages"][1]["content"].lower()
            return DummyResp("A1\nA2\nA3")
    class VerifyChat(DummyChat):
        def __init__(self): self.completions = VerifyCompletions()

    monkeypatch.setattr(qg_mod, "get_client", lambda: types.SimpleNamespace(chat=VerifyChat()))
    out = qg_mod.question_answers("Q1?\nQ2?\nQ3?")
    assert "A1" in out

# simplify_text 

def test_simplify_text_calls_api(monkeypatch):
    class VerifyCompletions(DummyCompletions):
        def create(self, **k):
            assert "Simplify the following text" in k["messages"][1]["content"]
            return DummyResp("Simplified output.")
    class VerifyChat(DummyChat):
        def __init__(self): self.completions = VerifyCompletions()

    monkeypatch.setattr(sim_mod, "get_client", lambda: types.SimpleNamespace(chat=VerifyChat()))
    out = sim_mod.simplify_text("hello")
    assert "Simplified" in out