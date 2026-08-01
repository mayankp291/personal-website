<script>
  import { onMount } from 'svelte';
  /**
   * @typedef {{id: string, label: string, detail: string, description: string, meta: string[][], links: string[], statusKey?: string}} ArchNode
   * @typedef {{id: string, name: string, tag: string, num: string, description: string, nodes: ArchNode[]}} ArchZone
   */
  const zones = [
    {
      id: 'public',
      name: 'Public internet',
      tag: 'untrusted',
      num: 'ZONE 01',
      description: 'The untrusted side. Anyone can reach the site, so this boundary assumes hostile traffic and gives attackers nothing to attach to.',
      nodes: [
        { id: 'browser', label: 'Visitor browser', detail: 'Request origin', description: 'Any client on the internet. Requests are ordinary HTTPS with no secrets at the edge; the public surface is assumed hostile and stays behind Cloudflare.', meta: [['protocol', 'HTTPS'], ['port', '443'], ['tls', 'TLS 1.3']], links: ['dns'] }
      ]
    },
    {
      id: 'edge',
      name: 'Cloudflare edge',
      tag: 'managed',
      num: 'ZONE 02',
      description: 'Cloudflare owns DNS, TLS, CDN caching, and the Pages frontend. api.mayankp.me enters a tunnel here; no homelab IP is ever published.',
      nodes: [
        { id: 'dns', label: 'DNS + TLS', detail: 'Edge termination', description: 'A-proxied DNS records for mayankp.me and api.mayankp.me. Cloudflare terminates TLS and manages certificates automatically, so the site never serves its own certs.', meta: [['records', 'A · proxied'], ['tls', 'Cloudflare-managed'], ['cache', 'CDN global']], links: ['browser', 'pages', 'tunnel'] },
        { id: 'pages', label: 'Cloudflare Pages', detail: 'SvelteKit static', description: 'The SvelteKit build is prerendered to static assets and deployed by GitHub Actions. Pages serves from the CDN with no homelab origin — the portfolio stays online even when the lab is down.', meta: [['deploy', 'GitHub Actions'], ['build', 'adapter-static'], ['origin', 'none']], links: ['dns'] },
        { id: 'tunnel', label: 'Tunnel edge', detail: 'api.mayankp.me', description: 'A named tunnel maps api.mayankp.me to the cloudflared daemon in the homelab. The edge holds the connection; the homelab never needs a public IP or router rules.', meta: [['hostname', 'api.mayankp.me'], ['transport', 'QUIC outbound'], ['route', 'tunnel → daemon']], links: ['dns', 'cloudflared'] }
      ]
    },
    {
      id: 'lab',
      name: 'Homelab host',
      tag: 'trusted · 169.42.0.189',
      num: 'ZONE 03',
      description: 'The physical host at 169.42.0.189. Its only listener is the tunnel daemon on loopback; the home router has no inbound forwards.',
      nodes: [
        { id: 'cloudflared', label: 'cloudflared', detail: 'Tunnel daemon', description: 'Runs as a root-managed systemd service on the host. It opens the outbound tunnel and forwards decrypted requests to the API container on the loopback interface.', meta: [['service', 'cloudflared.service (root)'], ['listen', '127.0.0.1:8000'], ['direction', 'outbound only']], links: ['tunnel', 'api'] }
      ]
    },
    {
      id: 'runtime',
      name: 'Podman runtime',
      tag: 'rootless · quadlet',
      num: 'ZONE 04',
      description: 'Rootless Podman containers driven by Quadlet user units. Data persists in named volumes; containers are disposable.',
      nodes: [
        { id: 'podnet', label: 'Podman network', detail: 'Private bridge', description: 'The rootless Podman network that connects containers to each other. Containers resolve each other by name over a private bridge — only the API\'s loopback port is published.', meta: [['driver', 'bridge'], ['dns', 'built-in'], ['publish', 'loopback only']], links: ['api', 'postgres', 'immich'] },
        { id: 'api', label: 'FastAPI', detail: 'Status + content API', description: 'FastAPI under uvicorn serving the public endpoints. Status answers come from an in-memory cache refreshed by the sampler; CORS is locked to the site\'s own origins.', statusKey: 'website-api', meta: [['stack', 'uvicorn · FastAPI'], ['cache', '15s TTL'], ['cors', 'site origins only']], links: ['podnet', 'sampler', 'sqlite', 'postgres', 'immich'] },
        { id: 'sampler', label: 'Status sampler', detail: 'Every 30 seconds', description: 'A background asyncio task collects health samples every 30 seconds: HTTP probes for Immich, TCP connect for PostgreSQL, and implicit availability for the API itself.', meta: [['cadence', 'every 30s'], ['writes', 'SQLite'], ['runtime', 'asyncio task']], links: ['api', 'sqlite'] },
        { id: 'sqlite', label: 'SQLite', detail: 'Uptime history', description: 'Uptime history lives in a SQLite database at /data/status.db, mounted from the personal-website-status volume so it survives container rebuilds.', meta: [['path', '/data/status.db'], ['volume', 'personal-website-status'], ['format', 'service_checks']], links: ['api', 'sampler'] },
        { id: 'postgres', label: 'PostgreSQL 17', detail: 'Persistent data', description: 'PostgreSQL 17 used today as the connectivity target for health checks; it will become the persistence layer for content. Never exposed beyond the private network.', statusKey: 'postgresql', meta: [['version', '17'], ['probe', 'TCP :5432'], ['reach', 'network-internal']], links: ['api', 'podnet'] },
        { id: 'immich', label: 'Immich', detail: 'Photo library', description: 'Self-hosted photo library, reachable only inside the homelab network. The dashboard learns about it through a sanitized ping — never through application URLs.', statusKey: 'immich', meta: [['probe', 'GET /api/server/ping'], ['reach', 'network-internal'], ['status', 'sanitized']], links: ['api', 'podnet'] }
      ]
    }
  ];

  const nodeById = Object.fromEntries(zones.flatMap((zone) => zone.nodes.map((node) => [node.id, node])));

  const connectors = [
    { label: 'HTTPS · TLS 1.3 · DNS proxied' },
    { label: 'Outbound QUIC tunnel · no inbound ports' },
    { label: 'Published loopback · 127.0.0.1:8000' }
  ];

  const traces = {
    page: ['browser', 'dns', 'pages'],
    api: ['browser', 'dns', 'tunnel', 'cloudflared', 'api', 'sqlite']
  };

  let selected = $state(zones[0].nodes[0]);
  /** @type {string | null} */
  let hover = $state(null);
  /** @type {'page' | 'api' | null} */
  let trace = $state(null);
  /** @type {ArchZone | null} */
  let focusZone = $state(null);
  /** @type {Array<{id: string, name: string, status: string, latency_ms: number | null, detail: string}>} */
  let statuses = $state([]);

  /** @param {string} nodeId */
  function pathPos(nodeId) {
    if (!trace) return -1;
    return traces[trace].indexOf(nodeId);
  }

  /** @param {string} nodeId */
  function nodeIndex(nodeId) {
    return zones.flatMap((zone) => zone.nodes).findIndex((node) => node.id === nodeId) + 1;
  }

  /** @param {ArchNode} node */
  function zoneName(node) {
    return zones.find((zone) => zone.nodes.some((candidate) => candidate.id === node.id))?.name ?? '';
  }

  /** @param {number} zoneIndex */
  function zoneCrossDelay(zoneIndex) {
    if (!trace) return 0;
    let max = -1;
    for (let z = 0; z <= zoneIndex; z += 1) {
      for (const node of zones[z].nodes) {
        const position = traces[trace].indexOf(node.id);
        if (position > max) max = position;
      }
    }
    return max < 0 ? 0 : (max + 1) * 0.3;
  }

  /** @param {ArchNode} node */
  function statusFor(node) {
    if (!node.statusKey) return null;
    return statuses.find((service) => service.id === node.statusKey) ?? null;
  }

  /** @param {ArchNode} node */
  function nodeDotClass(node) {
    if (!node.statusKey) return 'live-dot';
    const status = statusFor(node);
    if (!status) return 'live-dot';
    return status.status === 'operational' ? 'live-dot live-ok' : 'live-dot live-bad';
  }

  async function fetchStatus() {
    try {
      const response = await fetch('https://api.mayankp.me/api/v1/homelab/status');
      if (!response.ok) throw new Error(`status ${response.status}`);
      statuses = (await response.json()).services;
    } catch {
      statuses = [];
    }
  }

  onMount(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  });
</script>

<svelte:head>
  <title>Homelab Architecture · Mayank Panjiyara</title>
  <meta name="description" content="Interactive architecture of Mayank's self-hosted homelab platform." />
</svelte:head>

<main class="subpage architecture-page wrap">
  <a class="back-link" href="/lab">← Back to SRE lab</a>
  <span class="eyebrow">SRE lab / 002</span>
  <h1>A small system,<br /><em>deliberately drawn.</em></h1>
  <p class="subpage-intro">A map of how this website moves from a public request to private services, and where the boundaries are designed to hold.</p>

  <section class="diagram" aria-label="Interactive homelab architecture" class:trace-page={trace === 'page'}>
    <div class="diagram-toolbar">
      <span class="eyebrow">Network topology / {zones.flatMap((zone) => zone.nodes).length} nodes · {zones.length} zones</span>
      <div class="toolbar-right">
        <span class="legend"><i class="legend-dot legend-ok"></i>probed live<i class="legend-dot"></i>static layer</span>
        <div class="trace-buttons" role="group" aria-label="Request trace controls">
          <button class:trace-btn-active={trace === 'page'} class="trace-btn trace-page-btn" onclick={() => trace = trace === 'page' ? null : 'page'} aria-pressed={trace === 'page'}>Trace: page request</button>
          <button class:trace-btn-active={trace === 'api'} class="trace-btn" onclick={() => trace = trace === 'api' ? null : 'api'} aria-pressed={trace === 'api'}>Trace: API request</button>
        </div>
      </div>
    </div>

    {#key trace}
      {#each zones as zone, zoneIndex}
        <div class:zone-dim={focusZone && focusZone.id !== zone.id} class:zone-alt={zone.id === 'edge' || zone.id === 'lab'} class="zone">
          <button class:zone-head-active={focusZone?.id === zone.id} class="zone-head" onclick={() => focusZone = focusZone?.id === zone.id ? null : zone} aria-pressed={focusZone?.id === zone.id}>
            <span class="zone-num">{zone.num} / {zone.tag}</span>
            <span class="zone-name">{zone.name}</span>
          </button>
          <div class="zone-body">
            {#each zone.nodes as node, index}
              {@const position = pathPos(node.id)}
              <button class:node-active={selected.id === node.id} class:node-dim={hover && hover !== node.id && !nodeById[hover].links.includes(node.id)} class:node-linked={hover && nodeById[hover].links.includes(node.id) && hover !== node.id} class:trace-node={position >= 0} class="node" onclick={() => { selected = node; focusZone = null; }} onmouseenter={() => hover = node.id} onmouseleave={() => hover = null} aria-pressed={selected.id === node.id} style={position >= 0 ? `--i:${position * 0.3}s` : ''}>
                <span class="node-top"><span class="node-num">0{nodeIndex(node.id)}</span><i class={nodeDotClass(node)}></i></span>
                <strong>{node.label}</strong>
                <small>{node.detail}</small>
              </button>
            {/each}
          </div>
        </div>
        {#if zoneIndex < zones.length - 1}
          <div class="connector" class:trace-on={trace && traces[trace].some((id) => zones[zoneIndex + 1].nodes.some((node) => node.id === id))}>
            <span>{connectors[zoneIndex].label}</span>
            <i class="connector-dot" style="--d:{zoneCrossDelay(zoneIndex)}s"></i>
          </div>
        {/if}
      {/each}
    {/key}

    <div class="node-detail">
      {#if focusZone}
        <div>
          <span class="eyebrow">Selected zone / {focusZone.id}</span>
          <h2>{focusZone.name}</h2>
          <p>{focusZone.description}</p>
        </div>
        <div class="detail-side">
          <div class="detail-stat"><span>members</span><strong>{focusZone.nodes.length}</strong></div>
          <div class="detail-stat"><span>boundary</span><strong>{focusZone.tag}</strong></div>
          <div class="detail-conns">{#each focusZone.nodes as node}<span class="conn-chip">{node.label}</span>{/each}</div>
        </div>
      {:else}
        <div>
          <span class="eyebrow">Selected layer / {selected.id}</span>
          <h2>{selected.label}</h2>
          <p>{selected.description}</p>
          <div class="detail-conns"><span class="conn-label">connections</span>{#each selected.links as link}<span class="conn-chip">{nodeById[link].label}</span>{/each}</div>
        </div>
        <div class="detail-side">
          <div class="meta-table">{#each selected.meta as [key, value]}<div><span>{key}</span><strong>{value}</strong></div>{/each}</div>
          <div class="detail-status">
            {#if selected.statusKey}
              <i class={nodeDotClass(selected)}></i>
              {@const status = statusFor(selected)}
              {#if status}
                <span>{status.name} · {status.status}{status.latency_ms === null ? '' : ` · ${status.latency_ms}ms`}</span>
              {:else}
                <span class="detail-offline">probe pending — no live sample yet</span>
              {/if}
            {:else}
              <i class="live-dot"></i>
              <span class="detail-offline">static layer · not probed</span>
            {/if}
          </div>
          <div class="detail-zone"><span>zone</span><strong>{zoneName(selected)}</strong></div>
        </div>
      {/if}
    </div>
  </section>

  <section class="boundary-notes"><div class="section-heading"><span class="eyebrow">Operating principles</span><span class="section-count">Designed boundaries</span></div><div class="boundary-grid"><article><strong>01</strong><h2>Public by choice</h2><p>The frontend is public. Backend health is deliberately reduced to a small, sanitized contract.</p></article><article><strong>02</strong><h2>Private by default</h2><p>Immich and homelab services stay on the private network; the dashboard does not become an application gateway.</p></article><article><strong>03</strong><h2>Recoverable</h2><p>Services are independently managed by systemd, with persistent data isolated from disposable containers.</p></article></div></section>
</main>

<style>
  .architecture-page h1 { margin-bottom: 35px; }
  .diagram { background: #111820; border: 1px solid var(--line); margin-top: 75px; padding: 28px; }
  .diagram-toolbar { align-items: center; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; padding-bottom: 16px; }
  .toolbar-right { align-items: center; display: flex; gap: 22px; }
  .legend { color: var(--muted); font-family: 'DM Mono'; font-size: .56rem; display: flex; align-items: center; gap: 7px; }
  .legend-dot { background: #4a5560; border-radius: 50%; display: inline-block; height: 7px; width: 7px; }
  .legend-ok { background: var(--acid); }
  .trace-buttons { display: flex; gap: 8px; }
  .trace-btn { background: transparent; border: 1px solid #3b4851; color: var(--muted); cursor: pointer; font-family: 'DM Mono'; font-size: .58rem; padding: 9px 12px; text-transform: uppercase; }
  .trace-btn:hover { border-color: var(--blue); color: #d9e1e6; }
  .trace-page-btn:hover { border-color: var(--acid); }
  .trace-btn-active { border-color: var(--acid); color: var(--acid); }
  .trace-page .trace-btn-active { border-color: var(--blue); color: var(--blue); }
  .zone { border: 1px solid #3b4851; margin-top: 18px; transition: opacity .2s; }
  .zone-dim { opacity: .18; }
  .zone-head { align-items: center; background: transparent; border: 0; color: #d9e1e6; cursor: pointer; display: flex; font: inherit; justify-content: space-between; padding: 13px 16px; width: 100%; }
  .zone-head:hover, .zone-head-active { background: #19242c; }
  .zone-num { color: var(--acid); font-family: 'DM Mono'; font-size: .58rem; letter-spacing: .06em; }
  .zone-alt .zone-num { color: var(--blue); }
  .zone-name { font-family: 'Space Grotesk'; font-size: 1.05rem; font-weight: 500; }
  .zone-body { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); padding: 16px; }
  .node { background: transparent; border: 1px solid #3b4851; color: #d9e1e6; cursor: pointer; display: grid; gap: 6px; padding: 16px; position: relative; text-align: left; transition: border-color .15s, background .15s, opacity .15s; }
  .node:hover, .node-active { background: #19242c; border-color: var(--acid); }
  .node-top { align-items: center; display: flex; justify-content: space-between; }
  .node-num { color: var(--acid); font-family: 'DM Mono'; font-size: .56rem; }
  .node strong { font-family: 'Space Grotesk'; font-size: .95rem; font-weight: 500; }
  .node small { color: var(--muted); font-family: 'DM Mono'; font-size: .55rem; }
  .node-dim { opacity: .22; }
  .node-linked { border-color: #5a6b75; }
  .live-dot { background: #4a5560; border-radius: 50%; height: 8px; width: 8px; }
  .live-ok { background: var(--acid); }
  .live-bad { background: #f0bd55; }
  .trace-node { animation: node-pulse 1.2s ease-out var(--i, 0s) both; border-color: var(--acid); }
  .trace-page .trace-node { animation-name: node-pulse-blue; border-color: var(--blue); }
  @keyframes node-pulse { 0% { box-shadow: 0 0 0 0 rgba(215, 255, 104, .45); } 100% { box-shadow: 0 0 0 16px rgba(215, 255, 104, 0); } }
  @keyframes node-pulse-blue { 0% { box-shadow: 0 0 0 0 rgba(131, 184, 255, .45); } 100% { box-shadow: 0 0 0 16px rgba(131, 184, 255, 0); } }
  .connector { align-items: center; color: var(--muted); display: flex; font-family: 'DM Mono'; font-size: .56rem; height: 46px; justify-content: center; position: relative; text-transform: uppercase; }
  .connector::before { border-top: 1px dashed #3b4851; content: ''; left: 4%; position: absolute; right: 4%; top: 50%; }
  .connector span { background: #111820; padding: 0 12px; position: relative; z-index: 1; }
  .connector-dot { background: var(--acid); border-radius: 50%; height: 7px; left: calc(50% - 3.5px); opacity: 0; position: absolute; top: -5px; width: 7px; z-index: 2; }
  .trace-page .connector-dot { background: var(--blue); }
  .connector.trace-on .connector-dot { animation: dot-down 1.2s linear var(--d, 0s) both; }
  @keyframes dot-down { 0% { opacity: 0; top: -5px; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { opacity: 0; top: calc(100% + 5px); } }
  .node-detail { border-top: 1px solid var(--line); display: grid; gap: 40px; grid-template-columns: 1fr 300px; margin-top: 30px; padding-top: 28px; }
  .node-detail h2 { font-size: 2.2rem; margin: 18px 0 10px; }
  .node-detail p { color: var(--muted); line-height: 1.7; margin: 0; max-width: 640px; }
  .detail-side { border-left: 1px solid var(--line); padding-left: 28px; }
  .meta-table { display: grid; gap: 11px; }
  .meta-table div { align-items: baseline; display: flex; font-family: 'DM Mono'; font-size: .6rem; justify-content: space-between; }
  .meta-table span { color: var(--muted); text-transform: uppercase; }
  .meta-table strong { color: #b2bdc4; font-weight: 400; text-align: right; }
  .detail-status { align-items: center; border-top: 1px solid var(--line); display: flex; font-family: 'DM Mono'; font-size: .62rem; gap: 9px; margin-top: 22px; padding-top: 16px; }
  .detail-status .live-dot { margin: 0; }
  .detail-offline { color: var(--muted); }
  .detail-zone { border-top: 1px solid var(--line); display: flex; font-family: 'DM Mono'; font-size: .6rem; justify-content: space-between; margin-top: 14px; padding-top: 14px; }
  .detail-zone span { color: var(--muted); text-transform: uppercase; }
  .detail-zone strong { color: var(--acid); font-weight: 400; }
  .detail-conns { align-items: center; display: flex; flex-wrap: wrap; gap: 7px; margin-top: 24px; }
  .conn-label { color: var(--muted); font-family: 'DM Mono'; font-size: .58rem; margin-right: 4px; text-transform: uppercase; }
  .conn-chip { border: 1px solid var(--line); color: #b2bdc4; font-family: 'DM Mono'; font-size: .56rem; padding: 6px 8px; }
  .detail-stat { display: flex; font-family: 'DM Mono'; font-size: .6rem; justify-content: space-between; margin-bottom: 9px; }
  .detail-stat span { color: var(--muted); text-transform: uppercase; }
  .detail-stat strong { color: var(--acid); font-weight: 400; }
  .boundary-notes { padding: 110px 0 40px; }
  .boundary-grid { display: grid; gap: 15px; grid-template-columns: repeat(3, 1fr); padding-top: 25px; }
  .boundary-grid article { border-top: 1px solid var(--line); padding: 20px 0; }
  .boundary-grid strong { color: var(--acid); font-family: 'DM Mono'; font-size: .65rem; }
  .boundary-grid h2 { font-size: 1.45rem; margin: 30px 0 12px; }
  .boundary-grid p { color: var(--muted); font-size: .85rem; line-height: 1.65; margin: 0; }
  @media (max-width: 700px) { .diagram { padding: 18px; }.diagram-toolbar { align-items: start; flex-direction: column; gap: 14px; }.toolbar-right { align-items: start; flex-direction: column; gap: 12px; }.zone-body { grid-template-columns: 1fr; }.zone-head { gap: 10px; }.node-detail { gap: 25px; grid-template-columns: 1fr; }.detail-side { border-left: 0; border-top: 1px solid var(--line); padding: 22px 0 0; }.boundary-grid { grid-template-columns: 1fr; }.boundary-notes { padding-top: 80px; } }
</style>
