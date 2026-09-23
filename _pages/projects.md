---
layout: default
title: Projects
permalink: /projects/
---

{%- assign projects = site.data.projects | where_exp: "p", "p.draft != true" -%}
{%- assign groups = "professional|Professional Work,side|Side Projects,pet|Pet Projects" | split: "," -%}

<section class="projects">
    <h2 class="section-title">projects</h2>
    <p class="page-lede">
        Things I've built - from professional work to side businesses and pet projects I hack on for fun.
    </p>

    {%- for g in groups -%}
    {%- assign parts = g | split: "|" -%}
    {%- assign items = projects | where: "kind", parts[0] -%}
    <h3 class="project-group-title">{{ parts[1] }}</h3>
    {%- if items.size > 0 -%}
    <ul class="project-list project-list-detailed">
        {%- for p in items -%}
        {%- include project-card.html project=p detailed=true -%}
        {%- endfor -%}
    </ul>
    {%- else -%}
    <p class="project-empty">Write-ups coming soon.</p>
    {%- endif -%}
    {%- endfor -%}
</section>
