/* Literature database explorer for docs/literature/database.md.
 *
 * Loads papers.json (built by literature_review_claude/build_db.py) and renders
 * facet filters, live summary bars and an expandable paper table. Activates only on
 * pages that contain <div id="litdb" data-src="...">.
 */
(function () {
  "use strict";

  var FACETS = [
    { key: "category", label: "Category", multi: false },
    { key: "year", label: "Year", multi: false },
    { key: "metric_types", label: "Metric type", multi: true },
    { key: "metric_families", label: "Metric", multi: true },
    { key: "loss_families", label: "Loss function", multi: true },
    { key: "task_tags", label: "Task", multi: true },
    { key: "dataset_tags", label: "Dataset", multi: true },
    { key: "source", label: "Extraction source", multi: false },
  ];

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else if (k === "class") node.className = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) {
      if (c) node.appendChild(c);
    });
    return node;
  }

  function values(paper, facet) {
    var v = paper[facet.key];
    if (v === null || v === undefined || v === "") return [];
    return Array.isArray(v) ? v : [String(v)];
  }

  function init(root) {
    if (root.dataset.ready) return;
    root.dataset.ready = "1";
    var src = new URL(root.dataset.src, window.location.href).href;
    root.textContent = "Loading literature database…";
    fetch(src)
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (db) {
        render(root, db);
      })
      .catch(function (err) {
        root.textContent = "Could not load the literature database (" + err.message + ").";
      });
  }

  function render(root, db) {
    var papers = db.papers;
    var state = { q: "", sel: {}, mode: {}, sort: "year", dir: -1 };
    FACETS.forEach(function (f) {
      state.sel[f.key] = new Set();
      state.mode[f.key] = "any";
    });

    root.textContent = "";
    var search = el("input", {
      type: "search",
      class: "litdb-search",
      placeholder: "Search title, authors, metrics, losses, datasets…",
      "aria-label": "Search papers",
    });
    var reset = el("button", { class: "md-button litdb-reset", type: "button", text: "Reset filters" });
    var dl = el("button", { class: "md-button litdb-reset", type: "button", text: "Download CSV (filtered)" });
    var count = el("p", { class: "litdb-count" });
    var facetBox = el("div", { class: "litdb-facets" });
    var summary = el("div", { class: "litdb-summary" });
    var table = el("div", { class: "litdb-table" });
    root.appendChild(el("div", { class: "litdb-toolbar" }, [search, reset, dl]));
    root.appendChild(count);
    root.appendChild(facetBox);
    root.appendChild(summary);
    root.appendChild(table);

    function matchesExcept(paper, skipKey) {
      if (state.q) {
        var hay = [
          paper.title, paper.authors.join(" "), paper.venue, paper.model_family, paper.task,
          paper.datasets, paper.eval_metrics, paper.loss_functions, paper.notes, paper.id,
        ].join(" ").toLowerCase();
        var terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
        for (var i = 0; i < terms.length; i++) if (hay.indexOf(terms[i]) < 0) return false;
      }
      for (var j = 0; j < FACETS.length; j++) {
        var f = FACETS[j];
        if (f.key === skipKey) continue;
        var sel = state.sel[f.key];
        if (!sel.size) continue;
        var vals = values(paper, f);
        if (state.mode[f.key] === "all") {
          var ok = true;
          sel.forEach(function (s) {
            if (vals.indexOf(s) < 0) ok = false;
          });
          if (!ok) return false;
        } else if (!vals.some(function (v) { return sel.has(v); })) {
          return false;
        }
      }
      return true;
    }

    function renderFacets() {
      facetBox.textContent = "";
      FACETS.forEach(function (f) {
        var counts = {};
        papers.forEach(function (p) {
          if (!matchesExcept(p, f.key)) return;
          values(p, f).forEach(function (v) {
            counts[v] = (counts[v] || 0) + 1;
          });
        });
        var all = {};
        papers.forEach(function (p) {
          values(p, f).forEach(function (v) {
            all[v] = true;
          });
        });
        var keys = Object.keys(all).sort(function (a, b) {
          if (f.key === "year") return b.localeCompare(a);
          return (counts[b] || 0) - (counts[a] || 0) || a.localeCompare(b);
        });
        var chips = keys.map(function (v) {
          var active = state.sel[f.key].has(v);
          var n = counts[v] || 0;
          var chip = el("button", {
            type: "button",
            class: "litdb-chip" + (active ? " is-active" : "") + (n ? "" : " is-empty"),
            "aria-pressed": active ? "true" : "false",
          }, [el("span", { text: v }), el("span", { class: "litdb-chip-n", text: String(n) })]);
          chip.addEventListener("click", function () {
            if (active) state.sel[f.key].delete(v);
            else state.sel[f.key].add(v);
            update();
          });
          return chip;
        });
        var head = el("div", { class: "litdb-facet-head" }, [el("strong", { text: f.label })]);
        if (f.multi) {
          var mode = el("button", {
            type: "button",
            class: "litdb-mode",
            title: "Toggle between papers matching ANY or ALL selected values",
            text: state.mode[f.key] === "all" ? "match ALL" : "match ANY",
          });
          mode.addEventListener("click", function () {
            state.mode[f.key] = state.mode[f.key] === "all" ? "any" : "all";
            update();
          });
          head.appendChild(mode);
        }
        var details = el("details", { class: "litdb-facet" }, [
          el("summary", {}, [head]),
          el("div", { class: "litdb-chips" }, chips),
        ]);
        if (state.sel[f.key].size || f.key === "category" || f.key === "metric_types") {
          details.open = true;
        }
        facetBox.appendChild(details);
      });
    }

    function bars(title, key, rows) {
      var counts = {};
      rows.forEach(function (p) {
        p[key].forEach(function (v) {
          counts[v] = (counts[v] || 0) + 1;
        });
      });
      var top = Object.keys(counts)
        .sort(function (a, b) { return counts[b] - counts[a]; })
        .slice(0, 12);
      var max = top.length ? counts[top[0]] : 1;
      var list = top.map(function (k) {
        var bar = el("span", { class: "litdb-bar-fill" });
        bar.style.width = (100 * counts[k] / max).toFixed(1) + "%";
        return el("div", { class: "litdb-bar" }, [
          el("span", { class: "litdb-bar-label", text: k }),
          el("span", { class: "litdb-bar-track" }, [bar]),
          el("span", { class: "litdb-bar-n", text: String(counts[k]) }),
        ]);
      });
      return el("div", { class: "litdb-card" }, [el("strong", { text: title })].concat(
        list.length ? list : [el("p", { text: "No papers match." })]));
    }

    function field(label, value, link) {
      if (!value) return null;
      var dd = el("dd");
      if (link) dd.appendChild(el("a", { href: value, target: "_blank", rel: "noopener", text: value }));
      else dd.textContent = value;
      return el("div", {}, [el("dt", { text: label }), dd]);
    }

    function tags(list, cls) {
      return el("span", { class: "litdb-tags" }, list.map(function (t) {
        return el("span", { class: "litdb-tag " + (cls || ""), text: t });
      }));
    }

    function renderTable(rows) {
      table.textContent = "";
      var cols = [
        { key: "id", label: "ID" },
        { key: "year", label: "Year" },
        { key: "title", label: "Paper" },
        { key: "category", label: "Category" },
      ];
      var headRow = el("tr", {}, cols.map(function (c) {
        var th = el("th", { scope: "col", class: "litdb-sortable" }, [
          el("span", { text: c.label + (state.sort === c.key ? (state.dir > 0 ? " ▲" : " ▼") : "") }),
        ]);
        th.addEventListener("click", function () {
          if (state.sort === c.key) state.dir = -state.dir;
          else { state.sort = c.key; state.dir = c.key === "year" ? -1 : 1; }
          update();
        });
        return th;
      }).concat([el("th", { scope: "col", text: "Metrics" })]));

      rows.sort(function (a, b) {
        var x = a[state.sort], y = b[state.sort];
        if (x === y) return a.id.localeCompare(b.id);
        return (x > y ? 1 : -1) * state.dir;
      });

      var body = el("tbody");
      rows.forEach(function (p) {
        var authors = p.authors.length > 3 ? p.authors.slice(0, 3).join(", ") + " et al." : p.authors.join(", ");
        var titleCell = el("td", {}, [
          el("span", { class: "litdb-title", text: p.title }),
          el("span", { class: "litdb-sub", text: [authors, p.venue].filter(Boolean).join(" · ") }),
        ]);
        var tr = el("tr", { class: "litdb-row", tabindex: "0" }, [
          el("td", { text: p.id }),
          el("td", { text: p.year ? String(p.year) : "" }),
          titleCell,
          el("td", { text: p.category }),
          el("td", {}, [tags(p.metric_families)]),
        ]);
        var detail = el("tr", { class: "litdb-detail", hidden: "hidden" }, [
          el("td", { colspan: "5" }, [
            el("dl", {}, [
              field("Model family", p.model_family),
              field("Task", p.task),
              field("Loss functions", p.loss_functions),
              field("Loss families", p.loss_families.join(", ")),
              field("Evaluation metrics", p.eval_metrics),
              field("Metric types", p.metric_types.join(", ")),
              field("Embedding extractor", p.embedding_extractor),
              field("Datasets", p.datasets),
              field("Leads / fs / length", [p.n_leads && p.n_leads + " lead(s)",
                p.fs_hz && p.fs_hz + " Hz", p.signal_length_s && p.signal_length_s + " s"]
                .filter(Boolean).join(" · ")),
              field("Notes", p.notes),
              field("Takeaway for ECGEN-Eval", p.takeaway),
              field("Code", p.code, true),
              field("Paper", p.url, true),
              field("Extracted from", p.source),
            ]),
          ]),
        ]);
        function toggle() {
          detail.hidden = !detail.hidden;
          tr.classList.toggle("is-open", !detail.hidden);
        }
        tr.addEventListener("click", toggle);
        tr.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); }
        });
        body.appendChild(tr);
        body.appendChild(detail);
      });
      table.appendChild(el("table", {}, [el("thead", {}, [headRow]), body]));
    }

    function filtered() {
      return papers.filter(function (p) { return matchesExcept(p, null); });
    }

    function update() {
      var rows = filtered();
      count.textContent = rows.length + " of " + papers.length + " papers · database generated " +
        db.meta.generated + " (" + db.meta.scope + ")";
      renderFacets();
      summary.textContent = "";
      summary.appendChild(bars("Evaluation metrics", "metric_families", rows));
      summary.appendChild(bars("Loss functions", "loss_families", rows));
      renderTable(rows);
    }

    function csvCell(v) {
      v = Array.isArray(v) ? v.join("; ") : v === null || v === undefined ? "" : String(v);
      return '"' + v.replace(/"/g, '""') + '"';
    }

    search.addEventListener("input", function () {
      state.q = search.value.trim();
      update();
    });
    reset.addEventListener("click", function () {
      state.q = "";
      search.value = "";
      FACETS.forEach(function (f) { state.sel[f.key].clear(); state.mode[f.key] = "any"; });
      update();
    });
    dl.addEventListener("click", function () {
      var keys = ["id", "year", "title", "authors", "venue", "url", "category", "model_family", "task",
        "datasets", "loss_functions", "loss_families", "eval_metrics", "metric_families",
        "metric_types", "code", "notes", "takeaway"];
      var lines = [keys.join(",")].concat(filtered().map(function (p) {
        return keys.map(function (k) { return csvCell(p[k]); }).join(",");
      }));
      var blob = new Blob([lines.join("\n")], { type: "text/csv" });
      var a = el("a", { href: URL.createObjectURL(blob), download: "ecgen-literature-filtered.csv" });
      document.body.appendChild(a);
      a.click();
      a.remove();
    });
    update();
  }

  function boot() {
    var root = document.getElementById("litdb");
    if (root) init(root);
  }
  if (typeof document$ !== "undefined" && document$.subscribe) document$.subscribe(boot);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
