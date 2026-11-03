"""What the learner sees: feedback first, then one coarse band per dimension, no aggregate and
no numbers (design doc §12). Shared by the CLI and the Phase 6 review sheet."""

from eval_engine.schemas.trace import EvaluationTrace


def learner_view(trace: EvaluationTrace) -> list[str]:
    lines: list[str] = []
    items = trace.feedback.items if trace.feedback else []
    for item in items:
        if item.kind in ("approach", "divergence", "off_topic"):
            lines += [item.text, ""]
    improve = [i for i in items if i.kind == "improve"]
    if improve:
        lines.append("To work on:")
        lines += [f"  {n}. {i.text}" for n, i in enumerate(improve, start=1)]
        lines.append("")
    for item in items:
        if item.kind == "originality":
            lines += [item.text, ""]
    worked = [i for i in items if i.kind == "worked"]
    if worked:
        lines.append("What worked:")
        lines += [f"  - {i.text}" for i in worked]
        lines.append("")
    lines.append("Bands:")
    lines += [f"  {d.value:<13} {band}" for d, band in trace.bands.items()]
    return lines
