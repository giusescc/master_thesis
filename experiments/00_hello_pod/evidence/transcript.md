# Evidence transcript -- 00_hello_pod

Every HTTP exchange performed by this experiment, in order.
Authorization and DPoP headers are redacted; they are secrets.

## 1. Alice: PUT http://localhost:3000/alice/private-note.ttl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/private-note.ttl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 2. Alice: GET http://localhost:3000/alice/private-note.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/private-note.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fprivate-note.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/private-note.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640711233-text/turtle"`

## 3. Bob: GET http://localhost:3000/alice/private-note.ttl

- **Status:** `403`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3000/alice/private-note.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/private-note.ttl.acl>; rel="acl"`

## 4. anonymous: GET http://localhost:3000/alice/private-note.ttl

- **Status:** `401`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3000/alice/private-note.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/private-note.ttl.acl>; rel="acl"`
- **WWW-Authenticate:** `Bearer scope="openid webid"`

## 5. anonymous: GET http://localhost:3000/alice/

- **Status:** `200`
- **WAC-Allow:** `user="read",public="read"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/pim/space#Storage>; rel="type", <http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640711233-text/turtle"`

## 6. Alice: DELETE http://localhost:3000/alice/private-note.ttl

- **Status:** `205`

