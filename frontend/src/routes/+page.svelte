<script>
  import { projects } from '$lib/projects.js';

  const experience = [
    { period: 'Oct 2024 — present', role: 'Windows Infrastructure Engineer', company: 'Micron', detail: 'Manage Windows Server infrastructure across 15+ data centers in Asia and the USA, providing L3 escalation support for complex production issues.', impact: ['2,300+ servers refreshed', '600+ VMs migrated', '100+ hours saved / month'], tags: ['Windows Server', 'Nutanix', 'VMware', 'Splunk'] },
    { period: 'Mar 2024 — Jun 2024', role: 'Software Engineer', company: 'Tensorplex Labs', detail: 'Contributed to a Bittensor subnet and built Airflow data pipelines for web scraping and preprocessing, increasing collection efficiency by 90%.', impact: ['90% more efficient collection', '30x more diverse synthetic data'], tags: ['Python', 'Airflow', 'Machine Learning'] },
    { period: 'May 2023 — Nov 2023', role: 'Software Engineer Intern', company: 'Keysight Technologies', detail: 'Moved 12 Spark batch jobs to cluster mode and configured Airflow on Kubernetes and Docker for 1,000+ daily batch runs.', impact: ['24% faster batch jobs', '32% lower resource use'], tags: ['Scala', 'Spark', 'Kubernetes'] },
    { period: 'May 2022 — Aug 2022', role: 'Cloud Engineer Intern', company: 'Singtel', detail: 'Supported an Azure cloud migration through application POCs and reduced legacy code refactoring time by 93%.', impact: ['93% less refactor time'], tags: ['Azure', 'Cloud migration'] }
  ];

  const skillGroups = [
    { name: 'Languages', items: ['Python', 'PowerShell', 'Bash', 'C/C++', 'Java'] },
    { name: 'Infrastructure', items: ['VMware', 'Nutanix', 'Windows Administration', 'OpenShift', 'Unix/Linux', 'Scripting', 'ServiceNow', 'ITIL', 'Splunk'] },
    { name: 'Certifications', items: ['Nutanix Certified Associate', 'NCP - Artificial Intelligence', 'NCP - Multicloud Automation'] }
  ];
</script>

<svelte:head>
  <title>Mayank Panjiyara · Systems and software</title>
</svelte:head>

<main>
  <section class="hero wrap">
    <div class="hero-kicker"><span class="pulse"></span> Windows Infrastructure Engineer · Micron</div>
    <h1>I keep critical<br /><em>systems moving.</em></h1>
    <div class="hero-bottom">
      <p class="hero-intro">I operate infrastructure at scale, automate the repetitive, and stay curious about what happens underneath the interfaces we use every day.</p>
      <a class="arrow-link" href="#about">Meet Mayank <span>↓</span></a>
    </div>
    <div class="signal-grid" aria-hidden="true">
      <span>data centers</span><strong>15+</strong><span>servers refreshed</span><strong>2.3k+</strong><span>hours saved / month</span><strong>100+</strong>
    </div>
  </section>

  <section id="about" class="about-section section wrap">
    <div class="section-heading"><span class="eyebrow">About me</span><span class="section-count">01 / introduction</span></div>
    <div class="about-grid">
      <div class="portrait-frame"><img src="/me.gif" alt="Mayank Panjiyara" /></div>
      <div class="about-copy"><span class="eyebrow">Let me introduce myself</span><h2>Hi, my name is <em>Mayank.</em></h2><p>I am an infrastructure engineer who likes servers, coffee, solving problems, and trying new things. I work across Windows, virtualization, cloud platforms, automation, and observability.</p><div class="contact-details"><a href="mailto:mayankp@u.nus.edu"><span>Email</span>mayankp@u.nus.edu ↗</a><a href="https://github.com/mayankp291"><span>GitHub</span>mayankp291 ↗</a><a href="https://www.linkedin.com/in/mayank-panjiyara"><span>LinkedIn</span>Mayank Panjiyara ↗</a></div><a class="resume-download" href="/resume.pdf" download>Download resume <span>↓</span></a></div>
    </div>
  </section>

  <section id="experience" class="section experience-section wrap">
    <div class="section-heading"><span class="eyebrow">Experience</span><span class="section-count">Production systems / software / cloud</span></div>
    <div class="experience-list">{#each experience as item}<article class="experience-card"><div class="experience-meta"><span>{item.period}</span><div class="impact-list">{#each item.impact as metric}<strong>{metric}</strong>{/each}</div></div><div class="experience-main"><h2>{item.role}</h2><p class="company">{item.company}</p><p>{item.detail}</p><div class="tags">{#each item.tags as tag}<span>{tag}</span>{/each}</div></div></article>{/each}</div>
  </section>

  <section id="work" class="section wrap">
    <div class="section-heading"><span class="eyebrow">Selected work</span><span class="section-count">05 / projects</span></div>
    <div class="project-list">
      {#each projects as project}
        <article class="project-card">
          <span class="project-number">{project.number}</span>
          <div><h2>{project.title} <small>{project.term}</small></h2><p>{project.detail}</p><p class="attribution">{project.attribution}</p></div>
          <div class="tags">{#each project.tags as tag}<span>{tag}</span>{/each}</div>
          <a class="card-arrow" href={`/projects/${project.slug}`} aria-label="Read about {project.title}">↗</a>
        </article>
      {/each}
    </div>
  </section>

  <section class="education-section section wrap">
    <div class="section-heading"><span class="eyebrow">Education</span><span class="section-count">Singapore · 2020 — 2024</span></div>
    <div class="education-card"><div><span class="eyebrow">National University of Singapore</span><h2>Bachelor's (Honours) in<br /><em>Computer Engineering.</em></h2></div><div><p>Advanced Computer Networks · Linux Kernel · Robotics · Data Structures and Algorithms · Real-Time Operating Systems · Parallel and Concurrent Computing</p></div></div>
  </section>

  <section id="skills" class="section skills-section wrap">
    <div class="section-heading"><span class="eyebrow">Skill sets</span><span class="section-count">Languages / systems / credentials</span></div>
    <div class="skills-grid">{#each skillGroups as group}<article class="skill-group"><h2>{group.name}</h2><div class="skill-cloud">{#each group.items as item}<span>{item}</span>{/each}</div></article>{/each}</div>
  </section>

  <section id="lab" class="lab-section">
    <div class="wrap lab-inner">
      <div><span class="eyebrow">Next chapter</span><h2>Still learning.<br /><em>Always building.</em></h2></div>
      <div class="lab-copy"><p>This site is becoming a home for experiments, infrastructure notes, and small tools that make systems more legible.</p><a class="arrow-link" href="/lab">Visit the lab <span>↗</span></a></div>
    </div>
  </section>

  <section id="contact" class="contact-section wrap">
    <span class="eyebrow">Have a hard problem?</span><h2>Let's make it<br /><em>less mysterious.</em></h2><div class="contact-actions"><a class="contact-link" href="mailto:mayankp@u.nus.edu">mayankp@u.nus.edu <span>↗</span></a><a class="resume-link" href="/resume.pdf" download>Download resume <span>↓</span></a></div>
  </section>
</main>
