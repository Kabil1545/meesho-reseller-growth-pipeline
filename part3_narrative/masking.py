"""Part 3.4 - Masking policy: external-facing text must never expose a raw reseller name."""


def alias_for(reseller_id: str) -> str:
    """RS019 -> ALIAS-19, RS006 -> ALIAS-06."""
    return f"ALIAS-{reseller_id[3:]}"


def assert_no_raw_names_leak(text: str, reseller_names: "list[str]") -> bool:
    """True if no raw reseller_name appears verbatim in text; False on any leak."""
    return not any(name and name in text for name in reseller_names)
