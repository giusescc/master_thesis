# Specification quotes and CSS 7.2.0 source excerpts: revocation experiment

Retrieved on **2026-09-24**. Each page was downloaded as raw HTML or plain text with `curl`.
The raw copies were kept in a session scratch directory (not committed). The text was extracted with a Python HTML parser, so
quotes are the page's own words. Only whitespace was normalised: HTML indentation and RFC
plain-text line wraps were joined into single lines. Wording, capitalisation and punctuation
were not changed. Nothing below comes from memory.

**Section numbers.** The Solid TR pages (Protocol, WAC, Notifications) number their sections
with CSS counters, so the numbers do not appear in the HTML text. I computed the numbers from
the nesting of `<section>` elements, following the page's own counter rules. The computed
numbers match the Notifications Protocol's own TOC wherever it shows numbers (for example,
"4.1 Security Considerations"). The **#anchor** is always the authoritative reference.
ACP, the WebSocket and Webhook channels, LDN, ODRL, DPV and the RFCs print their numbers in
the text, and those are quoted as printed.

---

## 1. Solid Protocol

**Spec:** Solid Protocol, *Draft Community Group Report, 12 May 2024* (Version 0.11). This
version: https://solidproject.org/TR/2024/protocol-20240512. Fetched from
https://solidproject.org/TR/protocol.

### 1a. Status codes (401 / 403 / 404)

§2.1 HTTP Server: https://solidproject.org/TR/protocol#server-unauthenticated
> When a client does not provide valid credentials when requesting a resource that requires it (see WebID), servers MUST send a response with a 401 status code (unless 404 is preferred for security reasons).

§2.2 HTTP Client: https://solidproject.org/TR/protocol#client-authentication-different-credentials
> When a client receives a response with a 403 or 404 status code, the client MAY repeat the request with different credentials.

§8.1 CORS Server: https://solidproject.org/TR/protocol#server-cors
> […] If the server wishes to block access to a resource, this MUST NOT happen via CORS but MUST instead be communicated to the Solid app in the browser through HTTP status codes such as 401, 403, or 404 [RFC9110].

§3.1 URI Slash Semantics: https://solidproject.org/TR/protocol#server-authorization-redirect
> Servers MUST authorize prior to this optional redirect.

§4.3.2 Description Resource: https://solidproject.org/TR/protocol#server-description-resource-authorization
> When an HTTP request targets a description resource, the server MUST apply the authorization rule that is used for the subject resource with which the description resource is associated.

**Silent.** The Protocol has no normative sentence saying when a server must use 403 rather
than 404 for an authenticated agent that lacks permission.

### 1b. Is authorization evaluated on every request?

§11 Authorization: https://solidproject.org/TR/protocol#server-wac-acp
> Servers MUST conform to either or both Web Access Control [WAC] and Access Control Policy [ACP] specifications.

§11.1 Web Access Control (informative text): https://solidproject.org/TR/protocol#web-access-control
> Server manages the association between a resource and an ACL resource with the acl Link Relation, and applies the authorization conditions on requested operations.

**Silent.** I searched for "cach", "immediate", "take effect" and "per request". The Protocol
never states whether authorization is evaluated on each request, and never says when a change
to an ACL takes effect.

### 1c. Access-control discovery (`rel=acl`) and WAC-Allow

§4.3 Auxiliary Resources: https://solidproject.org/TR/protocol#server-link-auxiliary-type
> Servers MUST advertise auxiliary resources associated with a subject resource by responding to HEAD and GET requests by including the HTTP Link header field with the rel parameter [RFC8288].

The auxiliary-types table in §4.3 lists: `Web Access Control | acl | [WAC]`.

§4.3.1 Web Access Control: https://solidproject.org/TR/protocol#auxiliary-resources-web-access-control
> An auxiliary resource of type Web Access Control provides access control description of a subject resource (Web Access Control).

**WAC-Allow.** The Protocol has no WAC-Allow requirement of its own. The string "WAC-Allow"
does not occur in the fetched page. The requirement is in the WAC spec (§2c below).

### 1d. Caching

§2.1 HTTP Server: https://solidproject.org/TR/protocol#server-caching
> Servers SHOULD conform to HTTP Caching [RFC9111].

§2.2 HTTP Client: https://solidproject.org/TR/protocol#client-caching
> Clients MAY conform to HTTP Caching [RFC9111].

**Silent.** The Protocol has no Cache-Control guidance for protected resources. Beyond the two
sentences above, it does not discuss caching.

### 1e. Notifications

§7.1 Solid Notifications Protocol: https://solidproject.org/TR/protocol#notifications-protocol
> Entities in a Solid ecosystem use the Solid Notifications Protocol to communicate about changes affecting a resource.

https://solidproject.org/TR/protocol#server-notifications-protocol-resource-server
> Servers MUST conform to the Solid Notifications Protocol [SOLID-NOTIFICATIONS-PROTOCOL] by implementing the Resource Server to enable clients to discover subscription resources and notification channels available to a given resource or storage.

https://solidproject.org/TR/protocol#server-notifications-protocol-subscription-server
> Servers MUST conform to the Solid Notifications Protocol [SOLID-NOTIFICATIONS-PROTOCOL] by implementing the Subscription Server to process and produce instructions for subscription requests.

https://solidproject.org/TR/protocol#server-notifications-protocol-notification-sender
> Servers MUST conform to the Solid Notifications Protocol [SOLID-NOTIFICATIONS-PROTOCOL] by implementing the Notification Sender to produce and send messages to a Notification Receiver.

### 1f. LDN / `ldp:inbox`

§6 Linked Data Notifications: https://solidproject.org/TR/protocol#server-ldn
> A Solid server MUST conform to the LDN specification by implementing the Receiver parts to receive notifications and make Inbox contents available [LDN].

https://solidproject.org/TR/protocol#client-ldn
> A Solid client MUST conform to the LDN specification by implementing the Sender or Consumer parts to discover the location of a resource’s Inbox, and to send notifications to an Inbox or to retrieve the contents of an Inbox [LDN].

---

## 2. Web Access Control (WAC)

**Spec:** Web Access Control, *Draft Community Group Report, 12 May 2024*. This version:
https://solidproject.org/TR/2024/wac-20240512. Conformance keywords are "MUST" and "MUST NOT"
only (§1.3).

### 2a. ACL resource discovery

§3.1 ACL Resource Discovery: https://solidproject.org/TR/wac#server-link-acl
> When a server wants to enable applications to discover Authorizations associated with a given resource, the server MUST advertise the ACL resource that is associated with a resource by responding to an HTTP request including a Link header with the rel value of acl (acl Link Relation) and the ACL resource as link target [RFC8288].

https://solidproject.org/TR/wac#client-link-acl
> Clients MUST discover the ACL resource associated with a resource by making an HTTP request on the target URL, and checking the HTTP Link header with the rel parameter.

https://solidproject.org/TR/wac#client-acl-uri
> Clients MUST NOT derive the URI of the ACL resource through string operations on the URI of the resource.

§6.2 acl Link Relation: https://solidproject.org/TR/wac#acl-link-relation
> Asserts that the link target provides an access control resource for the link context.

### 2b. Authorization evaluation

§5.1 Effective ACL Resource: https://solidproject.org/TR/wac#effective-acl-resource-without-representation
> When an ACL resource associated with a resource does not have a representation (ACL Resource Representation), no Authorizations can be immediately checked against the requested resource. In this case, a container resource’s ACL resource might apply on every access to a member resource, in specifying Authorizations for the requested resource.

§5.3 Authorization Evaluation: https://solidproject.org/TR/wac#authorization-evaluation-applicable
> The evaluation of an authorization is concerned with finding Authorizations that match the required parameters of an operation (Authorization Conformance). Evaluation stops when all access permission requests have been granted by one or more Authorizations. Authorizations that do not match a required access permission have no effect on the outcome of the evaluation. Access is granted when conforming Authorizations are matched, otherwise access is denied.

§5.3.1 Reading and Writing Resources: https://solidproject.org/TR/wac#server-read-operation
> When an operation requests to read a resource, the server MUST match an Authorization allowing the acl:Read access privilege on the resource.

https://solidproject.org/TR/wac#server-control-operation
> When an operation requests to read and write an ACL resource, the server MUST match an Authorization allowing the acl:Control access privilege on the resource.

§3.2 ACL Resource Representation: https://solidproject.org/TR/wac#server-get-acl-without-representation
> When an authorized HTTP GET or HEAD request targets an ACL resource without an existing representation, the server MUST respond with the 404 status code as per [RFC9110].

### 2c. WAC-Allow

§5.3.4 Access Privileges: https://solidproject.org/TR/wac#server-wac-allow
> Servers MUST advertise client’s access privileges on a resource by including the WAC-Allow HTTP header (WAC-Allow) in the response of HTTP GET and HEAD requests.

https://solidproject.org/TR/wac#client-wac-allow
> Clients MUST discover access privileges on a resource by making an HTTP GET or HEAD request on the target resource, and checking the WAC-Allow header value for access parameters listing the allowed access modes per permission group (WAC-Allow).

https://solidproject.org/TR/wac#server-cors-aceh-wac-allow
> When a server participates in the CORS protocol [FETCH], the server MUST include WAC-Allow in the Access-Control-Expose-Headers field-value in the HTTP response.

§6.1 wac-allow HTTP Header: https://solidproject.org/TR/wac#wac-allow
> The WAC-Allow HTTP header’s field-value is a comma-separated list of access-params. access-param is a whitespace-separated list of access-modes granted to a permission-group.

> This specification defines the following permission-groups: user Permissions granted to the agent requesting the resource. public Permissions granted to the public.

This is a definition list in the source (`user` / `public`), shown here on one line.

### 2d. When ACL changes take effect, and caching of authorization

**Silent.** I searched for "cach", "immediate", "take effect" and "stale". Neither topic is
addressed. The only "immediately" is the sentence quoted in 2b, and it is about inheritance,
not timing. The closest related text is non-normative.

§8.1 Security Considerations: https://solidproject.org/TR/wac#consider-acl-resource-activities
> Implementations are encouraged to use mechanisms to record activities about ACL resources for the purpose of accountability and integrity, e.g., by having audit trails, notification of changes, reasons for change, preserving provenance information.

§7.1 Authorization Extensions: https://solidproject.org/TR/wac#extension-acl-authorization
> As ACL resources are RDF sources; Authorization descriptions can be extended or limited by constraints, e.g., temporal or spatial constraints; and duties, e.g., payments, can be imposed on permissions; but no behaviour is defined by this specification. For example, the ODRL Information Model can be used to set obligations required to be met by agents prior to accessing a resource.

---

## 3. Access Control Policy (ACP)

**Spec:** Access Control Policy (ACP), *Version 0.9.0, 2022-05-18*. This version:
https://solidproject.org/TR/2022/acp-20220518. Numbers below are printed on the page.

### 3a. ACR discovery

§7.1 Conforming resource server: https://solidproject.org/TR/acp#conforming-resource-server
> Conforming resource servers MUST provide ACP servers with resource access Contexts and MUST authorize resource access according to grant graphs produced by a conforming ACP server.

> When responding to requests targetting access controlled resources, conforming resource servers MUST include a Link header with the rel value of acl and controlled resources' ACRs as the link target RFC 8288.

§7.2 Conforming ACP server: https://solidproject.org/TR/acp#conforming-acp-server
> When responding to requests targetting an ACR, conforming ACP servers MUST include a Link header with the rel value of type and the http://www.w3.org/ns/solid/acp#AccessControlResource IRI as the link target.

> The lifecycle of Access Control Resources SHOULD take into account the lifecycle of resources they control access to.

### 3b. `acp:memberAccessControl` and inheritance

§4.1 Access Control Resource: https://solidproject.org/TR/acp#acp-member-access-control
> acp:memberAccessControl The member access control property transitively connects ACRs of member resources to Access Controls.

§6.1 Resolved Access Control: https://solidproject.org/TR/acp#resolved-access-control
> An ACP engine MUST grant exactly those Access Modes allowed by Effective Policies.

§6.2 Effective Policies: https://solidproject.org/TR/acp#effective-policies
> A Policy MUST control access to a resource if: it is applied by an Access Control of an ACR of the resource; or, it is applied by a member Access Control of an ACR of an ancestor of the resource.

### 3c. Timing of changes, and advertising permissions

**Silent** on when changes take effect: I searched for "cach", "immediate" and "take effect".

**Silent** on advertising the requester's permissions: "WAC-Allow" does not occur, and there
is no equivalent header. The only advertisement requirements are these OPTIONS-on-ACR Link
headers, which describe what the ACP server *supports*, not what the requester is *granted*.

§7.2: https://solidproject.org/TR/acp#conforming-acp-server
> When responding to OPTIONS requests targetting an ACR, conforming ACP servers MUST include a Link header for each supported Access Mode with the rel value of http://www.w3.org/ns/solid/acp#grant and the full IRI of the supported Access Mode as the link target.

---

## 4. Solid Notifications Protocol

**Spec:** Solid Notifications Protocol, *Draft Community Group Report, 12 May 2024*
(Version 0.3.0). This version:
https://solidproject.org/TR/2024/notifications-protocol-20240512.

I also checked the Editor's Draft (https://solid.github.io/notifications/protocol,
*Editor's Draft 2024-06-03*, version 0.4.0). It contains no unsubscribe, DELETE, revocation or
expiry text either.

### 4a. Authorization, at subscription time and afterwards

§2 Protocol: https://solidproject.org/TR/notifications-protocol#authentication-authorization
> This specification does not require a specific authentication and authorization mechanism to be used with the Solid Notification Protocol. Implementations are encouraged to use existing approaches, such as those described in the Solid Protocol sections on Authentication and Authorization [SOLID-PROTOCOL].

§2.1 Discovery: https://solidproject.org/TR/notifications-protocol#discovery
> Choosing the most appropriate topic resource from which to begin discovery is at the discretion of the Discovery Client, since notifications may be available for any resource for authorized access subjects.

> Resource Servers can advertise subscription services that can be used to create notification channels: for protected resource, which relies on capability URL to protect the channel; with specific features required by the subscribing client.

> Resource Servers can advertise existing notification channels to provide notifications: for protected resource, which does not rely on capability URL to protect the channel; for public read resource.

§4.3 Security and Privacy Review (non-normative): https://solidproject.org/TR/notifications-protocol#security-privacy-review-personal-data
> Access to subscription service and notification message are only granted to authorized access subjects.

https://solidproject.org/TR/notifications-protocol#security-privacy-review-temporary-id
> The subscription response content can contain a capability URL to protect the notification channel which is only exposed to authorized Subscription Clients.

**Silent.** The spec never says whether the Notification Sender must re-check authorization
before sending each notification, or after access to the topic changes. It has no text on
revoking or ending channels when permissions change.

### 4b. Channel lifetime: `startAt` and `endAt`

§2.3.2 Features: https://solidproject.org/TR/notifications-protocol#notify-startAt
> The proposed or actual starting date and time of a notification channel with value represented in the xsd:dateTime datatype.

https://solidproject.org/TR/notifications-protocol#notify-endAt
> The proposed or actual ending date and time of a notification channel with value represented in the xsd:dateTime datatype.

https://solidproject.org/TR/notifications-protocol#notification-features
> These shared features are listed as an initial baseline, though not all notification channel types are required to implement these.

**Silent** on any maximum duration, and on what a server must do when `endAt` is reached.

### 4c. Unsubscribe, and who may unsubscribe

**Silent.** "unsubscri" and "DELETE" do not occur in the TR or in the ED. The spec defines no
`unsubscribe_endpoint` or anything equivalent. §2.2 Subscription
(https://solidproject.org/TR/notifications-protocol#subscription-server-subscription-request-methods)
lists only these methods:
> Subscription Servers MUST support the GET, HEAD, OPTIONS, and POST methods [RFC9110] on the subscription service.

### 4d. `receiveFrom` and `sendTo`

§3.3 Notification Channel: https://solidproject.org/TR/notifications-protocol#notify-receiveFrom
> One receiveFrom property to identify the resource on the Notification Sender that can be used to establish a connection to receive notifications.

https://solidproject.org/TR/notifications-protocol#notify-sendTo
> Zero or one sendTo property to identify the resource where the Notification Receiver can accept notifications.

https://solidproject.org/TR/notifications-protocol#notify-sender
> Zero or one sender property to identify the Notification Sender

### 4e. Notification message data model

§3.4 Notification Message: https://solidproject.org/TR/notifications-protocol#notification-message-data-model
> The core notification data is expressed with the Activity Streams [ACTIVITYSTREAMS-VOCABULARY] and Solid Notifications vocabularies.

- `#message-id`: "One id property to identify the notification."
- `#message-type`: "At least one type property indicating a specific type of activity (Activity Types)."
- `#message-object`: "One object property to identify the (topic) resource that the notification is about."
- `#message-published`: "One published property to indicate the date and time of the notification."
- `#message-state`: "Zero or one state property to indicate the last known state of the resource."

The spec's example uses `"type": "Update"` together with the `https://www.w3.org/ns/activitystreams` context.

§2.4 Notification Message: https://solidproject.org/TR/notifications-protocol#notification-message
> Notification Receivers are encouraged to be aware that anything can be included in the notification message […] so when it comes to making use of notification data, receivers may want to take precautions when ascertaining the veracity of the contents.

§4.1 Security Considerations (non-normative): https://solidproject.org/TR/notifications-protocol#consider-exposing-information
> Subscription Servers and Notification Senders are strongly discouraged from exposing information beyond the minimum amount necessary to enable a feature.

---

## 5. WebSocketChannel2023

**Spec:** Solid Notifications: WebSocketChannel2023, *Editor's Draft, 2022-12-27* (Created,
Published and Modified are all 2022-12-27). URL:
https://solid.github.io/notifications/websocket-channel-2023. Section numbers come from the
page TOC. Conformance keywords are MUST and MUST NOT only.

§2 WebSocketChannel2023 Type: https://solid.github.io/notifications/websocket-channel-2023#subscription-type
> An WebSocketChannel2023 API MUST conform to the Solid Notifications Protocol. [SOLID-NOTIFICATIONS]

> A client establishes a subscription using the WebSocketChannel2023 type by sending an authorized subscription request to the subscription resource based on Solid Notifications Protocol discovery.

§2.1 Subscription Example (non-normative): https://solid.github.io/notifications/websocket-channel-2023#websocket-subscription
> A successful response will contain a URL to the subscription API (receiveFrom) that can be used directly with a JavaScript client.

The example response has `"receiveFrom": "wss://websocket.example/?auth=Ys3KiUq"`, which is a
capability-style URL. The JavaScript example opens it with `new WebSocket(url, protocol)` and
sends no credentials.

§3 Authentication and Authorization: https://solid.github.io/notifications/websocket-channel-2023#authentication-authorization
> As described by the Solid Notifications Protocol section on Authorization, the WebSocket subscription API requires authorization and follows the guidance of the Solid Protocol sections on Authentication and Authorization [SOLID-PROTOCOL].

**Silent.** There is no normative text requiring authentication or authorization when a client
connects to `receiveFrom`. The page has no security considerations section.

---

## 6. WebhookChannel2023

**Spec:** Solid WebhookChannel2023, *Draft Community Group Report*, version 0.1. The page is
generated by Bikeshed and was stamped "4 August 2026" when fetched. That is the render date
and may change on each rebuild. URL: https://solid.github.io/notifications/webhook-channel-2023.
Section numbers are printed on the page.

Per its "Document conventions", RFC 2119 keywords in this document are normative "[h]owever,
for readability, these words do not appear in all uppercase letters". In the fetched text they
do appear in capitals.

§1.1 Specification Goals: https://solid.github.io/notifications/webhook-channel-2023#goals
> Verifiable requests to a notification receiver - a notification receiver must be able to confirm if a request truly came from a specific notification sender.

> Unsubscribing from a WebHook - Unlike websockets, where sockets can simply be closed by the client, if a notifications receiver wants to unsubscribe from a webhook, it must alert the subscription server.

Open issues are embedded under §1.1: "solid/notifications/155 Make AuthN/AuthZ of each channel
explicit" and "solid/notifications/145 Define unsubscribing". Under §2 there is also
"solid/notifications/134 Notification Sender - authentication may require both identities
client & agent (user)".

§2 WebhookChannel2023 Type: https://solid.github.io/notifications/webhook-channel-2023#channel-type
> The value of the sendTo property MUST be a URI, using the https scheme.

> A client establishes a subscription using the WebhookChannel2023 type by sending an authenticated subscription request to the Subscription Resource retrieved via Solid Notifications discovery.

> The sendTo field MUST contain the https URL of the webhook endpoint, where the notification sender is expected to send notifications.

> The id field MUST be a URI, which identifies the created notification channel.

> The sender field MUST contain a URI which identifies the notifications sender.

§3 Authentication and Authorization: https://solid.github.io/notifications/webhook-channel-2023#auth
> Subscription client MUST perform authenticated subscription request.

> Notification Sender MUST perform authenticated request to sendTo webhook endpoint, using identity provided as sender in the subscription response.

> As described by the Solid Notifications Protocol section on Authorization, the WebhookChannel2023 requires authorization and follows the guidance of the Solid Protocol sections on Authentication and Authorization [Solid.Protocol].

> It is beyond the scope of this document to describe how a client fetches an access token.

**Unsubscribe mechanism: silent.** It appears only as a goal (§1.1) plus open issue #145. The
page has no security considerations section.

---

## 7. RFC 9111, HTTP Caching (STD 98, June 2022)

Fetched as plain text from https://www.rfc-editor.org/rfc/rfc9111.txt. RFC line wraps are joined.

§3.5 Storing Responses to Authenticated Requests: https://www.rfc-editor.org/rfc/rfc9111#section-3.5
> A shared cache MUST NOT use a cached response to a request with an Authorization header field (Section 11.6.2 of [HTTP]) to satisfy any subsequent request unless the response contains a Cache-Control field with a response directive (Section 5.2.2) that allows it to be stored by a shared cache, and the cache conforms to the requirements of that directive for that response.
>
> In this specification, the following response directives have such an effect: must-revalidate (Section 5.2.2.2), public (Section 5.2.2.9), and s-maxage (Section 5.2.2.10).

§3 Storing Responses in Caches, the relevant bullet: https://www.rfc-editor.org/rfc/rfc9111#section-3
> if the cache is shared: the Authorization header field is not present in the request (see Section 11.6.2 of [HTTP]) or a response directive is present that explicitly allows shared caching (see Section 3.5); and

§4.2.2 Calculating Heuristic Freshness: https://www.rfc-editor.org/rfc/rfc9111#section-4.2.2
> Since origin servers do not always provide explicit expiration times, a cache MAY assign a heuristic expiration time when an explicit time is not specified, employing algorithms that use other field values (such as the Last-Modified time) to estimate a plausible expiration time. This specification does not provide specific algorithms, but it does impose worst-case constraints on their results.
>
> A cache MUST NOT use heuristics to determine freshness when an explicit expiration time is present in the stored response. Because of the requirements in Section 3, heuristics can only be used on responses without explicit freshness whose status codes are defined as "heuristically cacheable" (e.g., see Section 15.1 of [HTTP]) and on responses without explicit freshness that have been marked as explicitly cacheable (e.g., with a public response directive).
>
> […]
>
> If the response has a Last-Modified header field (Section 8.8.2 of [HTTP]), caches are encouraged to use a heuristic expiration value that is no more than some fraction of the interval since that time. A typical setting of this fraction might be 10%.
>
> *Note:* […] Therefore, origin servers are encouraged to send explicit directives (e.g., Cache-Control: no-cache) if they wish to prevent caching.

§5.2.2.7 private: https://www.rfc-editor.org/rfc/rfc9111#section-5.2.2.7
> The unqualified private response directive indicates that a shared cache MUST NOT store the response (i.e., the response is intended for a single user). It also indicates that a private cache MAY store the response, subject to the constraints defined in Section 3, even if the response would not otherwise be heuristically cacheable by a private cache.

A factual note, not a quote: DPoP-authenticated Solid requests carry `Authorization: DPoP …`,
which is an Authorization header field.

---

## 8. Linked Data Notifications (LDN)

**Spec:** Linked Data Notifications, *W3C Recommendation 2 May 2017*. This version:
https://www.w3.org/TR/2017/REC-ldn-20170502/. Numbers are printed on the page.

§3.1 Discovery: https://www.w3.org/TR/ldn/#discovery
> make an HTTP HEAD or GET request on the target URL, and use the Link header with a rel value of http://www.w3.org/ns/ldp#inbox.

> make an HTTP GET request on the target URL to retrieve an RDF representation [RDF 1.1], whose encoded RDF graph contains a relation of type http://www.w3.org/ns/ldp#inbox. The subject of that relation is target and the object is the Inbox.

> These may be carried out in either order, but if the first fails to result in an Inbox the second MUST be tried.

> A resource MUST advertise only one Inbox.

§3.2 Sender: https://www.w3.org/TR/ldn/#sender
> Following discovery, senders who want to send notifications MUST deliver them through a POST request to the Inbox URL. Senders can expect a 201 Created (with a Location Link header) or a 202 Accepted in response to a successful request.

> The sender MAY include additional headers or content for the purposes of authentication or authorization e.g., Authorization: Bearer XXX.

§3.3.1 Receiving notifications: https://www.w3.org/TR/ldn/#receiving-notifications
> Upon receipt of a POST request, if the notification resource was processed successfully, receivers MUST respond with status code 201 Created and the Location header set to the URL from which the notification data can be retrieved (see Consumer). If the request was queued to be processed asynchronously, the receiver MUST respond with a status code of 202 Accepted and include information about the status of the request in the body of the response.

§3.3.2 Making Inbox contents available to consumers: https://www.w3.org/TR/ldn/#receiving-inbox-contents
> A successful GET request on the Inbox MUST return a HTTP 200 OK with the URIs of notifications, subject to the requester’s access (returning 4xx error codes as applicable).

§3.3.3 Sender Verification: https://www.w3.org/TR/ldn/#sender-verification
> Receivers SHOULD verify the sender of the notification.

§3.4 Consumer: https://www.w3.org/TR/ldn/#consumer
> Fetching the individual notifications — if any, how many, or according to a particular criteria (e.g., content-length, timestamp) — is at the discretion of the consumer.

**Acknowledgement of processing.** A 201 means only that the notification resource was
"processed successfully" in the sense of being created and retrievable. LDN defines no signal
that a human or application has read the notification or acted on it. Whether and when the
consumer fetches it "is at the discretion of the consumer" (quoted above).

§5.3 Subscribing to Notifications: https://www.w3.org/TR/ldn/#subscribing-to-notifications
> This kind of subscription mechanism is left out of scope, but senders, receivers and consumers are not prohibited from making such an arrangement.

---

## 9. RFC 9449, OAuth 2.0 Demonstrating Proof of Possession (DPoP) (September 2023)

Fetched as plain text from https://www.rfc-editor.org/rfc/rfc9449.txt.

§4.2 DPoP Proof JWT Syntax: https://www.rfc-editor.org/rfc/rfc9449#section-4.2
> htu: The HTTP target URI (Section 7.1 of [RFC9110]) of the request to which the JWT is attached, without query and fragment parts.

> htm: The value of the HTTP method (Section 9.1 of [RFC9110]) of the request to which the JWT is attached.

§4.3 Checking DPoP Proofs: https://www.rfc-editor.org/rfc/rfc9449#section-4.3
> To validate a DPoP proof, the receiving server MUST ensure the following:
> […]
> 8. The htm claim matches the HTTP method of the current request.
> 9. The htu claim matches the HTTP URI value for the HTTP request in which the JWT was received, ignoring any query and fragment parts.
> […]
> To reduce the likelihood of false negatives, servers SHOULD employ syntax-based normalization (Section 6.2.2 of [RFC3986]) and scheme-based normalization (Section 6.2.3 of [RFC3986]) before comparing the htu claim.

---

## 10. ODRL and DPV

### ODRL

**ODRL Information Model 2.2**, *W3C Recommendation 15 February 2018*,
https://www.w3.org/TR/2018/REC-odrl-model-20180215/.
**ODRL Vocabulary & Expression 2.2**, *W3C Recommendation 15 February 2018*,
https://www.w3.org/TR/2018/REC-odrl-vocab-20180215/.

The Information Model page does not state the namespace. It is in the Vocabulary spec:

Vocab §2.1 Namespaces: https://www.w3.org/TR/odrl-vocab/#namespaces
> odrl | http://www.w3.org/ns/odrl/2/ | ODRL Vocabulary

| Term | IRI (as shown) | Definition (verbatim) | Source |
|---|---|---|---|
| odrl:Policy | `http://www.w3.org/ns/odrl/2/Policy` | "A non-empty group of Permissions and/or Prohibitions." | Vocab §3.1.1, https://www.w3.org/TR/odrl-vocab/#term-Policy |
| odrl:target | `http://www.w3.org/ns/odrl/2/target` | "The target property indicates the Asset that is the primary subject to which the Rule action directly applies." | Vocab §3.5.1, https://www.w3.org/TR/odrl-vocab/#term-target |
| odrl:assignee | `http://www.w3.org/ns/odrl/2/assignee` | "The Party is the recipient of the Rule." | Vocab §3.7.1, https://www.w3.org/TR/odrl-vocab/#term-assignee |
| odrl:action | `http://www.w3.org/ns/odrl/2/action` | "The operation relating to the Asset for which the Rule is being subjected." (label "Has Action") | Vocab §3.11.2, https://www.w3.org/TR/odrl-vocab/#term-action |
| odrl:Action | `http://www.w3.org/ns/odrl/2/Action` | "An operation on an Asset." | Vocab §3.11.1, https://www.w3.org/TR/odrl-vocab/#term-Action |
| odrl:read | `http://www.w3.org/ns/odrl/2/read` | "To obtain data from the Asset." Note: "For example, the ability to read a record from a database (the Asset)." Included In: use | Vocab §4.4.35, https://www.w3.org/TR/odrl-vocab/#term-read |
| odrl:Permission | `http://www.w3.org/ns/odrl/2/Permission` | "The ability to perform an Action over an Asset." | Vocab §3.9.1, https://www.w3.org/TR/odrl-vocab/#term-Permission |

Information Model wording for the same concepts:

- §2 ODRL Information Model, https://www.w3.org/TR/odrl-model/#infoModel: "Policy - A non-empty group of Permissions (via the permission property) and/or Prohibitions (via the prohibition property) and/or Duties (via the obligation property)."
- §2.2.1 Relation Property, https://www.w3.org/TR/odrl-model/#relation: "target: indicates that the Asset is the primary subject to which the Rule action directly applies."
- §2.3.1 Function Property, https://www.w3.org/TR/odrl-model/#function: "assignee: indicates that the Party that is the recipient the of Rule. For example, the Party being granted a Permission or required to fulfil an agreed Duty." The garbled "the recipient the of Rule" is in the original.
- §2.4 Action Class, https://www.w3.org/TR/odrl-model/#action: "An Action class indicates an operation that can be exercised on an Asset. An Action is associated with the Asset via the action property in a Rule."
- §2.1 Policy Class, https://www.w3.org/TR/odrl-model/#policy: "A Policy MUST have one uid property value (of type IRI [rfc3987]) to identify the Policy."

### DPV

**Data Privacy Vocabulary (DPV) version 2.3**, *Final Community Group Report, 25 February 2026*.
This version: https://www.w3.org/community/reports/dpvcg/CG-FINAL-dpv-20260225/.
https://w3id.org/dpv redirects to https://w3c-cg.github.io/dpv/2.3/dpv/. Full definitions come
from the module pages (`/modules/legal_basis`, `/modules/rights`, `/modules/entities`), all of
the same version and date.

The rights concepts are now in the core `dpv:` namespace. The old
`https://w3id.org/dpv/rights` URL returned HTTP **404** (it redirected to
https://w3c-cg.github.io/dpv/rights).

Namespace (https://w3id.org/dpv, §Introduction):
> The namespace for DPV terms is https://w3id.org/dpv#, the suggested prefix is dpv

| Term | IRI | Definition (verbatim) | Usage note (verbatim) | Source |
|---|---|---|---|---|
| dpv:ConsentWithdrawn | `https://w3id.org/dpv#ConsentWithdrawn` | "The state where the consent is withdrawn or revoked specifically by the data subject and which prevents it from being further used as a valid state" | "This state can be considered a form of 'revocation' of consent, where the revocation can only be performed by the data subject. Therefore we suggest using ConsentRevoked when it is a non-data-subject entity, and ConsentWithdrawn when it is the data subject" | legal_basis §9.1.20, https://w3id.org/dpv/modules/legal_basis#ConsentWithdrawn (parent: dpv:ConsentStatusInvalidForProcessing) |
| dpv:ConsentRevoked | `https://w3id.org/dpv#ConsentRevoked` | "The state where the consent is revoked by an entity other than the data subject and which prevents it from being further used as a valid state" | "An example of this state is when a Data Controller stops utilising previously obtaining consent, such as when that service no longer exists" | legal_basis §9.1.15, https://w3id.org/dpv/modules/legal_basis#ConsentRevoked |
| dpv:WithdrawConsent | `https://w3id.org/dpv#WithdrawConsent` | "Control for withdrawing consent" | "Indicates how the data subject can withdraw consent e.g. used with dpv:isExercisedAt" | legal_basis §9.1.147, https://w3id.org/dpv/modules/legal_basis#WithdrawConsent |
| dpv:Consent | `https://w3id.org/dpv#Consent` | "Consent of the Data Subject for specified process or activity" | none | legal_basis §9.1.7, https://w3id.org/dpv/modules/legal_basis#Consent (added 2026-09-29 for P7 notice v2) |
| dpv:hasConsentStatus | `https://w3id.org/dpv#hasConsentStatus` | "Specifies the state or status of consent" | none | legal_basis §9.2.2, https://w3id.org/dpv/modules/legal_basis#hasConsentStatus |
| dpv:RightExerciseNotice | `https://w3id.org/dpv#RightExerciseNotice` | "Information associated with exercising of an active right such as where and how to exercise the right, information required for it, or updates on an exercised rights request" | "This concept is intended for providing information regarding a right exercise. For specific instances of such exercises, see RightExerciseActivity and RightExerciseRecord." | rights §5.1.6, https://w3id.org/dpv/modules/rights#RightExerciseNotice |
| dpv:RightExerciseActivity | `https://w3id.org/dpv#RightExerciseActivity` | "An activity representing an exercising of an active right" | "There may be multiple activities associated with exercising and fulfilling rights. See the RightExerciseRecord concept for record-keeping of such activities in a cohesive manner." | rights §5.1.5, https://w3id.org/dpv/modules/rights#RightExerciseActivity |
| dpv:RightExerciseRecord | `https://w3id.org/dpv#RightExerciseRecord` | "Record of a Right being exercised" | "This concept represents a record of one or more right exercise activities, such as those associated with a single data subject or service or entity" | rights §5.1.7, https://w3id.org/dpv/modules/rights#RightExerciseRecord |
| dpv:hasDataSubject | `https://w3id.org/dpv#hasDataSubject` | "Indicates association with Data Subject" | none | entities §6.2.9, https://w3id.org/dpv/modules/entities#hasDataSubject |
| dpv:hasRecipient | `https://w3id.org/dpv#hasRecipient` | "Indicates Recipient of Data" | "Also used to indicate the Recipient of a Right Exercise Activity" | entities §6.2.15, https://w3id.org/dpv/modules/entities#hasRecipient |

The DPV definitions have no terminal full stop on the page. They are quoted as shown.

Re-fetched live on 2026-09-29 for P7 notice v2 (`curl -L`: https://w3id.org/dpv → 200
https://w3c-cg.github.io/dpv/2.3/dpv/; https://w3id.org/dpv/modules/legal_basis → 200, same version and
date). `dpv:ConsentWithdrawn`, `dpv:ConsentRevoked` and `dpv:hasConsentStatus` read exactly as quoted above.

---

## 11. Community Solid Server v7.2.0: source excerpts

- `git ls-remote https://github.com/CommunitySolidServer/CommunitySolidServer refs/tags/v7.2.0 'refs/tags/v7.2.0^{}'` returned
  **`b4fe28370bc297308fdf9329b6eb7901dde5395f  refs/tags/v7.2.0`**. It is a lightweight tag, so
  no `^{}` line was returned, and the hash is the commit.
- Shallow clone (session scratch, not committed), detached HEAD at b4fe2837. `package.json` line 3 is `"version": "7.2.0"`.
- The thesis config `@css:config/file.json` imports `css:config/ldp/authorization/webacl.json`
  (line 19) and `css:config/http/notifications/all.json` (line 9). `all.json` enables WebSocket,
  Webhook and StreamingHTTP channels.

All excerpts below come from reading the code. None of them were tested at runtime.

### (a) WAC and ACP readers read the access document on every request

`src/authorization/WebAclReader.ts`:
- Lines 67–72, in `handle`, run on each call: `const aclMap = await this.getAclMatches(...)`, then `const storeMap = await this.findAuthorizationStatements(aclMap);`.
- Line 159–161: `const acl = this.aclStrategy.getAuxiliaryIdentifier(identifier);` then `if (await this.resourceSet.hasResource(acl)) {`.
- Line 195: `const data = await this.aclStore.getRepresentation(aclIdentifier, { type: { [INTERNAL_QUADS]: 1 }});`.

The only caches on this path are WeakMaps keyed by object identity. The keys are objects
created during the request, so the caches do not carry permissions across requests:
- `src/storage/CachedResourceSet.ts` L5: `* Caches resource existence in a \`WeakMap\` tied to the \`ResourceIdentifier\` object.`
- `src/http/auxiliary/SuffixAuxiliaryIdentifierStrategy.ts` L19–20 creates a new object on every call: `return { path: \`${identifier.path}${this.suffix}\` };`.
- `config/ldp/authorization/readers/default.json` L8–11, the PermissionReader: `"comment": "Caches permissions based on credentials and requested modes. …"`, `"@type": "CachedHandler"`, `"fields": [ "credentials", "requestedModes" ]`.
- `src/util/handlers/CachedHandler.ts` L10: `* A {@link WeakMap} is used internally so strict object equality determines cache hits,`.
- `config/ldp/authentication/dpop-bearer.json` L5–7: `"comment": "Caches the credentials based on the incoming request."`, `"@type": "CachedHandler"`.

`src/authorization/AcpReader.ts`:
- L38: `* Caches data so no duplicate calls are made to the {@link ResourceStore} for a single request.`
- L56: `const resourceCache = new IdentifierMap<IAccessControlledResource[]>();`. The cache is created inside `handle`, so it is new for every request.
- L149: `({ data } = await this.acrStore.getRepresentation(acrIdentifier, { type: { [INTERNAL_QUADS]: 1 }}));`.

### (b) NotificationSubscriber: `maxDuration` default and authorization at subscribe

`src/server/notifications/NotificationSubscriber.ts`:
- L46–49: `* Overrides the expiration feature of channels, by making sure they always expire after the \`maxDuration\` value.` … `* Value is set in minutes. 0 is infinite.` `* Defaults to 20160 minutes, which is 2 weeks.`
- L80: `this.maxDuration = (args.maxDuration ?? 20160) * 60 * 1000;`
- L111–116 clamp `channel.endAt = Date.now() + this.maxDuration;`.
- L118–122: `// Verify if the client is allowed to subscribe` / `await this.authorize(credentials, channel);` / `// Store the channel once it has been authorized` / `await this.storage.add(channel);`
- L139–148: `authorize()` calls `this.channelType.extractModes(channel)`, then `permissionReader.handleSafe`, then `authorizer.handleSafe`.
- `src/server/notifications/BaseChannelType.ts` L290–291: `extractModes` requires only `AccessMode.read` on `channel.topic`.

A grep of `config/` found no `maxDuration` override, so the default applies. The subscriber's
identity is not stored on the channel. `BaseChannelType.ts` L150–151 reads
`// eslint-disable-next-line unused-imports/no-unused-vars` above
`public async initChannel(data: Store, credentials: Credentials)`, and the channel object built
at L230–234 has only `id`, `type` and `topic`, plus features.

### (c) WebSocket2023Listener: no authentication or authorization when connecting to `receiveFrom`

`src/server/notifications/WebSocketChannel2023/WebSocket2023Listener.ts`:
- L27–33, `canHandle`, only looks the channel up: `const channel = await this.storage.get(id);` then `if (!channel) { throw new NotImplementedHttpError(\`Unknown or expired WebSocket channel ${id}\`); }`.
- L36–42, `handle`, accepts and passes on: `this.logger.info(\`Accepted WebSocket connection listening to changes on ${channel.topic}\`);`.
- It has no credentials extractor, permission reader or authorizer.

The URL is the capability:
- `BaseChannelType.ts` L231: `id: joinUrl(this.path, randomUUID()),`.
- `WebSocketChannel2023Type.ts` L46: `receiveFrom: generateWebSocketUrl(channel.id),`.
- `WebSocket2023Util.ts` L10: `return \`ws${id.slice('http'.length)}\`;`.

Expiry of open sockets (`WebSocket2023Storer.ts`):
- L13–16: `* \`cleanupTimer\` defines in minutes how often the stored WebSockets are closed` `* if their corresponding channel has expired.` `* Defaults to 60 minutes.` `* Open WebSockets will not receive notifications if their channel expired.`
- L51–60, `closeExpiredSockets`: `socket.send(\`Notification channel has expired\`); socket.close();`.

Expiry itself is checked lazily. `KeyValueChannelStorage.ts` L31:
`if (typeof channel.endAt === 'number' && channel.endAt < Date.now()) {` deletes the channel and returns undefined.

### (d) Notification emission: permissions are not re-checked

`src/server/notifications/ListeningActivityHandler.ts` L39–75, `emit()`:
- `const channelIds = await this.storage.getAll(topic);`
- For each channel, it skips if expired (`if (!channel) { // Notification channel has expired continue; }`), if rate-limited (L54), or if before `startAt` (L59).
- Otherwise it runs `this.handler.handleSafe({ channel, activity, topic, metadata })`.

`ComposedNotificationHandler.ts` L39–50 runs generate, then a state check, then serialize, then `emitter.handleSafe`.

A grep of `src/server/notifications` for `permission|authoriz|credentials` finds matches only in
`NotificationSubscriber.ts`, `StreamingHttpRequestHandler.ts` (authorizes once at connect,
L46–48: `// Verify if the client is allowed to connect` / `await this.authorize(credentials, topic);`),
the `initChannel` signatures, and `WebhookEmitter.ts` (its own outgoing DPoP header). The emit
path contains no permission check.

### (e) NotificationUnsubscriber: DELETE with no authorization check, returns 205

`src/server/notifications/NotificationUnsubscriber.ts` L23–32:
```ts
public async handle({ operation }: OperationHttpHandlerInput): Promise<ResponseDescription> {
  const id = operation.target.path;
  const existed = await this.storage.delete(id);
  if (!existed) {
    throw new NotFoundHttpError();
  }
  ...
  return new ResetResponseDescription();
```
- `src/http/output/response/ResetResponseDescription.ts` L4: `* Corresponds to a 205 response.`, and L8 `super(205);`.
- It is wired in `config/http/notifications/base/http.json` L46–55 (`"comment": "Handles deleting notification channels."`, `"allowedMethods": [ "DELETE" ]`, `"@type": "NotificationUnsubscriber"`) under the route `"allowedPathNames": [ "^/.notifications/" ]` (L9).
- No credentials extractor or authorizer is injected. Anyone who knows the channel id (a UUID URL) can delete the channel. An unknown id gives 404.

### (f) Cache-Control

`grep -rni 'cache-control|cacheControl|no-store|max-age' src config templates` has exactly
**one** hit: `src/server/middleware/StaticAssetHandler.ts` L218, `'cache-control': \`max-age=${this.expires}\`,`
(L213–220 `getCacheHeaders()`). `config/http/static/default.json` L8 sets
`"options_expires": 86400,`. That applies only to static assets (favicon,
`/.well-known/css/styles/`, fonts, images), not to LDP resources.

For LDP resources, CSS sends no Cache-Control. It does send a constant `Vary` header:
`config/http/middleware/handlers/constant-headers.json` L10–11, `"Vary"` /
`"Accept,Authorization,Origin"`.

### (g) The WAC-Allow writer is wired for WAC only

- `src/server/WacAllowHttpHandler.ts` L65–93 runs for HEAD/GET (`// WAC-Allow is only needed for HEAD/GET requests`). It re-reads permissions (`await this.permissionReader.handleSafe({ credentials, requestedModes })`) and public permissions (`credentials: {}`), then adds metadata.
- It is always in the chain: `config/ldp/handler/default.json` L27.
- The header itself is written by `src/http/output/metadata/WacAllowMetadataWriter.ts` L32, `addHeader(input.response, 'WAC-Allow', headerStrings.join(','));`.
- That writer is registered only in `config/ldp/authorization/acl/wac-allow.json`, which is imported only by `config/ldp/authorization/webacl.json` (L4, L23–28 `"comment": "WAC-Allow header indicates available permissions."`).
- `config/ldp/authorization/acp.json` does not import it. So under ACP, CSS 7.2.0 emits no WAC-Allow header; this is read from the config and was not tested.
- The writer's docstring (L10–12) cites an older wording, "Solid, §10.1: "Servers exposing client’s access privileges on a resource URL MUST advertise by including the WAC-Allow HTTP header…"". That wording is not the current TR text.

### (h) CSS does not end channels when ACLs change

- `grep -rln -i acl src/server/notifications` matches only `BaseChannelType.ts`, and those matches are "SHACL", not ACLs.
- Channels are deleted only in `KeyValueChannelStorage.ts`, through `deleteChannel` (expiry: L31–36, L84) and `NotificationUnsubscriber.ts` L26.
- Nothing listens for ACL or ACR changes in order to revoke channels.

### (i) How WebhookChannel2023 notifications are authenticated

`src/server/notifications/WebhookChannel2023/WebhookEmitter.ts`:
- L62–64: `// Currently the spec does not define how the notification sender should identify.` / `// The format used here has been chosen to be similar` / `// to how ID tokens are described in the Solid-OIDC specification for consistency.`
- L65–78: `new SignJWT({ webid: this.webId, azp: this.webId, sub: this.webId, cnf: { jkt: keyThumbprint } })…setAudience([ this.webId, 'solid' ]).setIssuer(this.issuer)`. The token expires after 20 minutes by default (L23–24).
- L81–84: DPoP proof `{ htu: webhookChannel.sendTo, htm: 'POST' }` with `typ: 'dpop+jwt'`.
- L90–97: `fetch(webhookChannel.sendTo, { method: 'POST', headers: { … authorization: \`DPoP ${dpopToken}\`, dpop: dpopProof } …})`.

On the WebID route:
- `WebhookWebId.ts` L12: `* Generates a fixed WebID that we use to identify the server for notifications sent using a WebhookChannel2023.`
- L22–23: `<> solid:oidcIssuer <${trimTrailingSlashes(baseUrl)}>.`
- Path: `/.notifications/` (`base/description.json` L28), plus `WebhookChannel2023/` (`webhooks/routes.json` L8), plus `webId` (L14). The WebID is therefore `<baseUrl>/.notifications/WebhookChannel2023/webId`.

`WebhookChannel2023Type.ts` L54 validates `sendTo` only with `minCount: 1, maxCount: 1`. I found
no https-scheme check there, even though the spec requires one.

### (j) No listing endpoint for subscriptions or channels

- `NotificationChannelStorage.getAll(topic)` (`NotificationChannelStorage.ts` L19–25) is called only by `ListeningActivityHandler.ts` L44. That is internal; no HTTP handler exposes it.
- The notification routes accept HEAD, GET or POST on the per-type subscription endpoints (`base/http.json` L32; GET returns the channel type description, `NotificationSubscriber.ts` L84–90) and DELETE on channel ids.
- An owner therefore has no endpoint in CSS 7.2.0 to list the channels open on their resource.
- Channels are stored in the internal key-value storage under `/notifications/` (`base/storage.json`, `"relativePath": "/notifications/"`).

---

## Retrieval failures and caveats

1. **`https://w3id.org/dpv/rights`** returned **HTTP 404** (it redirected to https://w3c-cg.github.io/dpv/rights). In DPV 2.3 the rights concepts are in the `dpv:` namespace, retrieved from `https://w3id.org/dpv/modules/rights` (200). A separate "dpv-rights" namespace was not retrieved.
2. **WebFetch was not used.** Every source was fetched as raw HTML or text with `curl`, which is stricter than a summarised fetch.
3. **Computed section numbers.** For the Solid Protocol and WAC TR pages the numbers are computed (see the header note). Cite by anchor if in doubt.
4. **Webhook page date.** WebhookChannel2023 shows a render date of "4 August 2026". This is the Bikeshed build date, not a publication date.
5. **Not re-fetched.** The Solid-OIDC spec and the legacy WebSocket API were not re-fetched. They are out of scope.
6. **No EUR-Lex text** was involved.
