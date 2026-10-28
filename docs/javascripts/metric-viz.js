/*
 * Interactive metric explainers for the "Metrics Explained" pages (docs/metrics/*.md).
 *
 * Every <div class="mviz" data-viz="NAME"> becomes a widget: presets, sliders, a plot and live
 * read-outs. The data are small simulated sets generated in the browser; the scores use the
 * same formulas as ecgen_eval/metrics/ (simplified only where noted on the page).
 */
(function () {
  "use strict";

  var SVGNS = "http://www.w3.org/2000/svg";

  // ------------------------------------------------------------------ utilities

  function mulberry32(seed) {
    return function () {
      seed = (seed + 0x6d2b79f5) | 0;
      var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function normals(seed, n) {
    var r = mulberry32(seed), out = new Float64Array(n);
    for (var i = 0; i < n; i += 2) {
      var u = 1 - r(), v = r(), m = Math.sqrt(-2 * Math.log(u));
      out[i] = m * Math.cos(2 * Math.PI * v);
      if (i + 1 < n) out[i + 1] = m * Math.sin(2 * Math.PI * v);
    }
    return out;
  }

  function uniforms(seed, n) {
    var r = mulberry32(seed), out = new Float64Array(n);
    for (var i = 0; i < n; i++) out[i] = r();
    return out;
  }

  function mean(a) {
    var s = 0;
    for (var i = 0; i < a.length; i++) s += a[i];
    return s / a.length;
  }

  function std(a) {
    var m = mean(a), s = 0;
    for (var i = 0; i < a.length; i++) s += (a[i] - m) * (a[i] - m);
    return Math.sqrt(s / a.length);
  }

  function median(a) {
    var b = Array.prototype.slice.call(a).sort(function (x, y) { return x - y; });
    var n = b.length;
    return n % 2 ? b[(n - 1) / 2] : 0.5 * (b[n / 2 - 1] + b[n / 2]);
  }

  function fmt(x, d) {
    if (!isFinite(x)) return x > 0 ? "∞" : "–";
    var a = Math.abs(x);
    if (a < 1e-6) return (0).toFixed(d == null ? 3 : d);
    if (a < 1e-3 || a >= 1e5) return x.toExponential(2);
    return x.toFixed(d == null ? 3 : d);
  }

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    setAttrs(n, attrs);
    (kids || []).forEach(function (k) {
      if (k != null) n.appendChild(typeof k === "string" ? document.createTextNode(k) : k);
    });
    return n;
  }

  function sv(tag, attrs, kids) {
    var n = document.createElementNS(SVGNS, tag);
    setAttrs(n, attrs);
    (kids || []).forEach(function (k) { if (k != null) n.appendChild(k); });
    return n;
  }

  function setAttrs(n, attrs) {
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") n.textContent = attrs[k];
      else if (attrs[k] != null) n.setAttribute(k, attrs[k]);
    });
  }

  function cssVar(name, fallback) {
    var v = getComputedStyle(document.body).getPropertyValue(name).trim();
    return v || fallback;
  }

  // Jensen–Shannon divergence between two samples, binned exactly like
  // heart_rate.py / hrv.py / spectral_entropy.py (50 bins over the joint range, natural log).
  function jsSamples(p, q, nBins) {
    nBins = nBins || 50;
    var lo = Infinity, hi = -Infinity, i;
    for (i = 0; i < p.length; i++) { lo = Math.min(lo, p[i]); hi = Math.max(hi, p[i]); }
    for (i = 0; i < q.length; i++) { lo = Math.min(lo, q[i]); hi = Math.max(hi, q[i]); }
    if (!(hi > lo)) return { js: 0, lo: lo, hi: hi, hp: [], hq: [] };
    var hp = hist(p, lo, hi, nBins), hq = hist(q, lo, hi, nBins);
    return { js: jsDist(hp, hq), lo: lo, hi: hi, hp: hp, hq: hq };
  }

  function hist(v, lo, hi, nBins) {
    var h = new Float64Array(nBins), w = (hi - lo) / nBins;
    for (var i = 0; i < v.length; i++) {
      var b = Math.floor((v[i] - lo) / w);
      h[Math.min(nBins - 1, Math.max(0, b))] += 1;
    }
    return h;
  }

  function jsDist(a, b) {
    var p = normalise(a, 1e-10), q = normalise(b, 1e-10), js = 0;
    for (var i = 0; i < p.length; i++) {
      var m = 0.5 * (p[i] + q[i]);
      js += 0.5 * (p[i] * Math.log(p[i] / m) + q[i] * Math.log(q[i] / m));
    }
    return Math.min(Math.max(js, 0), Math.LN2);
  }

  function normalise(a, add) {
    var s = 0, out = new Float64Array(a.length), i;
    for (i = 0; i < a.length; i++) { out[i] = a[i] + (add || 0); s += out[i]; }
    for (i = 0; i < a.length; i++) out[i] /= s;
    return out;
  }

  // In-place radix-2 FFT; returns the power spectrum of a Hann-windowed segment.
  function powerSpectrum(seg) {
    var n = seg.length, re = new Float64Array(n), im = new Float64Array(n), i, j, k;
    for (i = 0; i < n; i++) re[i] = seg[i] * (0.5 - 0.5 * Math.cos((2 * Math.PI * i) / (n - 1)));
    for (i = 1, j = 0; i < n; i++) {
      var bit = n >> 1;
      for (; j & bit; bit >>= 1) j ^= bit;
      j ^= bit;
      if (i < j) { var t = re[i]; re[i] = re[j]; re[j] = t; }
    }
    for (var len = 2; len <= n; len <<= 1) {
      var ang = (-2 * Math.PI) / len, wr = Math.cos(ang), wi = Math.sin(ang);
      for (i = 0; i < n; i += len) {
        var cr = 1, ci = 0;
        for (k = 0; k < len / 2; k++) {
          var a = i + k, b = a + len / 2;
          var xr = re[b] * cr - im[b] * ci, xi = re[b] * ci + im[b] * cr;
          re[b] = re[a] - xr; im[b] = im[a] - xi;
          re[a] += xr; im[a] += xi;
          var nr = cr * wr - ci * wi;
          ci = cr * wi + ci * wr; cr = nr;
        }
      }
    }
    var out = new Float64Array(n / 2 + 1);
    for (i = 0; i <= n / 2; i++) out[i] = re[i] * re[i] + im[i] * im[i];
    return out;
  }

  // Welch PSD with 256-sample Hann segments and 50 % overlap (psd.py uses nperseg=min(256, T)).
  function welch(x) {
    var nper = 256, step = 128, acc = null, count = 0;
    for (var s = 0; s + nper <= x.length; s += step) {
      var seg = x.subarray(s, s + nper), m = mean(seg), d = new Float64Array(nper);
      for (var i = 0; i < nper; i++) d[i] = seg[i] - m;
      var p = powerSpectrum(d);
      if (!acc) acc = new Float64Array(p.length);
      for (i = 0; i < p.length; i++) acc[i] += p[i];
      count++;
    }
    for (var k = 0; k < acc.length; k++) acc[k] /= count;
    return acc;
  }

  // ------------------------------------------------------------------ ECG model

  // Sum-of-Gaussians beat: [offset from R (s), amplitude (mV), width (s)] for P, Q, R, S, T.
  var WAVES = [[-0.2, 0.15, 0.025], [-0.035, -0.12, 0.01], [0, 1.0, 0.011],
    [0.035, -0.25, 0.011], [0.26, 0.32, 0.045]];

  function beatOpts(o) {
    return Object.assign({ amp: 1, qrs: 1, t: 1, rr: 0.85 }, o || {});
  }

  function beatAt(dt, o) {
    var v = 0;
    for (var k = 0; k < 5; k++) {
      var off = WAVES[k][0], a = WAVES[k][1] * o.amp, wd = WAVES[k][2];
      if (k >= 1 && k <= 3) { off *= o.qrs; wd *= o.qrs; }
      if (k === 4) { a *= o.t; off *= Math.sqrt(o.rr / 0.85); }
      var z = (dt - off) / wd;
      if (z > -6 && z < 6) v += a * Math.exp(-0.5 * z * z);
    }
    return v;
  }

  // One beat sampled on [0, dur) with the R peak at rPos seconds.
  function beat(fs, dur, rPos, o) {
    var n = Math.round(fs * dur), x = new Float64Array(n);
    for (var i = 0; i < n; i++) x[i] = beatAt(i / fs - rPos, o);
    return x;
  }

  // R-peak times for a strip: mean heart rate, respiratory (slow) modulation and beat noise.
  function rTimes(hr, slowMs, noiseMs, dur, seed) {
    var r = mulberry32(seed), z = normals(seed + 1, 400), out = [];
    var rr0 = 60 / hr, t = -r() * rr0, phase = r() * 2 * Math.PI, k = 0;
    while (t < dur + 1) {
      var rr = rr0 + (slowMs / 1000) * Math.sin(2 * Math.PI * 0.25 * t + phase) + (noiseMs / 1000) * z[k++ % 400];
      t += Math.max(0.25, rr);
      out.push(t);
    }
    return out;
  }

  function strip(fs, dur, peaks, o, noise, seed, extra) {
    var n = Math.round(fs * dur), x = new Float64Array(n), z = normals(seed, n);
    peaks.forEach(function (rt, j) {
      var rr = j > 0 ? rt - peaks[j - 1] : 60 / 70;
      var oo = Object.assign({}, o, { rr: rr });
      var i0 = Math.max(0, Math.floor((rt - 0.45) * fs)), i1 = Math.min(n, Math.ceil((rt + 0.7) * fs));
      for (var i = i0; i < i1; i++) x[i] += beatAt(i / fs - rt, oo);
    });
    for (var i = 0; i < n; i++) {
      var t = i / fs;
      x[i] += noise * z[i];
      if (extra) {
        x[i] += (extra.wander || 0) * Math.sin(2 * Math.PI * 0.3 * t + 1.3);
        x[i] += (extra.mains || 0) * Math.sin(2 * Math.PI * 50 * t);
      }
    }
    return x;
  }

  // ------------------------------------------------------------------ plotting

  function plot(w, h, m, xd, yd) {
    var svg = sv("svg", { viewBox: "0 0 " + w + " " + h, class: "mviz-svg", preserveAspectRatio: "xMidYMid meet" });
    var p = { svg: svg, w: w, h: h, m: m, xd: xd, yd: yd };
    p.X = function (x) { return m.l + ((x - xd[0]) / (xd[1] - xd[0])) * (w - m.l - m.r); };
    p.Y = function (y) { return h - m.b - ((y - yd[0]) / (yd[1] - yd[0])) * (h - m.t - m.b); };
    return p;
  }

  function line(p, xs, ys, cls, extra) {
    var d = "";
    for (var i = 0; i < ys.length; i++) {
      var x = typeof xs === "function" ? xs(i) : xs[i];
      d += (i ? "L" : "M") + p.X(x).toFixed(1) + " " + p.Y(ys[i]).toFixed(1);
    }
    p.svg.appendChild(sv("path", Object.assign({ d: d, class: cls, fill: "none" }, extra || {})));
  }

  function dot(p, x, y, r, cls) {
    p.svg.appendChild(sv("circle", { cx: p.X(x).toFixed(1), cy: p.Y(y).toFixed(1), r: r, class: cls }));
  }

  function text(p, x, y, s, cls, anchor) {
    p.svg.appendChild(sv("text", { x: x, y: y, class: cls || "mv-label", "text-anchor": anchor || "start", text: s }));
  }

  function axes(p, o) {
    var m = p.m, x0 = m.l, x1 = p.w - m.r, y0 = p.h - m.b, y1 = m.t;
    p.svg.appendChild(sv("path", { d: "M" + x0 + " " + y1 + "V" + y0 + "H" + x1, class: "mv-axis", fill: "none" }));
    (o.xticks || []).forEach(function (t) {
      var X = p.X(t);
      p.svg.appendChild(sv("path", { d: "M" + X + " " + y0 + "v4", class: "mv-axis" }));
      text(p, X, y0 + 14, o.xfmt ? o.xfmt(t) : String(t), "mv-tick", "middle");
    });
    (o.yticks || []).forEach(function (t) {
      var Y = p.Y(t);
      p.svg.appendChild(sv("path", { d: "M" + (x0 - 4) + " " + Y + "h4", class: "mv-axis" }));
      text(p, x0 - 6, Y + 3, o.yfmt ? o.yfmt(t) : String(t), "mv-tick", "end");
    });
    if (o.xlabel) text(p, (x0 + x1) / 2, p.h - 4, o.xlabel, "mv-label", "middle");
    if (o.ylabel) {
      p.svg.appendChild(sv("text", { x: 12, y: (y0 + y1) / 2, class: "mv-label", "text-anchor": "middle",
        transform: "rotate(-90 12 " + (y0 + y1) / 2 + ")", text: o.ylabel }));
    }
  }

  function bars(p, h, lo, hi, cls) {
    var n = h.length, w = (hi - lo) / n;
    for (var i = 0; i < n; i++) {
      if (!h[i]) continue;
      var x = p.X(lo + i * w), x2 = p.X(lo + (i + 1) * w), y = p.Y(h[i]);
      p.svg.appendChild(sv("rect", { x: x.toFixed(1), y: y.toFixed(1), width: Math.max(0.5, x2 - x - 0.5).toFixed(1),
        height: Math.max(0, p.Y(0) - y).toFixed(1), class: cls }));
    }
  }

  function legend(items) {
    return el("div", { class: "mviz-legend" }, items.map(function (it) {
      return el("span", {}, [el("i", { class: "mviz-swatch " + it[0] }), it[1]]);
    }));
  }

  // ------------------------------------------------------------------ widget frame

  function frame(root) {
    root.textContent = "";
    root.classList.add("mviz-ready");
    var presetBar = el("div", { class: "mviz-presets" });
    var ctr = el("div", { class: "mviz-controls" });
    var stage = el("div", { class: "mviz-stage" });
    var out = el("div", { class: "mviz-out", "aria-live": "polite" });
    root.appendChild(presetBar);
    root.appendChild(ctr);
    root.appendChild(stage);
    root.appendChild(out);
    var inputs = {}, shows = {}, defs = {}, draw = function () {}, pending = false;

    function schedule() {
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () { pending = false; run(); });
    }

    function run() {
      stage.textContent = "";
      out.textContent = "";
      draw();
    }

    function value(k) {
      var d = defs[k], v = parseFloat(inputs[k].value);
      return d.values ? d.values[v] : v;
    }

    function show(k) {
      var d = defs[k];
      shows[k].textContent = d.labels ? d.labels[parseInt(inputs[k].value, 10)] : fmt(value(k), d.digits) + (d.unit || "");
    }

    var api = {
      stage: stage,
      out: out,
      slider: function (k, label, min, max, step, val, opt) {
        opt = opt || {};
        var d = defs[k] = { values: opt.values, labels: opt.labels, unit: opt.unit, digits: opt.digits == null ? 2 : opt.digits };
        var input = el("input", { type: "range", min: d.values ? 0 : min, max: d.values ? d.values.length - 1 : max,
          step: d.values ? 1 : step, value: d.values ? d.values.indexOf(val) : val, "aria-label": label });
        inputs[k] = input;
        shows[k] = el("span", { class: "mviz-val" });
        input.addEventListener("input", function () { show(k); schedule(); });
        ctr.appendChild(el("label", { class: "mviz-slider", title: opt.help || "" },
          [el("span", { class: "mviz-lab" }, [label, shows[k]]), input]));
        show(k);
      },
      v: value,
      presets: function (list) {
        list.forEach(function (pr) {
          var b = el("button", { type: "button", class: "mviz-preset", text: pr[0] });
          b.addEventListener("click", function () {
            Object.keys(pr[1]).forEach(function (k) {
              var d = defs[k];
              inputs[k].value = d.values ? d.values.indexOf(pr[1][k]) : pr[1][k];
              show(k);
            });
            presetBar.querySelectorAll(".mviz-preset").forEach(function (o) { o.classList.toggle("is-active", o === b); });
            schedule();
          });
          presetBar.appendChild(b);
        });
        if (list.length) presetBar.insertBefore(el("span", { class: "mviz-presets-lab", text: "Try:" }), presetBar.firstChild);
      },
      readouts: function (items) {
        items.forEach(function (it) {
          out.appendChild(el("div", { class: "mviz-card" + (it.main ? " is-main" : "") + (it.tone ? " is-" + it.tone : "") }, [
            el("span", { class: "mviz-card-lab", text: it.label }),
            el("span", { class: "mviz-card-val", text: it.value }),
            it.note ? el("span", { class: "mviz-card-note", text: it.note }) : null,
          ]));
        });
      },
      draw: function (fn) {
        draw = fn;
        run();
        // Redraw on light/dark switch so canvas colours follow the theme.
        new MutationObserver(schedule).observe(document.body, { attributes: true, attributeFilter: ["data-md-color-scheme"] });
      },
    };
    return api;
  }

  // ------------------------------------------------------------------ 2-D helpers

  function cov2(xs, ys) {
    var n = xs.length, mx = mean(xs), my = mean(ys), a = 0, b = 0, c = 0;
    for (var i = 0; i < n; i++) {
      var dx = xs[i] - mx, dy = ys[i] - my;
      a += dx * dx; b += dx * dy; c += dy * dy;
    }
    return { mx: mx, my: my, a: a / (n - 1), b: b / (n - 1), c: c / (n - 1) }; // np.cov uses ddof=1
  }

  // Fréchet distance between two 2-D Gaussians. For 2x2 SPD A, B: tr sqrt(AB) = sqrt(tr AB + 2 sqrt(det AB)).
  function frechet2(P, Q) {
    var eps = 1e-6, A = [P.a + eps, P.b, P.c + eps], B = [Q.a + eps, Q.b, Q.c + eps];
    var tr = A[0] * B[0] + 2 * A[1] * B[1] + A[2] * B[2];
    var det = (A[0] * A[2] - A[1] * A[1]) * (B[0] * B[2] - B[1] * B[1]);
    var trSqrt = Math.sqrt(Math.max(0, tr + 2 * Math.sqrt(Math.max(0, det))));
    var meanTerm = (P.mx - Q.mx) * (P.mx - Q.mx) + (P.my - Q.my) * (P.my - Q.my);
    var covTerm = A[0] + A[2] + B[0] + B[2] - 2 * trSqrt;
    return { fd: meanTerm + covTerm, meanTerm: meanTerm, covTerm: covTerm };
  }

  function ellipse(p, C, k, cls) {
    var tr = (C.a + C.c) / 2, dd = Math.sqrt(((C.a - C.c) * (C.a - C.c)) / 4 + C.b * C.b);
    var l1 = tr + dd, l2 = Math.max(1e-9, tr - dd), ang = 0.5 * Math.atan2(2 * C.b, C.a - C.c);
    var sx = (p.w - p.m.l - p.m.r) / (p.xd[1] - p.xd[0]);
    var cx = p.X(C.mx), cy = p.Y(C.my);
    p.svg.appendChild(sv("ellipse", { cx: cx, cy: cy, rx: k * Math.sqrt(l1) * sx, ry: k * Math.sqrt(l2) * sx,
      transform: "rotate(" + ((-ang * 180) / Math.PI).toFixed(2) + " " + cx + " " + cy + ")", class: cls }));
    p.svg.appendChild(sv("path", { d: "M" + (cx - 5) + " " + cy + "h10M" + cx + " " + (cy - 5) + "v10", class: cls + " mv-cross" }));
  }

  function cloud2(z, n, off, sx, sy, rho, dx, dy) {
    var xs = new Float64Array(n), ys = new Float64Array(n), c = Math.sqrt(1 - rho * rho);
    for (var i = 0; i < n; i++) {
      var a = z[off + 2 * i], b = z[off + 2 * i + 1];
      xs[i] = dx + sx * a;
      ys[i] = dy + sy * (rho * a + c * b);
    }
    return [xs, ys];
  }

  function scatter(p, pts, cls, r) {
    for (var i = 0; i < pts[0].length; i++) dot(p, pts[0][i], pts[1][i], r || 2.6, cls);
  }

  // ------------------------------------------------------------------ widgets

  var VIZ = {};

  // Fréchet distance (fd, fed): two Gaussian clouds, their fitted ellipses and the two terms.
  VIZ.frechet = function (root) {
    var f = frame(root), fed = root.dataset.variant === "fed";
    var z = normals(11, 2000), zb = normals(29, 2000);
    f.slider("dx", "Mean shift (x)", -3, 3, 0.1, 0);
    f.slider("dy", "Mean shift (y)", -3, 3, 0.1, 0);
    f.slider("sc", "Synthetic spread", 0.3, 2, 0.05, 1, { unit: "×" });
    f.slider("rho", "Synthetic correlation", -0.9, 0.9, 0.05, 0.6);
    f.slider("n", "Samples per set", 20, 500, 10, 200, { digits: 0 });
    f.presets([
      ["Identical", { dx: 0, dy: 0, sc: 1, rho: 0.6, n: 200 }],
      ["Shifted mean", { dx: 1.5, dy: 0.5, sc: 1, rho: 0.6, n: 200 }],
      ["Too little variety", { dx: 0, dy: 0, sc: 0.4, rho: 0.6, n: 200 }],
      ["Wrong correlation", { dx: 0, dy: 0, sc: 1, rho: -0.6, n: 200 }],
      ["Only 30 samples", { dx: 0, dy: 0, sc: 1, rho: 0.6, n: 30 }],
    ]);
    f.draw(function () {
      var n = f.v("n"), sc = f.v("sc");
      var R = cloud2(z, n, 0, 1, 1, 0.6, 0, 0);
      var S = cloud2(z, n, 1000, sc, sc, f.v("rho"), f.v("dx"), f.v("dy"));
      var R2 = cloud2(zb, n, 0, 1, 1, 0.6, 0, 0);
      var Cr = cov2(R[0], R[1]), Cs = cov2(S[0], S[1]), res = frechet2(Cr, Cs);
      var base = frechet2(Cr, cov2(R2[0], R2[1]));
      var p = plot(420, 380, { l: 40, r: 10, t: 10, b: 36 }, [-5, 5], [-4.5, 4.5]);
      axes(p, { xticks: [-4, -2, 0, 2, 4], yticks: [-4, -2, 0, 2, 4],
        xlabel: fed ? "embedding dimension 1" : "feature 1 (z-scored)",
        ylabel: fed ? "embedding dimension 2" : "feature 2 (z-scored)" });
      scatter(p, R, "mv-real mv-pt");
      scatter(p, S, "mv-synth mv-pt");
      ellipse(p, Cr, 2, "mv-real mv-ell");
      ellipse(p, Cs, 2, "mv-synth mv-ell");
      p.svg.appendChild(sv("path", { d: "M" + p.X(Cr.mx) + " " + p.Y(Cr.my) + "L" + p.X(Cs.mx) + " " + p.Y(Cs.my), class: "mv-link" }));
      f.stage.appendChild(legend([["mv-real", "Real"], ["mv-synth", "Synthetic"], ["mv-ellkey", "Fitted Gaussian (2σ ellipse)"]]));
      f.stage.appendChild(p.svg);
      f.readouts([
        { label: fed ? "FED" : "FD", value: fmt(res.fd), main: true, note: "lower is better" },
        { label: "Mean term ‖μr − μs‖²", value: fmt(res.meanTerm), note: "where the clouds sit" },
        { label: "Covariance term", value: fmt(res.covTerm), note: "shape and spread" },
        { label: "Real vs real (same n)", value: fmt(base.fd), note: "noise floor: what 'identical' scores" },
      ]);
    });
  };

  // MMD (1-D for clarity): kernel mean embeddings of the two samples.
  VIZ.mmd = function (root) {
    var f = frame(root), n = 150, zr = normals(5, n), zs = normals(6, n), u = uniforms(7, n);
    f.slider("shift", "Mean shift", -2, 2, 0.05, 0);
    f.slider("sc", "Synthetic spread", 0.3, 2.5, 0.05, 1, { unit: "×" });
    f.slider("modes", "Split into two modes", 0, 0.95, 0.05, 0, { help: "Keeps mean and variance fixed" });
    f.slider("bw", "Kernel width shown (× median)", 0, 0, 1, 1, { values: [0.1, 0.3, 1, 3, 10], digits: 1 });
    f.presets([
      ["Identical", { shift: 0, sc: 1, modes: 0 }],
      ["Shifted", { shift: 1, sc: 1, modes: 0 }],
      ["Two modes, same mean & variance", { shift: 0, sc: 1, modes: 0.9 }],
      ["Too narrow", { shift: 0, sc: 0.4, modes: 0 }],
    ]);
    function kmat(A, B, bws) {
      var d = [], i, j;
      for (i = 0; i < A.length; i++) for (j = 0; j < B.length; j++) d.push((A[i] - B[j]) * (A[i] - B[j]));
      var s2 = median(d) + 1e-9, K = new Float64Array(d.length);
      for (i = 0; i < d.length; i++) {
        var k = 0;
        for (j = 0; j < bws.length; j++) k += Math.exp(-d[i] / (2 * bws[j] * s2));
        K[i] = k / bws.length;
      }
      return { K: K, s2: s2 };
    }
    function mmd2(X, Y, bws) {
      var xx = kmat(X, X, bws).K, yy = kmat(Y, Y, bws).K, xy = kmat(X, Y, bws).K, sx = 0, sy = 0, i, j;
      var n1 = X.length, n2 = Y.length;
      for (i = 0; i < n1; i++) for (j = 0; j < n1; j++) if (i !== j) sx += xx[i * n1 + j];
      for (i = 0; i < n2; i++) for (j = 0; j < n2; j++) if (i !== j) sy += yy[i * n2 + j];
      return Math.max(0, sx / (n1 * (n1 - 1)) + sy / (n2 * (n2 - 1)) - 2 * mean(xy));
    }
    f.draw(function () {
      var a = f.v("modes"), sc = f.v("sc"), sh = f.v("shift"), c = Math.sqrt(1 - a * a);
      var X = zr, Y = new Float64Array(n);
      for (var i = 0; i < n; i++) Y[i] = sh + sc * (a * (u[i] < 0.5 ? -1 : 1) + c * zs[i]);
      var bw = f.v("bw");
      var s2 = kmat(X, Y, [1]).s2, h = Math.sqrt(bw * s2);
      var grid = [], er = [], es = [];
      for (var g = -5; g <= 5.0001; g += 0.05) {
        grid.push(g);
        var kr = 0, ks = 0;
        for (i = 0; i < n; i++) {
          kr += Math.exp(-((g - X[i]) * (g - X[i])) / (2 * h * h));
          ks += Math.exp(-((g - Y[i]) * (g - Y[i])) / (2 * h * h));
        }
        er.push(kr / n); es.push(ks / n);
      }
      var top = Math.max(Math.max.apply(null, er), Math.max.apply(null, es)) * 1.1;
      var p = plot(640, 300, { l: 44, r: 10, t: 10, b: 36 }, [-5, 5], [-0.08 * top, top]);
      axes(p, { xticks: [-4, -2, 0, 2, 4], xlabel: "feature value (e.g. RMS of a lead, z-scored)", ylabel: "mean kernel" });
      // Shade the gap between the two embeddings: MMD measures its size.
      var d = "M" + p.X(grid[0]) + " " + p.Y(er[0]);
      for (i = 1; i < grid.length; i++) d += "L" + p.X(grid[i]) + " " + p.Y(er[i]);
      for (i = grid.length - 1; i >= 0; i--) d += "L" + p.X(grid[i]) + " " + p.Y(es[i]);
      p.svg.appendChild(sv("path", { d: d + "Z", class: "mv-gap" }));
      line(p, grid, er, "mv-real mv-line");
      line(p, grid, es, "mv-synth mv-line");
      for (i = 0; i < n; i++) {
        p.svg.appendChild(sv("path", { d: "M" + p.X(X[i]).toFixed(1) + " " + (p.Y(0) - 16) + "v6", class: "mv-real mv-rug" }));
        p.svg.appendChild(sv("path", { d: "M" + p.X(Y[i]).toFixed(1) + " " + (p.Y(0) - 8) + "v6", class: "mv-synth mv-rug" }));
      }
      f.stage.appendChild(legend([["mv-real", "Real (samples below, kernel mean above)"], ["mv-synth", "Synthetic"], ["mv-gapkey", "Gap MMD measures"]]));
      f.stage.appendChild(p.svg);
      var vr = std(X) * std(X), vs = std(Y) * std(Y), dm = mean(X) - mean(Y);
      var fd1 = dm * dm + vr + vs - 2 * Math.sqrt(vr * vs);
      f.readouts([
        { label: "MMD² (ECGEN-Eval kernels 0.1, 1, 10)", value: fmt(mmd2(X, Y, [0.1, 1, 10]), 4), main: true, note: "lower is better" },
        { label: "MMD² with the kernel shown", value: fmt(mmd2(X, Y, [bw]), 4) },
        { label: "Fréchet (Gaussian fit) for comparison", value: fmt(fd1, 4), note: "blind to shape beyond mean/variance" },
      ]);
    });
  };

  // Sliced Wasserstein: project 2-D clouds on directions, compare sorted projections.
  VIZ.swd = function (root) {
    var f = frame(root), n = 200, z = normals(13, 4 * n);
    f.slider("dx", "Mean shift (x)", -3, 3, 0.1, 1);
    f.slider("sc", "Synthetic spread", 0.3, 2, 0.05, 1, { unit: "×" });
    f.slider("rho", "Synthetic correlation", -0.9, 0.9, 0.05, 0.6);
    f.slider("th", "Projection angle", 0, 175, 5, 30, { unit: "°", digits: 0 });
    f.presets([
      ["Identical", { dx: 0, sc: 1, rho: 0.6 }],
      ["Shift along x", { dx: 1.5, sc: 1, rho: 0.6, th: 0 }],
      ["Same marginals, wrong correlation", { dx: 0, sc: 1, rho: -0.6, th: 45 }],
    ]);
    function w1(a, b) {
      var A = Array.prototype.slice.call(a).sort(function (x, y) { return x - y; });
      var B = Array.prototype.slice.call(b).sort(function (x, y) { return x - y; });
      var s = 0;
      for (var i = 0; i < A.length; i++) s += Math.abs(A[i] - B[i]);
      return s / A.length;
    }
    function proj(P, th) {
      var c = Math.cos(th), s = Math.sin(th), o = new Float64Array(P[0].length);
      for (var i = 0; i < o.length; i++) o[i] = c * P[0][i] + s * P[1][i];
      return o;
    }
    f.draw(function () {
      var R = cloud2(z, n, 0, 1, 1, 0.6, 0, 0), S = cloud2(z, n, 2 * n, f.v("sc"), f.v("sc"), f.v("rho"), f.v("dx"), 0);
      var th = (f.v("th") * Math.PI) / 180, curve = [], angs = [];
      for (var k = 0; k < 36; k++) { angs.push(k * 5); curve.push(w1(proj(R, (k * 5 * Math.PI) / 180), proj(S, (k * 5 * Math.PI) / 180))); }
      var swd = mean(curve);
      var row = el("div", { class: "mviz-row" });
      var p = plot(330, 320, { l: 34, r: 8, t: 8, b: 30 }, [-5, 5], [-5, 5]);
      axes(p, { xticks: [-4, 0, 4], yticks: [-4, 0, 4] });
      scatter(p, R, "mv-real mv-pt", 2.2);
      scatter(p, S, "mv-synth mv-pt", 2.2);
      p.svg.appendChild(sv("path", { d: "M" + p.X(-6 * Math.cos(th)) + " " + p.Y(-6 * Math.sin(th)) + "L" + p.X(6 * Math.cos(th)) + " " + p.Y(6 * Math.sin(th)), class: "mv-dir" }));
      var pr = proj(R, th), ps = proj(S, th);
      var lo = -6, hi = 6, hr = hist(pr, lo, hi, 40), hs = hist(ps, lo, hi, 40);
      var top = Math.max(Math.max.apply(null, hr), Math.max.apply(null, hs)) * 1.1;
      var q = plot(330, 150, { l: 34, r: 8, t: 8, b: 30 }, [lo, hi], [0, top]);
      axes(q, { xticks: [-4, 0, 4], xlabel: "position along the projection line" });
      bars(q, hr, lo, hi, "mv-real mv-bar");
      bars(q, hs, lo, hi, "mv-synth mv-bar");
      var c = plot(330, 150, { l: 34, r: 8, t: 8, b: 30 }, [0, 180], [0, Math.max.apply(null, curve) * 1.15 + 1e-6]);
      axes(c, { xticks: [0, 45, 90, 135, 180], xfmt: function (t) { return t + "°"; }, xlabel: "W₁ for every angle (mean = SWD)" });
      line(c, angs, curve, "mv-accent mv-line");
      dot(c, f.v("th"), w1(pr, ps), 4, "mv-accent mv-dotc");
      row.appendChild(p.svg);
      row.appendChild(el("div", { class: "mviz-col" }, [q.svg, c.svg]));
      f.stage.appendChild(legend([["mv-real", "Real"], ["mv-synth", "Synthetic"], ["mv-dirkey", "Projection line"]]));
      f.stage.appendChild(row);
      f.readouts([
        { label: "SWD (mean over 36 angles)", value: fmt(swd), main: true, note: "lower is better" },
        { label: "W₁ along the shown line", value: fmt(w1(pr, ps)) },
      ]);
    });
  };

  // k-NN precision & recall, matching pr_dist.py (nearest point's k-NN radius).
  VIZ.prdist = function (root) {
    var f = frame(root), n = 120, z = normals(21, 4 * n), u = uniforms(22, 2 * n);
    f.slider("sc", "Synthetic spread", 0.2, 2.5, 0.05, 1, { unit: "×" });
    f.slider("dx", "Mean shift", -3, 3, 0.1, 0);
    f.slider("mb", "Share of synthetic in the small mode", 0, 0.6, 0.02, 0.3, { digits: 2 });
    f.slider("k", "k (neighbour for the radius)", 1, 10, 1, 3, { digits: 0 });
    f.slider("view", "Draw k-NN balls around", 0, 0, 1, 0, { values: [0, 1], labels: ["real points", "synthetic points"] });
    f.presets([
      ["Good model", { sc: 1, dx: 0, mb: 0.3 }],
      ["Mode dropped", { sc: 1, dx: 0, mb: 0 }],
      ["Too narrow", { sc: 0.35, dx: 0, mb: 0.3 }],
      ["Too noisy", { sc: 2.2, dx: 0, mb: 0.3 }],
      ["Shifted", { sc: 1, dx: 2, mb: 0.3 }],
    ]);
    // Real data: a big mode (e.g. normal beats) and a small one (e.g. ectopic beats), 30 % share.
    function make(share, sc, dx, off, uo) {
      var xs = new Float64Array(n), ys = new Float64Array(n);
      for (var i = 0; i < n; i++) {
        var small = u[uo + i] < share;
        var cx = small ? 2.6 : -0.8, cy = small ? 1.8 : -0.4, s = small ? 0.45 : 0.9;
        xs[i] = cx + dx + sc * s * z[off + 2 * i];
        ys[i] = cy + sc * s * z[off + 2 * i + 1];
      }
      return [xs, ys];
    }
    function radii(P, k) {
      var r = new Float64Array(P[0].length);
      for (var i = 0; i < r.length; i++) {
        var d = [];
        for (var j = 0; j < r.length; j++) if (i !== j) d.push(Math.hypot(P[0][i] - P[0][j], P[1][i] - P[1][j]));
        d.sort(function (a, b) { return a - b; });
        r[i] = d[Math.min(k, d.length) - 1];
      }
      return r;
    }
    function covered(A, B, rB) {
      var out = [];
      for (var i = 0; i < A[0].length; i++) {
        var best = Infinity, bi = -1;
        for (var j = 0; j < B[0].length; j++) {
          var d = Math.hypot(A[0][i] - B[0][j], A[1][i] - B[1][j]);
          if (d < best) { best = d; bi = j; }
        }
        out.push(best <= rB[bi]);
      }
      return out;
    }
    f.draw(function () {
      var R = make(0.3, 1, 0, 0, 0), S = make(f.v("mb"), f.v("sc"), f.v("dx"), 2 * n, n), k = f.v("k");
      var rR = radii(R, k), rS = radii(S, k);
      var inR = covered(S, R, rR), inS = covered(R, S, rS);
      var prec = mean(inR.map(Number)), rec = mean(inS.map(Number)), F = (2 * prec * rec) / (prec + rec + 1e-9);
      var p = plot(460, 380, { l: 34, r: 8, t: 8, b: 30 }, [-5, 6], [-4.5, 4.8]);
      var sx = (p.w - p.m.l - p.m.r) / (p.xd[1] - p.xd[0]);
      axes(p, { xticks: [-4, -2, 0, 2, 4, 6], yticks: [-4, -2, 0, 2, 4] });
      var ballsOn = f.v("view") === 0 ? [R, rR, "mv-real"] : [S, rS, "mv-synth"];
      for (var i = 0; i < n; i++) {
        p.svg.appendChild(sv("circle", { cx: p.X(ballsOn[0][0][i]), cy: p.Y(ballsOn[0][1][i]), r: ballsOn[1][i] * sx, class: ballsOn[2] + " mv-ball" }));
      }
      for (i = 0; i < n; i++) {
        dot(p, R[0][i], R[1][i], 3, "mv-real mv-pt" + (inS[i] ? "" : " mv-miss"));
        dot(p, S[0][i], S[1][i], 3, "mv-synth mv-pt" + (inR[i] ? "" : " mv-miss"));
      }
      f.stage.appendChild(legend([["mv-real", "Real"], ["mv-synth", "Synthetic"], ["mv-misskey", "Hollow = outside the other set's manifold"]]));
      f.stage.appendChild(p.svg);
      f.readouts([
        { label: "pr_dist score (F)", value: fmt(F), main: true, note: "higher is better" },
        { label: "Precision", value: fmt(prec), note: "synthetic points inside the real manifold" },
        { label: "Recall", value: fmt(rec), note: "real points inside the synthetic manifold" },
      ]);
    });
  };

  // Nearest-neighbour distance and authenticity (nn_dist.py).
  VIZ.nndist = function (root) {
    var f = frame(root), n = 60, z = normals(31, 2 * n), zn = normals(32, 2 * n), zj = normals(33, 2 * n);
    f.slider("mem", "Synthetic samples that copy a real one", 0, 1, 0.05, 0, { unit: "", digits: 2 });
    f.slider("jit", "Copy jitter", 0, 0.5, 0.01, 0.05);
    f.presets([
      ["Novel samples", { mem: 0 }],
      ["Half copied", { mem: 0.5, jit: 0.05 }],
      ["Everything copied", { mem: 1, jit: 0.02 }],
    ]);
    function nn(A, B, same) {
      var d = [], idx = [];
      for (var i = 0; i < A[0].length; i++) {
        var best = Infinity, bi = -1;
        for (var j = 0; j < B[0].length; j++) {
          if (same && i === j) continue;
          var dd = Math.hypot(A[0][i] - B[0][j], A[1][i] - B[1][j]);
          if (dd < best) { best = dd; bi = j; }
        }
        d.push(best); idx.push(bi);
      }
      return { d: d, idx: idx };
    }
    f.draw(function () {
      var R = [new Float64Array(n), new Float64Array(n)], S = [new Float64Array(n), new Float64Array(n)];
      var m = Math.round(f.v("mem") * n), jit = f.v("jit");
      for (var i = 0; i < n; i++) {
        R[0][i] = z[2 * i]; R[1][i] = z[2 * i + 1];
        if (i < m) { S[0][i] = R[0][i] + jit * zj[2 * i]; S[1][i] = R[1][i] + jit * zj[2 * i + 1]; }
        else { S[0][i] = zn[2 * i]; S[1][i] = zn[2 * i + 1]; }
      }
      var rs = nn(R, S), rr = nn(R, R, true), sr = nn(S, R), thr = median(rr.d);
      var auth = mean(sr.d.map(function (d) { return d > thr ? 1 : 0; }));
      var p = plot(440, 380, { l: 34, r: 8, t: 8, b: 30 }, [-3.5, 3.5], [-3.2, 3.2]);
      axes(p, { xticks: [-3, 0, 3], yticks: [-3, 0, 3] });
      for (i = 0; i < n; i++) {
        var j = sr.idx[i], close = sr.d[i] <= thr;
        p.svg.appendChild(sv("path", { d: "M" + p.X(S[0][i]) + " " + p.Y(S[1][i]) + "L" + p.X(R[0][j]) + " " + p.Y(R[1][j]), class: close ? "mv-nnbad" : "mv-nn" }));
      }
      scatter(p, R, "mv-real mv-pt", 3.2);
      scatter(p, S, "mv-synth mv-pt", 3.2);
      f.stage.appendChild(legend([["mv-real", "Real (training)"], ["mv-synth", "Synthetic"], ["mv-nnbadkey", "Closer than typical real neighbours"]]));
      f.stage.appendChild(p.svg);
      f.readouts([
        { label: "nn_dist score", value: fmt(mean(rs.d)), main: true, note: "mean real → nearest synthetic" },
        { label: "Real → real baseline", value: fmt(mean(rr.d)), note: "a novel generator scores about this" },
        { label: "Authenticity", value: fmt(auth), tone: auth < 0.35 ? "bad" : null, note: "share of synthetic farther than the median real gap" },
      ]);
    });
  };

  // Point-wise signal metrics (prd, mae, psnr, ssim) on one real beat and one synthetic beat.
  VIZ.pointwise = function (root) {
    var f = frame(root), hl = root.dataset.highlight || "prd", fs = 250, zn = normals(41, 400);
    f.slider("amp", "Amplitude", 0.5, 1.5, 0.01, 1, { unit: "×" });
    f.slider("shift", "Time shift", -60, 60, 2, 0, { unit: " ms", digits: 0 });
    f.slider("noise", "Noise", 0, 0.15, 0.005, 0, { unit: " mV", digits: 3 });
    f.slider("base", "Baseline offset", -0.3, 0.3, 0.01, 0, { unit: " mV" });
    f.slider("t", "T-wave amplitude", -1, 1.5, 0.05, 1, { unit: "×" });
    f.presets([
      ["Identical", { amp: 1, shift: 0, noise: 0, base: 0, t: 1 }],
      ["20 ms late", { amp: 1, shift: 20, noise: 0, base: 0, t: 1 }],
      ["Noisy", { amp: 1, shift: 0, noise: 0.06, base: 0, t: 1 }],
      ["Baseline drift", { amp: 1, shift: 0, noise: 0, base: 0.2, t: 1 }],
      ["Inverted T wave", { amp: 1, shift: 0, noise: 0, base: 0, t: -0.6 }],
    ]);
    f.draw(function () {
      var x = beat(fs, 1, 0.4, beatOpts()), o = beatOpts({ amp: f.v("amp"), t: f.v("t") });
      var y = beat(fs, 1, 0.4 + f.v("shift") / 1000, o), n = x.length, i;
      for (i = 0; i < n; i++) y[i] += f.v("base") + f.v("noise") * zn[i];
      var se = 0, ae = 0, xx = 0, mx = mean(x), my = mean(y), vx = 0, vy = 0, cxy = 0, lo = Infinity, hi = -Infinity;
      for (i = 0; i < n; i++) {
        var d = x[i] - y[i];
        se += d * d; ae += Math.abs(d); xx += x[i] * x[i];
        vx += (x[i] - mx) * (x[i] - mx); vy += (y[i] - my) * (y[i] - my); cxy += (x[i] - mx) * (y[i] - my);
        lo = Math.min(lo, x[i]); hi = Math.max(hi, x[i]);
      }
      vx /= n; vy /= n; cxy /= n;
      var mse = se / n, L = hi - lo, C1 = (0.01 * L) * (0.01 * L), C2 = (0.03 * L) * (0.03 * L);
      var lum = (2 * mx * my + C1) / (mx * mx + my * my + C1), cs = (2 * cxy + C2) / (vx + vy + C2);
      var vals = {
        prd: 100 * Math.sqrt(se / xx), mae: ae / n, rmse: Math.sqrt(mse),
        psnr: mse > 0 ? 10 * Math.log10((L * L) / mse) : Infinity, ssim: lum * cs,
      };
      var p = plot(640, 260, { l: 44, r: 10, t: 10, b: 34 }, [0, 1], [-0.6, 1.5]);
      axes(p, { xticks: [0, 0.2, 0.4, 0.6, 0.8, 1], yticks: [-0.5, 0, 0.5, 1, 1.5], xlabel: "time (s)", ylabel: "mV" });
      // Error area between the two signals.
      var d2 = "M" + p.X(0) + " " + p.Y(x[0]);
      for (i = 1; i < n; i++) d2 += "L" + p.X(i / fs) + " " + p.Y(x[i]);
      for (i = n - 1; i >= 0; i--) d2 += "L" + p.X(i / fs) + " " + p.Y(y[i]);
      p.svg.appendChild(sv("path", { d: d2 + "Z", class: "mv-gap" }));
      line(p, function (k) { return k / fs; }, x, "mv-real mv-line");
      line(p, function (k) { return k / fs; }, y, "mv-synth mv-line");
      f.stage.appendChild(legend([["mv-real", "Real beat"], ["mv-synth", "Synthetic beat (its nearest neighbour)"], ["mv-gapkey", "Point-wise error"]]));
      f.stage.appendChild(p.svg);
      var cards = [
        { k: "prd", label: "PRD (%)", value: fmt(vals.prd, 1), note: "lower is better" },
        { k: "mae", label: "MAE (mV)", value: fmt(vals.mae, 4), note: "lower is better" },
        { k: "mae", label: "RMSE (mV)", value: fmt(vals.rmse, 4), note: "in extra of mae" },
        { k: "psnr", label: "PSNR (dB)", value: fmt(vals.psnr, 1), note: "higher is better" },
        { k: "ssim", label: "SSIM", value: fmt(vals.ssim, 3), note: "higher is better" },
      ];
      cards.forEach(function (c) { c.main = c.k === hl && c.label.indexOf("RMSE") < 0; });
      if (hl === "ssim") {
        cards.push({ label: "luminance term", value: fmt(lum, 3), note: "compares means" });
        cards.push({ label: "contrast × structure", value: fmt(cs, 3), note: "compares variance and shape" });
      }
      f.readouts(cards);
    });
  };

  // Dynamic time warping with a Sakoe–Chiba band (dtw.py: squared cost, sqrt at the end).
  VIZ.dtw = function (root) {
    var f = frame(root), fs = 100;
    f.slider("shift", "Time shift", -150, 150, 5, 60, { unit: " ms", digits: 0 });
    f.slider("str", "Time stretch (slower rhythm)", 0.8, 1.25, 0.01, 1, { unit: "×" });
    f.slider("win", "Band width (window)", 0.02, 1, 0.01, 0.1, { help: "fraction of the length" });
    f.presets([
      ["Shifted 60 ms", { shift: 60, str: 1, win: 0.1 }],
      ["Shift beyond the band", { shift: 150, str: 1, win: 0.05 }],
      ["Stretched", { shift: 0, str: 1.2, win: 0.1 }],
      ["No band (full DTW)", { shift: 150, str: 1, win: 1 }],
    ]);
    f.draw(function () {
      // Slightly widened QRS so the 100 Hz demo grid resolves the R peak.
      var o = beatOpts({ qrs: 1.6 }), a = beat(fs, 1.2, 0.45, o), st = f.v("str"), sh = f.v("shift") / 1000, n = a.length, i, j;
      var b = new Float64Array(n);
      for (i = 0; i < n; i++) b[i] = beatAt((i / fs - 0.45 - sh) / st, o);
      var w = Math.max(1, Math.floor(f.v("win") * n)), D = [], cost = [];
      for (i = 0; i <= n; i++) { D.push(new Float64Array(n + 1).fill(Infinity)); }
      D[0][0] = 0;
      for (i = 1; i <= n; i++) {
        cost.push(new Float64Array(n));
        for (j = Math.max(1, i - w); j <= Math.min(n, i + w); j++) {
          var c = (a[i - 1] - b[j - 1]) * (a[i - 1] - b[j - 1]);
          D[i][j] = c + Math.min(D[i - 1][j], D[i][j - 1], D[i - 1][j - 1]);
        }
        for (j = 0; j < n; j++) cost[i - 1][j] = (a[i - 1] - b[j]) * (a[i - 1] - b[j]);
      }
      var dtw = Math.sqrt(D[n][n]), eu = 0;
      for (i = 0; i < n; i++) eu += (a[i] - b[i]) * (a[i] - b[i]);
      eu = Math.sqrt(eu);
      var path = [], pi = n, pj = n;
      while (pi > 1 || pj > 1) {
        path.push([pi - 1, pj - 1]);
        var opts = [[pi - 1, pj - 1], [pi - 1, pj], [pi, pj - 1]].filter(function (q) { return q[0] >= 1 && q[1] >= 1; });
        opts.sort(function (q, r) { return D[q[0]][q[1]] - D[r[0]][r[1]]; });
        if (!opts.length) break;
        pi = opts[0][0]; pj = opts[0][1];
      }
      path.push([0, 0]);
      var row = el("div", { class: "mviz-row" });
      var p = plot(420, 300, { l: 10, r: 10, t: 10, b: 30 }, [0, 1.2], [-2.2, 1.4]);
      axes(p, { xticks: [0, 0.4, 0.8, 1.2], xlabel: "time (s)" });
      var off = 1.5;
      path.forEach(function (q, k) {
        if (k % 4) return;
        p.svg.appendChild(sv("path", { d: "M" + p.X(q[0] / fs) + " " + p.Y(a[q[0]]) + "L" + p.X(q[1] / fs) + " " + p.Y(b[q[1]] - off), class: "mv-match" }));
      });
      line(p, function (k) { return k / fs; }, a, "mv-real mv-line");
      line(p, function (k) { return k / fs; }, Array.prototype.map.call(b, function (v) { return v - off; }), "mv-synth mv-line");
      // Cost matrix with band and optimal warping path.
      var size = 260, cv = el("canvas", { width: size, height: size, class: "mviz-canvas", "aria-label": "DTW cost matrix" });
      var ctx = cv.getContext("2d"), cell = size / n, mx = 0;
      for (i = 0; i < n; i++) for (j = 0; j < n; j++) mx = Math.max(mx, cost[i][j]);
      var bg = cssVar("--md-default-bg-color", "#fff"), fg = cssVar("--mviz-heat", "#3949ab");
      ctx.fillStyle = bg; ctx.fillRect(0, 0, size, size);
      ctx.fillStyle = fg;
      for (i = 0; i < n; i++) for (j = 0; j < n; j++) {
        ctx.globalAlpha = Math.sqrt(cost[i][j] / (mx || 1)) * 0.85;
        ctx.fillRect(j * cell, size - (i + 1) * cell, cell + 0.5, cell + 0.5);
      }
      ctx.globalAlpha = 1;
      ctx.strokeStyle = cssVar("--md-default-fg-color--light", "#888");
      ctx.setLineDash([4, 3]);
      ctx.beginPath();
      ctx.moveTo(w * cell, size); ctx.lineTo(size, w * cell);
      ctx.moveTo(0, size - w * cell); ctx.lineTo(size - w * cell, 0);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.strokeStyle = cssVar("--mviz-synth", "#e8590c");
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      path.forEach(function (q, k) {
        var X = (q[1] + 0.5) * cell, Y = size - (q[0] + 0.5) * cell;
        if (k) ctx.lineTo(X, Y); else ctx.moveTo(X, Y);
      });
      ctx.stroke();
      row.appendChild(p.svg);
      row.appendChild(el("figure", { class: "mviz-fig" }, [cv, el("figcaption", { text: "Cost matrix (rows: real, columns: synthetic). Dark = large difference; dashed = band; line = optimal warping path." })]));
      f.stage.appendChild(legend([["mv-real", "Real"], ["mv-synth", "Synthetic (drawn lower)"], ["mv-matchkey", "Matched samples"]]));
      f.stage.appendChild(row);
      f.readouts([
        { label: "DTW distance", value: fmt(dtw), main: true, note: "lower is better" },
        { label: "Euclidean distance (no warping)", value: fmt(eu), note: "what a point-wise metric sees" },
        { label: "Band", value: w + " samples", note: "|i − j| ≤ window × length" },
      ]);
    });
  };

  // Template correlation (sqi.py): mean of normalised real beats vs each synthetic beat.
  VIZ.sqi = function (root) {
    var f = frame(root), fs = 250, N = 25, zr = normals(51, 8 * N), zs = normals(52, 8 * N), nz = normals(53, 260 * N);
    f.slider("qrs", "QRS width", 0.7, 2.2, 0.05, 1, { unit: "×" });
    f.slider("t", "T-wave amplitude", -1, 1.5, 0.05, 1, { unit: "×" });
    f.slider("jit", "Timing jitter", 0, 80, 2, 8, { unit: " ms", digits: 0 });
    f.slider("noise", "Noise", 0, 0.2, 0.005, 0.02, { unit: " mV", digits: 3 });
    f.presets([
      ["Realistic", { qrs: 1, t: 1, jit: 8, noise: 0.02 }],
      ["Wide QRS", { qrs: 1.8, t: 1, jit: 8, noise: 0.02 }],
      ["Inverted T", { qrs: 1, t: -0.7, jit: 8, noise: 0.02 }],
      ["Misaligned beats", { qrs: 1, t: 1, jit: 60, noise: 0.02 }],
      ["Very noisy", { qrs: 1, t: 1, jit: 8, noise: 0.15 }],
      ["Mean beat only", { qrs: 1, t: 1, jit: 0, noise: 0 }],
    ]);
    function unit(x) {
      var lo = Infinity, hi = -Infinity, i, o = new Float64Array(x.length);
      for (i = 0; i < x.length; i++) { lo = Math.min(lo, x[i]); hi = Math.max(hi, x[i]); }
      for (i = 0; i < x.length; i++) o[i] = (x[i] - lo) / (hi - lo + 1e-12);
      return o;
    }
    function corr(a, b) {
      var ma = mean(a), mb = mean(b), s = 0, sa = 0, sb = 0;
      for (var i = 0; i < a.length; i++) { s += (a[i] - ma) * (b[i] - mb); sa += (a[i] - ma) * (a[i] - ma); sb += (b[i] - mb) * (b[i] - mb); }
      return s / Math.sqrt(sa * sb + 1e-12);
    }
    function make(z, k, qrs, t, jit, noise, nOff) {
      var o = beatOpts({ amp: 1 + 0.08 * z[8 * k], qrs: qrs * (1 + 0.04 * z[8 * k + 1]), t: t * (1 + 0.1 * z[8 * k + 2]) });
      var x = beat(fs, 0.9, 0.3 + (jit / 1000) * z[8 * k + 3], o);
      for (var i = 0; i < x.length; i++) x[i] += noise * nz[(nOff + k * 230 + i) % nz.length];
      return x;
    }
    f.draw(function () {
      var real = [], syn = [], k, i;
      for (k = 0; k < N; k++) real.push(unit(make(zr, k, 1, 1, 8, 0.02, 0)));
      for (k = 0; k < N; k++) syn.push(unit(make(zs, k, f.v("qrs"), f.v("t"), f.v("jit"), f.v("noise"), 7000)));
      var T = new Float64Array(real[0].length);
      real.forEach(function (x) { for (i = 0; i < T.length; i++) T[i] += x[i] / N; });
      var sq = mean(syn.map(function (x) { return corr(x, T); })), self = mean(real.map(function (x) { return corr(x, T); }));
      var p = plot(640, 260, { l: 44, r: 10, t: 10, b: 34 }, [0, 0.9], [-0.1, 1.1]);
      axes(p, { xticks: [0, 0.3, 0.6, 0.9], yticks: [0, 0.5, 1], xlabel: "time (s)", ylabel: "normalised amplitude" });
      syn.forEach(function (x) { line(p, function (j) { return j / fs; }, x, "mv-synth mv-thin"); });
      line(p, function (j) { return j / fs; }, T, "mv-real mv-bold");
      f.stage.appendChild(legend([["mv-real", "Real template (mean of normalised real beats)"], ["mv-synth", "Synthetic beats"]]));
      f.stage.appendChild(p.svg);
      f.readouts([
        { label: "SQI (synthetic)", value: fmt(sq), main: true, note: "higher is better" },
        { label: "Real self-SQI", value: fmt(self), note: "ceiling: real beats vs their own template (each is part of it)" },
      ]);
    });
  };

  // Mean normalised PSD of each set and their Jensen–Shannon divergence (psd.py).
  VIZ.psd = function (root) {
    var f = frame(root), fs = 250, dur = 8, R = 6;
    f.slider("hr", "Synthetic heart rate", 45, 120, 1, 70, { unit: " bpm", digits: 0 });
    f.slider("noise", "White noise", 0, 0.2, 0.005, 0.01, { unit: " mV", digits: 3 });
    f.slider("mains", "50 Hz interference", 0, 0.2, 0.005, 0, { unit: " mV", digits: 3 });
    f.slider("wander", "Baseline wander (0.3 Hz)", 0, 0.6, 0.01, 0, { unit: " mV" });
    f.presets([
      ["Matched", { hr: 70, noise: 0.01, mains: 0, wander: 0 }],
      ["Mains hum", { hr: 70, noise: 0.01, mains: 0.08, wander: 0 }],
      ["High-frequency noise", { hr: 70, noise: 0.12, mains: 0, wander: 0 }],
      ["Baseline wander", { hr: 70, noise: 0.01, mains: 0, wander: 0.4 }],
      ["Faster rhythm", { hr: 105, noise: 0.01, mains: 0, wander: 0 }],
    ]);
    var realCache = null;
    function meanPsd(list) {
      var acc = null;
      list.forEach(function (x) {
        var p = welch(x);
        if (!acc) acc = new Float64Array(p.length);
        for (var i = 0; i < p.length; i++) acc[i] += p[i] / list.length;
      });
      return normalise(acc, 0);
    }
    f.draw(function () {
      var hr = [68, 72, 64, 75, 70, 66];
      if (!realCache) {
        var rl = [];
        for (var k = 0; k < R; k++) rl.push(strip(fs, dur, rTimes(hr[k], 40, 15, dur, 100 + k), beatOpts(), 0.01, 200 + k));
        realCache = { sig: rl[0], psd: meanPsd(rl) };
      }
      var sl = [];
      for (k = 0; k < R; k++) {
        sl.push(strip(fs, dur, rTimes(f.v("hr") + (hr[k] - 70), 40, 15, dur, 300 + k), beatOpts(), f.v("noise"), 400 + k,
          { mains: f.v("mains"), wander: f.v("wander") }));
      }
      var ps = meanPsd(sl), pr = realCache.psd, freqs = [], i;
      for (i = 0; i < pr.length; i++) freqs.push((i * fs) / 256);
      var js = 0;
      for (i = 0; i < pr.length; i++) {
        var m = 0.5 * (pr[i] + ps[i]);
        if (pr[i] > 0) js += 0.5 * pr[i] * Math.log(pr[i] / (m + 1e-12));
        if (ps[i] > 0) js += 0.5 * ps[i] * Math.log(ps[i] / (m + 1e-12));
      }
      var row = el("div", { class: "mviz-col" });
      var t = plot(640, 150, { l: 44, r: 10, t: 8, b: 30 }, [0, 4], [-1.2, 1.6]);
      axes(t, { xticks: [0, 1, 2, 3, 4], xlabel: "first 4 s of one recording (s)" });
      var nT = 4 * fs;
      line(t, function (j) { return j / fs; }, Array.prototype.slice.call(realCache.sig, 0, nT).map(function (v) { return v + 0.35; }), "mv-real mv-line");
      line(t, function (j) { return j / fs; }, Array.prototype.slice.call(sl[0], 0, nT).map(function (v) { return v - 0.5; }), "mv-synth mv-line");
      var lg = function (v) { return Math.log10(Math.max(v, 1e-7)); };
      var p = plot(640, 260, { l: 44, r: 10, t: 8, b: 34 }, [0, 70], [-7, 0]);
      axes(p, { xticks: [0, 10, 20, 30, 40, 50, 60, 70], yticks: [-6, -4, -2, 0], yfmt: function (v) { return "1e" + v; },
        xlabel: "frequency (Hz)", ylabel: "share of power" });
      var keep = freqs.filter(function (q) { return q <= 70; }).length;
      line(p, freqs.slice(0, keep), Array.prototype.slice.call(pr, 0, keep).map(lg), "mv-real mv-line");
      line(p, freqs.slice(0, keep), Array.prototype.slice.call(ps, 0, keep).map(lg), "mv-synth mv-line");
      row.appendChild(t.svg);
      row.appendChild(p.svg);
      f.stage.appendChild(legend([["mv-real", "Real (6 recordings)"], ["mv-synth", "Synthetic (6 recordings)"]]));
      f.stage.appendChild(row);
      f.readouts([
        { label: "PSD JS divergence", value: fmt(js, 4), main: true, note: "0 = same spectrum, max ln 2 ≈ 0.693" },
      ]);
    });
  };

  // Distribution of per-recording spectral entropy (spectral_entropy.py).
  VIZ.spectralEntropy = function (root) {
    var f = frame(root), fs = 250, dur = 4, N = 80, zr = normals(61, N), zs = normals(62, N);
    f.slider("noise", "Synthetic noise level", 0.005, 0.15, 0.005, 0.03, { unit: " mV", digits: 3 });
    f.slider("var", "Noise varies between recordings", 0, 1.5, 0.05, 0.6, { help: "log-normal spread" });
    f.presets([
      ["Matched", { noise: 0.03, var: 0.6 }],
      ["Too clean", { noise: 0.008, var: 0.6 }],
      ["Too noisy", { noise: 0.1, var: 0.6 }],
      ["All alike", { noise: 0.03, var: 0 }],
    ]);
    function se(x) {
      var p = normalise(welch(x), 0), s = 0;
      for (var i = 0; i < p.length; i++) if (p[i] > 0) s -= p[i] * Math.log2(p[i]);
      return s;
    }
    var realSe = null;
    f.draw(function () {
      var k;
      if (!realSe) {
        realSe = [];
        for (k = 0; k < N; k++) {
          realSe.push(se(strip(fs, dur, rTimes(70 + 8 * zr[k], 30, 10, dur, 500 + k), beatOpts(), 0.03 * Math.exp(0.6 * zr[(k + 7) % N]), 600 + k)));
        }
      }
      var synSe = [];
      for (k = 0; k < N; k++) {
        synSe.push(se(strip(fs, dur, rTimes(70 + 8 * zs[k], 30, 10, dur, 700 + k), beatOpts(), f.v("noise") * Math.exp(f.v("var") * zs[(k + 7) % N]), 800 + k)));
      }
      var r = jsSamples(realSe, synSe, 50);
      var top = Math.max(Math.max.apply(null, r.hp), Math.max.apply(null, r.hq)) * 1.15;
      var p = plot(640, 260, { l: 44, r: 10, t: 10, b: 34 }, [r.lo, r.hi], [0, top]);
      var ticks = [];
      for (var t = Math.ceil(r.lo * 2) / 2; t <= r.hi; t += 0.5) ticks.push(+t.toFixed(1));
      axes(p, { xticks: ticks.length > 8 ? ticks.filter(function (_, i) { return i % 2 === 0; }) : ticks, xlabel: "spectral entropy per recording (bits)", ylabel: "recordings" });
      bars(p, r.hp, r.lo, r.hi, "mv-real mv-bar");
      bars(p, r.hq, r.lo, r.hi, "mv-synth mv-bar");
      f.stage.appendChild(legend([["mv-real", "Real (80 recordings)"], ["mv-synth", "Synthetic (80 recordings)"]]));
      f.stage.appendChild(p.svg);
      f.readouts([
        { label: "Spectral-entropy JS divergence", value: fmt(r.js, 4), main: true, note: "lower is better (max ln 2)" },
        { label: "Mean SE real / synthetic", value: fmt(mean(realSe), 2) + " / " + fmt(mean(synSe), 2), note: "bits" },
      ]);
    });
  };

  // Heart-rate distributions (heart_rate.py) with R-peak detection on an example strip.
  VIZ.heartRate = function (root) {
    var f = frame(root), N = 300, zr = normals(71, N), zs = normals(72, N), fs = 250;
    f.slider("mu", "Synthetic mean heart rate", 50, 115, 1, 72, { unit: " bpm", digits: 0 });
    f.slider("sd", "Synthetic spread (SD)", 1, 25, 0.5, 11, { unit: " bpm", digits: 1 });
    f.presets([
      ["Matched", { mu: 72, sd: 11 }],
      ["Too fast", { mu: 95, sd: 11 }],
      ["Too uniform", { mu: 72, sd: 2 }],
    ]);
    function detect(x) {
      // heart_rate.py: height = mean + 0.5·std, peaks at least 0.5 s apart.
      var h = mean(x) + 0.5 * std(x), dist = Math.round(0.5 * fs), peaks = [], i;
      for (i = 1; i < x.length - 1; i++) {
        if (x[i] >= h && x[i] >= x[i - 1] && x[i] > x[i + 1]) {
          if (peaks.length && i - peaks[peaks.length - 1] < dist) {
            if (x[i] > x[peaks[peaks.length - 1]]) peaks[peaks.length - 1] = i;
          } else peaks.push(i);
        }
      }
      return peaks;
    }
    f.draw(function () {
      var real = [], syn = [], i;
      for (i = 0; i < N; i++) {
        real.push(Math.min(150, Math.max(40, 72 + 11 * zr[i])));
        syn.push(Math.min(150, Math.max(40, f.v("mu") + f.v("sd") * zs[i])));
      }
      var r = jsSamples(real, syn, 50);
      var ex = strip(fs, 5, rTimes(f.v("mu"), 20, 10, 5, 77), beatOpts(), 0.02, 78);
      var pk = detect(ex), hr = pk.length > 1 ? (60 * fs) / ((pk[pk.length - 1] - pk[0]) / (pk.length - 1)) : NaN;
      var t = plot(640, 140, { l: 44, r: 10, t: 8, b: 30 }, [0, 5], [-0.6, 1.4]);
      axes(t, { xticks: [0, 1, 2, 3, 4, 5], xlabel: "example synthetic strip (s) — dots: detected R peaks" });
      line(t, function (j) { return j / fs; }, ex, "mv-synth mv-line");
      pk.forEach(function (k) { dot(t, k / fs, ex[k], 4, "mv-accent mv-dotc"); });
      var top = Math.max(Math.max.apply(null, r.hp), Math.max.apply(null, r.hq)) * 1.15;
      var p = plot(640, 240, { l: 44, r: 10, t: 10, b: 34 }, [r.lo, r.hi], [0, top]);
      var ticks = [];
      for (var v = Math.ceil(r.lo / 10) * 10; v <= r.hi; v += 10) ticks.push(v);
      axes(p, { xticks: ticks, xlabel: "heart rate per recording (bpm)", ylabel: "recordings" });
      bars(p, r.hp, r.lo, r.hi, "mv-real mv-bar");
      bars(p, r.hq, r.lo, r.hi, "mv-synth mv-bar");
      f.stage.appendChild(legend([["mv-real", "Real (300 recordings)"], ["mv-synth", "Synthetic (300 recordings)"]]));
      f.stage.appendChild(el("div", { class: "mviz-col" }, [t.svg, p.svg]));
      f.readouts([
        { label: "heart_rate score (JS)", value: fmt(r.js, 4), main: true, note: "lower is better (max ln 2)" },
        { label: "HR of the example strip", value: fmt(hr, 0) + " bpm", note: "60 / mean RR" },
      ]);
    });
  };

  // HRV statistics: SDNN, RMSSD and pNN50 per recording, JS divergence of each (hrv.py).
  VIZ.hrv = function (root) {
    var f = frame(root), N = 200;
    f.slider("slow", "Synthetic slow variability (breathing)", 0, 120, 2, 40, { unit: " ms", digits: 0 });
    f.slider("beat", "Synthetic beat-to-beat noise", 0, 80, 1, 15, { unit: " ms", digits: 0 });
    f.slider("dur", "Recording length (both sets)", 10, 120, 5, 10, { unit: " s", digits: 0 });
    f.presets([
      ["Matched", { slow: 40, beat: 15 }],
      ["Metronome (no variability)", { slow: 2, beat: 1 }],
      ["Erratic", { slow: 40, beat: 70 }],
      ["Matched, 2-minute strips", { slow: 40, beat: 15, dur: 120 }],
    ]);
    function stats(rt) {
      var rr = [], i;
      for (i = 1; i < rt.length; i++) rr.push((rt[i] - rt[i - 1]) * 1000);
      var d = [], nn50 = 0;
      for (i = 1; i < rr.length; i++) { d.push(rr[i] - rr[i - 1]); if (Math.abs(rr[i] - rr[i - 1]) > 50) nn50++; }
      // hrv.py: SDNN with ddof=1, RMSSD over successive differences, pNN50 as a fraction.
      var m = mean(rr), ss = 0;
      for (i = 0; i < rr.length; i++) ss += (rr[i] - m) * (rr[i] - m);
      var rmssd = Math.sqrt(mean(d.map(function (v) { return v * v; })));
      return [Math.sqrt(ss / Math.max(1, rr.length - 1)), rmssd, nn50 / Math.max(1, d.length)];
    }
    var zh = normals(81, N), zh2 = normals(82, N);
    f.draw(function () {
      var dur = f.v("dur"), real = [[], [], []], syn = [[], [], []], ex = null, exr = null, k;
      for (k = 0; k < N; k++) {
        var rr = rTimes(70 + 8 * zh[k], 40, 15, dur, 900 + k).filter(function (t) { return t >= 0 && t <= dur; });
        var ss = rTimes(70 + 8 * zh2[k], f.v("slow"), f.v("beat"), dur, 1900 + k).filter(function (t) { return t >= 0 && t <= dur; });
        var a = stats(rr), b = stats(ss);
        for (var q = 0; q < 3; q++) { real[q].push(a[q]); syn[q].push(b[q]); }
        if (k === 0) { exr = rr; ex = ss; }
      }
      var names = ["SDNN (ms)", "RMSSD (ms)", "pNN50 (fraction)"], js = [];
      var tach = plot(640, 150, { l: 44, r: 10, t: 8, b: 30 }, [0, dur], [450, 1300]);
      axes(tach, { xticks: [0, dur / 2, dur], yticks: [600, 900, 1200], xlabel: "time (s) — RR interval of each beat (tachogram)", ylabel: "RR (ms)" });
      [[exr, "mv-real"], [ex, "mv-synth"]].forEach(function (s) {
        var xs = [], ys = [];
        for (var i = 1; i < s[0].length; i++) { xs.push(s[0][i]); ys.push((s[0][i] - s[0][i - 1]) * 1000); }
        line(tach, xs, ys, s[1] + " mv-line");
        xs.forEach(function (x, i) { dot(tach, x, ys[i], 2.5, s[1] + " mv-dotc"); });
      });
      var row = el("div", { class: "mviz-row mviz-row3" });
      for (var q = 0; q < 3; q++) {
        var r = jsSamples(real[q], syn[q], 50);
        js.push(r.js);
        var top = Math.max(Math.max.apply(null, r.hp), Math.max.apply(null, r.hq)) * 1.15;
        var p = plot(220, 170, { l: 10, r: 10, t: 10, b: 34 }, [r.lo, r.hi], [0, top]);
        axes(p, { xticks: [r.lo, r.hi], xfmt: function (v) { return q === 2 ? v.toFixed(2) : v.toFixed(0); }, xlabel: names[q] + " · JS " + fmt(r.js, 3) });
        bars(p, r.hp, r.lo, r.hi, "mv-real mv-bar");
        bars(p, r.hq, r.lo, r.hi, "mv-synth mv-bar");
        row.appendChild(p.svg);
      }
      f.stage.appendChild(legend([["mv-real", "Real (200 recordings)"], ["mv-synth", "Synthetic (200 recordings)"]]));
      f.stage.appendChild(el("div", { class: "mviz-col" }, [tach.svg, row]));
      f.readouts([
        { label: "hrv score (mean of 3 JS)", value: fmt(mean(js), 4), main: true, note: "lower is better" },
        { label: "Mean SDNN real / synthetic", value: fmt(mean(real[0]), 0) + " / " + fmt(mean(syn[0]), 0) + " ms" },
        { label: "Mean RMSSD real / synthetic", value: fmt(mean(real[1]), 0) + " / " + fmt(mean(syn[1]), 0) + " ms" },
      ]);
    });
  };

  // ------------------------------------------------------------------ boot

  function boot() {
    document.querySelectorAll(".mviz[data-viz]:not(.mviz-ready)").forEach(function (root) {
      var fn = VIZ[root.dataset.viz];
      if (!fn) return;
      try {
        fn(root);
      } catch (e) {
        root.textContent = "This visualization could not be drawn: " + e.message;
        if (window.console) console.error(e);
      }
    });
  }
  if (typeof document$ !== "undefined" && document$.subscribe) document$.subscribe(boot);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
