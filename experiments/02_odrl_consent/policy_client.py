"""A policy-aware Solid client that enforces ODRL on itself.

The Community Solid Server does not read ODRL policies. This module shows what
"enforcement" would have to look like without server support: the *client*
fetches the policy attached to a resource, evaluates it, and declines to make
the request when a rule forbids it.

The point is not that this works -- it obviously does, it is forty lines of
rdflib. The point is what it implies:

* Compliance becomes **voluntary**. This client refuses; `curl` does not.
* The policy is evaluated by the party it constrains, which is precisely the
  party with an incentive to ignore it.
* Nothing about the protocol distinguishes a compliant client from a
  non-compliant one, so the data subject cannot tell which kind read her data.

Evaluation is deliberately simple-minded (ODRL 2.2 conflict resolution,
inheritance and duties are not implemented). A fuller evaluator exists --
`odrl-evaluator` by SolidLab, see RELATED_WORK.md -- and using it would not
change the finding, because the gap is not evaluator quality but the absence of
any server-side evaluation at all.
"""

from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph, Namespace, URIRef

ODRL = Namespace("http://www.w3.org/ns/odrl/2/")


@dataclass
class Decision:
    allowed: bool
    reason: str


def evaluate_read(
    policy_turtle: str,
    base: str,
    assignee: str,
    target: str,
    purpose: str | None = None,
) -> Decision:
    """Decide whether *this client* should perform a read, per the policy.

    Returns ``allowed=False`` when a Prohibition covers the read, or when a
    Permission's purpose constraint is not satisfied by the declared purpose.
    Absent any policy, the client does not invent restrictions -- it allows.
    """
    graph = Graph()
    try:
        graph.parse(data=policy_turtle, format="turtle", publicID=base)
    except Exception as exc:  # malformed policy must not silently allow
        return Decision(False, f"policy could not be parsed, refusing: {exc}")

    target_ref = URIRef(target)

    # 1. Prohibitions win outright in this simplified evaluator.
    for rule in graph.objects(None, ODRL.prohibition):
        if (rule, ODRL.target, target_ref) not in graph:
            continue
        for action in graph.objects(rule, ODRL.action):
            if action in (ODRL.read, ODRL.use, ODRL.distribute):
                return Decision(
                    False, f"prohibited: odrl:Prohibition on {action.split('/')[-1]}"
                )

    # 2. Otherwise a Permission must cover the read, and its purpose constraint
    #    (if any) must be satisfied by the purpose the client declares.
    for rule in graph.objects(None, ODRL.permission):
        if (rule, ODRL.target, target_ref) not in graph:
            continue
        if not any(a in (ODRL.read, ODRL.use) for a in graph.objects(rule, ODRL.action)):
            continue
        for constraint in graph.objects(rule, ODRL.constraint):
            if (constraint, ODRL.leftOperand, ODRL.purpose) not in graph:
                continue
            required = {str(o) for o in graph.objects(constraint, ODRL.rightOperand)}
            if purpose is None:
                return Decision(
                    False,
                    f"permission requires a purpose ({', '.join(sorted(required))}) "
                    "and none was declared",
                )
            if purpose not in required:
                return Decision(
                    False,
                    f"declared purpose {purpose} does not satisfy the constraint "
                    f"({', '.join(sorted(required))})",
                )
        return Decision(True, "permitted by odrl:Permission, purpose constraint satisfied")

    if len(graph) == 0:
        return Decision(True, "no policy attached; client does not invent restrictions")
    return Decision(False, "no odrl:Permission covers this read")
