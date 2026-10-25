/* Literature database explorer for docs/literature/database.md.
 *
 * Opens ecgen_literature.sqlite (built by literature_review_claude/build_db.py) in the
 * browser with sql.js, then renders facet filters, live summary bars, an expandable paper
 * table and a read-only SQL console. Filter dimensions come from the `facets` table, so new
 * facets added to the database appear without code changes. Activates only on pages that
 * contain <div id="litdb" data-src="..." data-sqljs="...">.
 */
(function () {
  "use strict";

  var OPEN_BY_DEFAULT = ["category", "metric_type"];

  var EXAMPLES = [
    ["Metric usage and ECGEN-Eval coverage", "SELECT * FROM metric_usage;"],
    ["Papers using FID and a Turing test",
      "SELECT p.id, p.year, p.title\nFROM papers p\n" +
      "WHERE p.id IN (SELECT paper_id FROM paper_facets WHERE facet = 'metric' AND term = 'FID / embedding Fréchet')\n" +
      "  AND p.id IN (SELECT paper_id FROM paper_facets WHERE facet = 'metric' AND term = 'Expert / Turing test')\n" +
      "ORDER BY p.year DESC;"],
    ["Loss functions per category",
      "SELECT c.term AS category, l.term AS loss, COUNT(*) AS n_papers\n" +
      "FROM paper_facets c JOIN paper_facets l ON l.paper_id = c.paper_id\n" +
      "WHERE c.facet = 'category' AND l.facet = 'loss'\nGROUP BY 1, 2 ORDER BY 1, 3 DESC;"],
    ["Metrics not covered by ECGEN-Eval",
      "SELECT metric, metric_type, n_papers FROM metric_usage\nWHERE ecgen_eval IS NULL ORDER BY n_papers DESC;"],
    ["Papers per year and category",
      "SELECT p.year, f.term AS category, COUNT(*) AS n\nFROM papers p JOIN paper_facets f ON f.paper_id = p.id AND f.facet = 'category'\n" +
      "GROUP BY 1, 2 ORDER BY 1 DESC, 3 DESC;"],
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
      if (c) node.appendChild(c);
    });
    return node;
  }

  function rows(db, sql, params) {
    var stmt = db.prepare(sql);
    if (params) stmt.bind(params);
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
        var db = new res[0].Database(new Uint8Array(res[1]));
        render(root, db);
      })
      .catch(function (err) {
        root.textContent = "Could not load the literature database (" + err.message + ").";
      });
  }

  function loadModel(db) {
    var meta = {};
    rows(db, "SELECT key, value FROM meta").forEach(function (r) { meta[r.key] = r.value; });
    var facets = rows(db, "SELECT name, label, multi FROM facets ORDER BY sort_order");
    var byId = {};
    var papers = rows(db,
      "SELECT p.*, (SELECT group_concat(name, '|') FROM (SELECT a.name FROM paper_authors pa " +
      "JOIN authors a ON a.id = pa.author_id WHERE pa.paper_id = p.id ORDER BY pa.position)) AS authors " +
      "FROM papers p");
    papers.forEach(function (p) {
      p.authors = p.authors ? p.authors.split("|") : [];
      p.f = {};
      byId[p.id] = p;
    });
    rows(db, "SELECT paper_id, facet, term FROM paper_facets").forEach(function (r) {
      var p = byId[r.paper_id];
      if (!p) return;
      (p.f[r.facet] = p.f[r.facet] || []).push(r.term);
    });
    papers.forEach(function (p) { p.category = (p.f.category || [""])[0]; });
    return { meta: meta, facets: facets, papers: papers };
  }

  function render(root, db) {
    var model = loadModel(db);
    var papers = model.papers;
    var FACETS = model.facets;
    var state = { q: "", sel: {}, mode: {}, sort: "year", dir: -1 };
    FACETS.forEach(function (f) {
      state.sel[f.name] = new Set();
      state.mode[f.name] = "any";
    });

    function values(paper, facet) {
      return paper.f[facet.name] || [];
    }

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
    root.appendChild(sqlConsole(db));

    function matchesExcept(paper, skipKey) {
      if (state.q) {
        var hay = [
          paper.id, paper.title, paper.authors.join(" "), paper.venue, paper.model_family,
          paper.task, paper.datasets, paper.eval_metrics, paper.loss_functions, paper.notes,
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
        var all = {};
        papers.forEach(function (p) {
          var match = matchesExcept(p, f.name);
          values(p, f).forEach(function (v) {
            all[v] = true;
            if (match) counts[v] = (counts[v] || 0) + 1;
          });
        });
        var keys = Object.keys(all).sort(function (a, b) {
          if (f.name === "year") return b.localeCompare(a);
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
        var wasOpen = state.open && state.open[f.name];
        details.open = wasOpen !== undefined ? wasOpen :
          state.sel[f.name].size > 0 || OPEN_BY_DEFAULT.indexOf(f.name) >= 0;
        details.addEventListener("toggle", function () {
          state.open = state.open || {};
          state.open[f.name] = details.open;
        });
        facetBox.appendChild(details);
      });
    }

    function bars(title, facet, list) {
      var counts = {};
      list.forEach(function (p) {
        (p.f[facet] || []).forEach(function (v) {
          counts[v] = (counts[v] || 0) + 1;
        });
      });
      var top = Object.keys(counts)
        .sort(function (a, b) { return counts[b] - counts[a]; })
        .slice(0, 12);
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
      else dd.textContent = value;
      return el("div", {}, [el("dt", { text: label }), dd]);
    }

    function tags(list) {
      return el("span", { class: "litdb-tags" }, (list || []).map(function (t) {
        return el("span", { class: "litdb-tag", text: t });
      }));
    }

    function renderTable(list) {
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

      list.sort(function (a, b) {
        var x = a[state.sort], y = b[state.sort];
        if (x === y) return a.id.localeCompare(b.id);
        return (x > y ? 1 : -1) * state.dir;
      });

      var body = el("tbody");
      list.forEach(function (p) {
        var authors = p.authors.length > 3 ? p.authors.slice(0, 3).join(", ") + " et al." : p.authors.join(", ");
        var tr = el("tr", { class: "litdb-row", tabindex: "0", "aria-expanded": "false" }, [
          el("td", { text: p.id }),
          el("td", { text: p.year ? String(p.year) : "" }),
          el("td", {}, [
            el("span", { class: "litdb-title", text: p.title }),
            el("span", { class: "litdb-sub", text: [authors, p.venue].filter(Boolean).join(" · ") }),
          ]),
          el("td", { text: p.category }),
          el("td", {}, [tags(p.f.metric)]),
        ]);
        var shape = [p.n_leads && p.n_leads + " lead(s)", p.fs_hz && p.fs_hz + " Hz",
          p.signal_length_s && p.signal_length_s + " s"].filter(Boolean).join(" · ");
        var detail = el("tr", { class: "litdb-detail", hidden: "hidden" }, [
          el("td", { colspan: "5" }, [
            el("dl", {}, [
              field("Model family", p.model_family),
              field("Task", p.task),
              field("Loss functions", p.loss_functions),
              field("Loss families", (p.f.loss || []).join(", ")),
              field("Evaluation metrics", p.eval_metrics),
              field("Metric types", (p.f.metric_type || []).join(", ")),
              field("Embedding extractor", p.embedding_extractor),
              field("Datasets", p.datasets),
              field("Leads / fs / length", shape),
              field("Notes", p.notes),
              field("Takeaway for ECGEN-Eval", p.takeaway),
              field("Code", p.code_url, true),
              field("Paper", p.url, true),
              field("Extracted from", p.extraction_source),
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
        body.appendChild(tr);
        body.appendChild(detail);
      });
      table.appendChild(el("table", {}, [el("thead", {}, [headRow]), body]));
    }

    function filtered() {
      return papers.filter(function (p) { return matchesExcept(p, null); });
    }

    function update() {
      var list = filtered();
      count.textContent = list.length + " of " + papers.length + " papers · database generated " +
        model.meta.generated + " (" + model.meta.scope + ")";
      renderFacets();
      summary.textContent = "";
      summary.appendChild(bars("Evaluation metrics", "metric", list));
      summary.appendChild(bars("Loss functions", "loss", list));
      renderTable(list);
    }

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
        "datasets", "loss_functions", "eval_metrics", "code_url", "notes", "takeaway"];
      var facetCols = FACETS.filter(function (f) { return f.multi; }).map(function (f) { return f.name; });
      var lines = [cols.concat(facetCols).join(",")].concat(filtered().map(function (p) {
        return cols.map(function (k) { return csvCell(p[k]); })
          .concat(facetCols.map(function (k) { return csvCell(p.f[k]); })).join(",");
      }));
      download(lines.join("\n"), "ecgen-literature-filtered.csv");
    });
    update();
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
    var area = el("textarea", { class: "litdb-sql", rows: "6", spellcheck: "false",
      "aria-label": "SQL query" });
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
    return el("details", { class: "litdb-facet litdb-console" }, [
      el("summary", {}, [el("strong", { text: "SQL console (advanced)" })]),
      el("div", { class: "litdb-console-body" }, [
        el("p", { text: "Query the SQLite database directly. Pick an example or write your own " +
          "read-only query; Ctrl/Cmd + Enter runs it." }),
        el("div", { class: "litdb-toolbar" }, [pick, run, save]),
        area, msg, out,
      ]),
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
