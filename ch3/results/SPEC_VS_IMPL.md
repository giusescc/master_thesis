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

## P3: notifications

Notification specs as fetched (`docs/spec_quotes.md` §4–6): Solid
Notifications Protocol 0.3.0 (TR, 2024-05-12; the 0.4.0 Editor's Draft was
checked too), WebSocketChannel2023 (Editor's Draft 2022-12-27),
WebhookChannel2023 (Draft CG Report 0.1).

### P3-1. Existing channels keep delivering after the revoke
- **Observed:** after alice revoked appR's Read on `person.ttl`, appR's
  existing WebSocket and Webhook channels on it delivered 20/20
  notifications each, on WAC and ACP, in 40/40 lifecycle runs (OBSERVATIONS § P3).
- **Spec (Notifications §2),** https://solidproject.org/TR/notifications-protocol#authentication-authorization:
  > This specification does not require a specific authentication and authorization mechanism to be used with the Solid Notification Protocol. Implementations are encouraged to use existing approaches, such as those described in the Solid Protocol sections on Authentication and Authorization [SOLID-PROTOCOL].
- **Spec (Notifications §4.3, non-normative),** https://solidproject.org/TR/notifications-protocol#security-privacy-review-personal-data:
  > Access to subscription service and notification message are only granted to authorized access subjects.
- **Spec position:** **silent** in normative text on re-checking
  authorization per notification or after access to the topic changes
  (`spec_quotes.md` §4a). The non-normative review sentence says notification
  messages are "only granted to authorized access subjects".
- **CSS source (v7.2.0, b4fe2837):** read permission is checked once, at
  subscription (`src/server/notifications/NotificationSubscriber.ts`
  L118–122, L139–148). `ListeningActivityHandler.ts` L39–75 (`emit`) has no
  permission check. Nothing listens for ACL/ACR changes (`spec_quotes.md` §11 b, d, h).
- **Verdict:** no normative deviation (the normative text is silent).
  **POSSIBLE DEVIATION** from the non-normative §4.3 sentence, if "authorized
  access subjects" is read as "authorized at the time of each message": appR
  was not authorized to read `person.ttl` when these messages were sent.

### P3-2. Nothing tells the channel holder that access ended
- **Observed:** no message on any of appR's channels in the 3 s after the
  revoke, and no message at any time mentioning the `.acl` / `.acr` (40/40 runs).
- **Spec:** the Notifications Protocol has no text on ending channels, or on
  notifying subscribers, when permissions change (`spec_quotes.md` §4a: searched,
  silent). The Protocol's §7.1 describes notifications as being
  "about changes affecting a resource", https://solidproject.org/TR/protocol#notifications-protocol:
  > Entities in a Solid ecosystem use the Solid Notifications Protocol to communicate about changes affecting a resource.
- **Spec position:** **silent.**
- **CSS source:** `spec_quotes.md` §11 (h): no ACL/ACR listener in
  `src/server/notifications`; channels are deleted only on expiry
  (`KeyValueChannelStorage.ts` L31–36, L84) or by `NotificationUnsubscriber.ts` L26.
- **Verdict:** consistent (silent spec).

### P3-3. `receiveFrom` works without credentials, including after the revoke
- **Observed:** appR's WebSocket reconnect to the old `receiveFrom` after the
  revoke sent no credentials, was accepted, and received the next modification
  (40/40). A new subscription on `person.ttl` after the revoke was 403.
- **Spec (WebSocketChannel2023 §3),** https://solid.github.io/notifications/websocket-channel-2023#authentication-authorization:
  > As described by the Solid Notifications Protocol section on Authorization, the WebSocket subscription API requires authorization and follows the guidance of the Solid Protocol sections on Authentication and Authorization [SOLID-PROTOCOL].
- **Spec (Notifications, temporary id),** https://solidproject.org/TR/notifications-protocol#security-privacy-review-temporary-id:
  > The subscription response content can contain a capability URL to protect the notification channel which is only exposed to authorized Subscription Clients.
- **Spec position:** requires authorization for the **subscription** API;
  **silent** on authenticating the connection to `receiveFrom`. The
  capability-URL model is described, and the spec's own example uses one.
- **CSS source:** `WebSocket2023Listener.ts` L27–42 only looks the channel up
  (no credentials, no authorizer); `receiveFrom` is derived from a random
  UUID channel id (`BaseChannelType.ts` L231, `WebSocketChannel2023Type.ts` L46).
- **Verdict:** consistent. The subscription check (403 after the revoke)
  enforces access; the `receiveFrom` URL is a capability that the revoke
  does not invalidate.

### P3-4. Channel expiry: `endAt` = 20160 min / 2 min; after it, silence, not refusal
- **Observed:** `endAt` was subscription time + 20160 min (default) or + 2 min
  (`maxDuration` = 2). After `endAt`, no notification arrived; the open socket
  was not closed by the server; a new WebSocket handshake to the expired
  `receiveFrom` completed, and CSS logged `Unknown or expired WebSocket channel`
  without delivering or closing (20/20 `short` runs;
  `excerpts/p3-expiry-css-log.txt`).
- **Spec (Notifications §2.3.2),** https://solidproject.org/TR/notifications-protocol#notify-endAt:
  > The proposed or actual ending date and time of a notification channel with value represented in the xsd:dateTime datatype.
- **Spec position:** **silent** on a maximum duration and on what a server
  does when `endAt` is reached (`spec_quotes.md` §4b).
- **CSS source:** `NotificationSubscriber.ts` L46–49, L80, L111–116 (default
  20160 min, clamp); `KeyValueChannelStorage.ts` L31 (expiry checked lazily);
  `WebSocket2023Storer.ts` L13–16, L51–60 (open sockets swept every 60 min by
  default, not reached within a run); `WebSocket2023Listener.ts` L27–33 (the
  error seen in the log).
- **Verdict:** consistent (silent spec). The accepted-then-silent handshake
  is a CSS implementation detail with no spec text to compare against.

### P3-5. Anyone who knows the channel id can unsubscribe; the owner cannot find it
- **Observed:** `DELETE <channel id>` returned 205 for bob, for an
  unauthenticated client and for alice, and appR received nothing afterwards
  (60/60). alice found no listing of appR's channel (storage description,
  subscription endpoint: 200 without the id; `/.notifications/`: 400) and a
  DELETE on the subscription endpoint returned 404.
- **Spec:** "unsubscri" and "DELETE" do not occur in the Notifications
  Protocol TR or ED (`spec_quotes.md` §4c). §2.2,
  https://solidproject.org/TR/notifications-protocol#subscription-server-subscription-request-methods:
  > Subscription Servers MUST support the GET, HEAD, OPTIONS, and POST methods [RFC9110] on the subscription service.
- **Spec (WebhookChannel2023 §1.1, goals),** https://solid.github.io/notifications/webhook-channel-2023#goals:
  > Unsubscribing from a WebHook - Unlike websockets, where sockets can simply be closed by the client, if a notifications receiver wants to unsubscribe from a webhook, it must alert the subscription server.

  (stated as a goal, with open issue solid/notifications#145 "Define unsubscribing").
- **Spec position:** **silent** on an unsubscribe method, on who may use it,
  and on an owner listing channels on their resources.
- **CSS source:** `NotificationUnsubscriber.ts` L23–32 (no credentials
  check; 205 via `ResetResponseDescription.ts` L8); wired in
  `config/http/notifications/base/http.json` L46–55. No listing endpoint
  (`spec_quotes.md` §11 j).
- **Verdict:** consistent (silent spec). CSS's unsubscribe is an extension;
  its only access control is knowledge of the UUID id.

### P3-6. Webhook `sendTo` over http was accepted; notifications are signed as the server
- **Observed:** appR subscribed with `sendTo` = `http://127.0.0.1:<port>/…`;
  CSS answered 200 and POSTed every notification there, with
  `Authorization: DPoP <token>` whose `webid` is
  `<base>/.notifications/WebhookChannel2023/webId`, and a `DPoP` proof
  (`htu` = the `sendTo` URL) (40/40 lifecycle runs).
- **Spec (WebhookChannel2023 §2),** https://solid.github.io/notifications/webhook-channel-2023#channel-type:
  > The value of the sendTo property MUST be a URI, using the https scheme.
- **Spec (WebhookChannel2023 §3),** https://solid.github.io/notifications/webhook-channel-2023#auth:
  > Notification Sender MUST perform authenticated request to sendTo webhook endpoint, using identity provided as sender in the subscription response.
- **CSS source:** `WebhookChannel2023Type.ts` L54 validates `sendTo` only by
  cardinality (no scheme check); `WebhookEmitter.ts` L62–97 builds the token
  and proof (`spec_quotes.md` §11 i).
- **Verdict:** **DEVIATION** on the https requirement: CSS 7.2.0 accepted and
  used an http `sendTo` (lab on 127.0.0.1; not predicted, recorded as seen).
  Authenticated delivery: consistent. The token's `webid` equals the `sender`
  in every successful Webhook subscription response (checked over all 40
  lifecycle runs' raw files after the run).

## P4: Comunica link traversal

### P4-1. A client's second query after the revoke is refused at the server
- **Observed:** Comunica 0.8.0, reused or fresh, re-requested `person.ttl` and
  got 403 from CSS 7.2.0 (WAC and ACP, 60/60). The query then failed as a
  whole (OBSERVATIONS § P4).
- **Spec (WAC §5.3.1 and ACP §6.1):** the same requirements as P1-1. Denial
  of this request is what they require.
- **Spec (Solid Protocol §2.2),** https://solidproject.org/TR/protocol#client-authentication-different-credentials:
  > When a client receives a response with a 403 or 404 status code, the client MAY repeat the request with different credentials.
- **Spec position:** **silent** on what a client does with data it read
  before a revoke (keeping, caching, discarding), and on how a query client
  treats a 403 met during traversal. The server's part is P1-1.
- **Verdict:** consistent for CSS. Comunica's handling (a whole-query error)
  is a client choice, with no spec text to compare it against.

## P5: aggregator

### P5-1. Withdrawn, never granted and deleted are indistinguishable to the recipient
- **Observed:** CSS 7.2.0 answered appR with the same 403, the same body
  and the same stable headers for a withdrawn grant, a never-granted resource
  and a deleted resource (WAC and ACP, 40/40; OBSERVATIONS § P5).
- **Spec (Solid Protocol §2.1),** https://solidproject.org/TR/protocol#server-unauthenticated:
  > When a client does not provide valid credentials when requesting a resource that requires it (see WebID), servers MUST send a response with a 401 status code (unless 404 is preferred for security reasons).
- **Spec (Solid Protocol §2.2),** https://solidproject.org/TR/protocol#client-authentication-different-credentials:
  > When a client receives a response with a 403 or 404 status code, the client MAY repeat the request with different credentials.
- **Spec (WAC §8.1, non-normative),** https://solidproject.org/TR/wac#consider-acl-resource-activities:
  > Implementations are encouraged to use mechanisms to record activities about ACL resources for the purpose of accountability and integrity, e.g., by having audit trails, notification of changes, reasons for change, preserving provenance information.
- **Spec position:** the Protocol's status-code text (`spec_quotes.md` §1a)
  has no sentence on telling an authenticated client *why* access is
  refused, or on a distinct status for "access withdrawn". For WAC and ACP,
  no search for such text was recorded when the quotes were fetched; the
  quoted sections (§2, §3) contain none. The nearest text is WAC §8.1 above,
  which is non-normative and does not say to whom a change is notified.
  Reading: **silent**, scoped to the text quoted.
- **Verdict:** consistent (silent spec). A recipient-side purge on 403 (our
  403-aware policy) cannot be triggered by "withdrawn" as such. It can only be
  triggered by "refused", which also covers deletion and never-granted.

### P5-2. Copied data stays unless the recipient deletes it
- **Observed:** the naive aggregator kept all 23 rows through 10 post-revoke
  syncs. Nothing from CSS reached it except the 403 on its own fetches.
- **Spec (WAC §5.3.1),** https://solidproject.org/TR/wac#server-read-operation:
  > When an operation requests to read a resource, the server MUST match an Authorization allowing the acl:Read access privilege on the resource.
- **Spec position:** access control applies to *operations on the server*;
  none of the Solid Protocol, WAC or ACP sections quoted in
  `spec_quotes.md` §1–3 has text on data a client has already copied. No
  dedicated search for such text was recorded. Reading: **silent**, scoped to
  the text quoted.
- **Verdict:** consistent (silent spec). Outside the server's reach by
  design; no CSS source is involved.

## P6: agent memory

### P6-1. An index built during access keeps answering after the revoke
- **Observed:** a memory built by appR before the revoke still retrieved the
  `person.ttl` chunks and produced the correct fixture values after the
  revoke. At the same moment, CSS 7.2.0 (WAC and ACP) answered appR's direct
  GET with 403 (20/20; OBSERVATIONS § P6).
- **Spec (WAC §5.3.1),** https://solidproject.org/TR/wac#server-read-operation:
  > When an operation requests to read a resource, the server MUST match an Authorization allowing the acl:Read access privilege on the resource.
- **Spec position:** access control applies to *operations on the server*.
  None of the Solid Protocol, WAC or ACP sections quoted in
  `spec_quotes.md` §1–3 has text on derived copies (indexes, embeddings)
  held by a client. No dedicated search for such text was recorded.
  Reading: **silent**, scoped to the text quoted.
- **Verdict:** consistent for CSS (the server-side denial is what §5.3.1
  requires). The memory is outside the server's reach, as in P5-2.

## P7: withdrawal notice

LDN is the W3C Recommendation of 2 May 2017 (`spec_quotes.md` §8). The Solid
Protocol requires LDN Receiver conformance (§1f).

### P7-1. The inbox accepted the notice with 201 + Location
- **Observed:** CSS 7.2.0 (WAC and ACP) answered alice's POST to each
  recipient's inbox with 201, a `Location` and an empty body (80/80 POSTs).
- **Spec (LDN §3.3.1),** https://www.w3.org/TR/ldn/#receiving-notifications:
  > Upon receipt of a POST request, if the notification resource was processed successfully, receivers MUST respond with status code 201 Created and the Location header set to the URL from which the notification data can be retrieved (see Consumer). If the request was queued to be processed asynchronously, the receiver MUST respond with a status code of 202 Accepted and include information about the status of the request in the body of the response.
- **Spec (Solid Protocol §6),** https://solidproject.org/TR/protocol#server-ldn:
  > A Solid server MUST conform to the LDN specification by implementing the Receiver parts to receive notifications and make Inbox contents available [LDN].
- **Spec position:** requires. **Verdict:** consistent.

### P7-2. 201 is the only thing the sender learns; no acknowledgement of processing
- **Observed:** alice's view was identical for cooperating and
  non-cooperating recipients (40/40): 201, then 403 on the `Location` and on
  the inbox (she has Append only).
- **Spec (LDN §3.4),** https://www.w3.org/TR/ldn/#consumer:
  > Fetching the individual notifications — if any, how many, or according to a particular criteria (e.g., content-length, timestamp) — is at the discretion of the consumer.
- **Spec (LDN §3.3.2),** https://www.w3.org/TR/ldn/#receiving-inbox-contents:
  > A successful GET request on the Inbox MUST return a HTTP 200 OK with the URIs of notifications, subject to the requester’s access (returning 4xx error codes as applicable).
- **Spec position:** LDN defines no acknowledgement that a notice was read or
  acted on (**silent**; `spec_quotes.md` §8 note). Reading the inbox is
  "subject to the requester's access", so alice's 403 is consistent.
- **Verdict:** consistent.

### P7-3. Inbox discovery through the profile's RDF, not a Link header
- **Observed:** the WebID profile had no `Link rel=inbox` header; the
  `ldp:inbox` triple that the recipient had added gave the inbox (80/80).
- **Spec (LDN §3.1),** https://www.w3.org/TR/ldn/#discovery:
  > These may be carried out in either order, but if the first fails to result in an Inbox the second MUST be tried.

  > A resource MUST advertise only one Inbox.
- **Spec position:** either discovery route is allowed. **Verdict:**
  consistent. Each profile advertised exactly one inbox (a fixed
  `ch3-inbox/`, reused across reps for this reason).

### P7-4. Sender verification was left to the access document
- **Observed:** the prototype handlers did not verify the notice's sender.
  Only alice (Append) and the owner could POST to the inbox, because of the
  access document the recipient wrote.
- **Spec (LDN §3.3.3),** https://www.w3.org/TR/ldn/#sender-verification:
  > Receivers SHOULD verify the sender of the notification.
- **Spec position:** recommends (SHOULD). **Verdict:** a gap in **our
  prototype**, not in CSS. The access document limited who could post. The
  handler did not check that the notice came from the agent it names.

### P7-5. Former recipients are not listed anywhere after the revoke
- **Observed:** after the revoke, the access document no longer named appR or
  bob. alice's recipient list came only from her own grant log (40/40).
- **Spec (WAC §8.1, non-normative),** https://solidproject.org/TR/wac#consider-acl-resource-activities:
  > Implementations are encouraged to use mechanisms to record activities about ACL resources for the purpose of accountability and integrity, e.g., by having audit trails, notification of changes, reasons for change, preserving provenance information.
- **Spec position:** encouraged, non-normative. There is no normative text
  on keeping a record of past grantees (for WAC and ACP, silent, scoped to
  the text quoted in `spec_quotes.md` §2–3).
- **Verdict:** consistent. Through the resource interface alice used,
  CSS 7.2.0 offered her no record of former grantees. We did not search the
  CSS source for internal audit logging, so "not implemented" is **not**
  claimed. The claim is only "not available to alice here".
