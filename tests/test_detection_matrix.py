import unittest

from app.scoring.confidence_scorer import EvidenceRecord, ScoredTerm
from app.scoring.detection_matrix import build_markdown_matrix


class DetectionMatrixTests(unittest.TestCase):
    def test_markdown_matrix_sanitizes_newlines_and_pipes_in_evidence(self) -> None:
        scored_terms = [
            ScoredTerm(
                term="ahu",
                normalized_term="ahu",
                category="equipment_type",
                confidence=0.72,
                status="Medium Confidence",
                source_confirmed=True,
                evidence=[
                    EvidenceRecord(
                        excerpt="Line one\nLine two | with pipe\nLine three",
                        match_type="exact",
                    )
                ],
            )
        ]

        markdown = build_markdown_matrix(scored_terms)

        self.assertIn("Line one Line two \\| with pipe Line three", markdown)
        self.assertNotIn("Line one\nLine two", markdown)


if __name__ == "__main__":
    unittest.main()
