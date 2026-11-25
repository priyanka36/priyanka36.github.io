---
layout: single
title: "Projects"
permalink: /projects/
kicker: "Research & Engineering"
subtitle: "Selected projects in multimodal AI, computer vision, NLP, and audio signal processing, from industry R&D and my studies."
---

<div class="filters" role="group" aria-label="Filter projects by topic">
  <button type="button" class="filter is-active" data-filter="all">All</button>
  <button type="button" class="filter" data-filter="multimodal">Multimodal</button>
  <button type="button" class="filter" data-filter="vision">Vision</button>
  <button type="button" class="filter" data-filter="nlp">NLP</button>
  <button type="button" class="filter" data-filter="audio">Audio</button>
</div>

<div class="cards">
{%- for post in site.posts -%}
  {%- if post.categories contains 'Projects' -%}
  {%- capture tagslug -%}{% for t in post.tags %}{{ t | downcase | slugify }} {% endfor %}{%- endcapture -%}
  <a class="card" href="{{ post.url | relative_url }}" data-tags="{{ tagslug | strip }}">
    {%- if post.header.teaser %}<div class="card-img"><img src="{{ post.header.teaser }}" alt="" loading="lazy"></div>{% endif %}
    <div class="card-body">
      <div class="chips">{% for t in post.tags %}<span class="chip">{{ t }}</span>{% endfor %}</div>
      <p class="card-title">{{ post.title }}</p>
      <p class="card-text">{{ post.excerpt | strip_html | truncate: 120 }}</p>
      <span class="card-cta">View project <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
    </div>
  </a>
  {%- endif -%}
{%- endfor -%}
</div>

<p class="after-cards">For peer-reviewed work, see <a href="{{ '/publications/' | relative_url }}">Publications</a>. More code is on my <a href="https://github.com/priyanka36">GitHub</a>.</p>

<script>
  (function () {
    var buttons = document.querySelectorAll('.filter');
    var cards = document.querySelectorAll('.cards .card');
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var f = btn.getAttribute('data-filter');
        buttons.forEach(function (b) { b.classList.toggle('is-active', b === btn); });
        cards.forEach(function (c) {
          var tags = (c.getAttribute('data-tags') || '').split(' ');
          c.hidden = !(f === 'all' || tags.indexOf(f) !== -1);
        });
      });
    });
  })();
</script>
