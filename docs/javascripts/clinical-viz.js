/*
 * Interactive explainers for the "Clinical Features Explained" pages (docs/clinical/*.md).
 *
 *   <div class="mviz" data-viz="beatAnatomy">            one heartbeat, its parts and the heart
 *   <div class="mviz" data-viz="clinical" data-focus=F>  one feature; F is hr, p, pr, qrs, qt,
 *                                                        st, t or hrv
 *
 * The beat is a schematic model built from clinical parameters (PR, QRS, QT, ...), so every
 * interval drawn is exactly the value shown. Builds on the toolkit exported by metric-viz.js.
 */
(function () {
  "use strict";

  var V = window.ECGViz;
  if (!V) return;
  var el = V.el, sv = V.sv, fmt = V.fmt;

  // ------------------------------------------------------------------ beat model

  // Times in ms relative to QRS onset, amplitudes in mV.
  var NORMAL = { pr: 160, pd: 100, pa: 0.15, qrs: 90, ra: 1.0, st: 0, qt: 390, ta: 0.3 };

  function params(o) { return Object.assign({}, NORMAL, o || {}); }

  // Cosine-eased interpolation through [u, v] knots (zero slope at every knot).
  function ease(knots, u) {
    for (var i = 1; i < knots.length; i++) {
      if (u <= knots[i][0]) {
        var a = knots[i - 1], b = knots[i], w = (u - a[0]) / (b[0] - a[0]);
        return a[1] + (b[1] - a[1]) * 0.5 * (1 - Math.cos(Math.PI * w));
      }
    }
    return knots[knots.length - 1][1];
  }

  // T wave spans the last 62 % of the ST–T stretch and peaks at 60 % of its width.
  function tOnset(o) { return Math.max(o.qrs + 10, o.qt - Math.max(80, 0.62 * (o.qt - o.qrs))); }

  function beatValue(o, t) {
    var v = 0, u = (t + o.pr) / o.pd;
    if (u > 0 && u < 1) v += o.pa * 0.5 * (1 - Math.cos(2 * Math.PI * u));
    if (t >= 0 && t <= o.qrs) {
      v += ease([[0, 0], [0.18, -0.08], [0.45, o.ra], [0.72, -0.25], [1, o.st]], t / o.qrs);
    } else if (t > o.qrs && t < o.qt) {
      var on = tOnset(o), dur = o.qt - on;
      v += t <= on ? o.st : o.st * (1 - (t - on) / dur);
      if (t > on) {
        var s = Math.sin(Math.PI * Math.pow((t - on) / dur, 1.36));
        v += o.ta * s * s;
      }
    }
    return v;
  }

  function tPeak(o) { var on = tOnset(o); return on + 0.6 * (o.qt - on); }
  function rPeak(o) { return 0.45 * o.qrs; }

  // ------------------------------------------------------------------ ECG paper

  // ECG paper: 1 small box = 40 ms × 0.1 mV, 1 big box = 200 ms × 0.5 mV. With h omitted the
  // boxes are square, as on real paper.
  function paper(t0, t1, v0, v1, w, h) {
    var m = { l: 8, r: 8, t: 8, b: 22 }, k = (w - m.l - m.r) / (t1 - t0);
    var p = V.plot(w, h || Math.round((v1 - v0) * 400 * k) + m.t + m.b, m, [t0, t1], [v0, v1]);
    var minor = "", major = "", i;
    for (i = Math.ceil(t0 / 40); i * 40 <= t1; i++) {
      var X = p.X(i * 40).toFixed(1), seg = "M" + X + " " + m.t + "V" + (p.h - m.b);
      if (i % 5 === 0) major += seg; else minor += seg;
    }
    for (i = Math.ceil(v0 * 10 - 1e-9); i <= v1 * 10 + 1e-9; i++) {
      var Y = p.Y(i / 10).toFixed(1), sg = "M" + m.l + " " + Y + "H" + (p.w - m.r);
      if (i % 5 === 0) major += sg; else minor += sg;
    }
    p.svg.appendChild(sv("path", { d: minor, class: "cv-grid" }));
    p.svg.appendChild(sv("path", { d: major, class: "cv-grid cv-grid-major" }));
    return p;
  }

  function trace(p, f, t0, t1, cls) {
    var d = "", step = (t1 - t0) / 900;
    for (var t = t0, i = 0; t <= t1 + 1e-9; t += step, i++) {
      d += (i ? "L" : "M") + p.X(t).toFixed(1) + " " + p.Y(f(t)).toFixed(1);
    }
    var path = sv("path", { d: d, class: cls || "cv-trace" });
    p.svg.appendChild(path);
    return path;
  }

  function label(p, x, y, s, cls, anchor) {
    p.svg.appendChild(sv("text", { x: x.toFixed(1), y: y.toFixed(1), class: cls || "cv-wave-lab",
      "text-anchor": anchor || "middle", text: s }));
  }

  // Shaded time span with a double-headed bracket and a label above it.
  function span(p, a, b, txt, row) {
    var X0 = p.X(a), X1 = p.X(b), y = p.m.t + 12 + 22 * (row || 0);
    p.svg.appendChild(sv("rect", { x: X0.toFixed(1), y: p.m.t, width: Math.max(0, X1 - X0).toFixed(1),
      height: p.h - p.m.t - p.m.b, class: "cv-band" }));
    p.svg.appendChild(sv("path", { d: "M" + X0 + " " + (y + 6) + "V" + (y - 6) + "M" + X1 + " " + (y + 6) + "V" + (y - 6) +
      "M" + X0 + " " + y + "H" + X1, class: "cv-caliper" }));
    var lab = sv("text", { x: ((X0 + X1) / 2).toFixed(1), y: y - 4, class: "cv-cal-lab", "text-anchor": "middle", text: txt });
    p.svg.appendChild(lab);
  }

  // Vertical arrow from the baseline to a measured level at time t.
  function rise(p, t, v0, v1, txt) {
    var X = p.X(t), Y0 = p.Y(v0), Y1 = p.Y(v1), dir = v1 >= v0 ? 1 : -1;
    p.svg.appendChild(sv("path", { d: "M" + X + " " + Y0 + "V" + Y1, class: "cv-caliper" }));
    if (Math.abs(Y1 - Y0) > 6) {
      p.svg.appendChild(sv("path", { d: "M" + (X - 4) + " " + (Y1 + 6 * dir) + "L" + X + " " + Y1 + "L" + (X + 4) + " " + (Y1 + 6 * dir),
        class: "cv-caliper" }));
    }
    p.svg.appendChild(sv("circle", { cx: X, cy: Y1, r: 3.5, class: "cv-mark" }));
    var small = Math.abs(Y1 - Y0) < 24;
    label(p, small ? X - 8 : X + 8, small ? Math.min(Y0, Y1) - 10 : (Y0 + Y1) / 2 + 4, txt, "cv-cal-lab", small ? "end" : "start");
  }

  function baseline(p, t0, t1, txt) {
    p.svg.appendChild(sv("path", { d: "M" + p.X(t0) + " " + p.Y(0) + "H" + p.X(t1), class: "cv-base" }));
    if (txt) label(p, p.X(t0) + 4, p.Y(0) + 14, txt, "cv-note", "start");
  }

  function scaleNote(p, txt) {
    label(p, p.m.l, p.h - 6, txt || "1 small box = 40 ms × 0.1 mV · 1 big box = 0.2 s × 0.5 mV", "cv-note", "start");
  }

  // Horizontal range bar: coloured zones, a marker at the value and the zone it falls in.
  function gauge(g) {
    var w = 640, h = 82, l = 10, r = 10, y = 44, bh = 12;
    var X = function (v) { return l + ((Math.min(g.max, Math.max(g.min, v)) - g.min) / (g.max - g.min)) * (w - l - r); };
    var svg = sv("svg", { viewBox: "0 0 " + w + " " + h, class: "mviz-svg cv-gauge", role: "img",
      "aria-label": g.title + ": " + g.valueText });
    svg.appendChild(sv("text", { x: l, y: 12, class: "cv-note", text: g.title }));
    g.zones.forEach(function (z) {
      svg.appendChild(sv("rect", { x: X(z[0]).toFixed(1), y: y, width: (X(z[1]) - X(z[0])).toFixed(1), height: bh,
        class: "cv-zone cv-zone-" + z[3] }));
      svg.appendChild(sv("text", { x: ((X(z[0]) + X(z[1])) / 2).toFixed(1), y: y + bh + 14, class: "cv-zone-lab",
        "text-anchor": "middle", text: z[2] }));
    });
    if (isFinite(g.value)) {
      var mx = X(g.value);
      svg.appendChild(sv("path", { d: "M" + (mx - 6) + " " + (y - 9) + "L" + (mx + 6) + " " + (y - 9) + "L" + mx + " " + (y - 1) + "Z",
        class: "cv-marker" }));
      svg.appendChild(sv("text", { x: Math.min(w - r, Math.max(l, mx)).toFixed(1), y: y - 12, class: "cv-cal-lab",
        "text-anchor": mx > w - 60 ? "end" : mx < 60 ? "start" : "middle", text: g.valueText }));
    }
    return svg;
  }

  function zoneOf(zones, v) {
    if (!isFinite(v)) return null;
    for (var i = 0; i < zones.length; i++) if (v < zones[i][1] || i === zones.length - 1) return zones[i];
    return null;
  }

  // ------------------------------------------------------------------ heart schematic

  function heart() {
    var svg = sv("svg", { viewBox: "0 0 200 236", class: "cv-heart", role: "img",
      "aria-label": "Schematic heart: two upper chambers (atria), two lower chambers (ventricles), SA node and AV node" });
    var parts = {};
    function add(key, tag, attrs) { var n = sv(tag, attrs); svg.appendChild(n); parts[key] = n; return n; }
    svg.appendChild(sv("path", { class: "cv-heart-out",
      d: "M100 222 C 40 182, 8 132, 16 84 C 22 44, 60 28, 86 44 L100 54 L114 44 C 140 28, 178 44, 184 84 C 192 132, 160 182, 100 222 Z" }));
    add("ra", "ellipse", { cx: 62, cy: 78, rx: 33, ry: 22, class: "cv-chamber" });
    add("la", "ellipse", { cx: 138, cy: 78, rx: 33, ry: 22, class: "cv-chamber" });
    add("rv", "path", { d: "M27 116 L96 116 L96 205 C 66 186 36 156 27 113 Z", class: "cv-chamber" });
    add("lv", "path", { d: "M173 116 L104 116 L104 205 C 134 186 164 156 173 113 Z", class: "cv-chamber" });
    add("wire", "path", { d: "M100 110 L100 160 M100 160 C 86 176 58 168 44 134 M100 160 C 114 176 142 168 156 134",
      class: "cv-wire" });
    add("sa", "circle", { cx: 46, cy: 64, r: 6, class: "cv-node" });
    add("av", "circle", { cx: 100, cy: 104, r: 6, class: "cv-node" });
    [["Atria", 62, 82], ["Atria", 138, 82], ["Ventricles", 62, 160], ["Ventricles", 138, 160]].forEach(function (t) {
      svg.appendChild(sv("text", { x: t[1], y: t[2], class: "cv-heart-lab", "text-anchor": "middle", text: t[0] }));
    });
    svg.appendChild(sv("text", { x: 6, y: 30, class: "cv-heart-lab", "text-anchor": "start", text: "SA node (pacemaker)" }));
    svg.appendChild(sv("text", { x: 109, y: 110, class: "cv-heart-lab", "text-anchor": "start", text: "AV node (gate)" }));
    var sub = el("div", { class: "cv-heart-state" });
    return { svg: svg, parts: parts, state: sub };
  }

  // ------------------------------------------------------------------ beat anatomy (overview)

  var SEGMENTS = [
    { key: "p", name: "P wave", a: function (o) { return -o.pr; }, b: function (o) { return -o.pr + o.pd; },
      on: { sa: "on", ra: "on", la: "on" }, state: "Upper chambers (atria) activated",
      text: "The heart's built-in pacemaker, the SA node, fires. An electrical wave spreads across the " +
        "two upper chambers (the atria), and they squeeze blood down into the lower chambers.",
      feats: [["P-wave duration", "p-wave.md"]] },
    { key: "pq", name: "PR segment", a: function (o) { return -o.pr + o.pd; }, b: function () { return 0; },
      on: { av: "on" }, state: "Signal held at the AV node",
      text: "The signal reaches the AV node, a gate between upper and lower chambers. It holds the " +
        "signal back for a moment so the lower chambers can finish filling. The line is flat because " +
        "the signal is passing through tissue too small to show up on the ECG.",
      feats: [["PR interval", "pr-interval.md"]] },
    { key: "qrs", name: "QRS complex", a: function () { return 0; }, b: function (o) { return o.qrs; },
      on: { wire: "on", rv: "on", lv: "on" }, state: "Lower chambers (ventricles) activated",
      text: "The signal races down special fast wiring and through the thick walls of the two lower " +
        "chambers (the ventricles), which start the main pumping stroke. It is the biggest spike " +
        "because the ventricles are the largest muscle in the heart.",
      feats: [["QRS duration", "qrs-duration.md"], ["Heart rate (R peaks)", "heart-rate.md"]] },
    { key: "st", name: "ST segment", a: function (o) { return o.qrs; }, b: function (o) { return tOnset(o); },
      on: { rv: "hold", lv: "hold" }, state: "Ventricles fully activated, squeezing",
      text: "Every ventricle cell is activated at once and the ventricles are squeezing. Electrically " +
        "nothing is changing, so the line should sit close to the baseline.",
      feats: [["ST deviation", "st-deviation.md"]] },
    { key: "t", name: "T wave", a: function (o) { return tOnset(o); }, b: function (o) { return o.qt; },
      on: { rv: "rec", lv: "rec" }, state: "Ventricles recharging (recovering)",
      text: "The ventricles electrically reset ('recharge') so they are ready for the next beat. The " +
        "QT interval measures the whole activate-and-recover cycle of the ventricles.",
      feats: [["T-wave amplitude", "t-wave.md"], ["QT / QTc", "qt-qtc.md"]] },
    { key: "rest", name: "Rest (TP)", a: function (o) { return o.qt; }, b: function () { return 700; },
      on: {}, state: "Heart relaxing and refilling",
      text: "The heart relaxes and refills with blood until the pacemaker fires again. When the heart " +
        "speeds up, this pause is what shrinks most. The time from one beat to the next gives the heart " +
        "rate, and how much it varies from beat to beat gives the heart-rate variability.",
      feats: [["Heart rate / RR", "heart-rate.md"], ["Heart-rate variability", "hrv.md"]] },
  ];

  function anatomy(root) {
    root.textContent = "";
    root.classList.add("mviz-ready");
    var o = params(), T0 = -320, T1 = 700;
    var bar = el("div", { class: "mviz-presets" });
    var p = paper(T0, T1, -0.4, 1.2, 640);
    var hl = sv("rect", { y: p.m.t, height: p.h - p.m.t - p.m.b, class: "cv-band", width: 0 });
    p.svg.appendChild(hl);
    p.svg.appendChild(sv("path", { d: "M" + p.X(T0) + " " + p.Y(0) + "H" + p.X(T1), class: "cv-base" }));
    trace(p, function (t) { return beatValue(o, t); }, T0, T1);
    var rq = rPeak(o);
    [["P", -o.pr + o.pd / 2, o.pa, -1], ["Q", 0.18 * o.qrs, -0.08, 1], ["R", rq, o.ra, -1],
      ["S", 0.72 * o.qrs, -0.25, 1], ["T", tPeak(o), o.ta, -1]].forEach(function (w) {
      label(p, p.X(w[1]), p.Y(w[2]) + (w[3] < 0 ? -8 : 16), w[0], "cv-wave-lab");
    });
    scaleNote(p);
    var cursor = sv("path", { class: "cv-cursor", d: "" });
    p.svg.appendChild(cursor);

    var h = heart(), cap = el("div", { class: "cv-caption", "aria-live": "polite" });
    var btns = {}, current = null;

    function select(seg) {
      current = seg;
      hl.setAttribute("x", p.X(Math.max(T0, seg.a(o))).toFixed(1));
      hl.setAttribute("width", Math.max(0, p.X(seg.b(o)) - p.X(Math.max(T0, seg.a(o)))).toFixed(1));
      Object.keys(h.parts).forEach(function (k) {
        h.parts[k].classList.remove("is-on", "is-hold", "is-rec");
        if (seg.on[k]) h.parts[k].classList.add("is-" + seg.on[k]);
      });
      h.state.textContent = seg.state;
      Object.keys(btns).forEach(function (k) { btns[k].classList.toggle("is-active", k === seg.key); });
      cap.textContent = "";
      cap.appendChild(el("strong", { text: seg.name + ". " }));
      cap.appendChild(document.createTextNode(seg.text + " "));
      cap.appendChild(el("span", { class: "cv-feats" }, ["Features: "].concat(seg.feats.map(function (f, i) {
        return el("span", {}, [i ? " · " : "", el("a", { href: (root.dataset.base || "") + f[1].replace(/\.md$/, "/"), text: f[0] })]);
      }))));
    }

    function segAt(t) {
      for (var i = 0; i < SEGMENTS.length; i++) if (t < SEGMENTS[i].b(o)) return SEGMENTS[i];
      return SEGMENTS[SEGMENTS.length - 1];
    }

    var playing = false, raf = 0, startT = 0, speed = 1 / 3;
    var play = el("button", { type: "button", class: "mviz-preset cv-play", text: "▶ Play a heartbeat (slowed 3×)" });
    function frameAt(now) {
      var t = T0 + (((now - startT) * speed) % (T1 - T0));
      cursor.setAttribute("d", "M" + p.X(t).toFixed(1) + " " + p.m.t + "V" + (p.h - p.m.b));
      var s = segAt(t);
      if (s !== current) select(s);
      if (playing) raf = requestAnimationFrame(frameAt);
    }
    function stop() {
      playing = false;
      cancelAnimationFrame(raf);
      cursor.setAttribute("d", "");
      play.textContent = "▶ Play a heartbeat (slowed 3×)";
    }
    play.addEventListener("click", function () {
      if (playing) { stop(); return; }
      playing = true;
      play.textContent = "❚❚ Pause";
      startT = performance.now();
      raf = requestAnimationFrame(frameAt);
    });
    bar.appendChild(play);
    bar.appendChild(el("span", { class: "mviz-presets-lab", text: "or pick a part:" }));
    SEGMENTS.forEach(function (s) {
      var b = el("button", { type: "button", class: "mviz-preset", text: s.name });
      b.addEventListener("click", function () { stop(); select(s); });
      btns[s.key] = b;
      bar.appendChild(b);
      // Clicking the trace selects the part under the pointer too.
      var hit = sv("rect", { x: p.X(Math.max(T0, s.a(o))).toFixed(1), y: p.m.t,
        width: Math.max(0, p.X(s.b(o)) - p.X(Math.max(T0, s.a(o)))).toFixed(1),
        height: p.h - p.m.t - p.m.b, class: "cv-hit" });
      hit.appendChild(sv("title", { text: s.name }));
      hit.addEventListener("click", function () { stop(); select(s); });
      p.svg.appendChild(hit);
    });

    root.appendChild(bar);
    root.appendChild(el("div", { class: "cv-anat" }, [
      el("div", { class: "cv-anat-ecg" }, [p.svg]),
      el("div", { class: "cv-anat-heart" }, [h.svg, h.state]),
    ]));
    root.appendChild(cap);
    select(SEGMENTS[2]);
  }

  // ------------------------------------------------------------------ one feature at a time

  var BEAT_WIN = [-360, 760];

  function beatPanel(o, note) {
    var p = paper(BEAT_WIN[0], BEAT_WIN[1], -0.45, 1.2, 640);
    trace(p, function (t) { return beatValue(o, t); }, BEAT_WIN[0], BEAT_WIN[1]);
    scaleNote(p, note);
    return p;
  }

  // RR-varying strip: beats at the given QRS-onset times (ms).
  function stripPanel(onsets, o, t1, w, h) {
    var p = paper(0, t1, -0.45, 1.2, w, h);
    var f = function (t) {
      var v = 0;
      for (var i = 0; i < onsets.length; i++) {
        var d = t - onsets[i];
        if (d > -o.pr - 10 && d < o.qt + 10) v += beatValue(o, d);
      }
      return v;
    };
    trace(p, f, 0, t1);
    return p;
  }

  // Bazett-like QT for a heart rate, kept short enough to end before the next P wave.
  function qtFor(rr) { return Math.min(400 * Math.sqrt(rr / 1000), rr - NORMAL.pr - 40); }

  var FOCUS = {};

  FOCUS.hr = function (f) {
    f.slider("hr", "Heart rate", 30, 180, 1, 72, { unit: " bpm", digits: 0 });
    f.presets([["Resting", { hr: 72 }], ["Asleep or athlete", { hr: 50 }], ["Climbing stairs", { hr: 130 }]]);
    var zones = [[30, 60, "slow (bradycardia)", "warn"], [60, 100, "typical at rest", "ok"], [100, 180, "fast (tachycardia)", "warn"]];
    return function () {
      var hr = f.v("hr"), rr = 60000 / hr, o = params({ qt: qtFor(rr) }), t1 = 4000, on = [];
      for (var t = 300; t < t1 + 400; t += rr) on.push(t);
      var p = stripPanel(on, o, t1, 900, 190);
      var a = on[0] + rPeak(o), b = on[1] + rPeak(o);
      if (b < t1) span(p, a, b, "RR = " + fmt(rr, 0) + " ms (" + fmt(rr / 200, 1) + " big boxes)");
      on.forEach(function (x) { if (x + rPeak(o) < t1) V.dot(p, x + rPeak(o), o.ra, 3.5, "cv-mark"); });
      scaleNote(p, "4-second strip · 1 big box = 0.2 s · dots: R peaks");
      f.stage.appendChild(p.svg);
      f.stage.appendChild(gauge({ title: "Heart rate (adult at rest)", min: 30, max: 180, zones: zones, value: hr, valueText: fmt(hr, 0) + " bpm" }));
      f.readouts([
        { label: "hr_bpm", value: fmt(hr, 0) + " bpm", main: true, note: "60 000 ÷ RR in ms" },
        { label: "rr_mean_ms", value: fmt(rr, 0) + " ms", note: "time between R peaks" },
        { label: "Quick rule", value: "300 ÷ " + fmt(rr / 200, 1) + " = " + fmt(hr, 0), note: "300 ÷ big boxes between beats" },
      ]);
    };
  };

  FOCUS.p = function (f) {
    f.slider("pd", "P-wave duration", 40, 180, 2, 100, { unit: " ms", digits: 0 });
    f.slider("pa", "P-wave height", 0, 0.3, 0.01, 0.15, { unit: " mV", digits: 2 });
    f.presets([["Typical", { pd: 100, pa: 0.15 }], ["Long and broad", { pd: 140, pa: 0.15 }], ["No P wave", { pd: 100, pa: 0 }]]);
    var zones = [[40, 120, "typical (up to 120 ms)", "ok"], [120, 180, "long", "warn"]];
    return function () {
      var pd = f.v("pd"), pa = f.v("pa"), o = params({ pd: pd, pa: pa, pr: Math.max(160, pd + 60) });
      var p = beatPanel(o);
      var seen = pa >= 0.02;
      if (seen) span(p, -o.pr, -o.pr + pd, "P = " + fmt(pd, 0) + " ms");
      else label(p, p.X(-o.pr + pd / 2), p.Y(0.35), "no P wave to measure", "cv-cal-lab");
      f.stage.appendChild(p.svg);
      f.stage.appendChild(gauge({ title: "P-wave duration", min: 40, max: 180, zones: zones, value: seen ? pd : NaN,
        valueText: fmt(pd, 0) + " ms" }));
      f.readouts([
        { label: "p_wave_duration_ms", value: seen ? fmt(pd, 0) + " ms" : "NaN", main: true,
          note: seen ? "P onset → P end" : "nothing to measure" },
        { label: "What it tells you", value: seen ? zoneOf(zones, pd)[2] : "no atrial wave", tone: seen && pd <= 120 ? null : "bad" },
      ]);
    };
  };

  FOCUS.pr = function (f) {
    f.slider("pr", "PR interval", 60, 320, 2, 160, { unit: " ms", digits: 0 });
    f.presets([["Typical", { pr: 160 }], ["Short", { pr: 100 }], ["Long (first-degree AV block)", { pr: 260 }]]);
    var zones = [[60, 120, "short", "warn"], [120, 200, "typical (120–200 ms)", "ok"], [200, 320, "long", "warn"]];
    return function () {
      var pr = f.v("pr"), o = params({ pr: pr, pd: Math.min(100, pr - 20) });
      var p = beatPanel(o);
      span(p, -pr, 0, "PR = " + fmt(pr, 0) + " ms");
      f.stage.appendChild(p.svg);
      f.stage.appendChild(gauge({ title: "PR interval", min: 60, max: 320, zones: zones, value: pr, valueText: fmt(pr, 0) + " ms" }));
      var z = zoneOf(zones, pr);
      f.readouts([
        { label: "pr_interval_ms", value: fmt(pr, 0) + " ms", main: true, note: "P onset → QRS onset" },
        { label: "What it tells you", value: z[2], tone: z[3] === "ok" ? null : "bad" },
        { label: "Boxes", value: fmt(pr / 40, 1) + " small", note: "typical: 3–5 small boxes" },
      ]);
    };
  };

  FOCUS.qrs = function (f) {
    f.slider("qrs", "QRS duration", 60, 200, 2, 90, { unit: " ms", digits: 0 });
    f.presets([["Typical", { qrs: 90 }], ["Borderline", { qrs: 114 }], ["Wide (bundle branch block)", { qrs: 140 }]]);
    var zones = [[60, 110, "typical", "ok"], [110, 120, "border", "warn"], [120, 200, "wide", "warn"]];
    return function () {
      var q = f.v("qrs"), o = params({ qrs: q, qt: Math.max(390, q + 260) });
      var p = beatPanel(o);
      span(p, 0, q, "QRS = " + fmt(q, 0) + " ms");
      f.stage.appendChild(p.svg);
      f.stage.appendChild(gauge({ title: "QRS duration", min: 60, max: 200, zones: zones, value: q, valueText: fmt(q, 0) + " ms" }));
      var z = zoneOf(zones, q);
      f.readouts([
        { label: "qrs_duration_ms", value: fmt(q, 0) + " ms", main: true, note: "QRS onset → QRS end" },
        { label: "What it tells you", value: q < 110 ? "fast, normal spread" : q < 120 ? "slightly slow spread" : "slow spread (wide QRS)",
          tone: z[3] === "ok" ? null : "bad" },
        { label: "Boxes", value: fmt(q / 40, 1) + " small", note: "wide: 3 small boxes or more" },
      ]);
    };
  };

  FOCUS.qt = function (f) {
    f.slider("qt", "QT interval", 300, 560, 2, 400, { unit: " ms", digits: 0 });
    f.slider("hr", "Heart rate", 40, 140, 1, 60, { unit: " bpm", digits: 0 });
    f.presets([
      ["Typical at 60 bpm", { qt: 400, hr: 60 }],
      ["Same QT, faster heart", { qt: 400, hr: 100 }],
      ["Typical at 100 bpm", { qt: 340, hr: 100 }],
      ["Long QT", { qt: 500, hr: 60 }],
    ]);
    var zones = [[300, 350, "short", "warn"], [350, 450, "typical", "ok"], [450, 500, "long-ish", "warn"], [500, 600, "long", "warn"]];
    return function () {
      var qt = f.v("qt"), hr = f.v("hr"), rr = 60000 / hr, qtc = qt / Math.sqrt(rr / 1000), o = params({ qt: qt });
      var p = beatPanel(o);
      span(p, 0, qt, "QT = " + fmt(qt, 0) + " ms");
      if (qt > rr - NORMAL.pr - 20) {
        label(p, p.X(BEAT_WIN[1]) - 4, p.Y(1.05), "at " + fmt(hr, 0) + " bpm the next beat would start before this T wave ends",
          "cv-cal-lab cv-warn-text", "end");
      }
      f.stage.appendChild(p.svg);
      f.stage.appendChild(gauge({ title: "QTc — QT corrected for heart rate (Bazett)", min: 300, max: 600, zones: zones, value: qtc,
        valueText: "QTc " + fmt(qtc, 0) + " ms" }));
      var z = zoneOf(zones, qtc);
      f.readouts([
        { label: "qt_interval_ms", value: fmt(qt, 0) + " ms", note: "QRS onset → T end" },
        { label: "qtc_bazett_ms", value: fmt(qtc, 0) + " ms", main: true, note: "QT ÷ √(RR in s), RR = " + fmt(rr / 1000, 2) + " s" },
        { label: "What it tells you", value: z[2], tone: z[3] === "ok" ? null : "bad", note: "typical QTc ≈ 350–450 ms" },
      ]);
    };
  };

  FOCUS.st = function (f) {
    f.slider("st", "ST level", -0.3, 0.3, 0.01, 0, { unit: " mV", digits: 2 });
    f.presets([["On the baseline", { st: 0 }], ["Raised", { st: 0.2 }], ["Lowered", { st: -0.15 }]]);
    var zones = [[-0.3, -0.05, "lowered", "warn"], [-0.05, 0.1, "near baseline", "ok"], [0.1, 0.3, "raised", "warn"]];
    return function () {
      var st = f.v("st"), o = params({ st: st }), j = o.qrs, mpt = j + 80;
      var p = beatPanel(o);
      baseline(p, BEAT_WIN[0], BEAT_WIN[1], "baseline");
      p.svg.appendChild(sv("path", { d: "M" + p.X(j) + " " + p.Y(-0.4) + "V" + p.Y(1.1), class: "cv-tick-line" }));
      label(p, p.X(j), p.Y(-0.4) + 2, "J point", "cv-note");
      rise(p, mpt, 0, beatValue(o, mpt), "ST " + (st >= 0 ? "+" : "") + fmt(st, 2) + " mV");
      f.stage.appendChild(p.svg);
      f.stage.appendChild(gauge({ title: "ST deviation, measured 80 ms after the J point", min: -0.3, max: 0.3, zones: zones, value: st,
        valueText: (st >= 0 ? "+" : "") + fmt(st, 2) + " mV" }));
      var z = zoneOf(zones, st);
      f.readouts([
        { label: "st_deviation_mv", value: (st >= 0 ? "+" : "") + fmt(st, 2) + " mV", main: true, note: "level − baseline" },
        { label: "What it tells you", value: z[2], tone: z[3] === "ok" ? null : "bad" },
        { label: "Boxes", value: fmt(Math.abs(st) * 10, 1) + " small", note: "1 small box = 0.1 mV = 1 mm" },
      ]);
    };
  };

  FOCUS.t = function (f) {
    f.slider("ta", "T-wave height", -0.4, 1.2, 0.01, 0.3, { unit: " mV", digits: 2 });
    f.presets([["Typical", { ta: 0.3 }], ["Flat", { ta: 0.04 }], ["Upside down", { ta: -0.25 }], ["Tall and peaked", { ta: 0.9 }]]);
    var zones = [[-0.4, 0, "upside down", "warn"], [0, 0.1, "flat", "warn"], [0.1, 0.5, "typical", "ok"], [0.5, 1.2, "tall", "warn"]];
    return function () {
      var ta = f.v("ta"), o = params({ ta: ta }), tp = tPeak(o);
      var p = beatPanel(o);
      baseline(p, BEAT_WIN[0], BEAT_WIN[1], "baseline");
      rise(p, tp, 0, ta, "T " + (ta >= 0 ? "+" : "") + fmt(ta, 2) + " mV");
      f.stage.appendChild(p.svg);
      f.stage.appendChild(gauge({ title: "T-wave height (rough guide for lead II)", min: -0.4, max: 1.2, zones: zones, value: ta,
        valueText: fmt(ta, 2) + " mV" }));
      var z = zoneOf(zones, ta);
      f.readouts([
        { label: "t_amplitude_mv", value: fmt(ta, 2) + " mV", main: true, note: "T peak − baseline" },
        { label: "What it tells you", value: z[2], tone: z[3] === "ok" ? null : "bad" },
        { label: "Compared with R", value: fmt((100 * ta) / o.ra, 0) + " %", note: "T is usually well below R" },
      ]);
    };
  };

  FOCUS.hrv = function (f) {
    f.slider("hr", "Average heart rate", 50, 110, 1, 66, { unit: " bpm", digits: 0 });
    f.slider("slow", "Breathing rhythm (slow swing)", 0, 150, 2, 60, { unit: " ms", digits: 0 });
    f.slider("fast", "Beat-to-beat randomness", 0, 150, 1, 15, { unit: " ms", digits: 0 });
    f.slider("dur", "Recording length", 10, 300, 10, 60, { unit: " s", digits: 0 });
    f.presets([
      ["Relaxed", { hr: 66, slow: 60, fast: 15 }],
      ["Stressed / exercising", { hr: 100, slow: 6, fast: 5 }],
      ["Irregular rhythm", { hr: 85, slow: 10, fast: 140 }],
      ["Relaxed, 10-second ECG", { hr: 66, slow: 60, fast: 15, dur: 10 }],
    ]);
    var z = V.normals(4242, 2000);
    return function () {
      var rr0 = 60000 / f.v("hr"), dur = f.v("dur") * 1000, slow = f.v("slow"), fast = f.v("fast");
      var onsets = [], rr = [], t = 250, k = 0;
      while (t < dur) {
        onsets.push(t);
        var next = Math.max(330, rr0 + slow * Math.sin((2 * Math.PI * t) / 4000) + fast * z[k++ % 2000]);
        rr.push(next);
        t += next;
      }
      rr = rr.slice(0, onsets.length - 1);
      var d = [], nn50 = 0, i;
      for (i = 1; i < rr.length; i++) { d.push(rr[i] - rr[i - 1]); if (Math.abs(rr[i] - rr[i - 1]) > 50) nn50++; }
      var m = V.mean(rr), ss = 0;
      for (i = 0; i < rr.length; i++) ss += (rr[i] - m) * (rr[i] - m);
      var sdnn = rr.length > 1 ? Math.sqrt(ss / (rr.length - 1)) : NaN;
      var rmssd = d.length ? Math.sqrt(V.mean(d.map(function (x) { return x * x; }))) : NaN;
      var pnn50 = d.length ? (100 * nn50) / d.length : NaN;

      var show = Math.min(dur, 10000);
      var p = stripPanel(onsets, params({ qt: qtFor(rr0) }), show, 900, 170);
      for (i = 0; i < onsets.length - 1 && onsets[i + 1] + rPeak(NORMAL) < show; i++) {
        var xa = onsets[i] + rPeak(NORMAL), xb = onsets[i + 1] + rPeak(NORMAL);
        label(p, p.X((xa + xb) / 2), p.m.t + 12, fmt(rr[i], 0), "cv-rr-lab");
      }
      scaleNote(p, "first 10 s · numbers: RR interval of each beat in ms");

      var tp = V.plot(900, 210, { l: 50, r: 12, t: 12, b: 34 }, [0, dur / 1000], [300, 1600]);
      V.axes(tp, { xticks: [0, dur / 2000, dur / 1000], yticks: [400, 800, 1200, 1600],
        xlabel: "time (s): each dot is one beat; red links jump by more than 50 ms", ylabel: "RR (ms)" });
      var xs = [], ys = [];
      for (i = 0; i < rr.length; i++) { xs.push(onsets[i + 1] / 1000); ys.push(rr[i]); }
      V.line(tp, xs, ys, "cv-tach");
      for (i = 1; i < rr.length; i++) {
        if (Math.abs(rr[i] - rr[i - 1]) > 50) {
          tp.svg.appendChild(sv("path", { d: "M" + tp.X(xs[i - 1]) + " " + tp.Y(ys[i - 1]) + "L" + tp.X(xs[i]) + " " + tp.Y(ys[i]),
            class: "cv-jump" }));
        }
      }
      xs.forEach(function (x, j) { V.dot(tp, x, ys[j], 2.4, "cv-mark"); });
      f.stage.appendChild(el("div", { class: "mviz-col" }, [p.svg, tp.svg]));
      f.readouts([
        { label: "hrv_sdnn_ms", value: fmt(sdnn, 0) + " ms", main: true, note: "overall spread of RR" },
        { label: "hrv_rmssd_ms", value: fmt(rmssd, 0) + " ms", note: "typical jump between neighbours" },
        { label: "hrv_pnn50", value: fmt(pnn50, 0) + " %", note: "jumps > 50 ms" },
        { label: "Beats used", value: String(rr.length + 1), note: f.v("dur") <= 10 ? "few beats: rough estimate" : "" },
      ]);
    };
  };

  function clinical(root) {
    var make = FOCUS[root.dataset.focus];
    if (!make) throw new Error("unknown data-focus " + root.dataset.focus);
    var f = V.frame(root);
    f.draw(make(f));
  }

  V.register("beatAnatomy", anatomy);
  V.register("clinical", clinical);
})();
