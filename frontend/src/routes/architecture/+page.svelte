<script>
  const nodes = [
    { id: 'edge', label: 'Cloudflare edge', detail: 'Public delivery', description: 'DNS, TLS, CDN caching, and the public boundary. Static pages are served from Cloudflare Pages without requiring the homelab to be online.', color: 'blue' },
    { id: 'frontend', label: 'SvelteKit', detail: 'Static frontend', description: 'The portfolio is prerendered into static assets. This keeps the public site fast, cacheable, and independent from backend availability.', color: 'acid' },
    { id: 'tunnel', label: 'Cloudflare Tunnel', detail: 'Private ingress', description: 'Only the API hostname crosses into the homelab. There is no direct inbound port forward to the home network.', color: 'blue' },
    { id: 'api', label: 'FastAPI', detail: 'Status + content API', description: 'The backend probes configured services, returns sanitized status data, and will own future content and contact workflows.', color: 'acid' },
    { id: 'services', label: 'Homelab services', detail: 'Immich + PostgreSQL', description: 'Applications remain on the private network. The public dashboard receives status summaries, never private addresses or credentials.', color: 'acid' },
    { id: 'runtime', label: 'Podman + systemd', detail: 'Rootless runtime', description: 'Containers are built and managed as rootless services through Podman Quadlet and user-level systemd units.', color: 'blue' }
  ];

  let selected = $state(nodes[0]);
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

  <section class="topology" aria-label="Interactive homelab architecture">
    <div class="topology-path">
      {#each nodes as node, index}
        <button class:node-active={selected.id === node.id} class:node-blue={node.color === 'blue'} class="topology-node" onclick={() => selected = node} aria-pressed={selected.id === node.id}><span>0{index + 1}</span><strong>{node.label}</strong><small>{node.detail}</small></button>
        {#if index < nodes.length - 1}<div class="topology-arrow" aria-hidden="true">↓</div>{/if}
      {/each}
    </div>
    <div class="topology-detail"><span class="eyebrow">Selected layer / {selected.id}</span><h2>{selected.label}</h2><p>{selected.description}</p></div>
  </section>

  <section class="boundary-notes"><div class="section-heading"><span class="eyebrow">Operating principles</span><span class="section-count">Designed boundaries</span></div><div class="boundary-grid"><article><strong>01</strong><h2>Public by choice</h2><p>The frontend is public. Backend health is deliberately reduced to a small, sanitized contract.</p></article><article><strong>02</strong><h2>Private by default</h2><p>Immich and homelab services stay on the private network; the dashboard does not become an application gateway.</p></article><article><strong>03</strong><h2>Recoverable</h2><p>Services are independently managed by systemd, with persistent data isolated from disposable containers.</p></article></div></section>
</main>

<style>
  .architecture-page h1 { margin-bottom: 35px; }.topology { background: #111820; border: 1px solid var(--line); margin-top: 75px; padding: 28px; }.topology-path { align-items: center; display: flex; flex-direction: column; }.topology-node { background: transparent; border: 1px solid #3b4851; color: #d9e1e6; cursor: pointer; display: grid; font: inherit; gap: 7px; padding: 18px 22px; text-align: left; transition: border-color .2s, background .2s; width: min(100%, 490px); }.topology-node:hover, .node-active { background: #19242c; border-color: var(--acid); }.node-blue.node-active { border-color: var(--blue); }.topology-node span { color: var(--acid); font-family: 'DM Mono'; font-size: .6rem; }.node-blue span { color: var(--blue); }.topology-node strong { font-family: 'Space Grotesk'; font-size: 1.15rem; font-weight: 500; }.topology-node small { color: var(--muted); font-family: 'DM Mono'; font-size: .62rem; }.topology-arrow { color: var(--acid); font-size: 1.2rem; height: 42px; padding-top: 10px; }.topology-detail { border-top: 1px solid var(--line); margin-top: 35px; padding: 25px 0 4px; }.topology-detail h2 { font-size: 2.2rem; margin: 18px 0 10px; }.topology-detail p { color: var(--muted); line-height: 1.7; margin: 0; max-width: 650px; }.boundary-notes { padding: 110px 0 40px; }.boundary-grid { display: grid; gap: 15px; grid-template-columns: repeat(3, 1fr); padding-top: 25px; }.boundary-grid article { border-top: 1px solid var(--line); padding: 20px 0; }.boundary-grid strong { color: var(--acid); font-family: 'DM Mono'; font-size: .65rem; }.boundary-grid h2 { font-size: 1.45rem; margin: 30px 0 12px; }.boundary-grid p { color: var(--muted); font-size: .85rem; line-height: 1.65; margin: 0; }
  @media (max-width: 700px) { .topology { padding: 18px; }.boundary-grid { grid-template-columns: 1fr; }.boundary-notes { padding-top: 80px; } }
</style>
