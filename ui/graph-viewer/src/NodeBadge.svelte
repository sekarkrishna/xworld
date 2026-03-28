<script>
  export let nodeType = "question";
  export let verdict = null;
  export let title = "";
  export let radius = 28;

  const VERDICT_COLOURS = {
    open: "#9CA3AF",
    supported: "#22C55E",
    refuted: "#EF4444",
    inconclusive: "#EAB308",
    deferred: "#3B82F6",
  };

  const TYPE_ICONS = {
    question: "?",
    hypothesis: "H",
    experiment: "⚗",
    result: "📊",
    insight: "✨",
  };

  const TYPE_SHAPES = {
    question: "circle",
    hypothesis: "diamond",
    experiment: "circle",
    result: "circle",
    insight: "circle",
  };

  $: fillColour = verdict ? VERDICT_COLOURS[verdict] || "#9CA3AF" : "#334155";
  $: strokeColour = verdict ? VERDICT_COLOURS[verdict] || "#9CA3AF" : "#64748b";
  $: icon = TYPE_ICONS[nodeType] || "?";
  $: shape = TYPE_SHAPES[nodeType] || "circle";
  $: truncTitle = title.length > 20 ? title.slice(0, 18) + "…" : title;
</script>

<style>
  .node-label {
    fill: #e2e8f0;
    font-size: 11px;
    text-anchor: middle;
    pointer-events: none;
    user-select: none;
  }
  .node-icon {
    fill: #ffffff;
    font-size: 16px;
    text-anchor: middle;
    dominant-baseline: central;
    pointer-events: none;
    user-select: none;
  }
  .node-shape {
    stroke-width: 2.5;
    transition: filter 0.15s;
  }
  .node-shape:hover {
    filter: brightness(1.3);
  }
</style>

{#if shape === "diamond"}
  <!-- Diamond shape for hypotheses -->
  <polygon
    class="node-shape"
    points="{0},{-radius} {radius},{0} {0},{radius} {-radius},{0}"
    fill={fillColour}
    stroke={strokeColour}
    fill-opacity="0.85"
  />
{:else}
  <!-- Circle shape for all other types -->
  <circle
    class="node-shape"
    cx="0"
    cy="0"
    r={radius}
    fill={fillColour}
    stroke={strokeColour}
    fill-opacity="0.85"
  />
{/if}

<!-- Type icon -->
<text class="node-icon" x="0" y="0">{icon}</text>

<!-- Title label below node -->
<text class="node-label" x="0" y={radius + 16}>{truncTitle}</text>
