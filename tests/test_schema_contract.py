# tests/test_schema_contract.py
from backend.schema import Recap, EnrichedSnippet


def test_recap_schema_validates():
    final_snippet = EnrichedSnippet(
        version=1,
        snippet_id="snippet_1",
        content="print('hello world')",
        diff_summary="Initial version",
        validation={"status": "valid"},
    )

    recap = Recap(
        final=final_snippet,
        rejected_versions=[
            EnrichedSnippet(
                version=2,
                snippet_id="snippet_2",
                content="print('oops')",
                diff_summary="Removed bad print",
                validation={"status": "invalid"},
            )
        ],
        summary="Recap summary text",
        aha_moments=["AST validation added"],
        quality_flags=["guardrails:pass"],
    )

    dumped = recap.model_dump()
    assert dumped["summary"] == "Recap summary text"
    assert dumped["final"]["content"] == "print('hello world')"
    assert dumped["rejected_versions"][0]["validation"]["status"] == "invalid"
