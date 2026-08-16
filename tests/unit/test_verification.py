from __future__ import annotations

import unittest

from grox.contracts import Evidence, TourResult
from grox.verification.core import IndependentVerifier


class IndependentVerifierTests(unittest.TestCase):
    def test_same_executor_cannot_verify_own_result(self) -> None:
        verifier = IndependentVerifier()
        result = TourResult(
            "ORD-self",
            "code-reviewer",
            "completed",
            "self-verification attempt",
            [Evidence("finding", {"claim": "evidence exists"})],
        )

        ok, message = verifier.verify("code-reviewer", "code-reviewer", result)

        self.assertFalse(ok)
        self.assertIn("not independent", message)


if __name__ == "__main__":
    unittest.main()
