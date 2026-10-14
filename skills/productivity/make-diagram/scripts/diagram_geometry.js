// Measures every diagram <svg> on the loaded page as the browser drew it and
// returns findings. check_diagram.py evaluates this once per colour scheme.
//
// The drawing vocabulary it reads:
//   g.node      a box: one shape (rect, ellipse, circle, polygon, path) and its text
//   g.decision  a diamond: one polygon and its question
//   g.group     a bubble or lane drawn around related nodes: one shape and a title
//   .arrow.<kind>  a line, polyline or path; kind is yes, no, data, loop or next
//   g.legend    the arrow-colour legend: one sample arrow and a short label per kind
// Any other <text> is an arrow label and must sit beside the arrow it labels.
(() => {
  const KINDS = ["yes", "no", "data", "loop", "next"];
  const MIN_FONT_PX = 15;
  const MAX_ROWS = 3;
  const MAX_ROW_CHARS = 32;
  const TOUCH_PX = 10;
  const LABEL_REACH_PX = 28;
  const END_CLEARANCE_PX = 14;
  const SAMPLE_STEP_PX = 3;
  const MIN_CONTRAST = 4.5;
  const SHAPES = "rect, ellipse, circle, polygon, path, polyline";
  const SCHEME_FALLBACK = matchMedia("(prefers-color-scheme: dark)").matches
    ? [18, 18, 18] : [255, 255, 255];

  const findings = [];
  const add = (rule, message) => findings.push({ rule, message });

  const box = (el) => {
    const r = el.getBoundingClientRect();
    return { l: r.left, t: r.top, r: r.right, b: r.bottom };
  };
  const grow = (b, d) => ({ l: b.l - d, t: b.t - d, r: b.r + d, b: b.b + d });
  const contains = (b, p) => p.x >= b.l && p.x <= b.r && p.y >= b.t && p.y <= b.b;
  const area = (b) => Math.max(0, b.r - b.l) * Math.max(0, b.b - b.t);
  const overlapArea = (a, b) => area({
    l: Math.max(a.l, b.l), t: Math.max(a.t, b.t),
    r: Math.min(a.r, b.r), b: Math.min(a.b, b.b),
  });
  const distanceToBox = (p, b) => Math.hypot(
    Math.max(b.l - p.x, 0, p.x - b.r), Math.max(b.t - p.y, 0, p.y - b.b));
  const centre = (b) => ({ x: (b.l + b.r) / 2, y: (b.t + b.b) / 2 });
  const corners = (b) => [
    { x: b.l, y: b.t }, { x: b.r, y: b.t }, { x: b.l, y: b.b }, { x: b.r, y: b.b }];
  const insideDiamond = (d, p) => {
    const c = centre(d);
    return Math.abs(p.x - c.x) / ((d.r - d.l) / 2)
      + Math.abs(p.y - c.y) / ((d.b - d.t) / 2) <= 1.0001;
  };
  const quote = (s) => `"${s}"`;

  const parseColour = (value) => {
    const m = /rgba?\(([^)]+)\)/.exec(value || "");
    if (!m) return null;
    const parts = m[1].split(/[ ,/]+/).filter(Boolean).map(Number);
    return { rgb: parts.slice(0, 3), alpha: parts.length > 3 ? parts[3] : 1 };
  };
  const blend = (top, alpha, under) => top.map((c, i) => c * alpha + under[i] * (1 - alpha));
  const luminance = (rgb) => {
    const [r, g, b] = rgb.map((c) => {
      const s = c / 255;
      return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const contrast = (a, b) => {
    const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
    return (hi + 0.05) / (lo + 0.05);
  };
  const hsl = (rgb) => {
    const [r, g, b] = rgb.map((c) => c / 255);
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const light = (max + min) / 2;
    if (max === min) return { h: 0, s: 0, l: light };
    const d = max - min;
    const s = light > 0.5 ? d / (2 - max - min) : d / (max + min);
    let h;
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) * 60;
    else if (max === g) h = ((b - r) / d + 2) * 60;
    else h = ((r - g) / d + 4) * 60;
    return { h, s, l: light };
  };
  const KIND_HUE = {
    yes: (c) => c.s >= 0.25 && c.h >= 75 && c.h <= 170,
    no: (c) => c.s >= 0.25 && (c.h >= 335 || c.h <= 20),
    data: (c) => c.s >= 0.25 && c.h >= 185 && c.h <= 250,
    loop: (c) => c.s >= 0.25 && c.h >= 25 && c.h <= 60,
    next: (c) => c.s <= 0.2,
  };
  const KIND_COLOUR_NAME = {
    yes: "green", no: "red", data: "blue", loop: "amber", next: "grey",
  };

  // Text rows: tspans and bare texts clustered by their vertical centre.
  const rowsOf = (root) => {
    const pieces = [];
    for (const text of root.querySelectorAll("text")) {
      const spans = [...text.querySelectorAll("tspan")].filter((s) => s.textContent.trim());
      for (const el of spans.length ? spans : [text]) {
        const content = el.textContent.trim();
        if (content) pieces.push({ box: box(el), content });
      }
    }
    pieces.sort((a, b) => centre(a.box).y - centre(b.box).y);
    const rows = [];
    for (const piece of pieces) {
      const last = rows[rows.length - 1];
      const height = piece.box.b - piece.box.t;
      if (last && Math.abs(centre(piece.box).y - last.y) < height * 0.6) {
        last.pieces.push(piece);
      } else {
        rows.push({ y: centre(piece.box).y, pieces: [piece] });
      }
    }
    return rows.map((row) => row.pieces
      .sort((a, b) => a.box.l - b.box.l).map((p) => p.content).join(" "));
  };

  const pageBackground = (svg) => {
    for (let el = svg.parentElement; el; el = el.parentElement) {
      const c = parseColour(getComputedStyle(el).backgroundColor);
      if (c && c.alpha > 0) return c.rgb;
    }
    const first = svg.querySelector(SHAPES);
    if (first && first.tagName === "rect" && !first.closest(".node, .decision, .group, .legend")) {
      const s = box(svg);
      if (area(box(first)) >= 0.9 * area(s)) {
        const c = parseColour(getComputedStyle(first).fill);
        if (c && c.alpha > 0) return c.rgb;
      }
    }
    return SCHEME_FALLBACK;
  };

  const shapeFill = (shape, under) => {
    const style = getComputedStyle(shape);
    const c = parseColour(style.fill);
    if (!c) return under;
    return blend(c.rgb, c.alpha * Number(style.fillOpacity || 1), under);
  };

  const samplePoints = (el) => {
    const ctm = el.getScreenCTM();
    const total = el.getTotalLength();
    const points = [];
    for (let s = 0; s < total; s += SAMPLE_STEP_PX) points.push(el.getPointAtLength(s));
    points.push(el.getPointAtLength(total));
    return points.map((p) => new DOMPoint(p.x, p.y).matrixTransform(ctm));
  };

  const segmentCrossing = (p1, p2, p3, p4) => {
    const d = (p2.x - p1.x) * (p4.y - p3.y) - (p2.y - p1.y) * (p4.x - p3.x);
    if (Math.abs(d) < 1e-9) return null;
    const u = ((p3.x - p1.x) * (p4.y - p3.y) - (p3.y - p1.y) * (p4.x - p3.x)) / d;
    const v = ((p3.x - p1.x) * (p2.y - p1.y) - (p3.y - p1.y) * (p2.x - p1.x)) / d;
    if (u < 0 || u > 1 || v < 0 || v > 1) return null;
    return { x: p1.x + u * (p2.x - p1.x), y: p1.y + u * (p2.y - p1.y) };
  };

  const diagrams = [...document.querySelectorAll("svg")]
    .filter((svg) => svg.querySelector(".node, .decision"));
  const texts = [];

  diagrams.forEach((svg, index) => {
    const label = diagrams.length > 1 ? `diagram ${index + 1}: ` : "";
    const say = (rule, message) => add(rule, label + message);
    const background = pageBackground(svg);
    const svgBox = box(svg);

    const shapeOf = (g) => g.querySelector(`:scope > :is(${SHAPES})`) || g.querySelector(SHAPES);
    const makeShape = (g, kind) => {
      const shape = shapeOf(g);
      const rows = rowsOf(g);
      return {
        g, kind, shape, rows,
        box: shape ? box(shape) : box(g),
        name: quote(rows[0] || `(untitled ${kind})`),
        attached: false,
      };
    };
    const nodes = [...svg.querySelectorAll(".node")].map((g) => makeShape(g, "node"));
    const decisions = [...svg.querySelectorAll(".decision")].map((g) => makeShape(g, "decision"));
    const groups = [...svg.querySelectorAll(".group")].map((g) => makeShape(g, "group"));
    const boxes = [...nodes, ...decisions];
    for (const shape of [...boxes, ...groups]) {
      if (!shape.shape) say("float", `${shape.kind} ${shape.name} has no shape to draw it`);
    }

    // A node sits in the smallest group whose bubble holds its centre.
    for (const node of boxes) {
      node.group = groups
        .filter((g) => g.g !== node.g && contains(g.box, centre(node.box)))
        .sort((a, b) => area(a.box) - area(b.box))[0];
    }

    const legend = svg.querySelector(".legend");
    const arrowElements = [...svg.querySelectorAll(".arrow")]
      .filter((el) => !el.closest(".legend"));
    const geometryOf = (el) => (el instanceof SVGGeometryElement
      ? el : el.querySelector("path, line, polyline"));

    const attachTo = (point) => {
      const hit = boxes
        .filter((s) => contains(grow(s.box, TOUCH_PX), point))
        .sort((a, b) => area(a.box) - area(b.box))[0];
      if (hit) return hit;
      return groups
        .filter((g) => contains(grow(g.box, TOUCH_PX), point)
          && !contains(grow(g.box, -TOUCH_PX), point))
        .sort((a, b) => area(a.box) - area(b.box))[0];
    };

    const arrows = [];
    for (const el of arrowElements) {
      const geometry = geometryOf(el);
      if (!geometry) continue;
      const kinds = KINDS.filter((k) => el.classList.contains(k));
      const points = samplePoints(geometry);
      const start = points[0];
      const end = points[points.length - 1];
      const from = attachTo(start);
      const to = attachTo(end);
      const style = getComputedStyle(geometry);
      const arrow = {
        el, geometry, kinds, points, start, end, from, to,
        stroke: parseColour(style.stroke),
        dashed: style.strokeDasharray && style.strokeDasharray !== "none",
        labels: [],
      };
      arrow.name = `arrow ${from ? from.name : "(from nowhere)"} → ${to ? to.name : "(to nowhere)"}`;
      if (from) from.attached = true;
      if (to) to.attached = true;
      arrows.push(arrow);
    }

    // Nothing floats.
    for (const arrow of arrows) {
      if (!arrow.from) say("float", `${arrow.name} starts in empty space`);
      if (!arrow.to) say("float", `${arrow.name} ends in empty space`);
    }
    const groupAttached = (g) => g && (g.attached || groupAttached(g.group));
    for (const g of groups) {
      g.group = groups
        .filter((o) => o !== g && contains(o.box, centre(g.box)) && area(o.box) > area(g.box))
        .sort((a, b) => area(a.box) - area(b.box))[0];
    }
    for (const node of boxes) {
      if (!node.attached && !groupAttached(node.group)) {
        say("float", `${node.kind} ${node.name} has no arrow to or from it, and no arrow reaches its group`);
      }
    }

    // Every text, for size, overlap, contrast and the words file.
    const allTexts = [...svg.querySelectorAll("text")].filter((t) => t.textContent.trim());
    const textInfo = allTexts.map((t) => ({
      el: t, box: box(t), content: t.textContent.trim().replace(/\s+/g, " "),
      owner: t.closest(".node, .decision, .group, .legend"),
    }));
    for (const t of textInfo) texts.push(t.content);

    for (const t of textInfo) {
      let smallest = Infinity;
      for (const el of [t.el, ...t.el.querySelectorAll("tspan")]) {
        const m = el.getScreenCTM();
        const scale = m ? Math.hypot(m.a, m.b) : 1;
        smallest = Math.min(smallest, parseFloat(getComputedStyle(el).fontSize) * scale);
      }
      if (smallest < MIN_FONT_PX - 0.05) {
        say("size", `${quote(t.content)} is ${smallest.toFixed(1)}px where it is drawn`);
      }
    }

    // Box text.
    for (const shape of boxes) {
      if (shape.rows.length > MAX_ROWS) {
        say("box", `${shape.kind} ${shape.name} has ${shape.rows.length} rows of text`);
      }
      for (const row of shape.rows) {
        if (row.length > MAX_ROW_CHARS) {
          say("box", `${shape.kind} ${shape.name} has a ${row.length}-character row: ${quote(row)}`);
        }
      }
    }

    // Overlaps, spills and text on lines.
    for (let i = 0; i < textInfo.length; i += 1) {
      for (let j = i + 1; j < textInfo.length; j += 1) {
        if (overlapArea(grow(textInfo[i].box, -1), grow(textInfo[j].box, -1)) > 0) {
          say("overlap", `${quote(textInfo[i].content)} overlaps ${quote(textInfo[j].content)}`);
        }
      }
    }
    for (const t of textInfo) {
      if (corners(t.box).some((p) => !contains(grow(svgBox, 0.5), p))) {
        say("overlap", `${quote(t.content)} runs past the edge of the drawing`);
      }
      const owner = boxes.find((s) => s.g === t.owner);
      if (owner && owner.shape) {
        const inner = grow(t.box, -1);
        const fits = owner.kind === "decision"
          ? corners(inner).every((p) => insideDiamond(owner.box, p))
          : corners(inner).every((p) => contains(owner.box, p));
        if (!fits) say("overlap", `${quote(t.content)} spills out of ${owner.kind} ${owner.name}`);
      }
      const inner = grow(t.box, -1);
      for (const arrow of arrows) {
        if (arrow.points.some((p) => contains(inner, p))) {
          say("overlap", `${quote(t.content)} sits on the ${arrow.name}`);
        }
      }
    }

    // Arrows that cross each other or run through a box they do not connect.
    const awayFromEnds = (arrow) => arrow.points.filter((p) =>
      Math.hypot(p.x - arrow.start.x, p.y - arrow.start.y) > END_CLEARANCE_PX
      && Math.hypot(p.x - arrow.end.x, p.y - arrow.end.y) > END_CLEARANCE_PX);
    for (const arrow of arrows) {
      const middle = awayFromEnds(arrow);
      for (const shape of boxes) {
        if (shape === arrow.from || shape === arrow.to || !shape.shape) continue;
        if (middle.some((p) => contains(grow(shape.box, -3), p))) {
          say("crossing", `${arrow.name} runs through ${shape.kind} ${shape.name}`);
        }
      }
    }
    const nearAnyEnd = (p, ...list) => list.some((a) =>
      [a.start, a.end].some((e) => Math.hypot(p.x - e.x, p.y - e.y) <= END_CLEARANCE_PX));
    for (let i = 0; i < arrows.length; i += 1) {
      for (let j = i + 1; j < arrows.length; j += 1) {
        const a = arrows[i];
        const b = arrows[j];
        let crossed = false;
        for (let s = 1; s < a.points.length && !crossed; s += 1) {
          for (let u = 1; u < b.points.length && !crossed; u += 1) {
            const p = segmentCrossing(a.points[s - 1], a.points[s], b.points[u - 1], b.points[u]);
            if (p && !nearAnyEnd(p, a, b)) crossed = true;
          }
        }
        if (crossed) say("crossing", `${a.name} crosses the ${b.name}`);
      }
    }

    // Direction.
    for (const arrow of arrows) {
      if (arrow.kinds.includes("loop")) continue;
      const dx = arrow.end.x - arrow.start.x;
      const dy = arrow.end.y - arrow.start.y;
      if (dy < -TOUCH_PX) say("direction", `${arrow.name} points upward`);
      else if (dx < -TOUCH_PX && dy <= TOUCH_PX) say("direction", `${arrow.name} points right to left within a row`);
    }

    // Loose text labels the nearest arrow, or it floats.
    for (const t of textInfo.filter((x) => !x.owner)) {
      let nearest = null;
      let distance = Infinity;
      for (const arrow of arrows) {
        for (const p of arrow.points) {
          const d = distanceToBox(p, t.box);
          if (d < distance) { distance = d; nearest = arrow; }
        }
      }
      if (nearest && distance <= LABEL_REACH_PX) nearest.labels.push(t.content);
      else say("float", `${quote(t.content)} is loose text that labels no arrow`);
    }

    // Decisions.
    for (const decision of decisions) {
      const out = arrows.filter((a) => a.from === decision);
      for (const kind of ["yes", "no"]) {
        const branch = out.filter((a) => a.kinds.includes(kind));
        if (!branch.length) say("decision", `decision ${decision.name} is missing its ${kind} branch`);
        for (const a of branch) {
          if (!a.labels.length) say("decision", `the ${kind} branch of decision ${decision.name} has no label`);
        }
      }
      for (const a of out.filter((x) => !x.kinds.some((k) => k === "yes" || k === "no"))) {
        say("decision", `decision ${decision.name} has a branch that is neither yes nor no (${a.name})`);
      }
      if (decision.shape && decision.shape.tagName !== "polygon") {
        say("decision", `decision ${decision.name} is drawn as a ${decision.shape.tagName}, not a diamond`);
      }
    }
    for (const arrow of arrows) {
      const branchKind = arrow.kinds.find((k) => k === "yes" || k === "no");
      if (branchKind && !(arrow.from && arrow.from.kind === "decision")) {
        say("decision", `${arrow.name} is coloured ${branchKind} but does not leave a decision`);
      }
    }

    // Colour.
    const strokesByKind = {};
    for (const arrow of arrows) {
      if (arrow.kinds.length !== 1) {
        say("colour", `${arrow.name} needs exactly one kind class (${KINDS.join(", ")})`);
        continue;
      }
      const kind = arrow.kinds[0];
      if (!arrow.stroke) {
        say("colour", `${arrow.name} has no stroke colour`);
        continue;
      }
      (strokesByKind[kind] = strokesByKind[kind] || new Set()).add(arrow.stroke.rgb.join(","));
      if (!KIND_HUE[kind](hsl(arrow.stroke.rgb))) {
        say("colour", `${arrow.name} is a ${kind} arrow but is not ${KIND_COLOUR_NAME[kind]} (rgb ${arrow.stroke.rgb.join(", ")})`);
      }
      if (kind === "loop" && !arrow.dashed) say("colour", `${arrow.name} is a loop arrow but is solid, not dashed`);
      if (kind !== "loop" && arrow.dashed) say("colour", `${arrow.name} is dashed but only loop arrows are dashed`);
    }
    for (const [kind, strokes] of Object.entries(strokesByKind)) {
      if (strokes.size > 1) say("colour", `${kind} arrows use ${strokes.size} different colours`);
    }
    const used = KINDS.filter((k) => arrows.some((a) => a.kinds.length === 1 && a.kinds[0] === k));
    if (used.length > 1 && !legend) {
      say("colour", `the diagram uses ${used.join(", ")} arrows and has no legend`);
    }
    if (legend) {
      const samples = KINDS.filter((k) => legend.querySelector(`.arrow.${k}`));
      for (const k of used.filter((x) => !samples.includes(x))) {
        say("colour", `the legend has no ${k} sample`);
      }
      for (const k of samples.filter((x) => !used.includes(x))) {
        say("colour", `the legend shows a ${k} arrow the diagram does not use`);
      }
      const legendTexts = textInfo.filter((t) => t.owner === legend);
      if (legendTexts.length > samples.length + 1) {
        say("float", `the legend holds ${legendTexts.length} texts for ${samples.length} arrow kinds; anything but arrow labels belongs in the flow`);
      }
      for (const t of legendTexts.filter((x) => x.content.split(" ").length > 4)) {
        say("float", `legend text ${quote(t.content)} is longer than an arrow label`);
      }
    }

    // Contrast in this colour scheme.
    for (const t of textInfo) {
      const ownerShape = [...boxes, ...groups].find((s) => s.g === t.owner);
      const behindGroup = ownerShape && ownerShape.group && ownerShape.group.shape
        ? shapeFill(ownerShape.group.shape, background) : background;
      const behind = ownerShape && ownerShape.shape
        ? shapeFill(ownerShape.shape, behindGroup) : background;
      const fill = parseColour(getComputedStyle(t.el).fill);
      if (!fill) continue;
      const colour = blend(fill.rgb, fill.alpha, behind);
      const ratio = contrast(colour, behind);
      if (ratio < MIN_CONTRAST) {
        say("contrast", `${quote(t.content)} has contrast ${ratio.toFixed(1)}:1`);
      }
      const filled = ownerShape && ownerShape.kind !== "group" && ownerShape.shape
        && parseColour(getComputedStyle(ownerShape.shape).fill);
      if (filled && luminance(colour) > luminance(behind)) {
        say("contrast", `${quote(t.content)} is light text on a darker fill; use dark text on a light fill`);
      }
    }

    // Captions.
    const figure = svg.closest("figure");
    if (figure) {
      if (figure.querySelector("figcaption")) say("caption", "the figure has a <figcaption>");
      let next = svg.nextElementSibling;
      while (next) {
        if (next.tagName !== "FIGCAPTION" && next.textContent.trim()) {
          say("caption", `text follows the drawing inside its figure: ${quote(next.textContent.trim().slice(0, 60))}`);
        }
        next = next.nextElementSibling;
      }
    }
  });

  return { diagrams: diagrams.length, findings, texts };
})()
