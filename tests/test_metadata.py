"""Tests for content metadata accessor API."""

import pytest

from pylatro.content.metadata import (
    MetadataNotFoundError,
    get_joker_display_name,
    get_joker_effect,
    get_joker_unlock_requirement,
)


def test_get_joker_metadata_for_known_joker():
    display_name = get_joker_display_name("joker")
    effect = get_joker_effect("joker")
    unlock_requirement = get_joker_unlock_requirement("joker")

    assert display_name
    assert effect
    assert unlock_requirement


def test_get_joker_metadata_raises_clean_error_for_unknown_joker():
    with pytest.raises(MetadataNotFoundError) as exc:
        get_joker_display_name("not_a_real_joker")

    assert "Unknown joker 'not_a_real_joker'" in str(exc.value)
