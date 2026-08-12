"""
test_referential_checks.py
Unit tests for the referential integrity check logic (Phase 2).
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "validation"))

from referential_checks import check_referential_integrity


def test_referential_integrity_all_pass():
    """
    On the actual project database, every referential check should
    report zero orphan rows — this test guards against a future
    regeneration or code change silently breaking a foreign key
    relationship.
    """
    results = check_referential_integrity(verbose=False)
    for check_name, orphan_count in results.items():
        assert orphan_count == 0, f"{check_name} has {orphan_count} orphan rows"