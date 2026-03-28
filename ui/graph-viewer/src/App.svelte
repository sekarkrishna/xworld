<script>
  import GraphTree from "./GraphTree.svelte";

  // Graph data is injected by Python as a JSON string replacing __GRAPH_DATA__
  let graphData = null;
  try {
    graphData = JSON.parse('__GRAPH_DATA__');
  } catch (e) {
    // Fallback: empty tree for dev mode
    graphData = {
      id: "demo",
      type: "question",
      title: "Demo Question",
      status: "pending",
      verdict: null,
      children: [],
    };
  }
</script>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0f172a;
  }
  .container {
    width: 100vw;
    height: 100vh;
  }
</style>

<div class="container">
  {#if graphData}
    <GraphTree data={graphData} />
  {:else}
    <p style="color: #9CA3AF; padding: 1rem;">No graph data available.</p>
  {/if}
</div>
