<script>
  import { onMount } from 'svelte';

  let state = 'loading';
  /** @type {null | {status: string, checked_at: string, services: Array<{name: string, status: string, detail: string, latency_ms: number | null}>}} */
  let dashboard = null;
  /** @type {null | {hours: number, services: Array<{id: string, name: string, points: Array<{timestamp: string, status: string, latency_ms: number | null}>}>}} */
  let history = null;
  /** @type {number | null} */
  let visits = null;
  let lastError = '';

  function apiOrigin() {
    if (typeof window !== 'undefined' && ['localhost', '127.0.0.1'].includes(window.location.hostname)) {
      return 'https://api.mayankp.me';
    }
    return 'https://api.mayankp.me';
  }

  async function refresh() {
    try {
      const [statusResponse, historyResponse, visitsResponse] = await Promise.all([
        fetch(`${apiOrigin()}/api/v1/homelab/status`),
        fetch(`${apiOrigin()}/api/v1/homelab/history?hours=24`),
        fetch(`${apiOrigin()}/api/v1/visits`)
      ]);
      if (!statusResponse.ok || !historyResponse.ok) throw new Error(`status ${statusResponse.status}`);
      dashboard = await statusResponse.json();
      history = await historyResponse.json();
      if (visitsResponse.ok) visits = (await visitsResponse.json()).total;
      state = 'ready';
      lastError = '';
    } catch (error) {
      state = 'error';
      lastError = error instanceof Error ? error.message : 'unknown error';
    }
  }

  function checkedTime() {
    return dashboard ? new Date(dashboard.checked_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--';
  }

  /** @param {{points: Array<{status: string}>}} service */
  function uptime(service) {
    if (!service.points.length) return '--';
    return `${Math.round((service.points.filter((point) => point.status === 'operational').length / service.points.length) * 100)}%`;
  }

  /** @param {{points: Array<{status: string}>}} service */
  function graphPoints(service) {
    if (!service.points.length) return '';
    const width = 300;
    const height = 54;
    const step = service.points.length === 1 ? 0 : width / (service.points.length - 1);
    return service.points.map((point, index) => `${Math.round(index * step)},${point.status === 'operational' ? 8 : height - 8}`).join(' ');
  }

  onMount(() => {
    refresh();
    const interval = setInterval(refresh, 30000);
    return () => clearInterval(interval);
  });
</script>

<svelte:head>
  <title>SRE Lab · Mayank Panjiyara</title>
  <meta name="description" content="Live, sanitized health status from Mayank's homelab." />
</svelte:head>

<main class="subpage lab-dashboard wrap">
  <a class="back-link" href="/">← Back home</a>
  <div class="lab-title-row"><div><span class="eyebrow">SRE lab / 001</span><h1>Observe.<br /><em>Measure. Learn.</em></h1></div><a class="architecture-link" href="/architecture">Explore architecture <span>↗</span></a></div>
  <p class="subpage-intro">A public, sanitized view of the systems behind this site. Checks run from the homelab and refresh every 30 seconds.</p>

  <section class="dashboard-summary" aria-live="polite">
    <div class="summary-row">
      <div class:summary-ok={dashboard?.status === 'operational'} class:summary-degraded={dashboard?.status === 'degraded'} class="summary-state"><span class="pulse"></span><strong>{state === 'loading' ? 'Checking systems' : dashboard?.status === 'operational' ? 'All systems operational' : state === 'error' ? 'Status unavailable' : 'Some systems need attention'}</strong><span class="status-meta">Checked {checkedTime()}</span></div>
      <div class="visit-stat"><strong>{visits === null ? '—' : visits.toLocaleString()}</strong><span>total site visits</span></div>
    </div>
    {#if state === 'error'}<p class="dashboard-error">The dashboard could not reach the status API ({lastError}).</p>{/if}
  </section>

  <section class="service-grid" aria-label="Homelab services">
    {#if dashboard}
      {#each dashboard.services as service}
        <article class="service-card"><div class="service-card-top"><span class:service-ok={service.status === 'operational'} class:service-bad={service.status !== 'operational'} class="service-dot"></span><span class="service-state">{service.status}</span></div><h2>{service.name}</h2><p>{service.detail}</p><footer><span>response</span><strong>{service.latency_ms === null ? '—' : `${service.latency_ms}ms`}</strong></footer></article>
      {/each}
    {:else}
      {#each ['Website API', 'Immich', 'PostgreSQL'] as service}<article class="service-card loading-card"><div class="service-dot"></div><h2>{service}</h2><p>Waiting for first check...</p></article>{/each}
    {/if}
  </section>

  <section class="uptime-section">
    <div class="uptime-heading"><span class="eyebrow">Uptime / last 24 hours</span><span class="section-count">One sample every status check</span></div>
    {#if history}
      {#each history.services as service}
        <article class="uptime-row"><div><h2>{service.name}</h2><span>{service.points.length} samples</span></div><svg viewBox="0 0 300 54" role="img" aria-label="{service.name} uptime graph"><line x1="0" y1="46" x2="300" y2="46" /><polyline points={graphPoints(service)} /></svg><strong>{uptime(service)}</strong></article>
      {/each}
    {:else}<p class="no-history">Collecting the first health sample...</p>{/if}
  </section>
</main>

<style>
  .lab-title-row { align-items: end; display: flex; justify-content: space-between; }
  .lab-title-row h1 { margin-bottom: 0; }
  .architecture-link { border: 1px solid var(--line); color: var(--blue); font-family: 'DM Mono'; font-size: .7rem; padding: 12px 14px; text-transform: uppercase; }
  .architecture-link:hover { border-color: var(--acid); color: var(--acid); }
  .architecture-link span { margin-left: 18px; }
  .dashboard-summary { margin-top: 65px; }
  .summary-row { display: flex; gap: 15px; }
  .summary-state { align-items: center; border: 1px solid var(--line); display: flex; gap: 10px; padding: 18px 20px; }
  .visit-stat { align-items: end; border: 1px solid var(--line); display: flex; flex-direction: column; justify-content: center; min-width: 170px; padding: 14px 20px; }
  .visit-stat strong { color: var(--acid); font-family: 'Space Grotesk'; font-size: 1.7rem; font-weight: 500; line-height: 1; }
  .visit-stat span { color: var(--muted); font-family: 'DM Mono'; font-size: .58rem; margin-top: 7px; text-transform: uppercase; }
  .summary-ok { border-color: #52632a; }.summary-degraded { border-color: #80602b; }
  .summary-state .pulse { margin: 0; }.summary-degraded .pulse { background: #f0bd55; }.summary-state strong { font-family: 'Space Grotesk'; font-size: 1.1rem; font-weight: 500; }.status-meta { color: var(--muted); font-family: 'DM Mono'; font-size: .65rem; margin-left: auto; }
  .dashboard-error { color: #f0bd55; font-family: 'DM Mono'; font-size: .7rem; }
  .service-grid { display: grid; gap: 15px; grid-template-columns: repeat(3, 1fr); margin-top: 15px; }
  .service-card { border: 1px solid var(--line); min-height: 230px; padding: 24px; }.service-card:hover { background: #111820; border-color: #43515a; }.service-card-top { align-items: center; display: flex; gap: 9px; }.service-dot { background: var(--acid); border-radius: 50%; display: inline-block; height: 8px; width: 8px; }.service-bad { background: #f0bd55; }.service-state { color: var(--muted); font-family: 'DM Mono'; font-size: .6rem; text-transform: uppercase; }.service-card h2 { font-size: 1.7rem; margin: 45px 0 12px; }.service-card p { color: var(--muted); font-size: .85rem; line-height: 1.6; }.service-card footer { border-top: 1px solid var(--line); display: flex; font-family: 'DM Mono'; font-size: .62rem; justify-content: space-between; margin-top: 28px; padding-top: 14px; text-transform: uppercase; }.service-card footer span { color: var(--muted); }.service-card footer strong { color: var(--acid); font-weight: 400; }.loading-card { opacity: .55; }
  .uptime-section { margin-top: 85px; }.uptime-heading { align-items: center; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; padding-bottom: 14px; }.uptime-row { align-items: center; border-bottom: 1px solid var(--line); display: grid; gap: 30px; grid-template-columns: 160px 1fr 60px; padding: 22px 0; }.uptime-row h2 { font-size: 1rem; letter-spacing: -.03em; }.uptime-row div span { color: var(--muted); font-family: 'DM Mono'; font-size: .58rem; }.uptime-row svg { height: 54px; overflow: visible; width: 100%; }.uptime-row line { stroke: var(--line); stroke-width: 1; }.uptime-row polyline { fill: none; stroke: var(--acid); stroke-linecap: round; stroke-linejoin: round; stroke-width: 2; }.uptime-row strong { color: var(--acid); font-family: 'Space Grotesk'; font-size: 1.5rem; font-weight: 500; text-align: right; }.no-history { color: var(--muted); font-family: 'DM Mono'; font-size: .7rem; padding-top: 20px; }
  @media (max-width: 700px) { .lab-title-row { align-items: start; flex-direction: column; gap: 35px; }.service-grid { grid-template-columns: 1fr; }.summary-row { align-items: stretch; flex-direction: column; }.summary-state { align-items: start; flex-wrap: wrap; }.summary-state .status-meta { margin-left: 18px; width: 100%; }.visit-stat { align-items: start; min-width: 0; }.uptime-row { gap: 15px; grid-template-columns: 105px 1fr 42px; }.uptime-row strong { font-size: 1rem; }.uptime-heading .section-count { display: none; } }
</style>
