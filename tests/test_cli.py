from __future__ import annotations

from pqrs_router import cli


def test_demo_runs(capsys):
    cli.demo()
    out = capsys.readouterr().out
    assert "Routing sample requests" in out
    assert "customer_service" in out
    assert "business days" in out


def test_route_prints_decision(capsys):
    cli.route("I demand a correction of an incorrect charge on my invoice.")
    out = capsys.readouterr().out
    assert "claim" in out
    assert "billing" in out


def test_main_dispatches_demo(monkeypatch):
    called = {"demo": False}
    monkeypatch.setattr(cli, "demo", lambda: called.__setitem__("demo", True))
    monkeypatch.setattr("sys.argv", ["pqrs-router", "demo"])
    cli.main()
    assert called["demo"] is True
