// P4 driver: Comunica link traversal (@comunica/query-sparql-link-traversal-solid 0.8.0)
// acting as appR. Driven by ch3/phases/p4_comunica/run.py over stdin/stdout, one JSON
// object per line, so the Python harness writes everything into the run's JSONL.
//
// Commands:  {"id", "cmd": "new", "engine"}                    create a QueryEngine
//            {"id", "cmd": "query", "engine", "query", "sources"}
//            {"id", "cmd": "invalidate", "engine"}            engine.invalidateHttpCache()
//            {"id", "cmd": "exit"}
// Output:    {"event": "http", "op", ...} for every HTTP request Comunica makes,
//            {"event": "reply", "id", "ok", ...} once per command.
//
// Authentication: Solid-OIDC client credentials with DPoP (ES256), written here with
// `jose`. No @inrupt library is used (Comunica installs one transitively; it is not
// wired in). Credentials come from the environment and are never printed.

import { createHash, randomUUID } from 'node:crypto';
import { createInterface } from 'node:readline';
import { QueryEngine } from '@comunica/query-sparql-link-traversal-solid';
import { SignJWT, exportJWK, generateKeyPair } from 'jose';

const ISSUER = process.env.CH3_ISSUER.replace(/\/$/, '');
const CLIENT_ID = process.env.CH3_CLIENT_ID;
const CLIENT_SECRET = process.env.CH3_CLIENT_SECRET;

const out = (obj) => process.stdout.write(`${JSON.stringify({ ts: new Date().toISOString(), ...obj })}\n`);

const { privateKey, publicKey } = await generateKeyPair('ES256');
const jwk = await exportJWK(publicKey);
const b64url = (buf) => Buffer.from(buf).toString('base64url');

async function proof(url, method, accessToken) {
  const u = new URL(url);
  u.search = '';
  u.hash = '';
  const payload = { htu: u.toString(), htm: method.toUpperCase(), jti: randomUUID(), iat: Math.floor(Date.now() / 1000) };
  if (accessToken) payload.ath = b64url(createHash('sha256').update(accessToken).digest());
  return new SignJWT(payload).setProtectedHeader({ alg: 'ES256', typ: 'dpop+jwt', jwk }).sign(privateKey);
}

let token;
async function accessToken() {
  if (token && token.exp - 60 > Date.now() / 1000) return token.value;
  const config = await (await fetch(`${ISSUER}/.well-known/openid-configuration`)).json();
  const basic = Buffer.from(`${encodeURIComponent(CLIENT_ID)}:${encodeURIComponent(CLIENT_SECRET)}`).toString('base64');
  const res = await fetch(config.token_endpoint, {
    method: 'POST',
    headers: { authorization: `Basic ${basic}`, 'content-type': 'application/x-www-form-urlencoded',
      dpop: await proof(config.token_endpoint, 'POST') },
    body: 'grant_type=client_credentials&scope=webid',
  });
  if (!res.ok) throw new Error(`token request failed: HTTP ${res.status}`);
  const body = await res.json();
  const claims = JSON.parse(Buffer.from(body.access_token.split('.')[1], 'base64url').toString());
  token = { value: body.access_token, exp: claims.exp };
  return token.value;
}

let currentOp = null;
async function authFetch(input, init = {}) {
  const url = typeof input === 'string' ? input : input.url ?? String(input);
  const method = (init.method ?? input.method ?? 'GET').toUpperCase();
  const headers = new Headers(init.headers ?? input.headers ?? {});
  const at = await accessToken();
  headers.set('authorization', `DPoP ${at}`);
  headers.set('dpop', await proof(url, method, at));
  const started = Date.now();
  const res = await fetch(url, { ...init, method, headers });
  out({ event: 'http', op: currentOp, method, url, status: res.status, ms: Date.now() - started,
    content_type: res.headers.get('content-type'), wac_allow: res.headers.get('wac-allow') });
  return res;
}

const engines = new Map();

async function handle(msg) {
  currentOp = msg.id;
  switch (msg.cmd) {
    case 'new':
      engines.set(msg.engine, new QueryEngine());
      return { engine: msg.engine };
    case 'invalidate':
      await engines.get(msg.engine).invalidateHttpCache();
      return { engine: msg.engine };
    case 'query': {
      const engine = engines.get(msg.engine);
      const stream = await engine.queryBindings(msg.query, { sources: msg.sources, fetch: authFetch });
      const rows = (await stream.toArray()).map((b) => Object.fromEntries([...b].map(([k, v]) => [k.value, v.value])));
      return { engine: msg.engine, rows };
    }
    case 'exit':
      setImmediate(() => process.exit(0));
      return {};
    default:
      throw new Error(`unknown command ${msg.cmd}`);
  }
}

const rl = createInterface({ input: process.stdin });
for await (const line of rl) {
  if (!line.trim()) continue;
  const msg = JSON.parse(line);
  try {
    out({ event: 'reply', id: msg.id, ok: true, ...(await handle(msg)) });
  } catch (error) {
    out({ event: 'reply', id: msg.id, ok: false, error: String(error?.message ?? error), error_name: error?.name });
  }
}
