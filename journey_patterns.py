"""You can't automate what you haven't standardised.

Ten common CRM journey patterns, each defined as required steps in order plus guards every
version must have. The checker scores how far a market's journey conforms, and lists the
gaps, so checks and agents can treat every market the same way. Standard library only.
"""
import json
import sys

GUARDS_ALL = ["exit_on_unsubscribe", "consent_check"]

PATTERNS = {
    "welcome": ["trigger:signup", "email", "wait", "email", "preference_center"],
    "reactivation": ["segment:inactive_90d", "email", "wait", "email", "suppress_if_no_open"],
    "abandoned_cart": ["trigger:cart_abandoned", "wait", "email", "exit_on_purchase"],
    "post_purchase": ["trigger:order", "email", "wait", "email:review_request"],
    "birthday": ["trigger:birthday", "email", "offer_expiry"],
    "win_back": ["segment:lapsed_customer", "email:offer", "wait", "email", "suppress_if_no_open"],
    "transactional": ["trigger:event", "email"],
    "newsletter": ["segment:newsletter_optin", "email", "frequency_cap"],
    "product_launch": ["segment:interest", "email:teaser", "wait", "email:launch", "frequency_cap"],
    "preference_update": ["trigger:preference_change", "email:confirmation"],
}
NO_CONSENT_NEEDED = {"transactional"}


def in_order(required, steps):
    """How many required steps appear in order (greedy subsequence match)."""
    i = matched = 0
    missing = []
    for r in required:
        j = i
        while j < len(steps) and steps[j] != r and not steps[j].startswith(r + ":"):
            j += 1
        if j < len(steps):
            matched += 1
            i = j + 1
        else:
            missing.append(r)
    return matched, missing


def check(journey):
    pattern = journey["pattern"]
    required = PATTERNS[pattern]
    matched, missing = in_order(required, journey["steps"])
    guards = [g for g in GUARDS_ALL if not (g == "consent_check" and pattern in NO_CONSENT_NEEDED)]
    missing_guards = [g for g in guards if g not in journey.get("guards", [])]
    total = len(required) + len(guards)
    score = round(100 * (matched + len(guards) - len(missing_guards)) / total)
    return {"journey": journey["name"], "pattern": pattern, "score": score,
            "missing_steps": missing, "missing_guards": missing_guards}


def main(path):
    with open(path, encoding="utf-8") as fh:
        journeys = json.load(fh)
    for j in journeys:
        r = check(j)
        gaps = r["missing_steps"] + [f"guard:{g}" for g in r["missing_guards"]]
        print(f"{r['score']:>3}%  {r['journey']:<28} {r['pattern']:<14} " + (", ".join(gaps) or "conforms"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "examples/welcome_journeys.json")
