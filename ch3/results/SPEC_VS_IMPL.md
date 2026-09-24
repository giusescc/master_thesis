# SPEC vs IMPLEMENTATION (Chapter 3)

For every observed behaviour: whether the relevant specification **requires**,
**forbids** or is **silent** on it, with the section URL and a verbatim quote
fetched at write time. Where CSS behaviour is inferred from source code, the
row cites the file path at the CSS v7.2.0 tag and its commit hash. Deviations
between spec and CSS 7.2.0 are flagged **DEVIATION**.

CSS source citations refer to **CommunitySolidServer tag `v7.2.0`, commit
`b4fe28370bc297308fdf9329b6eb7901dde5395f`** (lightweight tag). All spec text was
fetched on 2026-09-24. The full set of quotes, with retrieval notes, is in
[`../docs/spec_quotes.md`](../docs/spec_quotes.md). Spec versions: Solid
Protocol 0.11 (2024-05-12), WAC (2024-05-12), ACP 0.9.0 (2022-05-18).

Legend: **Spec position** = requires / forbids / silent. **Verdict** =
*consistent*, **DEVIATION**, or **POSSIBLE DEVIATION** (depends on how a
sentence is read; the reading is stated).

## P1: direct path

### P1-1. A read after the revoke is denied at once (WAC and ACP)
- **Observed:** CSS 7.2.0 with WAC and with ACP answered 403 to the first GET
  appR sent after alice's revoke response had arrived, in 20/20 runs
  (OBSERVATIONS § P1).
- **Spec (WAC §5.3.1),** https://solidproject.org/TR/wac#server-read-operation:
  > When an operation requests to read a resource, the server MUST match an Authorization allowing the acl:Read access privilege on the resource.
- **Spec (ACP §6.1),** https://solidproject.org/TR/acp#resolved-access-control:
  > An ACP engine MUST grant exactly those Access Modes allowed by Effective Policies.
- **Spec position on *timing*:** **silent.** The Solid Protocol, WAC and ACP
  have no sentence on when a change to an ACL/ACR takes effect or on caching
  authorization decisions (searched: "cach", "immediate", "take effect",
  "stale"; `docs/spec_quotes.md` §1b, §2d, §3c).
- **CSS source:** `src/authorization/WebAclReader.ts` L67–72, L195, and
  `src/authorization/AcpReader.ts` L56, L149 read the access document on every
  request. The only caches (`src/util/handlers/CachedHandler.ts` L10,
  `config/ldp/authorization/readers/default.json` L8–11) are WeakMaps keyed on
  per-request objects.
- **Verdict:** consistent. The spec requires the match. Immediacy is CSS's
  implementation choice, not a spec requirement.

### P1-2. The status for an authenticated agent without Read is 403
- **Observed:** 403 with body `{"name":"ForbiddenHttpError",…}` on both configs.
- **Spec (Solid Protocol §2.2),** https://solidproject.org/TR/protocol#client-authentication-different-credentials:
  > When a client receives a response with a 403 or 404 status code, the client MAY repeat the request with different credentials.
- **Spec (Solid Protocol §2.1),** https://solidproject.org/TR/protocol#server-unauthenticated
  (the unauthenticated case, for contrast):
  > When a client does not provide valid credentials when requesting a resource that requires it (see WebID), servers MUST send a response with a 401 status code (unless 404 is preferred for security reasons).
- **Spec position:** **silent** on choosing 403 vs 404 for an *authenticated*
  agent without permission. 403 is among the codes the Protocol names.
- **Verdict:** consistent.

### P1-3. `WAC-Allow` on 200 responses under WAC
- **Observed:** CSS 7.2.0 with WAC sent `WAC-Allow: user="read"` on appR's and
  bob's 200 responses.
- **Spec (WAC §5.3.4),** https://solidproject.org/TR/wac#server-wac-allow:
  > Servers MUST advertise client’s access privileges on a resource by including the WAC-Allow HTTP header (WAC-Allow) in the response of HTTP GET and HEAD requests.
- **Spec position:** requires. **Verdict:** consistent.

### P1-4. No `WAC-Allow` on 403 responses under WAC
- **Observed:** CSS 7.2.0 with WAC sent no `WAC-Allow` header on appR's 403
  responses after the revoke (all 10 WAC runs, ≈201 responses each).
- **Spec (WAC §5.3.4):** the same sentence as P1-3. It says "the response of
  HTTP GET and HEAD requests" and does not limit this to successful responses.
- **Spec position:** requires, *if* the sentence covers error responses.
- **CSS source:** `src/server/WacAllowHttpHandler.ts` L65–93 adds the header
  metadata inside the operation handler chain. It was not reached for the
  403 responses observed here. (Inferred from the observation plus the handler's
  position in `config/ldp/handler/default.json` L27; not traced line by line.)
- **Verdict:** **POSSIBLE DEVIATION.** On a literal reading (every GET/HEAD
  response), the header is missing. On a reading limited to responses that
  return the resource, it is consistent. The spec text does not settle this.

### P1-5. No `WAC-Allow` at all under ACP
- **Observed:** CSS 7.2.0 with ACP sent no `WAC-Allow` header on any response.
- **Spec (ACP §7.2),** https://solidproject.org/TR/acp#conforming-acp-server
  (the only advertisement requirement in ACP, which concerns *supported* modes
  on OPTIONS to an ACR, not the requester's grants):
  > When responding to OPTIONS requests targetting an ACR, conforming ACP servers MUST include a Link header for each supported Access Mode with the rel value of http://www.w3.org/ns/solid/acp#grant and the full IRI of the supported Access Mode as the link target.
- **Spec position:** ACP is **silent** on advertising the requester's
  permissions ("WAC-Allow" does not occur in ACP 0.9.0). The WAC requirement
  (P1-3) applies to WAC servers.
- **CSS source:** the writer is registered only in
  `config/ldp/authorization/acl/wac-allow.json`, imported only by
  `config/ldp/authorization/webacl.json`. `acp.json` does not import it.
- **Verdict:** consistent. It follows that under ACP a client has no header
  from which to learn its own permissions (see OBSERVATIONS § P1).

### P1-6. The ACL/ACR link is advertised on the resource
- **Observed:** alice discovered the `.acl` (WAC) and `.acr` (ACP) through
  `Link: <…>; rel="acl"` in every run (`ch3/lib/access.py`; `grant` and
  `revoke_done` lines log `doc_url`).
- **Spec (WAC §3.1),** https://solidproject.org/TR/wac#server-link-acl:
  > When a server wants to enable applications to discover Authorizations associated with a given resource, the server MUST advertise the ACL resource that is associated with a resource by responding to an HTTP request including a Link header with the rel value of acl (acl Link Relation) and the ACL resource as link target [RFC8288].
- **Spec (ACP §7.1),** https://solidproject.org/TR/acp#conforming-resource-server:
  > When responding to requests targetting access controlled resources, conforming resource servers MUST include a Link header with the rel value of acl and controlled resources' ACRs as the link target RFC 8288.
- **Spec position:** requires. **Verdict:** consistent.

## P2: HTTP caching

### P2-1. No `Cache-Control` / `Expires` on LDP resources; `Vary: Accept,Authorization,Origin`
- **Observed:** CSS 7.2.0 with WAC and with ACP sent no `Cache-Control` and
  no `Expires` on `person.ttl` (40/40 runs). It did send
  `Vary: Accept,Authorization,Origin`, `ETag` and `Last-Modified`.
- **Spec (Solid Protocol §2.1),** https://solidproject.org/TR/protocol#server-caching:
  > Servers SHOULD conform to HTTP Caching [RFC9111].
- **Spec (RFC 9111 §4.2.2),** https://www.rfc-editor.org/rfc/rfc9111#section-4.2.2:
  > Since origin servers do not always provide explicit expiration times, a cache MAY assign a heuristic expiration time when an explicit time is not specified, employing algorithms that use other field values (such as the Last-Modified time) to estimate a plausible expiration time.

  > […] Therefore, origin servers are encouraged to send explicit directives (e.g., Cache-Control: no-cache) if they wish to prevent caching.
- The Protocol gives no Cache-Control guidance for access-controlled
  resources (**silent**; `spec_quotes.md` §1d).
- **CSS source:** `src/server/middleware/StaticAssetHandler.ts` L218 is the
  only `cache-control` emitter (static assets). `Vary` comes from
  `config/http/middleware/handlers/constant-headers.json` L10–11.
- **Verdict:** consistent (the Protocol is silent; RFC 9111 does not require
  an origin to send Cache-Control). Consequence, observed: a proxy that
  honours origin headers (config A) stored nothing.

### P2-2. A shared cache configured to ignore the origin served stale and unauthenticated reads
- **Observed:** nginx config B (deliberately permissive) served the cached
  fixture to appR for ≈60 s after the revoke, and to an anonymous client.
  This is proxy behaviour under a configuration we wrote, not CSS behaviour.
- **Spec (RFC 9111 §3.5),** https://www.rfc-editor.org/rfc/rfc9111#section-3.5:
  > A shared cache MUST NOT use a cached response to a request with an Authorization header field (Section 11.6.2 of [HTTP]) to satisfy any subsequent request unless the response contains a Cache-Control field with a response directive (Section 5.2.2) that allows it to be stored by a shared cache, and the cache conforms to the requirements of that directive for that response.
- appR's requests carried `Authorization: DPoP …`, and CSS's responses
  carried no Cache-Control. Config B's reuse of them is therefore something
  RFC 9111 §3.5 forbids for a shared cache. The deviation is in the **proxy
  configuration we wrote** (a deliberately permissive one), not in CSS.
- **Spec (Solid Protocol, WAC, ACP):** **silent** on intermediaries caching
  authorized responses, and on notifying caches of access changes.
- **Verdict:** no CSS deviation; **DEVIATION by the config-B proxy** from
  RFC 9111 §3.5 (by design). The stale window is a property of the proxy
  configuration; CSS 7.2.0 has no mechanism to invalidate it.
