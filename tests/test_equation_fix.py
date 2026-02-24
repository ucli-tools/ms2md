"""
Tests for the EquationFixProcessor module.
"""

import unittest

from docx2md.processors.equation_fix import EquationFixProcessor


class TestEquationFixProcessor(unittest.TestCase):

    def _proc(self, config=None):
        return EquationFixProcessor(config)

    # ------------------------------------------------------------------
    # Pattern 1: garbled \sum_{}^{}var = val^{n}
    # ------------------------------------------------------------------

    def test_p1_sum_garbled_bounds(self):
        content = r"$$\sum_{}^{}i = 1^{n} x_i$$"
        result = self._proc().process(content)
        self.assertIn(r"\sum_{i=1}^{n}", result)
        self.assertNotIn(r"\sum_{}^{}", result)

    def test_p1_spaces_stripped(self):
        content = r"$$\sum_{}^{}k = 0^{N}$$"
        result = self._proc().process(content)
        self.assertIn(r"\sum_{k=0}^{N}", result)

    # ------------------------------------------------------------------
    # Pattern 2: word subscript with empty superscript
    # ------------------------------------------------------------------

    def test_p2_word_subscript(self):
        content = r"$$\sum_{row}^{} E_{ij}$$"
        result = self._proc().process(content)
        self.assertIn(r"\sum_{\text{row}}", result)
        self.assertNotIn(r"^{}", result)

    def test_p2_prod_word_subscript(self):
        content = r"$$\prod_{col}^{} f(x)$$"
        result = self._proc().process(content)
        self.assertIn(r"\prod_{\text{col}}", result)

    # ------------------------------------------------------------------
    # Pattern 3: trailing empty superscript removal
    # ------------------------------------------------------------------

    def test_p3_empty_superscript_removed(self):
        content = r"$$\sum_{n}^{}$$"
        result = self._proc().process(content)
        self.assertNotIn(r"^{}", result)
        self.assertIn(r"\sum_{n}", result)

    # ------------------------------------------------------------------
    # Pattern 4: \hslash → \hbar
    # ------------------------------------------------------------------

    def test_p4_hslash_replaced(self):
        content = r"The reduced Planck constant $\hslash$ is..."
        result = self._proc().process(content)
        self.assertIn(r"\hbar", result)
        self.assertNotIn(r"\hslash", result)

    # ------------------------------------------------------------------
    # Pattern 5: lowercase \mathbb → \mathbf
    # ------------------------------------------------------------------

    def test_p5_lowercase_mathbb(self):
        content = r"The vector $\mathbb{c}$ is..."
        result = self._proc().process(content)
        self.assertIn(r"\mathbf{c}", result)
        self.assertNotIn(r"\mathbb{c}", result)

    def test_p5_uppercase_mathbb_untouched(self):
        """Uppercase \mathbb{R} should remain unchanged."""
        content = r"The reals $\mathbb{R}$ are..."
        result = self._proc().process(content)
        self.assertIn(r"\mathbb{R}", result)

    # ------------------------------------------------------------------
    # Only applied inside math delimiters
    # ------------------------------------------------------------------

    def test_fixes_only_in_math(self):
        """\\hslash in plain text should NOT be changed (not inside $)."""
        content = r"Plain text \hslash mention."
        result = self._proc().process(content)
        self.assertIn(r"\hslash", result)

    # ------------------------------------------------------------------
    # Disabled processor
    # ------------------------------------------------------------------

    def test_disabled(self):
        config = {"equation_fix": {"enabled": False}}
        content = r"$$\sum_{}^{}i = 1^{n}$$"
        result = self._proc(config).process(content)
        self.assertEqual(result, content)


if __name__ == "__main__":
    unittest.main()
