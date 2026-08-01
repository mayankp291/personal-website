<script>
  let { data } = $props();
  const project = $derived(data.project);
</script>

<svelte:head>
  <title>{project.title} · Mayank Panjiyara</title>
  <meta name="description" content={project.detail} />
</svelte:head>

<main class="project-detail wrap">
  <a class="back-link" href="/#work">← Back to selected work</a>

  <div class="project-detail-header">
    <div>
      <span class="eyebrow">Project {project.number}</span>
      <h1>{project.title}<br /><em>{project.term}</em></h1>
    </div>
    {#if project.github}
      <a class="project-source" href={project.github} target="_blank" rel="noreferrer">View source <span>↗</span></a>
    {/if}
  </div>

  <div class="project-detail-lead">
    <p>{project.overview}</p>
    <div class="tags">{#each project.tags as tag}<span>{tag}</span>{/each}</div>
  </div>

  {#if project.diagram}
    <section class="architecture-block">
      <div class="detail-section-heading"><span class="eyebrow">Architecture</span><span class="section-count">Request path / deployment shape</span></div>
      <div class="architecture-diagram">
        {#each project.diagram as node, index}
          <div class="architecture-node"><span class="node-number">0{index + 1}</span><strong>{node.label}</strong><small>{node.detail}</small></div>
          {#if index < project.diagram.length - 1}<span class="architecture-arrow" aria-hidden="true">↓</span>{/if}
        {/each}
      </div>
    </section>
  {/if}

  <div class="project-detail-grid">
    <section>
      <div class="detail-section-heading"><span class="eyebrow">What I built</span><span class="section-count">Contributions</span></div>
      <ul class="contribution-list">{#each project.contributions as contribution}<li>{contribution}</li>{/each}</ul>
    </section>
    <section>
      <div class="detail-section-heading"><span class="eyebrow">Stack</span><span class="section-count">Tools and systems</span></div>
      <div class="detail-stack">{#each project.architecture as technology}<span>{technology}</span>{/each}</div>
    </section>
  </div>

  <a class="next-project" href="/#work">Back to all projects <span>↗</span></a>
</main>
