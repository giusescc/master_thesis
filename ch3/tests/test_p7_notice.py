"""P7 notice versions: v1 is unchanged, v2 adds only the DPV consent status (no servers needed)."""

from types import SimpleNamespace

ALICE = SimpleNamespace(web_id="http://localhost:3100/alice/profile/card#me")
BOB = SimpleNamespace(web_id="http://localhost:3100/bob/profile/card#me")
TARGET = "http://localhost:3100/alice/ch3/x/person.ttl"


def test_variant_selects_notice_version():
    from ch3.phases.p7_withdrawal.run import notice_version

    assert [notice_version(v) for v in ("cooperating", "non-cooperating")] == [1, 1]
    assert [notice_version(v) for v in ("cooperating-consent", "non-cooperating-consent")] == [2, 2]


def test_v1_has_no_consent_status_and_v2_adds_only_that():
    from ch3.phases.p7_withdrawal.run import has_consent_withdrawn, notice

    v1, v2 = notice(ALICE, BOB, TARGET, 1), notice(ALICE, BOB, TARGET, 2)
    assert not has_consent_withdrawn(v1)
    assert has_consent_withdrawn(v2)
    assert set(v2) - set(v1) == {"ch3n:withdrawnConsent"}
    for key in set(v1) - {"@id", "ch3n:withdrawnAt"}:
        assert v1[key] == v2[key]
