/*
 * Repository facts for the header's second and later "Go to repository" links.
 *
 * Material fetches the latest release, stars and forks for the link it mounts from repo_url, and
 * caches that one answer under `__source` for every link on the page. The links
 * docs/overrides/partials/source.html adds for further repositories carry `data-idfkit-source`
 * instead; this file fetches each one's facts from the GitHub API, caches them per repository in
 * sessionStorage, and renders them in Material's own markup (`md-source__facts`), so they look
 * and animate like the first link's.
 */
(function () {
  "use strict";

  function compact(value) {
    if (value > 999) {
      const digits = ((value - 950) % 1000) > 99 ? 1 : 0;
      return ((value + 0.000001) / 1000).toFixed(digits) + "k";
    }
    return value.toString();
  }

  function readCache(key) {
    try {
      const raw = sessionStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (_) {
      return null;
    }
  }

  function writeCache(key, facts) {
    try {
      sessionStorage.setItem(key, JSON.stringify(facts));
    } catch (_) {
      /* Storage unavailable: fetch again next page. */
    }
  }

  function fetchJson(url) {
    return fetch(url).then(function (response) {
      return response.ok ? response.json() : null;
    }).catch(function () {
      return null;
    });
  }

  function fetchFacts(owner, repo) {
    const base = "https://api.github.com/repos/" + owner + "/" + repo;
    return Promise.all([fetchJson(base + "/releases/latest"), fetchJson(base)]).then(function (results) {
      const facts = {};
      if (results[0] && results[0].tag_name) facts.version = results[0].tag_name;
      if (results[1]) {
        facts.stars = results[1].stargazers_count;
        facts.forks = results[1].forks_count;
      }
      return facts;
    });
  }

  function render(link, facts) {
    const repository = link.querySelector(".md-source__repository");
    if (!repository || repository.querySelector(".md-source__facts")) return;
    const list = document.createElement("ul");
    list.className = "md-source__facts";
    Object.keys(facts).forEach(function (name) {
      const value = facts[name];
      if (value === undefined || value === null) return;
      const item = document.createElement("li");
      item.className = "md-source__fact md-source__fact--" + name;
      item.textContent = typeof value === "number" ? compact(value) : value;
      list.appendChild(item);
    });
    if (!list.children.length) return;
    repository.appendChild(list);
    repository.classList.add("md-source__repository--active");
  }

  function mount(link) {
    const match = link.href.match(/github\.com\/([^/]+)\/([^/#?]+)/i);
    if (!match) return;
    const key = "idfkit.__source." + match[1] + "/" + match[2];
    const cached = readCache(key);
    if (cached) {
      render(link, cached);
      return;
    }
    fetchFacts(match[1], match[2]).then(function (facts) {
      if (Object.keys(facts).length) {
        writeCache(key, facts);
        render(link, facts);
      }
    });
  }

  function mountAll() {
    document.querySelectorAll("a[data-idfkit-source]").forEach(mount);
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(mountAll);
  } else {
    mountAll();
  }
})();
