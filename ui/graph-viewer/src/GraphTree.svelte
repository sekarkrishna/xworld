<script>
  import { onMount } from "svelte";
  import * as d3 from "d3";
  import NodeBadge from "./NodeBadge.svelte";

  export let data;

  let svgEl;
  let gEl;
  let treeNodes = [];
  let treeLinks = [];
  let width = 800;
  let height = 600;

  const VERDICT_COLOURS = {
    open: "#9CA3AF",
    supported: "#22C55E",
    refuted: "#EF4444",
    inconclusive: "#EAB308",
    deferred: "#3B82F6",
  };

  const NODE_RADIUS = 28;
  const VERTICAL_SPACING = 120;
  const HORIZONTAL_SPACING = 180;

  function computeLayout(rootData) {
    const root = d3.hierarchy(rootData, (d) => d.children);
    const leafCount = root.leaves().length;
    const depth = root.height;

    const treeWidth = Math.max(HORIZONTAL_SPACING * leafCount, width);
    const treeHeight = Math.max(VERTICAL_SPACING * (depth + 1), height);

    const treeLayout = d3.tree().size([treeWidth, treeHeight - 80]);
    treeLayout(root);

    treeNodes = root.descendants();
    treeLinks = root.links();
  }

  function linkPath(d) {
    return d3.linkVertical()
      .x((d) => d.x)
      .y((d) => d.y)(d);
  }

  function handleNodeClick(nodeId) {
    window.parent.postMessage({ type: "node_click", nodeId }, "*");
  }

  onMount(() => {
    width = svgEl.clientWidth || 800;
    height = svgEl.clientHeight || 600;

    computeLayout(data);

    // Set up zoom
    const svg = d3.select(svgEl);
    const g = d3.select(gEl);

    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom);

    // Auto-fit: centre the tree
    if (treeNodes.length > 0) {
      const xs = treeNodes.map((n) => n.x);
      const ys = treeNodes.map((n) => n.y);
      const minX = Math.min(...xs) - 60;
      const maxX = Math.max(...xs) + 60;
      const minY = Math.min(...ys) - 60;
      const maxY = Math.max(...ys) + 60;
      const tw = maxX - minX;
      const th = maxY - minY;
      const scale = Math.min(width / tw, height / th, 1.2) * 0.85;
      const tx = width / 2 - ((minX + maxX) / 2) * scale;
      const ty = 40 - minY * scale;

      svg.call(
        zoom.transform,
        d3.zoomIdentity.translate(tx, ty).scale(scale)
      );
    }
  });
</script>

<style>
  svg {
    width: 100%;
    height: 100%;
    display: block;
  }
  .link {
    fill: none;
    stroke: #475569;
    stroke-width: 2;
    stroke-opacity: 0.6;
  }
  .edge-label {
    fill: #94a3b8;
    font-size: 10px;
    text-anchor: middle;
    pointer-events: none;
  }
</style>

<svg bind:this={svgEl}>
  <g bind:this={gEl}>
    <!-- Links -->
    {#each treeLinks as link}
      <path class="link" d={linkPath(link)} />
    {/each}

    <!-- Edge labels -->
    {#each treeLinks as link}
      {#if link.target.data.edge_type}
        <text
          class="edge-label"
          x={(link.source.x + link.target.x) / 2}
          y={(link.source.y + link.target.y) / 2 - 6}
        >
          {link.target.data.edge_type}
        </text>
      {/if}
    {/each}

    <!-- Nodes -->
    {#each treeNodes as node}
      <g
        transform="translate({node.x},{node.y})"
        on:click={() => handleNodeClick(node.data.id)}
        on:keydown={(e) => e.key === "Enter" && handleNodeClick(node.data.id)}
        role="button"
        tabindex="0"
        style="cursor: pointer;"
      >
        <NodeBadge
          nodeType={node.data.type}
          verdict={node.data.verdict}
          title={node.data.title}
          radius={NODE_RADIUS}
        />
      </g>
    {/each}
  </g>
</svg>
