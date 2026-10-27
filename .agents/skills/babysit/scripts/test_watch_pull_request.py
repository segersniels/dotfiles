import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("watch_pull_request.py")
MODULE_SPEC = importlib.util.spec_from_file_location("watch_pull_request", MODULE_PATH)
watch = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(watch)

VIEWER = "me"


def remark(id, author="reviewer", created_at="2026-10-27T10:00:00Z", **extra):
    return {"kind": "issue_comment", "id": id, "author": author, "created_at": created_at, "body": "text", "url": "u", **extra}


def check(name, result="passed"):
    return {"name": name, "result": result, "url": f"https://ci/{name}"}


def pull_request(**overrides):
    pr = {
        "number": 1,
        "url": "https://github.com/o/r/pull/1",
        "base_branch": "main",
        "head_sha": "aaaaaaa1",
        "head_author": VIEWER,
        "merged": False,
        "closed": False,
        "mergeable": True,
        "mergeable_state": "blocked",
        "checks": [check("lint", "pending")],
        "remarks": [remark("1", created_at="2026-10-27T09:00:00Z")],
    }
    pr.update(overrides)
    return pr


def kinds(changes):
    return [change["kind"] for change in changes]


class EvaluateTest(unittest.TestCase):
    def setUp(self):
        self.state = watch.initial_state(pull_request())

    def test_unchanged_pr_reports_nothing(self):
        changes, _ = watch.evaluate(self.state, pull_request(), VIEWER)
        self.assertEqual(changes, [])

    def test_reports_new_comments_from_others_only(self):
        remarks = pull_request()["remarks"] + [remark("2"), remark("3", author="ME")]
        changes, state = watch.evaluate(self.state, pull_request(remarks=remarks), VIEWER)

        self.assertEqual(kinds(changes), ["remarks"])
        self.assertEqual([item["id"] for item in changes[0]["remarks"]], ["2"])

        changes, _ = watch.evaluate(state, pull_request(remarks=remarks), VIEWER)
        self.assertEqual(changes, [])

    def test_tells_apart_comments_in_the_same_second(self):
        first = [remark("1", created_at="2026-10-27T09:00:00Z"), remark("2", created_at="2026-10-27T09:00:00Z")]
        changes, _ = watch.evaluate(self.state, pull_request(remarks=first), VIEWER)

        self.assertEqual([item["id"] for item in changes[0]["remarks"]], ["2"])

    def test_reports_a_failed_check_again_after_a_rerun_fails(self):
        changes, state = watch.evaluate(self.state, pull_request(checks=[check("lint", "failed")]), VIEWER)
        self.assertEqual(kinds(changes), ["checks_failed"])

        changes, state = watch.evaluate(state, pull_request(checks=[check("lint", "failed")]), VIEWER)
        self.assertEqual(changes, [])

        changes, state = watch.evaluate(state, pull_request(checks=[check("lint", "pending")]), VIEWER)
        changes, _ = watch.evaluate(state, pull_request(checks=[check("lint", "failed")]), VIEWER)
        self.assertEqual(kinds(changes), ["checks_failed"])

    def test_reports_passed_checks_once_per_head(self):
        green = [check("lint"), check("test")]
        changes, state = watch.evaluate(self.state, pull_request(checks=green), VIEWER)
        self.assertEqual(changes, [{"kind": "checks_passed", "count": 2}])

        changes, state = watch.evaluate(state, pull_request(checks=green), VIEWER)
        self.assertEqual(changes, [])

        changes, _ = watch.evaluate(state, pull_request(head_sha="bbbbbbb2", checks=green), VIEWER)
        self.assertEqual(kinds(changes), ["checks_passed"])

    def test_reports_pushes_by_others_only(self):
        changes, _ = watch.evaluate(self.state, pull_request(head_sha="bbbbbbb2", checks=[]), VIEWER)
        self.assertEqual(changes, [])

        changes, _ = watch.evaluate(self.state, pull_request(head_sha="bbbbbbb2", head_author="kevin", checks=[]), VIEWER)
        self.assertEqual(changes, [{"kind": "pushed", "author": "kevin"}])

    def test_reports_a_conflict_once_and_keeps_it_while_github_computes(self):
        changes, state = watch.evaluate(self.state, pull_request(mergeable=False), VIEWER)
        self.assertEqual(kinds(changes), ["conflicting"])

        changes, state = watch.evaluate(state, pull_request(mergeable=None), VIEWER)
        self.assertEqual(changes, [])
        self.assertTrue(state["conflicting"])

    def test_reports_ready_to_merge_once(self):
        changes, state = watch.evaluate(self.state, pull_request(mergeable_state="clean"), VIEWER)
        self.assertEqual(kinds(changes), ["ready"])

        changes, _ = watch.evaluate(state, pull_request(mergeable_state="clean"), VIEWER)
        self.assertEqual(changes, [])

    def test_counts_comment_only_updates_in_a_row(self):
        _, state = watch.evaluate(self.state, pull_request(remarks=[remark("2")]), VIEWER)
        self.assertEqual(state["comment_only_updates"], 1)

        _, state = watch.evaluate(state, pull_request(remarks=[remark("3", created_at="2026-10-27T11:00:00Z")]), VIEWER)
        self.assertEqual(state["comment_only_updates"], 2)

        _, state = watch.evaluate(state, pull_request(checks=[check("lint", "failed")]), VIEWER)
        self.assertEqual(state["comment_only_updates"], 0)


class RemarksTest(unittest.TestCase):
    def test_skips_unpublished_and_empty_comment_reviews(self):
        reviews = [
            {"id": 10, "state": "PENDING", "body": "draft", "user": {"login": "a"}},
            {"id": 11, "state": "COMMENTED", "body": "", "user": {"login": "a"}},
            {"id": 12, "state": "APPROVED", "body": "", "user": {"login": "a"}, "submitted_at": "t"},
        ]
        review_comments = [
            {"id": 20, "pull_request_review_id": 10, "user": {"login": "a"}},
            {"id": 21, "pull_request_review_id": 11, "in_reply_to_id": 5, "user": {"login": "a"}},
        ]
        remarks = watch.remarks_from([], review_comments, reviews)

        self.assertEqual([(item["kind"], item["id"]) for item in remarks], [("review_comment", "21"), ("review", "12")])
        self.assertEqual(remarks[0]["thread_id"], "5")


class FormatTest(unittest.TestCase):
    def test_lists_comments_without_html_comments_and_with_reply_target(self):
        item = remark("7", kind="review_comment", thread_id="5", path="a.ts", line=3, body="<!-- bot -->\nFix   this")
        text = watch.format_update(pull_request(), [{"kind": "remarks", "remarks": [item]}])

        self.assertIn('reviewer on a.ts:3: "Fix this" u (review_comment 7, thread 5)', text)

    def test_shows_the_state_of_a_review_without_body(self):
        item = remark("8", kind="review", state="approved", body="")
        text = watch.format_update(pull_request(), [{"kind": "remarks", "remarks": [item]}])

        self.assertIn("reviewer: approved u (review 8)", text)


if __name__ == "__main__":
    unittest.main()
