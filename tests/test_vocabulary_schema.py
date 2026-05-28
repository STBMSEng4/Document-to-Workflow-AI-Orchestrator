import tempfile
import unittest
from pathlib import Path

from app.normalizers.term_normalizer import parse_kb_file
from app.schemas import VocabularyTerm


class VocabularySchemaTests(unittest.TestCase):
    def test_vocabulary_term_normalizes_aliases_and_defaults(self) -> None:
        term = VocabularyTerm(
            term="RTU",
            category="equipment_type",
            weight=1.0,
            aliases=" rooftop unit, RTU, rooftop unit ",
        )

        self.assertEqual(term.normalized_term, "RTU")
        self.assertEqual(term.aliases, ["rooftop unit", "RTU"])
        self.assertEqual(term.scope, "all")
        self.assertFalse(term.is_skip)

    def test_parse_kb_file_returns_validated_dicts(self) -> None:
        kb_text = """## equipment_type
| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| ahu | 1.00 | all | air handler, AHU | Main air handler |

## skip_term
| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| typ | 0.50 | all | typical | drawing shorthand |
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "kb.md"
            path.write_text(kb_text, encoding="utf-8")

            terms = parse_kb_file(path)

        self.assertEqual(len(terms), 2)
        self.assertEqual(terms[0]["category"], "equipment_type")
        self.assertEqual(terms[0]["aliases"], ["air handler", "AHU"])
        self.assertFalse(terms[0]["is_skip"])
        self.assertTrue(terms[1]["is_skip"])

    def test_parse_kb_file_ignores_term_type_index_section(self) -> None:
        kb_text = """## Term Type Index
| Term Type | Count | Purpose |
|---|---:|---|
| equipment_type | 66 | HVAC equipment |

## equipment_type
| Term | Weight | Scope | Variants | Notes |
|---|---:|---|---|---|
| rtu | 1.00 | all | rooftop unit, RTU | Rooftop unit |
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "kb.md"
            path.write_text(kb_text, encoding="utf-8")

            terms = parse_kb_file(path)

        self.assertEqual(len(terms), 1)
        self.assertEqual(terms[0]["term"], "rtu")
        self.assertEqual(terms[0]["category"], "equipment_type")


if __name__ == "__main__":
    unittest.main()
