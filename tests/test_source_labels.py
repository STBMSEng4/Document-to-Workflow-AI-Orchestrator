import unittest

from app.extractors.workflow_extractor import extract_workflow_items
from app.scoring.confidence_scorer import ScoredTerm


class SourceLabelTests(unittest.TestCase):
    def test_workflow_template_points_are_labeled_template_default(self) -> None:
        scored = ScoredTerm(
            term="rtu",
            normalized_term="RTU",
            category="equipment_type",
            confidence=0.92,
            status="Confirmed",
            source_confirmed=True,
        )

        output = extract_workflow_items("RTU controls narrative", scored_terms=[scored], template_decisions=[])

        self.assertGreater(len(output["points"]), 0)
        self.assertTrue(all(point["source_type"] == "template_default" for point in output["points"]))


if __name__ == "__main__":
    unittest.main()
