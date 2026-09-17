# Evidence transcript -- 02_odrl_consent

Every HTTP exchange performed by this experiment, in order.
Authorization and DPoP headers are redacted; they are secrets.

## 1. Alice: PUT http://localhost:3000/alice/research-dataset.ttl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/research-dataset.ttl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 2. Alice: HEAD http://localhost:3000/alice/research-dataset.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101038-text/turtle"`

## 3. Alice: PUT http://localhost:3000/alice/research-dataset.ttl.acl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/research-dataset.ttl.acl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 4. Alice: HEAD http://localhost:3000/alice/research-dataset.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101038-text/turtle"`

## 5. Alice: PATCH http://localhost:3000/alice/research-dataset.ttl.meta

- **Status:** `205`

## 6. Alice: HEAD http://localhost:3000/alice/research-dataset.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101060-text/turtle"`

## 7. Alice: GET http://localhost:3000/alice/research-dataset.ttl.meta

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <urn:npm:solid:community-server:meta:DescriptionResource>; rel="type", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl.meta>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`

## 8. Alice: PUT http://localhost:3000/alice/research-dataset.ttl.meta

*PUT to a description resource*

- **Status:** `405`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 9. Bob: GET http://localhost:3000/alice/research-dataset.ttl

*Bob reads while an ODRL Permission is in force*

- **Status:** `200`
- **WAC-Allow:** `user="read"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101060-text/turtle"`

## 10. Alice: PATCH http://localhost:3000/alice/research-dataset.ttl.meta

- **Status:** `205`

## 11. Bob: GET http://localhost:3000/alice/research-dataset.ttl

*Bob reads while an ODRL PROHIBITION forbids it*

- **Status:** `200`
- **WAC-Allow:** `user="read"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101093-text/turtle"`

## 12. Bob: PUT http://localhost:3000/bob/redistributed-dataset.ttl

*Bob redistributes despite odrl:Prohibition on odrl:distribute*

- **Status:** `201`
- **Location:** `http://localhost:3000/bob/redistributed-dataset.ttl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 13. Bob: HEAD http://localhost:3000/alice/research-dataset.ttl

- **Status:** `200`
- **WAC-Allow:** `user="read"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101093-text/turtle"`

## 14. Bob: GET http://localhost:3000/alice/research-dataset.ttl.meta

- **Status:** `200`
- **WAC-Allow:** `user="read"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <urn:npm:solid:community-server:meta:DescriptionResource>; rel="type", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl.meta>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`

## 15. Bob: GET http://localhost:3000/alice/research-dataset.ttl

*A non-cooperating client makes the same request*

- **Status:** `200`
- **WAC-Allow:** `user="read"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101093-text/turtle"`

## 16. Bob: GET http://localhost:3000/alice/research-dataset.ttl

*Bob declares a DPV purpose that CONTRADICTS the policy constraint*

- **Status:** `200`
- **WAC-Allow:** `user="read"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101093-text/turtle"`

## 17. Alice: HEAD http://localhost:3000/alice/research-dataset.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101093-text/turtle"`

## 18. Alice: GET http://localhost:3000/alice/research-dataset.ttl.meta

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <urn:npm:solid:community-server:meta:DescriptionResource>; rel="type", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl.meta>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`

## 19. Alice: PUT http://localhost:3000/alice/research-dataset.ttl

*Alice makes an ORDINARY data update*

- **Status:** `205`

## 20. Alice: HEAD http://localhost:3000/alice/research-dataset.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101137-text/turtle"`

## 21. Alice: GET http://localhost:3000/alice/research-dataset.ttl.meta

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <urn:npm:solid:community-server:meta:DescriptionResource>; rel="type", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl.meta>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`

## 22. Alice: PATCH http://localhost:3000/alice/research-dataset.ttl.meta

- **Status:** `205`

## 23. Alice: HEAD http://localhost:3000/alice/research-dataset.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101150-text/turtle"`

## 24. Alice: PUT http://localhost:3000/alice/research-dataset.ttl

- **Status:** `205`

## 25. Alice: HEAD http://localhost:3000/alice/research-dataset.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/research-dataset.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/research-dataset.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640101159-text/turtle"`

## 26. Alice: GET http://localhost:3000/alice/research-dataset.ttl.meta

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <urn:npm:solid:community-server:meta:DescriptionResource>; rel="type", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fresearch-dataset.ttl.meta>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`

## 27. Alice: DELETE http://localhost:3000/alice/research-dataset.ttl

*cleanup*

- **Status:** `205`

## 28. Bob: DELETE http://localhost:3000/bob/redistributed-dataset.ttl

*cleanup*

- **Status:** `205`

