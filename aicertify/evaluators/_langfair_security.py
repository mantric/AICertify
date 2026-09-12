"""Security gate for the optional LangFair evaluator stack.

LangFair currently depends on NLTK. GitHub advisory GHSA-8mgp-746c-j5xp affects
NLTK through 3.10.3: model-artifact save APIs can bypass the path sandbox and
write outside allowed roots. Upstream has merged the fix, but no patched NLTK
release exists yet.

AICertify does not import NLTK directly. Keep LangFair disabled whenever its
installed NLTK is still in the affected range; the gate automatically permits
a future patched NLTK release without another AICertify code change.
"""

from importlib.metadata import PackageNotFoundError, version

_AFFECTED_NLTK_MAX = (3, 10, 3)


def _release_tuple(value: str) -> tuple[int, ...]:
    """Return the numeric release prefix from a PEP 440-ish version string."""
    parts: list[int] = []
    for part in value.split("."):
        digits = "".join(character for character in part if character.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def require_safe_langfair_stack() -> None:
    """Raise ImportError unless LangFair's NLTK dependency is patched.

    Missing LangFair/NLTK is treated as unavailable by the caller. Installed
    NLTK releases through 3.10.3 are deliberately rejected because no released
    version contains the upstream model-artifact path-security fix yet.
    """
    try:
        nltk_version = version("nltk")
    except PackageNotFoundError as exc:
        raise ImportError("LangFair requires NLTK, which is not installed") from exc

    release = _release_tuple(nltk_version)
    if release and release <= _AFFECTED_NLTK_MAX:
        raise ImportError(
            "LangFair disabled: installed NLTK "
            f"{nltk_version} is affected by GHSA-8mgp-746c-j5xp; "
            "use the first patched NLTK release newer than 3.10.3"
        )
