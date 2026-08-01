export const projects = [
  {
    slug: 'project-rice',
    number: '01',
    title: 'Project RICE',
    term: 'Google Developer Society',
    detail: 'A scalable volunteer management platform that streamlines coordination and task assignment for a non-profit.',
    attribution: 'Modular MVC-style backend with TypeScript, Express.js, MongoDB, and REST APIs.',
    tags: ['TypeScript', 'Express.js', 'MongoDB'],
    github: null,
    overview: 'A team-built platform for turning volunteer coordination into a clear, manageable workflow. The service organized volunteers, tasks, and assignments behind a modular backend.',
    contributions: ['Collaborated in a 30-person team.', 'Designed RESTful APIs for core platform functionality.', 'Implemented a modular MVC-style backend architecture.'],
    architecture: ['TypeScript', 'Express.js', 'MongoDB', 'REST APIs', 'MVC']
  },
  {
    slug: 'geofencing',
    number: '02',
    title: 'Geofencing',
    term: 'Engineering Society for Good',
    detail: 'A portable BLE GPS solution for real-time tracking of 100+ specially-abled students at Rainbow Centre School.',
    attribution: 'BLE 5.0 beacons, MQTT, AWS, Firebase, Python, and a cloud web application.',
    tags: ['Python', 'AWS', 'MQTT'],
    github: 'https://github.com/EGSC-NUS-Rainbow-Centre-IPS',
    overview: 'A portable location system that replaced manual CCTV monitoring with real-time signals and a cloud web application, improving monitoring and incident response.',
    contributions: ['Built a BLE 5.0 beacon and base-station workflow.', 'Connected location events to AWS over MQTT.', 'Supported monitoring for more than 100 students.'],
    architecture: ['BLE 5.0', 'MQTT', 'AWS', 'Firebase', 'Python', 'Web application']
  },
  {
    slug: 'lasertag-plus-plus',
    number: '03',
    title: 'LaserTag++',
    term: 'NUS Computer Engineering capstone',
    detail: 'A two-player laser tag game with AI hand actions, built as a five-person capstone team.',
    attribution: 'Multi-server communication across phones and game systems using TCP/IP, MQTT, threads, and queues.',
    tags: ['Python', 'TCP/IP', 'Concurrency'],
    github: 'https://github.com/mayankp291/CG4002-Capstone-LaserTag-Plus',
    overview: 'A distributed game system connecting FPGA hardware, a server, laptops, and mobile devices. The project combined real-time communication with machine-learning-powered hand actions.',
    contributions: ['Handled communications between servers, phones, and game systems.', 'Used TCP/IP and MQTT for device messaging.', 'Managed concurrent streams with threads and queues.'],
    architecture: ['Python', 'TCP/IP', 'MQTT', 'Threads', 'Queues', 'FPGA']
  },
  {
    slug: 'coding-competitions',
    number: '04',
    title: 'Coding competitions',
    term: 'Selected builds',
    detail: 'Sixth place and Best Design at MindfulHacks 2021 for a mental-health app connecting psychologists and caregivers.',
    attribution: 'Semi-finalist at the NUS Blockchain Hackathon 2022 with an NFT creation website for non-technical users.',
    tags: ['Product design', 'Web', 'Hackathons'],
    github: null,
    overview: 'A collection of fast, focused builds made under competition constraints, balancing useful product ideas with clear and approachable interfaces.',
    contributions: ['Won sixth place and Best Design at MindfulHacks 2021.', 'Built a mental-health matching concept for psychologists and caregivers.', 'Reached the semi-finals of the NUS Blockchain Hackathon 2022.'],
    architecture: ['Product design', 'Web development', 'Rapid prototyping']
  },
  {
    slug: 'personal-website',
    number: '05',
    title: 'Personal website platform',
    term: 'This site · 2026',
    detail: 'A self-hosted content and SRE platform with a Cloudflare Pages frontend and a Podman homelab backend.',
    attribution: 'SvelteKit, FastAPI, PostgreSQL, Podman Quadlet, systemd, and Cloudflare Tunnel.',
    tags: ['SvelteKit', 'FastAPI', 'Podman'],
    github: 'https://github.com/mayankp291/personal-website',
    overview: 'This website is both a portfolio and an operating system for the portfolio. The public frontend is static and globally delivered through Cloudflare Pages, while the API and data layer run privately in my homelab.',
    contributions: ['Designed a static-first SvelteKit frontend for fast, SEO-friendly delivery.', 'Built a FastAPI service with health and content endpoints.', 'Deployed PostgreSQL and the API as rootless Podman services managed by systemd.', 'Used Cloudflare Tunnel to expose only the API hostname without opening the homelab to inbound traffic.'],
    architecture: ['SvelteKit', 'Cloudflare Pages', 'FastAPI', 'PostgreSQL', 'Podman', 'Quadlet', 'Cloudflare Tunnel'],
    diagram: [
      { label: 'Visitors', detail: 'HTTPS / CDN' },
      { label: 'Cloudflare Pages', detail: 'Static SvelteKit frontend' },
      { label: 'Cloudflare Tunnel', detail: 'api.mayankp.me' },
      { label: 'FastAPI', detail: 'Rootless Podman service' },
      { label: 'PostgreSQL', detail: 'Persistent homelab volume' }
    ]
  }
];

/** @param {string} slug */
export function getProject(slug) {
  return projects.find((project) => project.slug === slug);
}
