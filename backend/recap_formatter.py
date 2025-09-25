from backend.schema import Recap


def format_recap(data: Recap) -> dict:
    """Return dual output: human-readable string and raw JSON dict."""
    human = []
    human.append(f"Session ID: {data.session_id}")

    if data.final and data.final.content:
        human.append("✅ Final snippet selected")
    else:
        human.append("⚠️ No final snippet found")

    if data.rejected:
        human.append(f"❌ {len(data.rejected)} rejected versions")

    if data.aha_moments:
        human.append(f"Aha moments: {', '.join(data.aha_moments)}")

    if data.quality_flags:
        human.append(f"Flags: {', '.join(data.quality_flags)}")

    human.append(f"Summary: {data.text_summary}")

    return {"human_readable": "\n".join(human), "raw_json": data.model_dump()}
