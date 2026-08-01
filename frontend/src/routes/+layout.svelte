<script>
  import '../app.css';

  let { children } = $props();
</script>

<svelte:head>
  <meta name="theme-color" content="#0b0f14" />
  <meta name="description" content="Mayank Panjiyara is a Windows Infrastructure Engineer building and operating systems at scale." />
</svelte:head>

<header class="site-header">
  <a class="brand" href="/" aria-label="Mayank Panjiyara home">
    <span class="brand-mark">MP</span>
    <span>mayankp.me</span>
  </a>
  <nav aria-label="Main navigation">
    <a href="/#about">About</a>
    <a href="/#work">Work</a>
    <a href="/#experience">Experience</a>
    <a href="/#skills">Skills</a>
    <a href="/lab">Lab</a>
    <a class="nav-contact" href="/#contact">Let's talk <span aria-hidden="true">↗</span></a>
  </nav>
</header>

{@render children()}

<footer class="site-footer">
  <span>© {new Date().getFullYear()} Mayank Panjiyara</span>
  <span class="footer-status"><i></i> Systems nominal</span>
  <a href="mailto:hi@mayankp.me">hi@mayankp.me ↗</a>
</footer>
