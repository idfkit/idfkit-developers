/*
 * What this pull request changed, on the page (PR previews only).
 *
 * scripts/annotate_preview.py writes the difference into the preview's HTML: `data-pv="added"`,
 * `data-pv="changed"` (followed by `<template class="pv-previous">` holding the old block),
 * `<details class="pv-removed">` and `data-pv-page` on the article. This file only draws the
 * controls: a banner on a new page, and a bar with the count, previous/next, the old version of a
 * changed block, a highlight toggle and the list of changed pages.
 *
 * It is copied into the preview by that script and is never part of a production build: nothing
 * under docs/ or in mkdocs.yml names it.
 *
 * `navigation.instant` swaps the page content without a load, so everything here runs from
 * Material's `document$`, which emits once per page, first load included.
 */
(() => {
  "use strict";

  const root = new URL("../", document.currentScript.src);
  const OFF = "pv-highlights-off";
  let summary = null;
  let chunks = [];
  let current = -1;

  const read = () => {
    try {
      return window.sessionStorage.getItem(OFF) === "1";
    } catch {
      return false;
    }
  };
  const write = (off) => {
    try {
      if (off) window.sessionStorage.setItem(OFF, "1");
      else window.sessionStorage.removeItem(OFF);
    } catch {
      /* storage unavailable: the toggle still works for this page */
    }
  };

  const el = (tag, props = {}, ...children) => {
    const node = Object.assign(document.createElement(tag), props);
    node.append(...children);
    return node;
  };

  const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;

  // An attribute, not a class: Material styles `table:not([class])`, so a class would unstyle a table.
  function select(index) {
    chunks[current]?.removeAttribute("data-pv-current");
    current = index;
    const chunk = chunks[current];
    if (!chunk) return;
    chunk.setAttribute("data-pv-current", "");
    chunk.scrollIntoView({ block: "center", behavior: "smooth" });
    update();
  }

  // The old version of a changed block follows it. Material wraps a table in two divs after load,
  // which leaves the template beside the outer wrapper rather than beside the table.
  function previousOf(chunk) {
    let node = chunk;
    while (
      node &&
      !node.nextElementSibling &&
      node.parentElement?.matches(".md-typeset__table, .md-typeset__scrollwrap")
    ) {
      node = node.parentElement;
    }
    const template = node?.nextElementSibling;
    return template?.matches("template.pv-previous") ? template : null;
  }

  function togglePrevious() {
    const template = previousOf(chunks[current]);
    if (!template) return;
    const shown = template.nextElementSibling;
    if (shown?.matches(".pv-previous-shown")) shown.remove();
    else template.after(el("div", { className: "pv-previous-shown" }, template.content.cloneNode(true)));
    update();
  }

  let bar = null;
  function update() {
    if (!bar) return;
    const chunk = chunks[current];
    bar.querySelector(".pv-previous-button").disabled = !previousOf(chunk);
    bar.querySelector(".pv-position").textContent =
      current < 0 ? "" : `${current + 1}/${chunks.length}`;
  }

  function pagesList() {
    const pages = Object.entries(summary?.pages ?? {});
    const removed = summary?.removed ?? [];
    if (!pages.length && !removed.length) return null;
    const items = pages.map(([path, info]) =>
      el(
        "li",
        {},
        el("a", { href: new URL(path, root).href }, path || "(home)"),
        el("span", { className: "pv-tag" }, info.status === "new" ? " new" : ""),
      ),
    );
    for (const path of removed) {
      items.push(el("li", { className: "pv-gone" }, `${path || "(home)"} removed`));
    }
    return el(
      "details",
      { className: "pv-pages" },
      el("summary", {}, `Changed pages (${pages.length + removed.length})`),
      el("ul", {}, ...items),
    );
  }

  function render() {
    document.documentElement.classList.toggle("pv-off", read());
    document.querySelector(".pv-bar")?.remove();
    bar = null;
    const article = document.querySelector("article.md-content__inner");
    if (!article) return;

    chunks = [...article.querySelectorAll("[data-pv]")].filter(
      (node) => !node.parentElement?.closest("[data-pv]"),
    );
    current = -1;
    const state = article.dataset.pvPage;

    if (state === "new" && !article.querySelector(".pv-banner")) {
      article.prepend(el("p", { className: "pv-banner" }, "New page in this pull request."));
    }

    const label =
      state === "new"
        ? "New page"
        : chunks.length
          ? plural(chunks.length, "change")
          : "No changes on this page";
    const button = (text, title, onclick, className = "") =>
      el("button", { type: "button", textContent: text, title, onclick, className });
    const toggle = el("input", { type: "checkbox", checked: !read() });
    toggle.addEventListener("change", () => {
      write(!toggle.checked);
      document.documentElement.classList.toggle("pv-off", !toggle.checked);
    });

    bar = el(
      "div",
      { className: "pv-bar", role: "region", ariaLabel: "Changes in this pull request" },
      el("strong", {}, label),
      el("span", { className: "pv-position" }),
      button("↑", "Previous change", () =>
        chunks.length && select(current <= 0 ? chunks.length - 1 : current - 1),
      ),
      button("↓", "Next change", () => chunks.length && select((current + 1) % chunks.length)),
      button("Old", "Show or hide the base version of this block", togglePrevious, "pv-previous-button"),
      el("label", { title: "Show or hide the highlights" }, toggle, " Highlights"),
    );
    if (!chunks.length) for (const b of bar.querySelectorAll("button")) b.disabled = true;
    const list = pagesList();
    if (list) bar.append(list);
    document.body.append(bar);
    update();
  }

  fetch(new URL("preview-changes/summary.json", root))
    .then((response) => (response.ok ? response.json() : null))
    .then((data) => {
      summary = data;
      const list = pagesList();
      if (bar && list && !bar.querySelector(".pv-pages")) bar.append(list);
    })
    .catch(() => {});

  if (window.document$) window.document$.subscribe(render);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", render);
  else render();
})();
