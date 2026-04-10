import json

from daily import build_diff, is_valid_ip, safe_parse_tags


def test_safe_parse_tags_accepts_json_and_literal():
    assert safe_parse_tags(json.dumps(["mgmt-if", "vpn"])) == ["mgmt-if", "vpn"]
    assert safe_parse_tags("['db', 'backup']") == ["db", "backup"]
    assert safe_parse_tags("not-parseable") == []


def test_build_diff_detects_added_removed_and_changed_fields():
    previous = [
        ("10.0.0.1/24", "old-desc", "old.local", ["mgmt-if"]),
        ("10.0.0.2/24", "stay", "same.local", ["mgmt-if"]),
    ]
    current = [
        ("10.0.0.1/24", "new-desc", "new.local", ["mgmt-if", "vpn"]),
        ("10.0.0.3/24", "added", "added.local", ["mgmt-if"]),
    ]

    diff = build_diff(previous, current)

    assert ["10.0.0.3/24", "added", "added.local", ["mgmt-if"]] in diff["added"]
    assert ["10.0.0.2/24", "stay", "same.local", ["mgmt-if"]] in diff["removed"]
    assert "10.0.0.1/24" in diff["changed"]
    assert diff["changed"]["10.0.0.1/24"]["description"]["old"] == "old-desc"
    assert diff["changed"]["10.0.0.1/24"]["description"]["new"] == "new-desc"


def test_is_valid_ip_accepts_ipv4_and_ipv6_with_prefix():
    assert is_valid_ip("10.0.0.1/24") is True
    assert is_valid_ip("2a01:4f8:222:15a4::2/64") is True


def test_is_valid_ip_rejects_invalid_values():
    assert is_valid_ip(None) is False
    assert is_valid_ip("10.0.0.1") is False
    assert is_valid_ip("not-an-ip") is False
