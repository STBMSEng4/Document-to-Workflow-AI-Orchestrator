import unittest

from app.scoring.confidence_scorer import score_term


class ConfidenceScorerTests(unittest.TestCase):
    def test_short_term_does_not_match_inside_ocr_garbage(self) -> None:
        text = "7 Tora sure fav overtone | x | 8 [cRacscHanceruters] |_ Miamittegratin"

        result = score_term(
            term="crac",
            normalized_term="crac",
            category="equipment_type",
            aliases=[],
            source_text=text,
        )

        self.assertEqual(result.confidence, 0.00)
        self.assertEqual(result.status, "Not Detected")
        self.assertFalse(result.source_confirmed)

    def test_exact_whole_word_match_still_scores(self) -> None:
        text = "The CRAC unit shall report alarms to the BAS."

        result = score_term(
            term="crac",
            normalized_term="crac",
            category="equipment_type",
            aliases=[],
            source_text=text,
        )

        self.assertGreater(result.confidence, 0.0)
        self.assertTrue(result.source_confirmed)


if __name__ == "__main__":
    unittest.main()
