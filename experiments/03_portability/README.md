# 03 — Portability: what actually survives a move between providers?

## Goal

Alice has a realistic small pod on provider A. She moves to provider B. What
arrives, what breaks, and what silently stops meaning anything?

"Migrate the data" hides the whole question, so this experiment performs the
move **two ways** and compares them:

- **Verbatim** — bytes preserved exactly. Internal links therefore still point
  at provider A, the pod she has just left.
- **Rewritten** — every `localhost:3000/alice/` IRI rewritten to
  `localhost:3001/alice2/`. Links resolve, but her data has been silently
  mutated, and anyone else who linked to the old IRIs now points at stale
  content.

It then asks the question that separates *portability* from *switching*: after
the move, Alice leaves provider A. Do the migrated links still work?

And underneath all of it sits identity. Alice's WebID is
`localhost:3000/alice/profile/card#me` — hosted by the provider she is leaving.
Every ACL that mentions her, every `owl:sameAs`, every link, names an identifier
that belongs to her old provider. So the experiment also tests a variant where
the WebID is **provider-independent** and only `pim:storage` changes.

> **Simulation caveat, stated up front.** Three `localhost` ports (3000, 3001,
> 3002) *simulate* three independent origins. They are not separate providers.
> Real-world DNS, TLS, CORS, contractual and organisational boundaries are out
> of scope, and nothing here should be read as a claim about them.

## Alice's pod (all data synthetic)

~10 resources, two levels of nesting, cross-references, one binary, and one
container carrying its own ACL:

```
thesis-lab/                     <- container WITH ITS OWN .acl
  profile.ttl                   -> links to contacts/ and notes/
  contacts/
    carol.ttl                   (fictional person)
    dave.ttl                    (fictional person)
  notes/
    note-1.ttl                  -> links to contacts/carol.ttl and media/portrait.png
    note-2.ttl                  -> links to note-1.ttl
  media/
    portrait.png                generated binary, depicts nobody
    portrait.ttl                licence metadata for the image
```

The image's licence statement is **part of the test scenario** — it is content
being migrated, and whether it survives is one of the things observed. It is not
a legal statement about this repository.

## Hypotheses (written and committed before the run)

### Moving the data

> **Amendment, recorded before the run.** Check 1 originally predicted a literal
> count of `9`. That was an arithmetic slip about this experiment's own fixture
> (which creates 7 documents plus 4 containers), not a claim about Solid. Rather
> than let a miscount surface as a spurious `UNEXPECTED`, the check was changed
> *before running* to the more meaningful form: does traversal reveal **every
> resource that was actually created**? The amendment is noted here and in the
> commit history rather than made silently.


| # | Check | Expected | Meaning if it holds |
|---|---|---|---|
| 1 | Traversal via `ldp:contains` finds every resource that was created | `True` | Enumeration works — **ENFORCED** |
| 2 | That traversal also reveals the container's `.acl` | `False` | Auxiliary resources are invisible to a naive export — **NOT-SUPPORTED** |
| 3 | Every resource is recreated on provider B | `True` | The bytes move — **ENFORCED** |
| 4 | The binary's content type survives | `image/png` | Media types move — **ENFORCED** |
| 5 | The binary is byte-identical (SHA-256) | `True` | No corruption — **ENFORCED** |
| 6 | The image's licence metadata survives | `True` | Attached metadata moves as data — **ENFORCED** |

### Links and meaning

| # | Check | Expected | Meaning if it holds |
|---|---|---|---|
| 7 | After **verbatim** copy, internal links still name provider **A** | `True` | Data moved, meaning did not — **NOT-SUPPORTED** |
| 8 | Rewriting links requires a bespoke client-side step | `True` | No protocol mechanism does this — **NOT-SUPPORTED** |
| 9 | After **rewriting**, internal links resolve on provider B | `200` | Rewriting works, but we wrote it — **ENFORCED** |

### Access control

| # | Check | Expected | Meaning if it holds |
|---|---|---|---|
| 10 | The custom container ACL is carried over by the migration | `False` | ACLs do not travel with data — **NOT-SUPPORTED** |
| 11 | The ACL can be explicitly written on provider B | `True` | It is at least expressible there — **ENFORCED** |
| 12 | Bob, whose WebID is hosted by provider **A**, reads the migrated resource on provider **B** using his provider-A credentials | `200` | Solid-OIDC is genuinely cross-provider — **ENFORCED** |

### The consent policy

| # | Check | Expected | Meaning if it holds |
|---|---|---|---|
| 13 | The ODRL policy can be re-attached on provider B | `True` | It moves as bytes — **ENFORCED** |
| 14 | It is still inert on provider B | `200` under a Prohibition | Inertness is a property of the stack, not the server instance — **DECLARED-ONLY** |

### Identity

| # | Check | Expected | Meaning if it holds |
|---|---|---|---|
| 15 | `owl:sameAs` linking the new WebID to the old one is accepted as data | `True` | It can be *said* — **ENFORCED** |
| 16 | An ACL naming Alice's **old** WebID grants access to her **new** identity | `403` | Nothing honours `owl:sameAs` — **NOT-SUPPORTED** |
| 17 | A redirect or tombstone can be left at the old WebID | `False` | No mechanism to forward an identity — **NOT-SUPPORTED** |
| 18 | A provider-independent WebID on a third origin can be linked to the account | `True` | Possible, after an ownership proof — **ENFORCED** |
| 19 | That independent identity can access provider B | `200` | Identity and storage can be decoupled — **ENFORCED** |
| 20 | Switching storage means changing only `pim:storage`; the WebID is unchanged | `True` | The identifier survives the move — **ENFORCED** |

### Leaving provider A (switching, not copying)

| # | Check | Expected | Meaning if it holds |
|---|---|---|---|
| 21 | After Alice's data is deleted from A, **verbatim**-migrated links resolve | `404` | Verbatim portability depends on the provider she left continuing to serve — **NOT-SUPPORTED** |
| 22 | The **rewritten** copy's links still resolve | `200` | Rewriting survives departure — **ENFORCED** |
| 23 | With provider A **stopped**, Bob can still authenticate to provider B | `False` | An identity hosted by a provider dies with it — **NOT-SUPPORTED** |
| 24 | With provider A stopped, the **independent-WebID** identity still authenticates to provider B | `200` | An independent identifier survives — **ENFORCED** |

Checks 23 and 24 are the comparison the whole experiment is built around: the
same operation, once with a provider-hosted identity and once with an
independent one.

## Bears on (open questions, not conclusions)

- **GDPR Art. 20** — the right to receive personal data in a structured, commonly
  used, machine-readable format and to transmit it "without hindrance". Observed:
  the bytes move and are machine-readable; internal references, access rules and
  identity do not move with them.
- **GDPR Art. 17** — erasure, once the data is also held elsewhere.
- **EU Data Act, Chapter VI** — switching between data processing services.
  Observed facts bear on what "switching" requires beyond copying bytes.
  Regulation (EU) 2023/2854, OJ L, 2023/2854, 22.12.2023 —
  https://eur-lex.europa.eu/eli/reg/2023/2854/oj
- **DMA Art. 6(9)** — effective portability of data provided by the end user.
  Regulation (EU) 2022/1925, OJ L 265, 12.10.2022, p. 1 —
  https://eur-lex.europa.eu/eli/reg/2022/1925/oj
- **GDPR** — Regulation (EU) 2016/679, OJ L 119, 4.5.2016, p. 1 —
  https://eur-lex.europa.eu/eli/reg/2016/679/oj

All quoted phrases above are to be verified against the Official Journal text.

## Spec references

- **Solid Protocol** §4.2 Resource Containment (`ldp:contains`), §4.3 Auxiliary
  Resources, §4.3.2 Description Resource —
  https://solidproject.org/TR/protocol (v0.11.0, 2024-05-12)
- **WAC** §4.3 Access Subjects, §5.1 Effective ACL Resource —
  https://solidproject.org/TR/wac (v1.0.0, 2024-05-12)
- **Solid-OIDC** §8, §9.3 — https://solidproject.org/TR/oidc
- `pim:storage` — http://www.w3.org/ns/pim/space#storage

## Result

_Not yet run._
