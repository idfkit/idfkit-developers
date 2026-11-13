/*
 * Repository facts for the header's second and later "Go to repository" links.
 *
 * Material fetches the latest release, stars and forks for the link it mounts from repo_url, and
 * caches that one answer under `__source` for every link on the page. The links
 * docs/overrides/partials/source.html adds for further repositories carry `data-idfkit-source`
 * instead; this file fetches each one's facts from the GitHub API, caches them per repository in
 * sessionStorage, and renders them in Material's own markup (`md-source__facts`), so they look
 * and animate like the first link's.
 *
 * Each repository is fetched at most once per session: the header and the drawer copy of a link
 * share one request, and a failed or rate-limited answer is remembered for the session rather than
 * retried on every page, as Material's own cached fetch does. The version is the newest published
 * release whose tag is not a `docs-YYYY.N` artifact tag, which idfkit-js also publishes as releases.
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

  function libraryVersion(releases) {
    if (!Array.isArray(releases)) return undefined;
    for (const release of releases) {
      if (!release.draft && !release.prerelease && !/^docs-/.test(release.tag_name)) {
        return release.tag_name;
      }
    }
    return undefined;
  }

  function fetchFacts(owner, repo) {
    const base = "https://api.github.com/repos/" + owner + "/" + repo;
    return Promise.all([fetchJson(base + "/releases?per_page=20"), fetchJson(base)]).then(function (results) {
      const facts = {};
      const version = libraryVersion(results[0]);
      if (version) facts.version = version;
      if (results[1]) {
        facts.stars = results[1].stargazers_count;
        facts.forks = results[1].forks_count;
      }
      return facts;
    });
  }

  // One promise per repository for the life of the page, shared by the header and drawer links.
  const pending = new Map();

  function factsFor(owner, repo) {
    const key = "idfkit.__source." + owner + "/" + repo;
    if (!pending.has(key)) {
      const cached = readCache(key);
      // An empty answer (rate limited, offline) is cached too, as Material caches its own, so a
      // reader is not charged another two requests on every page of the session.
      pending.set(key, cached ? Promise.resolve(cached) : fetchFacts(owner, repo).then(function (facts) {
        writeCache(key, facts);
        return facts;
      }));
    }
    return pending.get(key);
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
    if (!list.children.length) return; // nothing came back: leave the link as a plain link
    repository.appendChild(list);
    repository.classList.add("md-source__repository--active");
  }

  function mount(link) {
    const match = link.href.match(/github\.com\/([^/]+)\/([^/#?]+?)(?:\.git)?\/?(?:[#?]|$)/i);
    if (!match) return;
    factsFor(match[1], match[2]).then(function (facts) {
      render(link, facts);
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
