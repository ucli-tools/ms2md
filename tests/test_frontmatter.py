"""
Tests for the generate_yaml_frontmatter module.
"""

import unittest
from pathlib import Path

import yaml

from docx2md.processors.frontmatter import generate_yaml_frontmatter


class TestGenerateYamlFrontmatter(unittest.TestCase):

    def _gen(self, doc_props=None, config=None, path=None, content=""):
        return generate_yaml_frontmatter(
            doc_props or {},
            config or {},
            path or Path("test_document.docx"),
            content,
        )

    # ------------------------------------------------------------------
    # Title extraction
    # ------------------------------------------------------------------

    def test_title_from_doc_properties(self):
        fm_str, _ = self._gen(doc_props={"title": "My Title"})
        fm = yaml.safe_load(fm_str.strip("---\n"))
        self.assertEqual(fm["title"], "My Title")

    def test_title_from_body_bold(self):
        content = "**Introduction to Topology**\n\nBody text."
        fm_str, _ = self._gen(content=content)
        fm = yaml.safe_load(fm_str.strip("---\n"))
        self.assertEqual(fm["title"], "Introduction to Topology")

    def test_title_fallback_from_filename(self):
        fm_str, _ = self._gen(path=Path("my_great_document.docx"), content="Body.")
        fm = yaml.safe_load(fm_str.strip("---\n"))
        self.assertIn("My Great Document", fm["title"])

    # ------------------------------------------------------------------
    # Author and email
    # ------------------------------------------------------------------

    def test_author_from_doc_properties(self):
        fm_str, _ = self._gen(doc_props={"author": "Jane Doe"})
        fm = yaml.safe_load(fm_str.strip("---\n"))
        self.assertEqual(fm["author"], "Jane Doe")

    def test_author_from_body_name_email(self):
        content = "**Title**\n\nJane Doe -- <jane@example.com>\n\nBody."
        fm_str, _ = self._gen(content=content)
        fm = yaml.safe_load(fm_str.strip("---\n"))
        self.assertEqual(fm["author"], "Jane Doe")
        self.assertEqual(fm["email"], "jane@example.com")

    # ------------------------------------------------------------------
    # Subtitle
    # ------------------------------------------------------------------

    def test_subtitle_from_doc_properties(self):
        fm_str, _ = self._gen(doc_props={"subject": "A Subtitle"})
        fm = yaml.safe_load(fm_str.strip("---\n"))
        self.assertEqual(fm["subtitle"], "A Subtitle")

    def test_subtitle_from_body_italic(self):
        content = "**Title**\n\n*An Italic Subtitle*\n\nBody."
        fm_str, _ = self._gen(content=content)
        fm = yaml.safe_load(fm_str.strip("---\n"))
        self.assertEqual(fm["subtitle"], "An Italic Subtitle")

    # ------------------------------------------------------------------
    # mdtexpdf defaults present
    # ------------------------------------------------------------------

    def test_mdtexpdf_defaults_present(self):
        fm_str, _ = self._gen(doc_props={"title": "Test"})
        fm = yaml.safe_load(fm_str.strip("---\n"))
        self.assertIn("format", fm)
        self.assertIn("toc", fm)
        self.assertIn("no_numbers", fm)

    # ------------------------------------------------------------------
    # Re-run guard (already has frontmatter)
    # ------------------------------------------------------------------

    def test_no_double_prepend(self):
        content = "---\ntitle: Existing\n---\n\nBody."
        fm_str, returned_content = self._gen(content=content)
        self.assertEqual(fm_str, "")
        self.assertEqual(returned_content, content)

    # ------------------------------------------------------------------
    # Title block stripped from body
    # ------------------------------------------------------------------

    def test_title_block_stripped_from_body(self):
        content = "**My Title**\n\nBody paragraph."
        config = {"yaml_frontmatter": {"strip_body_title_block": True}}
        _, updated = self._gen(
            doc_props={"title": "My Title"},
            config=config,
            content=content,
        )
        self.assertNotIn("**My Title**", updated)
        self.assertIn("Body paragraph.", updated)

    # ------------------------------------------------------------------
    # Disabled generator
    # ------------------------------------------------------------------

    def test_disabled(self):
        config = {"yaml_frontmatter": {"enabled": False}}
        fm_str, content = self._gen(
            doc_props={"title": "T"},
            config=config,
            content="Body.",
        )
        self.assertEqual(fm_str, "")
        self.assertEqual(content, "Body.")


if __name__ == "__main__":
    unittest.main()
