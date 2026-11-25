---
title: "Blog"
permalink: /blogs/
layout: single
kicker: "Writing"
subtitle: "Technical write-ups on audio signal processing and machine learning, originally published on Medium."
---

<!-- To add an article, edit _data/blog.yml -->

<div class="series">
  <i class="fa-solid fa-headphones" aria-hidden="true"></i>
  <div><strong>Audio Signal Processing series</strong><span>{{ site.data.blog | size }} articles · from fundamentals to deep-learning source separation</span></div>
  <a class="series-link" href="https://medium.com/@poudelnipriyanka">All on Medium <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
</div>

<div class="blog-grid">
{%- for b in site.data.blog %}
  <a class="blog-card{% if forloop.first %} blog-card--featured{% endif %}" href="{{ b.url }}">
    <div class="blog-cover cover-{{ forloop.index | modulo: 4 }}"><i class="fa-solid {{ b.icon }}" aria-hidden="true"></i></div>
    <div class="blog-body">
      {% if forloop.first %}<span class="featured-label"><i class="fa-solid fa-star" aria-hidden="true"></i> Featured</span>{% endif %}
      <div class="chips">{% for t in b.tags %}<span class="chip">{{ t }}</span>{% endfor %}</div>
      <h3>{{ b.title }}</h3>
      <p>{{ b.summary }}</p>
      <span class="card-cta">Read on Medium <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></span>
    </div>
  </a>
{%- endfor %}
</div>
