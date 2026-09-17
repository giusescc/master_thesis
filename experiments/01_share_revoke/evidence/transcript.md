# Evidence transcript -- 01_share_revoke

Every HTTP exchange performed by this experiment, in order.
Authorization and DPoP headers are redacted; they are secrets.

## 1. Alice: PUT http://localhost:3000/alice/shared-note.ttl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/shared-note.ttl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 2. Alice: HEAD http://localhost:3000/alice/shared-note.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/shared-note.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fshared-note.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/shared-note.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640711385-text/turtle"`

## 3. Alice: PUT http://localhost:3000/alice/shared-note.ttl.acl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/shared-note.ttl.acl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 4. Bob: GET http://localhost:3000/alice/shared-note.ttl

*Bob reads while the grant is in force*

- **Status:** `200`
- **WAC-Allow:** `user="read"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/shared-note.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fshared-note.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/shared-note.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640711385-text/turtle"`

## 5. Bob: PUT http://localhost:3000/bob/copy-of-alices-note.ttl

*Bob copies into his own pod*

- **Status:** `201`
- **Location:** `http://localhost:3000/bob/copy-of-alices-note.ttl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 6. Alice: HEAD http://localhost:3000/alice/shared-note.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/shared-note.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fshared-note.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/shared-note.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640711385-text/turtle"`

## 7. Alice: PUT http://localhost:3000/alice/shared-note.ttl.acl

- **Status:** `205`

## 8. Bob: GET http://localhost:3000/alice/shared-note.ttl

*Bob retries with his ORIGINAL unexpired token*

- **Status:** `403`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3000/alice/shared-note.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/shared-note.ttl.acl>; rel="acl"`

## 9. Bob: GET http://localhost:3000/alice/shared-note.ttl

*Bob retries with a freshly issued token*

- **Status:** `403`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3000/alice/shared-note.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/shared-note.ttl.acl>; rel="acl"`

## 10. Bob: GET http://localhost:3000/bob/copy-of-alices-note.ttl

*Bob reads his own copy after revocation*

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/bob/copy-of-alices-note.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Fbob%2Fcopy-of-alices-note.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/bob/copy-of-alices-note.ttl.acl>; rel="acl", <http://localhost:3000/bob/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640711434-text/turtle"`

## 11. Alice: GET http://localhost:3000/bob/copy-of-alices-note.ttl

*Alice attempts to READ Bob's copy*

- **Status:** `403`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3000/bob/copy-of-alices-note.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/bob/copy-of-alices-note.ttl.acl>; rel="acl"`

## 12. Alice: DELETE http://localhost:3000/bob/copy-of-alices-note.ttl

*Alice attempts to DELETE Bob's copy*

- **Status:** `403`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3000/bob/copy-of-alices-note.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/bob/copy-of-alices-note.ttl.acl>; rel="acl"`

## 13. Alice: DELETE http://localhost:3000/alice/shared-note.ttl

*cleanup*

- **Status:** `205`

## 14. Bob: DELETE http://localhost:3000/bob/copy-of-alices-note.ttl

*cleanup*

- **Status:** `205`

