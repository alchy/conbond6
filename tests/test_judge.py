"""Soudci věrnosti extrakce (bench/judge.py) — dřív netestováno vůbec.
`ClaudeCliJudge` se testuje s nahraným `subprocess.run` (žádné skutečné
volání `claude` CLI v testech — bylo by drahé, pomalé a nehermetické)."""

import json
import subprocess
from unittest.mock import patch

from bench.judge import CachedJudge, ClaudeCliJudge, _parse_verdict, fingerprint


def test_fingerprint_je_deterministicky() -> None:
    a = fingerprint("narodit_se(kdo: X)", "X se narodil.")
    b = fingerprint("narodit_se(kdo: X)", "X se narodil.")
    c = fingerprint("narodit_se(kdo: Y)", "X se narodil.")
    assert a == b and a != c


def test_parse_verdict_z_json() -> None:
    assert _parse_verdict('{"verdikt": "tvrdí", "pozn": "sedí"}') == ("tvrdí", "sedí")
    assert _parse_verdict('blabla {"verdikt": "netvrdí", "pozn": "x"} blabla') == ("netvrdí", "x")


def test_parse_verdict_bez_json_padne_na_klicove_slovo() -> None:
    assert _parse_verdict("Odpověď: netvrdí, protože...")[0] == "netvrdí"
    assert _parse_verdict("nesmyslná odpověď bez klíčového slova")[0] == "částečně"


def _fake_run(result: dict, returncode: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=json.dumps(result), stderr="")


def test_claude_cli_judge_parsuje_uspesnou_odpoved() -> None:
    j = ClaudeCliJudge(model="haiku")
    fake = _fake_run({"is_error": False, "result": '{"verdikt": "tvrdí", "pozn": "sedí"}'})
    with patch("subprocess.run", return_value=fake) as run:
        v, note = j.judge("narodit_se(kdo: X, kde: Y)", "X se narodil v Y.")
    assert v == "tvrdí" and note == "sedí"
    cmd = run.call_args.args[0]
    assert cmd[:4] == ["claude", "-p", "--model", "haiku"] and "--tools" in cmd and "--json-schema" in cmd
    assert run.call_args.kwargs["cwd"] != "."  # mimo repo — viz docstring třídy


def test_claude_cli_judge_is_error_dava_castecne() -> None:
    j = ClaudeCliJudge(model="haiku")
    fake = _fake_run({"is_error": True, "result": "odmítnuto"})
    with patch("subprocess.run", return_value=fake):
        v, note = j.judge("x(kdo: Y)", "Y udělal x.")
    assert v == "částečně" and "odmítnuto" in note


def test_claude_cli_judge_selhani_procesu_je_runtime_error() -> None:
    j = ClaudeCliJudge(model="haiku")
    fake = _fake_run({}, returncode=1)
    with patch("subprocess.run", return_value=fake):
        try:
            j.judge("x(kdo: Y)", "Y udělal x.")
            assert False, "mělo selhat"
        except RuntimeError:
            pass


def test_cached_judge_druhe_volani_nepta_vnitrniho_soudce(tmp_path) -> None:
    class _Counting:
        name = "test"
        calls = 0

        def judge(self, render: str, sentence: str, context: str = "") -> tuple:  # pylint: disable=unused-argument
            self.calls += 1
            return "tvrdí", "ok"
    inner = _Counting()
    cache_path = tmp_path / "cache.json"
    cj = CachedJudge(inner, cache_path)  # type: ignore[arg-type]
    assert cj.judge("p(kdo: X)", "X.") == ("tvrdí", "ok")
    assert cj.judge("p(kdo: X)", "X.") == ("tvrdí", "ok")
    assert inner.calls == 1 and cj.hits == 1 and cj.misses == 1
    cj.flush()
    cj2 = CachedJudge(inner, cache_path)  # type: ignore[arg-type]
    assert cj2.judge("p(kdo: X)", "X.") == ("tvrdí", "ok")
    assert inner.calls == 1  # z disku, ne od vnitřního soudce
