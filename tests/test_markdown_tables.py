import unittest

from app.extractors._markdown_tables import parse_markdown_tables


class MarkdownTableParsingTests(unittest.TestCase):
    def test_parse_markdown_tables_handles_inline_pdf_rows(self) -> None:
        markdown = """## Equipment Schedule

| Tag | Type | Equipment | |---|---|---| | AHU-1 | AHU | Air Handling Unit 1 | | RTU-2 | RTU | Roof Top Unit 2 |
"""

        tables = parse_markdown_tables(markdown)

        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].headers, ["tag", "type", "equipment"])
        self.assertEqual(len(tables[0].rows), 2)
        self.assertEqual(tables[0].rows[0]["tag"], "AHU-1")
        self.assertEqual(tables[0].rows[1]["equipment"], "Roof Top Unit 2")


if __name__ == "__main__":
    unittest.main()
