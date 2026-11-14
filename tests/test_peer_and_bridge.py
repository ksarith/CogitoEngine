"""Offline tests for EXPERIMENTAL peer mode and the idea-generator bridge.

They cover mechanics (parsing, code-enforced independence limits, ledger,
selection, feed rules), not model behavior: whether peer seats actually behave
better than strict roles is CE-U09 and is not measured here.

Run: python -m unittest discover tests
"""

import json
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cogito.ideagen_bridge import (BridgeError, IdeaGenClient, Ledger, feed_run,  # noqa: E402
                                   main as bridge_main, medal_of, select_candidates, vet_board,
                                   vet_one)
from cogito.llm import LLMError, LLMResponse  # noqa: E402
from cogito.peer import (Seat, PeerFlow, PeerFlowAborted, parse_output,  # noqa: E402
                         peer_flow_from_yaml)

ROOT = Path(__file__).resolve().parent.parent
PEER_YAML = ROOT / "examples/flows/peer_cluster.yaml"


def fake(text):
    return LLMResponse(text, "m-1", "mistral", requested_model="m-latest",
                       base_url="https://example.test/v1", temperature=0.2)


def scripted(*texts):
    it = iter(texts)
    return lambda *a, **k: fake(next(it))


def three(**over):
    seats = [Seat("a", family=over.get("fa", "")), Seat("b", family=over.get("fb", "")),
             Seat("c", certifies=True, family=over.get("fc", ""))]
    return PeerFlow(seats)


class Parsing(unittest.TestCase):
    def test_notes_dispositions_labels(self):
        p = parse_output("Main text.\n[NOTE:objection] too heavy\nmore\n**[note:Counter_Proposal]** use X\n"
                         "[DISPOSITION:N1:partially answered] ok\n[LABEL:a:measured] fine")
        self.assertEqual(p.body, "Main text.")
        self.assertEqual([t for t, _ in p.notes], ["objection", "counter-proposal"])
        self.assertEqual(p.notes[0][1], "too heavy\nmore")
        self.assertEqual(p.dispositions[0][:2], ("n1", "partially answered"))
        self.assertEqual(p.labels[0][:2], ("a", "Measured"))

    def test_malformed_is_recorded_not_dropped(self):
        p = parse_output("x\n[NOTE:rant] hm\n[DISPOSITION:n1:maybe] y\n[LABEL:a:Vibes] z\n[NOTE:question]")
        self.assertEqual(len(p.malformed), 4)
        self.assertEqual((p.notes, p.dispositions, p.labels), ([], [], []))


class IndependenceIsEnforcedInCode(unittest.TestCase):
    def test_self_disposition_ignored_and_other_accepted(self):
        outs = ["body a\n[NOTE:objection] weak premise",
                "body b\n[DISPOSITION:n1:answered] mine\n[NOTE:question] why",
                "body c\n[DISPOSITION:n1:unresolved] no\n[DISPOSITION:n2:answered] ok"]
        with mock.patch("cogito.peer.call_llm", side_effect=scripted(*outs)):
            r = three().run("task")
        self.assertEqual([x["status"] for x in r.ledger()], ["unresolved", "answered"])
        self.assertEqual(r.seats[2].flags, [])
        self.assertEqual([r.status_of("n1").by, r.status_of("n2").by], ["c", "c"])

    def test_author_cannot_close_own_note(self):
        from cogito.peer import Note, PeerResult
        pr = PeerResult(task="t", notes=[Note("n1", "a", "objection", "x")])
        PeerFlow._record(pr, Seat("a"), parse_output("[DISPOSITION:n1:answered] mine"), [], set())
        self.assertFalse(pr.dispositions[0].accepted)
        self.assertEqual(pr.dispositions[0].flag, "self_disposition")
        self.assertIsNone(pr.status_of("n1"))      # still open: the author cannot close it
        PeerFlow._record(pr, Seat("b"), parse_output("[DISPOSITION:n1:answered] ok"), [], {"n1"})
        self.assertEqual(pr.status_of("n1").by, "b")

    def test_labels_only_from_certifier_and_never_for_self(self):
        outs = ["a\n[LABEL:a:Measured] self-praise",
                "b\n[LABEL:a:Measured] not a certifier",
                "c\n[LABEL:a:Analogous] ok\n[LABEL:c:Measured] me\n[LABEL:ghost:Measured] ?"]
        with mock.patch("cogito.peer.call_llm", side_effect=scripted(*outs)):
            r = three().run("t")
        ok = [(l.target, l.by) for l in r.labels if l.accepted]
        self.assertEqual(ok, [("a", "c")])
        flags = {l.flag for l in r.labels if not l.accepted}
        self.assertEqual(flags, {"label_not_authorized", "self_certification", "unknown_target"})

    def test_undisposed_is_flagged_loudly(self):
        outs = ["a\n[NOTE:question] q", "b\nignores it", "c\nalso"]
        with mock.patch("cogito.peer.call_llm", side_effect=scripted(*outs)):
            r = three().run("t")
        self.assertIn("undisposed:n1", r.seats[1].flags)
        self.assertEqual(r.still_open()[0]["id"], "n1")

    def test_notes_visible_to_next_seat_with_owed_marker(self):
        prompts = []

        def spy(prompt, **k):
            prompts.append(prompt)
            return fake("x\n[NOTE:objection] o" if len(prompts) == 1 else "y")

        with mock.patch("cogito.peer.call_llm", side_effect=spy):
            three().run("t")
        self.assertIn("n1 [objection] by a", prompts[1])
        self.assertIn("you owe a disposition", prompts[1])
        self.assertNotIn("you owe a disposition", prompts[0])

    def test_system_prompt_marks_certifier_only(self):
        s = []
        with mock.patch("cogito.peer.call_llm", side_effect=lambda p, system=None, **k: (s.append(system), fake("x"))[1]):
            three().run("t")
        self.assertNotIn("You are also a certifier seat", s[0])
        self.assertIn("You are also a certifier seat", s[2])


class Records(unittest.TestCase):
    def test_refusal_is_first_class_and_stops_when_asked(self):
        flow = PeerFlow([Seat("a", stop_on_refusal=True), Seat("b")])
        with mock.patch("cogito.peer.call_llm", side_effect=scripted("**[REFUSAL]** unfalsifiable")):
            r = flow.run("t")
        self.assertEqual(len(r.seats), 1)
        self.assertEqual(r.refused.seat_name, "a")

    def test_failure_keeps_completed_seats(self):
        def flaky(*a, **k):
            flaky.n += 1
            if flaky.n == 2:
                raise LLMError("500")
            return fake("ok")
        flaky.n = 0
        with mock.patch("cogito.peer.call_llm", side_effect=flaky):
            with self.assertRaises(PeerFlowAborted) as cm:
                three().run("t")
        self.assertEqual([s.seat_name for s in cm.exception.partial.seats], ["a"])
        self.assertIsInstance(cm.exception, LLMError)

    def test_provenance_and_family_warning(self):
        with mock.patch("cogito.peer.call_llm", side_effect=scripted("a", "b", "c")):
            r = three(fa="x", fb="x", fc="x").run("t")
        self.assertEqual(r.seats[0].agent_result.requested_model, "m-latest")
        self.assertIn("one declared family", r.independence_warning)
        with mock.patch("cogito.peer.call_llm", side_effect=scripted("a", "b", "c")):
            r2 = three(fa="x", fb="y", fc="z").run("t")
        self.assertNotIn("Not independent", r2.independence_warning)
        with mock.patch("cogito.peer.call_llm", side_effect=scripted("a", "b", "c")):
            r3 = three(fa="x", fb="y").run("t")      # c undisclosed
        self.assertIn("Not independent", r3.independence_warning)
        json.dumps(r.to_dict())                      # serializable

    def test_assembly_rules(self):
        for bad in ([Seat("a")], [Seat("a"), Seat("A")], [Seat("a", certifies=True), Seat("b")],
                    [Seat("n1"), Seat("b")], [Seat("bad name"), Seat("b")]):
            with self.assertRaises(ValueError):
                PeerFlow(bad)

    def test_yaml_strict_and_shipped_example_valid(self):
        self.assertEqual(len(peer_flow_from_yaml(PEER_YAML).seats), 4)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.yaml"
            p.write_text("seats:\n  - name: a\n    role: Skeptic\n  - name: b\n")
            with self.assertRaises(ValueError):
                peer_flow_from_yaml(p)
            p.write_text("steps: []\n")
            with self.assertRaises(ValueError):
                peer_flow_from_yaml(p)


# ----------------------------------------------------------------- bridge

IDEAS = [
    {"id": 1, "title": "Gold one", "pitch": "p1", "originality": 5, "feasibility": 4, "impact": 4, "reason": "r"},
    {"id": 2, "title": "Silver", "pitch": "p2", "originality": 4, "feasibility": 4, "impact": 3, "reason": "r"},
    {"id": 3, "title": "Bronze", "pitch": "p3", "originality": 3, "feasibility": 3, "impact": 3, "reason": "r"},
    {"id": 4, "title": "Unjudged", "pitch": "", "originality": None, "feasibility": None, "impact": None},
    {"id": 5, "title": "Hand gold", "pitch": "", "originality": None, "feasibility": None, "impact": None,
     "medalOverride": 3},
]


class FakeIdeaGen(BaseHTTPRequestHandler):
    seeds: list = []
    fail_seed = False

    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/api/boards":
            return self._send(200, {"boards": [{"id": 1, "title": "T", "goal": "g"}]})
        if self.path == "/api/boards/1":
            return self._send(200, {"board": {"id": 1, "title": "T", "goal": "Cheap water"},
                                    "ideas": IDEAS, "edges": []})
        self._send(404, {"error": "no"})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/api/boards/1/seed":
            if FakeIdeaGen.fail_seed:
                return self._send(502, {"error": "llm_failed"})
            FakeIdeaGen.seeds.append(body["text"])
            return self._send(200, {"idea": {"id": 100 + len(FakeIdeaGen.seeds)}})
        self._send(404, {"error": "no"})


class Bridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), FakeIdeaGen)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.srv.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def setUp(self):
        FakeIdeaGen.seeds, FakeIdeaGen.fail_seed = [], False
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.ledger = Ledger(self.dir / "ledger.jsonl")
        self.client = IdeaGenClient(self.url)

    def tearDown(self):
        self.tmp.cleanup()

    def vet(self, **kw):
        args = dict(arms=["peer"], peer_flow_path=PEER_YAML, min_medal=2, max_ideas=5, max_depth=2,
                    show_jury=False, out_dir=self.dir / "runs", ledger=self.ledger,
                    write_project=False, dry_run=False, log=lambda *a: None)
        args.update(kw)
        return vet_board(self.client, 1, **args)

    def test_medals_mirror_score_js(self):
        self.assertEqual([medal_of(i) for i in IDEAS], [3, 2, 1, None, 3])

    def test_selection_order_and_skips(self):
        picked, skipped = select_candidates(IDEAS, self.ledger, ["peer"], min_medal=2, max_ideas=2, max_depth=2)
        self.assertEqual([i["id"] for i in picked], [5, 1])       # hand gold fitness 14 > 13
        reasons = dict(skipped)
        self.assertEqual((reasons[3], reasons[4], reasons[2]), ("below_medal", "not_judged", "over_max_ideas"))

    def test_remote_url_refused(self):
        with self.assertRaises(BridgeError):
            IdeaGenClient("http://example.com:8300")
        IdeaGenClient("http://example.com:8300", allow_remote=True)

    def test_dry_run_calls_no_llm_and_writes_nothing(self):
        with mock.patch("cogito.peer.call_llm") as m:
            self.assertEqual(self.vet(dry_run=True), [])
        m.assert_not_called()
        self.assertFalse((self.dir / "runs").exists())

    def test_vet_then_feed_roundtrip_and_idempotence(self):
        script = ["open", "p\n[NOTE:counter-proposal] Use a magnetic separator instead of a sieve, "
                  "because salvage steel is plentiful.\n[NOTE:objection] weak\n[NOTE:counter-proposal] second",
                  "p\n[DISPOSITION:n1:answered] ok\n[DISPOSITION:n2:unresolved] x\n[DISPOSITION:n3:answered] y",
                  "cert\n[LABEL:pressure_a:Analogous] a"]
        with mock.patch("cogito.peer.call_llm", side_effect=scripted(*(script * 5))):
            runs = self.vet(max_ideas=1)
        self.assertEqual(len(runs), 1)
        run = runs[0]
        self.assertEqual((run["arm"], run["status"], run["source"]["idea_id"]), ("peer", "completed", 5))
        self.assertFalse(run["jury_shown_to_seats"])
        self.assertTrue((self.dir / "runs" / f"{run['run_id']}.md").exists())
        # the task given to seats must not carry the jury score by default
        self.assertNotIn("Jury opinion", run["result"]["seats"][0]["prompt"])
        fed = feed_run(self.client, run, self.ledger, log=lambda *a: None)
        self.assertEqual(len(fed), 2)                                  # two counter-proposals, objection not fed
        self.assertEqual(len(FakeIdeaGen.seeds), 2)
        self.assertEqual(fed[0]["depth"], 1)
        self.assertEqual(feed_run(self.client, run, self.ledger, log=lambda *a: None), [])  # idempotent
        # a vetted idea is not vetted again; fed ideas carry depth
        picked, skipped = select_candidates(IDEAS, Ledger(self.dir / "ledger.jsonl"), ["peer"],
                                            min_medal=2, max_ideas=5, max_depth=2)
        self.assertNotIn(5, [i["id"] for i in picked])

    def test_show_jury_is_opt_in_and_recorded(self):
        with mock.patch("cogito.peer.call_llm", side_effect=scripted(*(["x"] * 4))):
            run = self.vet(max_ideas=1, show_jury=True)[0]
        self.assertTrue(run["jury_shown_to_seats"])
        self.assertIn("Jury opinion", run["result"]["seats"][0]["prompt"])

    def test_refused_run_feeds_nothing_by_default(self):
        out = ["**[REFUSAL]** unfalsifiable\n[NOTE:counter-proposal] rethink as X", "y", "z", "w"]
        with mock.patch("cogito.peer.call_llm", side_effect=scripted(*out)):
            run = self.vet(max_ideas=1)[0]
        self.assertEqual(run["status"], "refused")
        self.assertEqual(feed_run(self.client, run, self.ledger, log=lambda *a: None), [])
        self.assertEqual(FakeIdeaGen.seeds, [])
        self.assertEqual(len(feed_run(self.client, run, self.ledger, include_refused=True,
                                      log=lambda *a: None)), 1)

    def test_aborted_run_is_recorded_but_retries(self):
        calls = {"n": 0}

        def flaky(*a, **k):
            calls["n"] += 1
            if calls["n"] == 2:
                raise LLMError("500")
            return fake("ok")

        with mock.patch("cogito.peer.call_llm", side_effect=flaky):
            run = self.vet(max_ideas=1)[0]
        self.assertEqual(run["status"], "aborted")
        self.assertEqual(len(run["result"]["seats"]), 1)
        self.assertEqual(self.ledger.vetted_arms(5), set())           # will retry
        self.assertEqual(feed_run(self.client, run, self.ledger, log=lambda *a: None), [])

    def test_depth_guard(self):
        self.ledger.add(kind="fed", run_id="r", note_id="n1", author="a", from_idea_id=1,
                        board_id=1, new_idea_id=2, depth=2)
        picked, skipped = select_candidates(IDEAS, self.ledger, ["peer"], min_medal=2, max_ideas=5, max_depth=2)
        self.assertIn((2, "depth_guard"), skipped)

    def test_both_arms_and_project_note_never_overwrites(self):
        proj = self.dir / "proj"
        proj.mkdir()
        (proj / "COGITO_VETTING.md").write_text("mine")
        ideas = [dict(IDEAS[0], projectPath=str(proj))]
        with mock.patch.object(IdeaGenClient, "board",
                               return_value={"board": {"id": 1, "goal": "g"}, "ideas": ideas}):
            with mock.patch("cogito.agent.call_llm", side_effect=scripted(*(["s"] * 5))), \
                 mock.patch("cogito.peer.call_llm", side_effect=scripted(*(["p"] * 4))):
                runs = self.vet(arms=["strict", "peer"], write_project=True)
        self.assertEqual({r["arm"] for r in runs}, {"strict", "peer"})
        self.assertEqual((proj / "COGITO_VETTING.md").read_text(), "mine")
        self.assertTrue((proj / "COGITO_VETTING-2.md").exists())

    def test_seed_http_error_surfaces(self):
        FakeIdeaGen.fail_seed = True
        run = {"run_id": "r1", "arm": "peer", "status": "completed", "source": {"board_id": 1, "idea_id": 1},
               "result": {"notes": [{"id": "n1", "author": "a", "type": "counter-proposal", "text": "x"}]}}
        with self.assertRaises(BridgeError):
            feed_run(self.client, run, self.ledger, log=lambda *a: None)
        self.assertEqual([r for r in self.ledger.rows if r["kind"] == "fed"], [])  # nothing recorded as fed

    def test_cli_boards_and_dry_run(self):
        self.assertEqual(bridge_main(["--url", self.url, "--ledger", str(self.dir / "l.jsonl"), "boards"]), 0)
        self.assertEqual(bridge_main(["--url", self.url, "--ledger", str(self.dir / "l.jsonl"),
                                      "vet", "1", "--dry-run"]), 0)
        self.assertEqual(bridge_main(["--url", "http://127.0.0.1:1", "boards"]), 1)


class VetOne(unittest.TestCase):
    """The pure entry point the idea generator's server spawns (stdin JSON -> stdout JSON)."""

    PAYLOAD = {"board_id": 1, "goal": "Cheap water", "arm": "peer", "show_jury": False,
               "idea": {"id": 7, "title": "Rain sieve", "pitch": "p", "originality": 4,
                        "feasibility": 4, "impact": 4, "reason": "strong"}}

    def test_peer_run_record_and_no_jury_by_default(self):
        with mock.patch("cogito.peer.call_llm", side_effect=scripted(*(["x\n[NOTE:counter-proposal] y"] * 4))):
            out = vet_one(dict(self.PAYLOAD), PEER_YAML)
        run = out["runs"][0]
        self.assertEqual((run["arm"], run["status"], run["source"]["idea_id"]), ("peer", "completed", 7))
        self.assertIn("markdown", run)
        self.assertNotIn("Jury opinion", run["result"]["seats"][0]["prompt"])
        self.assertEqual(run["result"]["notes"][0]["type"], "counter-proposal")
        json.dumps(out)

    def test_both_arms_and_validation(self):
        with mock.patch("cogito.agent.call_llm", side_effect=scripted(*(["s"] * 5))), \
             mock.patch("cogito.peer.call_llm", side_effect=scripted(*(["p"] * 4))):
            out = vet_one({**self.PAYLOAD, "arm": "both"}, PEER_YAML)
        self.assertEqual([r["arm"] for r in out["runs"]], ["strict", "peer"])
        for bad in ({**self.PAYLOAD, "arm": "x"}, {**self.PAYLOAD, "board_id": "1"},
                    {**self.PAYLOAD, "idea": {"title": "no id"}}):
            with self.assertRaises(ValueError):
                vet_one(bad, PEER_YAML)

    def test_provider_failure_is_an_aborted_run_not_a_crash(self):
        def boom(*a, **k):
            raise LLMError("MISTRAL_API_KEY not set")
        with mock.patch("cogito.peer.call_llm", side_effect=boom):
            run = vet_one(dict(self.PAYLOAD), PEER_YAML)["runs"][0]
        self.assertEqual(run["status"], "aborted")
        self.assertIn("MISTRAL_API_KEY", run["error"])

    def test_cli_stdout_is_json_only(self):
        import subprocess
        env = {"PATH": "/usr/bin:/bin"}   # no API keys: the run aborts, but cleanly
        proc = subprocess.run([sys.executable, "-m", "cogito.ideagen_bridge", "vet-one", "--stdin"],
                              input=json.dumps(self.PAYLOAD), capture_output=True, text=True,
                              cwd=ROOT, env=env, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["runs"][0]["status"], "aborted")
        bad = subprocess.run([sys.executable, "-m", "cogito.ideagen_bridge", "vet-one", "--stdin"],
                             input="not json", capture_output=True, text=True, cwd=ROOT, env=env, timeout=60)
        self.assertEqual(bad.returncode, 1)
        self.assertEqual(bad.stdout, "")


if __name__ == "__main__":
    unittest.main()
