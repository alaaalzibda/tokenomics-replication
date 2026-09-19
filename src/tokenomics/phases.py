"""ChatDev phase -> SDLC stage mapping.

Taken verbatim from Salim, Latendresse, Khatoonabadi and Shihab,
"Tokenomics: Quantifying Where Tokens Are Used in Agentic Software
Engineering", arXiv:2601.14470, Section 2.

The paper is explicit that this mapping is an abstraction and "represents one
of several possible mappings of the agent's activities" (Threats to Validity).
We keep it unchanged so that our numbers are comparable to theirs; any
alternative mapping belongs in a separate sensitivity analysis, not here.
"""

from __future__ import annotations

# SDLC stages, in the order the paper reports them.
STAGES = (
    "Design",
    "Coding",
    "Code Completion",
    "Code Review",
    "Testing",
    "Documentation",
)

# ChatDev internal phase name -> SDLC stage.
PHASE_TO_STAGE = {
    "DemandAnalysis": "Design",
    "LanguageChoose": "Design",
    "Coding": "Coding",
    "CodeComplete": "Code Completion",
    "CodeReview": "Code Review",
    "CodeReviewComment": "Code Review",
    "CodeReviewModification": "Code Review",
    "Test": "Testing",
    "TestErrorSummary": "Testing",
    "TestModification": "Testing",
    "EnvironmentDoc": "Documentation",
    "Reflection": "Documentation",
    "Manual": "Documentation",
}

# The published GPT-5 / ChatDev result we are testing against.
# Stage shares are "share of that task's total tokens, averaged over the tasks
# in which the stage actually ran" -- note n below.
PAPER_STAGE_SHARE = {
    "Code Review": 0.594,
    "Code Completion": 0.268,
    "Documentation": 0.201,
    "Testing": 0.103,
    "Coding": 0.086,
    "Design": 0.024,
}

# Number of the 30 tasks in which each stage was actually triggered.
# The paper flags the small n on Code Completion and Testing as a limitation.
PAPER_STAGE_N = {
    "Design": 30,
    "Coding": 30,
    "Code Completion": 6,
    "Code Review": 30,
    "Testing": 12,
    "Documentation": 30,
}

# Overall per-task token type split reported for GPT-5.
PAPER_TYPE_SHARE = {"input": 0.539, "output": 0.244, "reasoning": 0.216}

# Per-stage input/output/reasoning split reported for GPT-5.
PAPER_STAGE_TYPE_SHARE = {
    "Design":          {"input": 0.604, "output": 0.036, "reasoning": 0.360},
    "Coding":          {"input": 0.069, "output": 0.580, "reasoning": 0.351},
    "Code Completion": {"input": 0.477, "output": 0.417, "reasoning": 0.105},
    "Code Review":     {"input": 0.514, "output": 0.247, "reasoning": 0.239},
    "Testing":         {"input": 0.608, "output": 0.207, "reasoning": 0.184},
    "Documentation":   {"input": 0.802, "output": 0.083, "reasoning": 0.115},
}


class UnknownPhase(KeyError):
    """Raised when a trace contains a ChatDev phase we have no mapping for.

    Deliberately fatal. Silently dropping an unmapped phase would quietly
    change every denominator in the study.
    """


def stage_for(phase: str) -> str:
    try:
        return PHASE_TO_STAGE[phase]
    except KeyError as exc:
        raise UnknownPhase(
            f"No SDLC stage mapped for ChatDev phase {phase!r}. "
            f"Add it to PHASE_TO_STAGE and say so in the write-up."
        ) from exc
