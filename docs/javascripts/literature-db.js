/* Literature database explorer for docs/literature/database.md.
 *
 * Opens ecgen_literature.sqlite (built by literature_review_claude/build_db.py) in the
 * browser with sql.js and renders three views:
 *   - Papers: facet filters (built from the `facets` table), summary bars and an expandable
 *     paper table;
 *   - Metrics: metrics grouped by evaluation category (Fidelity, Utility, Privacy, Fairness,
 *     Robustness, ...) with the papers that use each one;
 *   - SQL: a read-only SQL console.
 * The URL hash deep-links to a view, e.g. #metrics/Privacy or #papers/P049.
 * Activates only on pages that contain <div id="litdb" data-src="..." data-sqljs="...">.
 */
(function () {
  "use strict";

  var OPEN_BY_DEFAULT = ["category", "eval_category", "data_type"];

  var EXAMPLES = [
    ["Metric usage per evaluation category", "SELECT * FROM metric_usage;"],
    ["Privacy evaluations (metric, how, paper)",
      "SELECT paper_id, year, metric_name, family, how\nFROM evaluation_details\n" +
      "WHERE category = 'Privacy'\nORDER BY year DESC;"],
    ["Papers with fairness or robustness analyses",
      "SELECT id, year, title, fairness, robustness\nFROM papers\n" +
      "WHERE fairness <> '' OR robustness <> ''\nORDER BY year DESC;"],
    ["Papers using FID and a Turing test",
      "SELECT p.id, p.year, p.title\nFROM papers p\n" +
      "WHERE p.id IN (SELECT paper_id FROM paper_facets WHERE facet = 'metric' AND term = 'FID / embedding Fréchet')\n" +
      "  AND p.id IN (SELECT paper_id FROM paper_facets WHERE facet = 'metric' AND term = 'Expert / Turing test')\n" +
      "ORDER BY p.year DESC;"],
    ["Metrics not covered by ECGEN-Eval",
      "SELECT category, metric, n_papers FROM metric_usage\nWHERE ecgen_eval IS NULL\nORDER BY n_papers DESC;"],
    ["12-lead papers by sampling rate",
      "SELECT f.term AS sampling_rate, COUNT(*) AS n_papers\nFROM paper_facets f\n" +
      "WHERE f.facet = 'sampling_rate'\n  AND f.paper_id IN (SELECT paper_id FROM paper_facets WHERE facet = 'leads' AND term = '12 leads')\n" +
      "GROUP BY 1 ORDER BY 2 DESC;"],
    ["Loss functions per model category",
      "SELECT c.term AS category, l.term AS loss, COUNT(*) AS n_papers\n" +
      "FROM paper_facets c JOIN paper_facets l ON l.paper_id = c.paper_id\n" +
      "WHERE c.facet = 'category' AND l.facet = 'loss'\nGROUP BY 1, 2 ORDER BY 1, 3 DESC;"],
    ["Schema", "SELECT type, name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%';"],
  ];

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else if (k === "class") node.className = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) {
      if (c) node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }

  function rows(db, sql) {
    var stmt = db.prepare(sql);
    var out = [];
    while (stmt.step()) out.push(stmt.getAsObject());
    stmt.free();
    return out;
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (window.initSqlJs) return resolve();
      var s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = function () { reject(new Error("could not load sql.js")); };
      document.head.appendChild(s);
    });
  }

  function init(root) {
    if (root.dataset.ready) return;
    root.dataset.ready = "1";
    var src = new URL(root.dataset.src, window.location.href).href;
    var sqljs = root.dataset.sqljs;
    var wasmDir = sqljs.slice(0, sqljs.lastIndexOf("/") + 1);
    root.textContent = "Loading literature database…";
    Promise.all([
      loadScript(sqljs).then(function () {
        return window.initSqlJs({ locateFile: function (f) { return wasmDir + f; } });
      }),
      fetch(src).then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.arrayBuffer();
      }),
    ])
      .then(function (res) {
        render(root, new res[0].Database(new Uint8Array(res[1])));
      })
      .catch(function (err) {
        root.textContent = "Could not load the literature database (" + err.message + ").";
      });
  }

  function loadModel(db) {
    var meta = {};
    rows(db, "SELECT key, value FROM meta").forEach(function (r) { meta[r.key] = r.value; });
    var facets = rows(db, "SELECT name, label, multi FROM facets ORDER BY sort_order");
    var categories = rows(db,
      "SELECT t.name, t.description FROM terms t JOIN facets f ON f.id = t.facet_id " +
      "WHERE f.name = 'eval_category' ORDER BY t.id");
    var ecgen = {};
    rows(db, "SELECT t.name, t.ecgen_eval FROM terms t JOIN facets f ON f.id = t.facet_id " +
      "WHERE f.name = 'metric'").forEach(function (r) { ecgen[r.name] = r.ecgen_eval || ""; });
    var byId = {};
    var papers = rows(db,
      "SELECT p.*, (SELECT group_concat(name, '|') FROM (SELECT a.name FROM paper_authors pa " +
      "JOIN authors a ON a.id = pa.author_id WHERE pa.paper_id = p.id ORDER BY pa.position)) AS authors " +
      "FROM papers p");
    papers.forEach(function (p) {
      p.authors = p.authors ? p.authors.split("|") : [];
      p.f = {};
      p.evals = [];
      byId[p.id] = p;
    });
    rows(db, "SELECT paper_id, facet, term FROM paper_facets").forEach(function (r) {
      var p = byId[r.paper_id];
      if (p) (p.f[r.facet] = p.f[r.facet] || []).push(r.term);
    });
    var evals = {};
    rows(db, "SELECT evaluation_id, paper_id, metric_name, family, category, how FROM evaluation_details")
      .forEach(function (r) {
        var e = evals[r.evaluation_id];
        if (!e) {
          e = evals[r.evaluation_id] = { paper: byId[r.paper_id], metric: r.metric_name,
            family: r.family, how: r.how || "", categories: [] };
          if (e.paper) e.paper.evals.push(e);
        }
        e.categories.push(r.category);
      });
    papers.forEach(function (p) { p.category = (p.f.category || [""])[0]; });
    return { meta: meta, facets: facets, categories: categories, ecgen: ecgen, papers: papers,
      byId: byId, evals: Object.keys(evals).map(function (k) { return evals[k]; }) };
  }

  function render(root, db) {
    var model = loadModel(db);
    var papers = model.papers;
    var FACETS = model.facets;
    var state = { q: "", sel: {}, mode: {}, sort: "year", dir: -1, open: {},
      tab: "papers", cat: "Fidelity", openMetrics: {} };
    FACETS.forEach(function (f) {
      state.sel[f.name] = new Set();
      state.mode[f.name] = "any";
    });

    function values(paper, facet) {
      return paper.f[facet.name] || [];
    }

    // ---------------------------------------------------------------- layout
    root.textContent = "";
    var tabs = {};
    var tabBar = el("div", { class: "litdb-tabs", role: "tablist" });
    var panels = {};
    [["papers", "Papers"], ["metrics", "Metrics by evaluation category"], ["sql", "SQL console"]]
      .forEach(function (t) {
        var b = el("button", { type: "button", role: "tab", class: "litdb-tab", text: t[1] });
        b.addEventListener("click", function () { showTab(t[0]); });
        tabs[t[0]] = b;
        tabBar.appendChild(b);
        panels[t[0]] = el("div", { class: "litdb-panel", role: "tabpanel" });
      });
    root.appendChild(tabBar);

    var search = el("input", { type: "search", class: "litdb-search",
      placeholder: "Search title, authors, metrics, losses, datasets…", "aria-label": "Search papers" });
    var reset = el("button", { class: "md-button litdb-reset", type: "button", text: "Reset filters" });
    var dl = el("button", { class: "md-button litdb-reset", type: "button", text: "Download CSV (filtered)" });
    var count = el("p", { class: "litdb-count" });
    var facetBox = el("div", { class: "litdb-facets" });
    var summary = el("div", { class: "litdb-summary" });
    var table = el("div", { class: "litdb-table" });
    // Filters in a left sidebar; results (count, summary charts, table) on the right.
    panels.papers.appendChild(el("div", { class: "litdb-layout" }, [
      el("aside", { class: "litdb-sidebar", "aria-label": "Filters" }, [
        search, el("div", { class: "litdb-toolbar" }, [reset, dl]), facetBox]),
      el("div", { class: "litdb-main" }, [count, summary, table]),
    ]));

    var catBar = el("div", { class: "litdb-chips litdb-catbar" });
    var catInfo = el("p", { class: "litdb-count" });
    var analyses = el("div");
    var metricTable = el("div", { class: "litdb-table" });
    [catInfo, catBar, analyses, metricTable].forEach(function (n) { panels.metrics.appendChild(n); });

    panels.sql.appendChild(sqlConsole(db));
    Object.keys(panels).forEach(function (k) { root.appendChild(panels[k]); });

    function showTab(name, noHash) {
      state.tab = name;
      Object.keys(panels).forEach(function (k) {
        panels[k].hidden = k !== name;
        tabs[k].classList.toggle("is-active", k === name);
        tabs[k].setAttribute("aria-selected", k === name ? "true" : "false");
      });
      if (name === "metrics") renderMetrics();
      if (!noHash) setHash();
    }

    function setHash() {
      var h = state.tab === "metrics" ? "#metrics/" + encodeURIComponent(state.cat) : "#" + state.tab;
      if (window.history && history.replaceState) history.replaceState(null, "", h);
    }

    // ---------------------------------------------------------------- papers view
    function matchesExcept(paper, skipKey) {
      if (state.q) {
        var hay = [
          paper.id, paper.title, paper.authors.join(" "), paper.venue, paper.model_family,
          paper.task, paper.datasets, paper.eval_metrics, paper.loss_functions, paper.notes,
          paper.fairness, paper.robustness, paper.privacy,
        ].join(" ").toLowerCase();
        var terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
        for (var i = 0; i < terms.length; i++) if (hay.indexOf(terms[i]) < 0) return false;
      }
      for (var j = 0; j < FACETS.length; j++) {
        var f = FACETS[j];
        if (f.name === skipKey) continue;
        var sel = state.sel[f.name];
        if (!sel.size) continue;
        var vals = values(paper, f);
        if (state.mode[f.name] === "all") {
          var ok = true;
          sel.forEach(function (s) { if (vals.indexOf(s) < 0) ok = false; });
          if (!ok) return false;
        } else if (!vals.some(function (v) { return sel.has(v); })) {
          return false;
        }
      }
      return true;
    }

    function filtered() {
      return papers.filter(function (p) { return matchesExcept(p, null); });
    }

    function renderFacets() {
      facetBox.textContent = "";
      FACETS.forEach(function (f) {
        var counts = {};
        var all = {};
        papers.forEach(function (p) {
          var match = matchesExcept(p, f.name);
          values(p, f).forEach(function (v) {
            all[v] = true;
            if (match) counts[v] = (counts[v] || 0) + 1;
          });
        });
        var order = f.name === "eval_category" ? model.categories.map(function (c) { return c.name; }) : null;
        var keys = Object.keys(all).sort(function (a, b) {
          if (f.name === "year") return b.localeCompare(a);
          if (order) return order.indexOf(a) - order.indexOf(b);
          if (a === "Not reported") return 1;
          if (b === "Not reported") return -1;
          return (counts[b] || 0) - (counts[a] || 0) || a.localeCompare(b);
        });
        if (!keys.length) return;
        var chips = keys.map(function (v) {
          var active = state.sel[f.name].has(v);
          var n = counts[v] || 0;
          var chip = el("button", {
            type: "button",
            class: "litdb-chip" + (active ? " is-active" : "") + (n ? "" : " is-empty"),
            "aria-pressed": active ? "true" : "false",
          }, [el("span", { text: v }), el("span", { class: "litdb-chip-n", text: String(n) })]);
          chip.addEventListener("click", function () {
            if (active) state.sel[f.name].delete(v);
            else state.sel[f.name].add(v);
            update();
          });
          return chip;
        });
        var head = el("div", { class: "litdb-facet-head" }, [el("strong", { text: f.label })]);
        if (state.sel[f.name].size) {
          head.appendChild(el("span", { class: "litdb-chip-n", text: state.sel[f.name].size + " selected" }));
        }
        if (f.multi) {
          var mode = el("button", {
            type: "button",
            class: "litdb-mode",
            title: "Toggle between papers matching ANY or ALL selected values",
            text: state.mode[f.name] === "all" ? "match ALL" : "match ANY",
          });
          mode.addEventListener("click", function (e) {
            e.preventDefault();
            state.mode[f.name] = state.mode[f.name] === "all" ? "any" : "all";
            update();
          });
          head.appendChild(mode);
        }
        var details = el("details", { class: "litdb-facet", "data-facet": f.name }, [
          el("summary", {}, [head]),
          el("div", { class: "litdb-chips" }, chips),
        ]);
        var wasOpen = state.open[f.name];
        details.open = wasOpen !== undefined ? wasOpen :
          state.sel[f.name].size > 0 || OPEN_BY_DEFAULT.indexOf(f.name) >= 0;
        details.addEventListener("toggle", function () { state.open[f.name] = details.open; });
        facetBox.appendChild(details);
      });
    }

    function bars(title, facet, list) {
      var counts = {};
      list.forEach(function (p) {
        (p.f[facet] || []).forEach(function (v) { counts[v] = (counts[v] || 0) + 1; });
      });
      var top = Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a]; }).slice(0, 12);
      var max = top.length ? counts[top[0]] : 1;
      var items = top.map(function (k) {
        var bar = el("span", { class: "litdb-bar-fill" });
        bar.style.width = (100 * counts[k] / max).toFixed(1) + "%";
        return el("div", { class: "litdb-bar" }, [
          el("span", { class: "litdb-bar-label", text: k, title: k }),
          el("span", { class: "litdb-bar-track" }, [bar]),
          el("span", { class: "litdb-bar-n", text: String(counts[k]) }),
        ]);
      });
      return el("div", { class: "litdb-card" }, [el("strong", { text: title })].concat(
        items.length ? items : [el("p", { text: "No papers match." })]));
    }

    function field(label, value, link) {
      if (!value) return null;
      var dd = el("dd");
      if (link) dd.appendChild(el("a", { href: value, target: "_blank", rel: "noopener", text: value }));
      else if (value.nodeType) dd.appendChild(value);
      else dd.textContent = value;
      return el("div", {}, [el("dt", { text: label }), dd]);
    }

    function tags(list) {
      return el("span", { class: "litdb-tags" }, (list || []).map(function (t) {
        return el("span", { class: "litdb-tag", text: t });
      }));
    }

    function evalTable(p) {
      if (!p.evals.length) return null;
      return el("table", { class: "litdb-evals" }, [
        el("thead", {}, [el("tr", {}, ["Metric (as in paper)", "Family", "Category", "How"]
          .map(function (h) { return el("th", { text: h }); }))]),
        el("tbody", {}, p.evals.map(function (e) {
          return el("tr", {}, [el("td", { text: e.metric }), el("td", { text: e.family }),
            el("td", { text: e.categories.join(", ") }), el("td", { text: e.how })]);
        })),
      ]);
    }

    function renderTable(list) {
      table.textContent = "";
      var cols = [
        { key: "id", label: "ID" },
        { key: "year", label: "Year" },
        { key: "title", label: "Paper" },
        { key: "category", label: "Model category" },
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
      }).concat([el("th", { scope: "col", text: "Evaluation categories" })]));

      list.sort(function (a, b) {
        var x = a[state.sort], y = b[state.sort];
        if (x === y) return a.id.localeCompare(b.id);
        return (x > y ? 1 : -1) * state.dir;
      });

      var body = el("tbody");
      list.forEach(function (p) {
        var authors = p.authors.length > 3 ? p.authors.slice(0, 3).join(", ") + " et al." : p.authors.join(", ");
        var tr = el("tr", { class: "litdb-row", tabindex: "0", "aria-expanded": "false", id: "litdb-" + p.id }, [
          el("td", { text: p.id }),
          el("td", { text: p.year ? String(p.year) : "" }),
          el("td", {}, [
            el("span", { class: "litdb-title", text: p.title }),
            el("span", { class: "litdb-sub", text: [authors, p.venue].filter(Boolean).join(" · ") }),
          ]),
          el("td", { text: p.category }),
          el("td", {}, [tags(p.f.eval_category)]),
        ]);
        var shape = [
          (p.f.leads || [])[0], (p.f.sampling_rate || [])[0], (p.f.segment_length || [])[0],
        ].filter(function (v) { return v && v !== "Not reported"; }).join(" · ");
        var detail = el("tr", { class: "litdb-detail", hidden: "hidden" }, [
          el("td", { colspan: "5" }, [
            el("dl", {}, [
              field("Model family", p.model_family),
              field("Task", p.task),
              field("Conditioning", (p.f.conditioning || []).join(", ")),
              field("Data type / format", (p.f.data_type || []).concat(p.f.data_format || []).join(", ")),
              field("Leads · sampling rate · segment", shape),
              field("Datasets", p.datasets),
              field("Data access", (p.f.data_access || [])[0]),
              field("Loss functions", p.loss_functions),
              field("Loss families", (p.f.loss || []).join(", ")),
              field("Evaluations", evalTable(p)),
              field("Fairness analysis", p.fairness),
              field("Robustness analysis", p.robustness),
              field("Privacy analysis", p.privacy),
              field("Embedding extractor", p.embedding_extractor),
              field("Notes", p.notes),
              field("Takeaway for ECGEN-Eval", p.takeaway),
              field("Code", p.code_url, true),
              field("Paper", p.url, true),
            ]),
          ]),
        ]);
        function toggle() {
          detail.hidden = !detail.hidden;
          tr.classList.toggle("is-open", !detail.hidden);
          tr.setAttribute("aria-expanded", detail.hidden ? "false" : "true");
        }
        tr.addEventListener("click", toggle);
        tr.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); }
        });
        tr._toggle = toggle;
        body.appendChild(tr);
        body.appendChild(detail);
      });
      table.appendChild(el("table", {}, [el("thead", {}, [headRow]), body]));
    }

    function update() {
      var list = filtered();
      count.textContent = list.length + " of " + papers.length + " papers · database generated " +
        model.meta.generated + " (" + model.meta.scope + ")";
      renderFacets();
      summary.textContent = "";
      summary.appendChild(bars("Evaluation categories", "eval_category", list));
      summary.appendChild(bars("Evaluation metrics", "metric", list));
      summary.appendChild(bars("Loss functions", "loss", list));
      renderTable(list);
      if (state.tab === "metrics") renderMetrics();
    }

    function openPaper(id) {
      search.value = id;
      state.q = id;
      FACETS.forEach(function (f) { state.sel[f.name].clear(); });
      showTab("papers");
      update();
      var tr = document.getElementById("litdb-" + id);
      if (tr) {
        tr._toggle();
        tr.scrollIntoView({ block: "center" });
      }
      if (window.history && history.replaceState) history.replaceState(null, "", "#papers/" + id);
    }

    // ---------------------------------------------------------------- metrics view
    function paperLink(p) {
      var a = el("a", { href: "#papers/" + p.id, text: p.id });
      a.addEventListener("click", function (e) { e.preventDefault(); openPaper(p.id); });
      return a;
    }

    function renderMetrics() {
      var list = filtered();
      var inSet = {};
      list.forEach(function (p) { inSet[p.id] = true; });
      var evals = model.evals.filter(function (e) { return e.paper && inSet[e.paper.id]; });

      var perCat = {};
      evals.forEach(function (e) {
        e.categories.forEach(function (c) { (perCat[c] = perCat[c] || {})[e.paper.id] = true; });
      });
      list.forEach(function (p) {
        [["fairness", "Fairness"], ["robustness", "Robustness"], ["privacy", "Privacy"]].forEach(function (k) {
          if (p[k[0]]) (perCat[k[1]] = perCat[k[1]] || {})[p.id] = true;
        });
      });

      catBar.textContent = "";
      model.categories.forEach(function (c) {
        var n = Object.keys(perCat[c.name] || {}).length;
        var active = state.cat === c.name;
        var chip = el("button", {
          type: "button", title: c.description || "",
          class: "litdb-chip litdb-catchip" + (active ? " is-active" : "") + (n ? "" : " is-empty"),
          "aria-pressed": active ? "true" : "false",
        }, [el("span", { text: c.name }), el("span", { class: "litdb-chip-n", text: n + " papers" })]);
        chip.addEventListener("click", function () {
          state.cat = c.name;
          state.openMetrics = {};
          setHash();
          renderMetrics();
        });
        catBar.appendChild(chip);
      });
      var desc = (model.categories.filter(function (c) { return c.name === state.cat; })[0] || {}).description;
      catInfo.textContent = (desc ? state.cat + ": " + desc + ". " : "") + "Based on " + list.length +
        " of " + papers.length + " papers (the filters on the Papers tab also apply here).";

      // Paper-level analyses (fairness / robustness / privacy free-text descriptions).
      analyses.textContent = "";
      var key = { Fairness: "fairness", Robustness: "robustness", Privacy: "privacy" }[state.cat];
      if (key) {
        var withText = list.filter(function (p) { return p[key]; })
          .sort(function (a, b) { return (b.year || 0) - (a.year || 0); });
        var det = el("details", { class: "litdb-facet" }, [
          el("summary", {}, [el("strong", { text: state.cat + " analyses described in papers (" + withText.length + ")" })]),
          el("ul", { class: "litdb-analyses" }, withText.map(function (p) {
            return el("li", {}, [paperLink(p), " (" + (p.year || "") + ") ",
              el("em", { text: p.title }), el("br"), el("span", { text: p[key] })]);
          })),
        ]);
        det.open = withText.length > 0 && withText.length <= 15;
        if (withText.length) analyses.appendChild(det);
      }

      // Metric families in this category with the papers using them.
      var fams = {};
      evals.forEach(function (e) {
        if (e.categories.indexOf(state.cat) < 0) return;
        var f = fams[e.family] = fams[e.family] || { name: e.family, evals: [], papers: {} };
        f.evals.push(e);
        f.papers[e.paper.id] = true;
      });
      var famList = Object.keys(fams).map(function (k) { return fams[k]; })
        .sort(function (a, b) {
          return Object.keys(b.papers).length - Object.keys(a.papers).length || a.name.localeCompare(b.name);
        });

      metricTable.textContent = "";
      if (!famList.length) {
        metricTable.appendChild(el("p", { text: "No metrics in this category for the current filters." }));
        return;
      }
      var body = el("tbody");
      famList.forEach(function (f) {
        var n = Object.keys(f.papers).length;
        var names = {};
        f.evals.forEach(function (e) { names[e.metric] = true; });
        var cov = model.ecgen[f.name];
        var tr = el("tr", { class: "litdb-row", tabindex: "0" }, [
          el("td", {}, [el("span", { class: "litdb-title", text: f.name }),
            el("span", { class: "litdb-sub", text: Object.keys(names).slice(0, 6).join(" · ") })]),
          el("td", { class: "litdb-num", text: String(n) }),
          el("td", {}, [cov ? el("code", { text: cov }) : el("span", { class: "litdb-sub", text: "not yet" })]),
        ]);
        var evRows = f.evals.slice().sort(function (a, b) { return (b.paper.year || 0) - (a.paper.year || 0); });
        var detail = el("tr", { class: "litdb-detail" }, [el("td", { colspan: "3" }, [
          el("table", { class: "litdb-evals" }, [
            el("thead", {}, [el("tr", {}, ["Paper", "Year", "Metric (as in paper)", "How it was used"]
              .map(function (h) { return el("th", { text: h }); }))]),
            el("tbody", {}, evRows.map(function (e) {
              return el("tr", {}, [
                el("td", {}, [paperLink(e.paper), el("span", { class: "litdb-sub", text: e.paper.title })]),
                el("td", { text: e.paper.year ? String(e.paper.year) : "" }),
                el("td", { text: e.metric }),
                el("td", { text: e.how }),
              ]);
            })),
          ]),
        ])]);
        detail.hidden = !state.openMetrics[f.name];
        tr.classList.toggle("is-open", !detail.hidden);
        function toggle() {
          detail.hidden = !detail.hidden;
          state.openMetrics[f.name] = !detail.hidden;
          tr.classList.toggle("is-open", !detail.hidden);
        }
        tr.addEventListener("click", toggle);
        tr.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); }
        });
        body.appendChild(tr);
        body.appendChild(detail);
      });
      metricTable.appendChild(el("table", {}, [
        el("thead", {}, [el("tr", {}, [el("th", { text: "Metric family (names used in papers)" }),
          el("th", { text: "Papers" }), el("th", { text: "In ECGEN-Eval" })])]),
        body,
      ]));
    }

    // ---------------------------------------------------------------- events
    search.addEventListener("input", function () {
      state.q = search.value.trim();
      update();
    });
    reset.addEventListener("click", function () {
      state.q = "";
      search.value = "";
      FACETS.forEach(function (f) { state.sel[f.name].clear(); state.mode[f.name] = "any"; });
      update();
    });
    dl.addEventListener("click", function () {
      var cols = ["id", "year", "title", "authors", "venue", "url", "category", "model_family", "task",
        "datasets", "loss_functions", "eval_metrics", "fairness", "robustness", "privacy", "code_url",
        "notes", "takeaway"];
      var facetCols = FACETS.filter(function (f) {
        return ["category", "year"].indexOf(f.name) < 0;
      }).map(function (f) { return f.name; });
      var lines = [cols.concat(facetCols).join(",")].concat(filtered().map(function (p) {
        return cols.map(function (k) { return csvCell(p[k]); })
          .concat(facetCols.map(function (k) { return csvCell(p.f[k]); })).join(",");
      }));
      download(lines.join("\n"), "ecgen-literature-filtered.csv");
    });

    function route(e) {
      var raw = decodeURIComponent((window.location.hash || "").slice(1));
      var cut = raw.indexOf("/");
      var h = cut < 0 ? [raw] : [raw.slice(0, cut), raw.slice(cut + 1)];
      if (h[0] === "metrics") {
        if (h[1] && model.categories.some(function (c) { return c.name === h[1]; })) state.cat = h[1];
        showTab("metrics", true);
        if (e) root.scrollIntoView({ block: "start" });
      } else if (h[0] === "papers" && h[1] && model.byId[h[1]]) {
        openPaper(h[1]);
      } else if (h[0] === "sql" || h[0] === "papers") {
        showTab(h[0], true);
      } else if (!state.routed) {
        showTab("papers", true);
      }
      state.routed = true;
    }

    update();
    route();
    window.addEventListener("hashchange", route);
  }

  function csvCell(v) {
    v = Array.isArray(v) ? v.join("; ") : v === null || v === undefined ? "" : String(v);
    return '"' + v.replace(/"/g, '""') + '"';
  }

  function download(text, name) {
    var a = el("a", { href: URL.createObjectURL(new Blob([text], { type: "text/csv" })), download: name });
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  function sqlConsole(db) {
    var area = el("textarea", { class: "litdb-sql", rows: "7", spellcheck: "false", "aria-label": "SQL query" });
    area.value = EXAMPLES[0][1];
    var pick = el("select", { class: "litdb-select", "aria-label": "Example queries" },
      EXAMPLES.map(function (e, i) { return el("option", { value: String(i), text: e[0] }); }));
    var run = el("button", { class: "md-button md-button--primary litdb-reset", type: "button", text: "Run query" });
    var save = el("button", { class: "md-button litdb-reset", type: "button", text: "Download result (CSV)" });
    var msg = el("p", { class: "litdb-count" });
    var out = el("div", { class: "litdb-table litdb-sql-out" });
    var last = null;

    function exec() {
      out.textContent = "";
      last = null;
      try {
        var sql = area.value.trim();
        if (!/^(select|with|pragma|explain)\b/i.test(sql)) {
          throw new Error("only read-only queries (SELECT / WITH / PRAGMA / EXPLAIN) are allowed");
        }
        var res = db.exec(sql);
        if (!res.length) { msg.textContent = "Query returned no rows."; return; }
        var r = res[res.length - 1];
        last = r;
        msg.textContent = r.values.length + " row(s)" + (r.values.length > 500 ? " (showing first 500)" : "");
        var head = el("tr", {}, r.columns.map(function (c) { return el("th", { text: c }); }));
        var body = el("tbody", {}, r.values.slice(0, 500).map(function (row) {
          return el("tr", {}, row.map(function (v) { return el("td", { text: v === null ? "" : String(v) }); }));
        }));
        out.appendChild(el("table", {}, [el("thead", {}, [head]), body]));
      } catch (err) {
        msg.textContent = "Error: " + err.message;
      }
    }

    pick.addEventListener("change", function () { area.value = EXAMPLES[+pick.value][1]; exec(); });
    run.addEventListener("click", exec);
    area.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); exec(); }
    });
    save.addEventListener("click", function () {
      if (!last) return;
      download([last.columns.map(csvCell).join(",")].concat(last.values.map(function (row) {
        return row.map(csvCell).join(",");
      })).join("\n"), "ecgen-literature-query.csv");
    });
    exec();
    return el("div", {}, [
      el("p", { text: "Query the SQLite database directly (tables: papers, evaluations, " +
        "evaluation_categories, facets, terms, paper_terms, authors; views: paper_facets, " +
        "evaluation_details, metric_usage). Pick an example or write a read-only query; " +
        "Ctrl/Cmd + Enter runs it." }),
      el("div", { class: "litdb-toolbar" }, [pick, run, save]),
      area, msg, out,
    ]);
  }

  function boot() {
    var root = document.getElementById("litdb");
    if (root) init(root);
  }
  if (typeof document$ !== "undefined" && document$.subscribe) document$.subscribe(boot);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
