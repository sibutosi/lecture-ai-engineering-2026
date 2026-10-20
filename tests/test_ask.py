import sys
from types import SimpleNamespace

from app import ask as ask_module


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        text="answer",
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=7),
    )
    client = SimpleNamespace(
        models=SimpleNamespace(generate_content=lambda **kwargs: response)
    )
    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: client)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")

    assert ask_module.ask("question") == "answer"
    assert "[tokens] input: 12, output: 7" in capsys.readouterr().out


def test_interactive_mode_reuses_chat_for_each_question(monkeypatch, capsys):
    questions = []

    def send_message(question):
        questions.append(question)
        return SimpleNamespace(
            text=f"answer to {question}",
            usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=7),
        )

    conversation = SimpleNamespace(send_message=send_message)
    client = SimpleNamespace(
        chats=SimpleNamespace(create=lambda **kwargs: conversation)
    )
    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: client)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(sys, "argv", ["app.ask", "--interactive"])
    answers = iter(["first question", "follow-up", "終了"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    ask_module.main()

    assert questions == ["first question", "follow-up"]
    assert "answer to follow-up" in capsys.readouterr().out