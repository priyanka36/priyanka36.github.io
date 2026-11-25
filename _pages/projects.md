---
layout: single
title: "Projects"
permalink: /projects/
---

<p class="lead">Selected engineering and research projects in computer vision, natural language processing, and audio signal processing, mostly from my industry R&amp;D work and earlier studies. For peer-reviewed work, see <a href="{{ '/publications/' | relative_url }}">Publications</a>.</p>

<div class="cards">
{%- for post in site.posts -%}
  {%- if post.categories contains 'Projects' -%}
  <a class="card" href="{{ post.url | relative_url }}">
    {%- if post.header.teaser %}<img src="{{ post.header.teaser }}" alt="" loading="lazy">{% endif %}
    <div class="card-body">
      <p class="card-title">{{ post.title }}</p>
      <p class="card-text">{{ post.excerpt | strip_html | truncate: 110 }}</p>
    </div>
  </a>
  {%- endif -%}
{%- endfor -%}
</div>
