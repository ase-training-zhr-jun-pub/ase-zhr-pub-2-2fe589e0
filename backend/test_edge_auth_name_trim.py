"""Edge-Case-Test: nutzer_id() trimmt Whitespace im Benutzernamen."""

import base64

from auth import nutzer_id


def test_whitespace_im_benutzernamen_wird_getrimmt():
    """Führender/abschließender Whitespace im Namensteil wird entfernt."""
    header = "Basic " + base64.b64encode(b" demo :").decode()
    assert nutzer_id(header) == "demo"
