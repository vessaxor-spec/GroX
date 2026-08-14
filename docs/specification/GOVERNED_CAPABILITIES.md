# GroX Governed Capability Expansion

A5 broadens the Vessel's operational reach without turning tools, adapters, services, or external systems into command authorities.

## Command boundary

The command spine remains:

**Commander → Pilot GorXu → Divisions → Standing Crew**

Mission Control remains a GroX-native policy/advisory service under GorXu. Tool Gateway v2, workspace isolation, network policy, browser capture, the secret broker, and MCP adapters are capabilities. They are not command layers and do not issue Mission Orders.

Every A5 tool invocation must remain attributable to one existing Mission Order. Capability never implies permission.

## Deny-wins authorization

A5 uses the existing Mission Order instead of creating a second capability contract.

A privileged action is permitted only when all applicable gates agree:

1. Commander intent and Pilot-owned Mission remain unchanged;
2. the selected Crew dossier contains the required capability;
3. the graph node declares the capability in `required_capabilities`;
4. the Mission Order explicitly grants the tool action in `allowed_actions`;
5. the action is not explicitly forbidden;
6. Mission mode permits the side-effect class;
7. host policy enables the capability;
8. resource, path, origin, secret, and adapter-specific grants permit the exact operation;
9. evidence is returned to the Mission Store;
10. verification remains independent when required.

A model, Crew member, tool result, fetched page, MCP server, or browser page cannot add its own grant.

## Tool Gateway v2

The Tool Gateway remains the single execution boundary for Crew tools. A5 adds governed paths without exposing raw host handles to Crew.

New explicit actions are:

- `workspace_exec`;
- `secret_use`;
- `net_fetch`;
- `browser_capture`;
- `mcp_call`;
- `mcp_mutate` as a separately gated mutation class.

Graph nodes may request only recognized explicit actions. Each explicit action must have a matching required Crew capability before an Order can be issued.

Host policy is source-controlled in `configs/tool-policy.json` where safe defaults are static. Runtime-specific origins, secret values, and MCP process definitions are injected privately and are not persisted to public Git.

## Isolated shell/code workspace

`workspace_exec` does not run a Crew command in the Vessel root.

The Tool Gateway selects one qualified host isolation backend and fails closed when neither is available.

**Namespace backend, preferred when supported:**

- a user namespace;
- a PID namespace;
- a network namespace;
- a chroot containing only a minimal shell and its runtime libraries;
- a private `/work` directory;
- CPU, address-space, file-size, and file-descriptor limits enforced with `prlimit`;
- an external timeout owned by the Tool Gateway.

**Docker backend, host-governed fallback:**

- a host-policy image pinned by digest and pre-provisioned before the Mission;
- `network=none`;
- all Linux capabilities dropped;
- `no-new-privileges`;
- read-only container root;
- PID, memory, CPU, file-size, and file-descriptor limits;
- only the A5-private ephemeral `/work` directory bind-mounted writable;
- no implicit image pull during Crew execution;
- container removal and workspace deletion after the tour.

Both backends deny normal host filesystem access and host networking. Mission evidence identifies the selected backend and retains only bounded stdout/stderr, isolation metadata, output file paths, sizes, and hashes.

If the host cannot provide either qualified backend, the capability is denied rather than downgraded to an unrestricted shell.

## Secret broker

The A5 secret broker is memory-only.

Mission Orders contain secret aliases, never secret values. A Crew member may receive a secret only when:

- `secret_use` is explicitly granted;
- the requested alias appears in the Order's `secret_grants`;
- the private broker currently holds that alias.

For the qualified workspace path, values become only selected shell environment variables. Secret-bearing exports are delivered over the isolated shell's stdin rather than command argv, host process environment, or Docker `Config.Env`. Known secret values are redacted from captured stdout/stderr. Normal workspace teardown removes files created during the tour, preventing the workspace from becoming a durable secret store.

Secret values are not written to Mission Orders, evidence records, Crew memory, or public source by the broker.

## Network/origin policy

`net_fetch` is read-only HTTP(S) GET in A5.

Network access requires two independent grants:

1. the origin must exist in host policy;
2. the same exact normalized origin must be granted by the Mission Order.

Current controls:

- schemes are limited to HTTP and HTTPS;
- credentials embedded in URLs are denied;
- origin comparison is exact by scheme, hostname, and non-default port;
- redirects are not followed;
- response size and timeout are bounded;
- response bodies are evidence marked as untrusted content.

An Order cannot widen host origin policy.

## Browser evidence capture

The browser does not receive independent network authority.

`browser_capture` first retrieves the approved HTML through the same `net_fetch` origin gate. GroX then renders that captured HTML offline in real Chromium/Chrome through Playwright. Browser-originated HTTP(S) requests are aborted.

Where the host supports the full A5 namespace set, the browser worker also runs inside user, PID, and network namespaces. Where user namespaces are blocked but the process is non-root, GroX instead requires Chromium's native sandbox and adds deny-at-resolution and dead-proxy controls. A root host without the outer namespace boundary is denied. This keeps network authority in the Gateway rather than silently falling back to an unsandboxed root browser.

Evidence includes:

- approved source origin and response hash;
- rendered-document hash;
- screenshot path, size, and SHA-256;
- selected browser isolation controls and Chromium sandbox mode;
- blocked origins observed during rendering.

Browser evidence lives under the private `configs/state/browser/` path and is excluded from source control.

This A5 path qualifies bounded browser rendering and evidence capture. It does not grant an unrestricted interactive desktop or arbitrary browser automation surface.

## MCP-compatible adapters

A5 supports pre-registered stdio MCP adapters using JSON-RPC initialization, tool discovery, and tool invocation.

Crew cannot supply adapter process commands. Host/Pilot configuration supplies a registry containing:

- adapter name;
- process argv;
- allowed tool names;
- tools classified as mutating where applicable.

The Mission Order must separately grant the adapter/tool pair in `mcp_grants`. A tool classified as mutating additionally requires `mcp_mutate` and an execution/repair mode that permits mutation.

The A5 qualification uses a read-only local stdio adapter. Networked MCP transports and arbitrary third-party adapter processes are not implicitly qualified by this gate.

## External-agent boundary

A2A-compatible external-agent delegation remains optional in A5 and is not implemented merely to satisfy a checklist. Any future external-agent adapter must remain below GorXu, receive bounded delegated authority, and return attributable evidence. External intelligence does not inherit GroX authority.

## Untrusted external content

Fetched content, rendered pages, and MCP results are data. They are not instructions to GorXu or Crew unless the Commander or Pilot separately incorporates a bounded claim into a Mission Order.

A5 evidence explicitly marks external content as untrusted where applicable.

## A5 qualification gate

A5 is qualified only when a real controlled multi-tool Mission proves all of the following on a fresh host path:

1. an eligible Crew member executes a shell tour inside a qualified namespace/chroot or Docker isolation boundary with network denial and resource limits;
2. an ephemeral secret alias is injected without its value appearing in durable Mission evidence;
3. an exact host-and-Order-approved origin is fetched while an unapproved origin is denied;
4. approved HTML is rendered by real headless Chromium/Chrome with browser networking disabled and screenshot/hash evidence captured;
5. a pre-registered read-only MCP tool is discovered and called through the stdio adapter;
6. each privileged action is present in the corresponding Mission Order and backed by Crew capability;
7. a mutating MCP tool is denied without the separate mutation grant;
8. all side effects are confined to approved private state or explicitly classified external calls;
9. an independent verifier closes the multi-tool Mission from evidence;
10. all A1-A4 authority, persistence, recovery, memory, routing, Repair, and verification tests remain green.

**Exit gate:** Standing Crew complete a real multi-tool Mission while every privileged action remains attributable to Commander intent, a Pilot-owned Mission Order, eligible Crew capability, host policy, evidence, and independent verification.
