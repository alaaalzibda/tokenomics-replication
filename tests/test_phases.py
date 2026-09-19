import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from tokenomics.phases import PHASE_TO_STAGE, STAGES, UnknownPhase, stage_for


def test_every_mapping_lands_in_a_known_stage():
    assert set(PHASE_TO_STAGE.values()) <= set(STAGES)


def test_unknown_phase_is_fatal_not_silent():
    with pytest.raises(UnknownPhase):
        stage_for("SomePhaseChatDevAddedLater")


def test_review_phases_group_together():
    assert stage_for("CodeReviewComment") == "Code Review"
    assert stage_for("CodeReviewModification") == "Code Review"
