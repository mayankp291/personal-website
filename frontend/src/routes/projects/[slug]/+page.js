import { error } from '@sveltejs/kit';
import { getProject, projects } from '$lib/projects.js';

export const prerender = true;

export function entries() {
  return projects.map(({ slug }) => ({ slug }));
}

export function load({ params }) {
  const project = getProject(params.slug);

  if (!project) {
    error(404, 'Project not found');
  }

  return { project };
}
