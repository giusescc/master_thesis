# Evidence transcript -- 03_portability

Every HTTP exchange performed by this experiment, in order.
Authorization and DPoP headers are redacted; they are secrets.

## 1. Alice@A: GET http://localhost:3000/alice/thesis-lab/

- **Status:** `404`
- **Allow:** `PUT`
- **Content-Type:** `text/turtle`
- **Link:** `<http://localhost:3000/alice/thesis-lab/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/.acl>; rel="acl"`

## 2. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/

- **Status:** `404`
- **Allow:** `PUT`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3000/alice/thesis-lab/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/.acl>; rel="acl"`

## 3. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/

- **Status:** `404`
- **Allow:** `PUT`
- **Content-Type:** `text/turtle`
- **Link:** `<http://localhost:3001/alice2/migrated-verbatim/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/.acl>; rel="acl"`

## 4. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/

- **Status:** `404`
- **Allow:** `PUT`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3001/alice2/migrated-verbatim/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/.acl>; rel="acl"`

## 5. Alice2@B: GET http://localhost:3001/alice2/migrated-rewritten/

- **Status:** `404`
- **Allow:** `PUT`
- **Content-Type:** `text/turtle`
- **Link:** `<http://localhost:3001/alice2/migrated-rewritten/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-rewritten/.acl>; rel="acl"`

## 6. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/

- **Status:** `404`
- **Allow:** `PUT`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3001/alice2/migrated-rewritten/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-rewritten/.acl>; rel="acl"`

## 7. Alice2@B: DELETE http://localhost:3001/alice2/sameas-test.ttl

- **Status:** `403`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3001/alice2/sameas-test.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/sameas-test.ttl.acl>; rel="acl"`

## 8. Alice@A: PUT http://localhost:3000/alice/thesis-lab/

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 9. Alice@A: PUT http://localhost:3000/alice/thesis-lab/contacts/

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/contacts/`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 10. Alice@A: PUT http://localhost:3000/alice/thesis-lab/notes/

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/notes/`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 11. Alice@A: PUT http://localhost:3000/alice/thesis-lab/media/

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/media/`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 12. Alice@A: PUT http://localhost:3000/alice/thesis-lab/profile.ttl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/profile.ttl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 13. Alice@A: PUT http://localhost:3000/alice/thesis-lab/contacts/carol.ttl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/contacts/carol.ttl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 14. Alice@A: PUT http://localhost:3000/alice/thesis-lab/contacts/dave.ttl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/contacts/dave.ttl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 15. Alice@A: PUT http://localhost:3000/alice/thesis-lab/notes/note-1.ttl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/notes/note-1.ttl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 16. Alice@A: PUT http://localhost:3000/alice/thesis-lab/notes/note-2.ttl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/notes/note-2.ttl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 17. Alice@A: PUT http://localhost:3000/alice/thesis-lab/media/portrait.ttl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/media/portrait.ttl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 18. Alice@A: PUT http://localhost:3000/alice/thesis-lab/media/portrait.png

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/media/portrait.png`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 19. Alice@A: HEAD http://localhost:3000/alice/thesis-lab/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731695-text/turtle"`

## 20. Alice@A: PUT http://localhost:3000/alice/thesis-lab/.acl

- **Status:** `201`
- **Location:** `http://localhost:3000/alice/thesis-lab/.acl`
- **Link:** `<http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 21. Alice@A: GET http://localhost:3000/alice/thesis-lab/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731761-text/turtle"`

## 22. Alice@A: GET http://localhost:3000/alice/thesis-lab/notes/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/notes/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fnotes%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/notes/.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731729-text/turtle"`

## 23. Alice@A: GET http://localhost:3000/alice/thesis-lab/media/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/media/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fmedia%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/media/.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731744-text/turtle"`

## 24. Alice@A: GET http://localhost:3000/alice/thesis-lab/contacts/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/contacts/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fcontacts%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/contacts/.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731710-text/turtle"`

## 25. Alice@A: GET http://localhost:3000/alice/thesis-lab/contacts/carol.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/contacts/carol.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fcontacts%2Fcarol.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/contacts/carol.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731703-text/turtle"`

## 26. Alice@A: GET http://localhost:3000/alice/thesis-lab/contacts/dave.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/contacts/dave.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fcontacts%2Fdave.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/contacts/dave.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731710-text/turtle"`

## 27. Alice@A: GET http://localhost:3000/alice/thesis-lab/media/portrait.png

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `image/png`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/media/portrait.png.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fmedia%2Fportrait.png>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/media/portrait.png.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731745-image/png"`

## 28. Alice@A: GET http://localhost:3000/alice/thesis-lab/media/portrait.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/media/portrait.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fmedia%2Fportrait.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/media/portrait.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731736-text/turtle"`

## 29. Alice@A: GET http://localhost:3000/alice/thesis-lab/notes/note-1.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/notes/note-1.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fnotes%2Fnote-1.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/notes/note-1.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731717-text/turtle"`

## 30. Alice@A: GET http://localhost:3000/alice/thesis-lab/notes/note-2.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/notes/note-2.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fnotes%2Fnote-2.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/notes/note-2.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731729-text/turtle"`

## 31. Alice@A: GET http://localhost:3000/alice/thesis-lab/profile.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/profile.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fprofile.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/profile.ttl.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731695-text/turtle"`

## 32. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 33. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/contacts/

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/contacts/`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 34. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/contacts/carol.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/contacts/carol.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 35. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/contacts/dave.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/contacts/dave.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 36. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/media/

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/media/`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 37. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/media/portrait.png

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/media/portrait.png`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 38. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/media/portrait.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/media/portrait.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 39. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/notes/

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/notes/`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 40. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 41. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/notes/note-2.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/notes/note-2.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 42. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/profile.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/profile.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 43. Alice2@B: PUT http://localhost:3001/alice2/migrated-rewritten/

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-rewritten/`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 44. Alice2@B: PUT http://localhost:3001/alice2/migrated-rewritten/contacts/

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-rewritten/contacts/`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 45. Alice2@B: PUT http://localhost:3001/alice2/migrated-rewritten/contacts/carol.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-rewritten/contacts/carol.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 46. Alice2@B: PUT http://localhost:3001/alice2/migrated-rewritten/contacts/dave.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-rewritten/contacts/dave.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 47. Alice2@B: PUT http://localhost:3001/alice2/migrated-rewritten/media/

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-rewritten/media/`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 48. Alice2@B: PUT http://localhost:3001/alice2/migrated-rewritten/media/portrait.png

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-rewritten/media/portrait.png`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 49. Alice2@B: PUT http://localhost:3001/alice2/migrated-rewritten/media/portrait.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-rewritten/media/portrait.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 50. Alice2@B: PUT http://localhost:3001/alice2/migrated-rewritten/notes/

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-rewritten/notes/`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 51. Alice2@B: PUT http://localhost:3001/alice2/migrated-rewritten/notes/note-1.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-rewritten/notes/note-1.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 52. Alice2@B: PUT http://localhost:3001/alice2/migrated-rewritten/notes/note-2.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-rewritten/notes/note-2.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 53. Alice2@B: PUT http://localhost:3001/alice2/migrated-rewritten/profile.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-rewritten/profile.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 54. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/contacts/carol.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/contacts/carol.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fcontacts%2Fcarol.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/contacts/carol.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731870-text/turtle"`

## 55. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/contacts/dave.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/contacts/dave.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fcontacts%2Fdave.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/contacts/dave.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731877-text/turtle"`

## 56. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/media/portrait.png

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `image/png`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/media/portrait.png.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fmedia%2Fportrait.png>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/media/portrait.png.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731889-image/png"`

## 57. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/media/portrait.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/media/portrait.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fmedia%2Fportrait.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/media/portrait.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731896-text/turtle"`

## 58. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fnotes%2Fnote-1.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731906-text/turtle"`

## 59. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/notes/note-2.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/notes/note-2.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fnotes%2Fnote-2.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/notes/note-2.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731913-text/turtle"`

## 60. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/profile.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/profile.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fprofile.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/profile.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731920-text/turtle"`

## 61. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/media/portrait.png

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `image/png`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/media/portrait.png.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fmedia%2Fportrait.png>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/media/portrait.png.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731889-image/png"`

## 62. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/media/portrait.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/media/portrait.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fmedia%2Fportrait.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/media/portrait.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731896-text/turtle"`

## 63. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fnotes%2Fnote-1.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731906-text/turtle"`

## 64. Alice2@B: GET http://localhost:3001/alice2/migrated-rewritten/notes/note-1.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-rewritten/notes/note-1.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-rewritten%2Fnotes%2Fnote-1.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-rewritten/notes/note-1.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731973-text/turtle"`

## 65. Alice2@B: GET http://localhost:3001/alice2/migrated-rewritten/contacts/carol.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-rewritten/contacts/carol.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-rewritten%2Fcontacts%2Fcarol.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-rewritten/contacts/carol.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731937-text/turtle"`

## 66. Alice2@B: HEAD http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fnotes%2Fnote-1.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731906-text/turtle"`

## 67. Alice2@B: PUT http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.acl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.acl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 68. Bob@A: GET http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl

*Bob (WebID hosted by provider A) reads on provider B*

- **Status:** `200`
- **WAC-Allow:** `user="read"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fnotes%2Fnote-1.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731906-text/turtle"`

## 69. Alice2@B: HEAD http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fnotes%2Fnote-1.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731906-text/turtle"`

## 70. Alice2@B: PATCH http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.meta

- **Status:** `205`

## 71. Alice2@B: HEAD http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fnotes%2Fnote-1.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640732132-text/turtle"`

## 72. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.meta

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <urn:npm:solid:community-server:meta:DescriptionResource>; rel="type", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fnotes%2Fnote-1.ttl.meta>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`

## 73. Bob@A: GET http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl

*Bob reads on provider B despite an odrl:Prohibition*

- **Status:** `200`
- **WAC-Allow:** `user="read"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fnotes%2Fnote-1.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640732132-text/turtle"`

## 74. Alice2@B: PATCH http://localhost:3001/alice2/profile/card

*Alice2 declares owl:sameAs her old WebID*

- **Status:** `205`

## 75. Alice2@B: PUT http://localhost:3001/alice2/sameas-test.ttl

- **Status:** `403`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3001/alice2/sameas-test.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/sameas-test.ttl.acl>; rel="acl"`

## 76. Alice2@B: HEAD http://localhost:3001/alice2/sameas-test.ttl

- **Status:** `403`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3001/alice2/sameas-test.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/sameas-test.ttl.acl>; rel="acl"`

## 77. Alice2@B: PUT http://localhost:3001/alice2/sameas-test.ttl.acl

- **Status:** `205`

## 78. Alice2@B: GET http://localhost:3001/alice2/sameas-test.ttl

*New identity tries to use a grant made to the OLD WebID*

- **Status:** `403`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3001/alice2/sameas-test.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/sameas-test.ttl.acl>; rel="acl"`

## 79. Alice2@B: PUT http://localhost:3001/alice2/independent-probe.ttl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/independent-probe.ttl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 80. Alice2@B: HEAD http://localhost:3001/alice2/independent-probe.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/independent-probe.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Findependent-probe.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/independent-probe.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640732479-text/turtle"`

## 81. Alice2@B: PUT http://localhost:3001/alice2/independent-probe.ttl.acl

- **Status:** `201`
- **Location:** `http://localhost:3001/alice2/independent-probe.ttl.acl`
- **Link:** `<http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023"`

## 82. Alice-independent: GET http://localhost:3001/alice2/independent-probe.ttl

*Independent WebID reads on provider B*

- **Status:** `200`
- **WAC-Allow:** `user="read"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/independent-probe.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Findependent-probe.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/independent-probe.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640732479-text/turtle"`

## 83. Alice@A: GET http://localhost:3000/alice/thesis-lab/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731761-text/turtle"`

## 84. Alice@A: GET http://localhost:3000/alice/thesis-lab/notes/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/notes/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fnotes%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/notes/.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731729-text/turtle"`

## 85. Alice@A: GET http://localhost:3000/alice/thesis-lab/media/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/media/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fmedia%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/media/.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731744-text/turtle"`

## 86. Alice@A: GET http://localhost:3000/alice/thesis-lab/contacts/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3000/alice/thesis-lab/contacts/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3000%2Falice%2Fthesis-lab%2Fcontacts%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/contacts/.acl>; rel="acl", <http://localhost:3000/alice/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731710-text/turtle"`

## 87. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/contacts/carol.ttl

- **Status:** `205`

## 88. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/media/portrait.png

- **Status:** `205`

## 89. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/media/portrait.ttl

- **Status:** `205`

## 90. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/contacts/dave.ttl

- **Status:** `205`

## 91. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/notes/note-1.ttl

- **Status:** `205`

## 92. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/notes/note-2.ttl

- **Status:** `205`

## 93. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/contacts/

- **Status:** `205`

## 94. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/media/

- **Status:** `205`

## 95. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/notes/

- **Status:** `205`

## 96. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/profile.ttl

- **Status:** `205`

## 97. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/

- **Status:** `205`

## 98. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fnotes%2Fnote-1.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640732132-text/turtle"`

## 99. Alice@A: GET http://localhost:3000/alice/thesis-lab/contacts/carol.ttl

*The owner asks for the same deleted resource*

- **Status:** `404`
- **Allow:** `PATCH, PUT`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3000/alice/thesis-lab/contacts/carol.ttl.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/contacts/carol.ttl.acl>; rel="acl"`

## 100. Alice2@B: GET http://localhost:3001/alice2/migrated-rewritten/contacts/carol.ttl

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-rewritten/contacts/carol.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-rewritten%2Fcontacts%2Fcarol.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-rewritten/contacts/carol.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731937-text/turtle"`

## 101. Alice-independent: GET http://localhost:3001/alice2/independent-probe.ttl

- **Status:** `200`
- **WAC-Allow:** `user="read"`
- **Allow:** `OPTIONS, HEAD, GET, PATCH, PUT, DELETE`
- **Accept-Patch:** `text/n3, application/sparql-update`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/independent-probe.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Findependent-probe.ttl>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/independent-probe.ttl.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640732479-text/turtle"`

## 102. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731919-text/turtle"`

## 103. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/notes/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/notes/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fnotes%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/notes/.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640732132-text/turtle"`

## 104. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/media/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/media/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fmedia%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/media/.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731895-text/turtle"`

## 105. Alice2@B: GET http://localhost:3001/alice2/migrated-verbatim/contacts/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-verbatim/contacts/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-verbatim%2Fcontacts%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-verbatim/contacts/.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731877-text/turtle"`

## 106. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/contacts/carol.ttl

- **Status:** `205`

## 107. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/media/portrait.png

- **Status:** `205`

## 108. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/media/portrait.ttl

- **Status:** `205`

## 109. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/contacts/dave.ttl

- **Status:** `205`

## 110. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/notes/note-1.ttl

- **Status:** `205`

## 111. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/notes/note-2.ttl

- **Status:** `205`

## 112. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/contacts/

- **Status:** `205`

## 113. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/media/

- **Status:** `205`

## 114. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/notes/

- **Status:** `205`

## 115. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/profile.ttl

- **Status:** `205`

## 116. Alice2@B: DELETE http://localhost:3001/alice2/migrated-verbatim/

- **Status:** `205`

## 117. Alice2@B: GET http://localhost:3001/alice2/migrated-rewritten/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-rewritten/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-rewritten%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-rewritten/.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731985-text/turtle"`

## 118. Alice2@B: GET http://localhost:3001/alice2/migrated-rewritten/notes/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-rewritten/notes/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-rewritten%2Fnotes%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-rewritten/notes/.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731980-text/turtle"`

## 119. Alice2@B: GET http://localhost:3001/alice2/migrated-rewritten/media/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-rewritten/media/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-rewritten%2Fmedia%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-rewritten/media/.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731961-text/turtle"`

## 120. Alice2@B: GET http://localhost:3001/alice2/migrated-rewritten/contacts/

- **Status:** `200`
- **WAC-Allow:** `user="append control read write"`
- **Allow:** `OPTIONS, HEAD, GET, POST`
- **Content-Type:** `text/turtle`
- **Link:** `<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://localhost:3001/alice2/migrated-rewritten/contacts/.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/http%3A%2F%2Flocalhost%3A3001%2Falice2%2Fmigrated-rewritten%2Fcontacts%2F>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/migrated-rewritten/contacts/.acl>; rel="acl", <http://localhost:3001/alice2/.well-known/solid>; rel="http://www.w3.org/ns/solid/terms#storageDescription"`
- **ETag:** `"1789640731944-text/turtle"`

## 121. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/contacts/carol.ttl

- **Status:** `205`

## 122. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/media/portrait.png

- **Status:** `205`

## 123. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/media/portrait.ttl

- **Status:** `205`

## 124. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/contacts/dave.ttl

- **Status:** `205`

## 125. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/notes/note-1.ttl

- **Status:** `205`

## 126. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/notes/note-2.ttl

- **Status:** `205`

## 127. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/contacts/

- **Status:** `205`

## 128. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/media/

- **Status:** `205`

## 129. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/notes/

- **Status:** `205`

## 130. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/profile.ttl

- **Status:** `205`

## 131. Alice2@B: DELETE http://localhost:3001/alice2/migrated-rewritten/

- **Status:** `205`

## 132. Alice2@B: DELETE http://localhost:3001/alice2/sameas-test.ttl

- **Status:** `403`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3001/alice2/sameas-test.ttl.meta>; rel="describedby", <http://localhost:3001/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3001/alice2/sameas-test.ttl.acl>; rel="acl"`

## 133. Alice2@B: DELETE http://localhost:3001/alice2/independent-probe.ttl

- **Status:** `205`

## 134. Alice@A: GET http://localhost:3000/alice/thesis-lab/

- **Status:** `404`
- **Allow:** `PUT`
- **Content-Type:** `text/turtle`
- **Link:** `<http://localhost:3000/alice/thesis-lab/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/.acl>; rel="acl"`

## 135. Alice@A: DELETE http://localhost:3000/alice/thesis-lab/

- **Status:** `404`
- **Allow:** `PUT`
- **Content-Type:** `application/json`
- **Link:** `<http://localhost:3000/alice/thesis-lab/.meta>; rel="describedby", <http://localhost:3000/.notifications/StreamingHTTPChannel2023/b0>; rel="http://www.w3.org/ns/solid/terms#updatesViaStreamingHttp2023", <http://localhost:3000/alice/thesis-lab/.acl>; rel="acl"`

