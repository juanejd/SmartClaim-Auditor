"""Unit tests for the pure _verify_citation function in audit/graph.py.

No mocks needed — _verify_citation is a pure function with no I/O, LLM calls,
or side effects. These tests document and enforce verbatim substring semantics.
"""

from app.audit.graph import _verify_citation


def test_citation_present_returns_true():
    """A citation that is a verbatim substring of a chunk returns True."""
    chunks = ["warranty covers manufacturing defects", "returned within 30 days"]
    assert _verify_citation("warranty covers manufacturing defects", chunks) is True


def test_citation_absent_returns_false():
    """A citation not present in any chunk returns False."""
    chunks = ["warranty covers manufacturing defects", "returned within 30 days"]
    assert _verify_citation("fire damage is excluded from coverage", chunks) is False


def test_empty_citation_returns_false():
    """An empty string citation returns False regardless of chunks."""
    chunks = ["some chunk with text", "another chunk"]
    assert _verify_citation("", chunks) is False


def test_citation_in_second_chunk():
    """A citation only in the second chunk still returns True."""
    chunks = ["first chunk with unrelated text", "the claimant filed on March 3"]
    assert _verify_citation("the claimant filed on March 3", chunks) is True


def test_empty_chunks_returns_false():
    """An empty chunks list always returns False, even for a non-empty citation."""
    assert _verify_citation("any citation text", []) is False


def test_citation_verbatim_matches_raw_chunk_text():
    """Citation taken verbatim from a chunk matches without any index prefix.

    Regression for RNF-02: _join() previously prepended '[N] ' to each chunk,
    so an LLM citation like 'compressor failures covered' was present in the
    prompt as '[1] compressor failures covered' but checked against the raw
    chunk — causing a spurious INSPECTION_REQUIRED downgrade.

    After the fix, _join() emits raw text; a verbatim substring of the original
    chunk must pass. A string containing the old numbered prefix form would NOT
    be a substring of the raw chunk and must fail.
    """
    chunk = "compressor failures covered for 12 months from purchase date"
    chunks = [chunk]

    # Verbatim substring of the raw chunk: must pass
    assert _verify_citation("compressor failures covered for 12 months", chunks) is True

    # Old numbered-prefix form: must fail (it is not in the raw chunk)
    assert _verify_citation("[1] compressor failures covered", chunks) is False
