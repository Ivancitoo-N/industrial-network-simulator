/**
 * Industrial Network Visualizer — D3.js Logic
 */

const svg = d3.select("#canvas");
const width = window.innerWidth - 320;
const height = window.innerHeight - 180;

const simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id).distance(150))
    .force("charge", d3.forceManyBody().strength(-1000))
    .force("center", d3.forceCenter(width / 2, height / 2));

const container = svg.append("g");

// Persistent state for D3
let nodesData = [];
let linksData = [];

function updateTopology(topology) {
    const { nodes: newNodes, links: newLinks } = topology;

    // 1. Object Constancy: Merge new data into existing node objects to preserve x/y/vx/vy
    const nodeMap = new Map(nodesData.map(d => [d.id, d]));
    nodesData = newNodes.map(d => {
        const existing = nodeMap.get(d.id);
        return existing ? Object.assign(existing, d) : d;
    });

    // 2. Map links to the actual node objects (D3 requirement)
    const activeNodeMap = new Map(nodesData.map(d => [d.id, d]));
    const processedLinks = newLinks.map(l => ({
        ...l,
        source: activeNodeMap.get(l.source.id || l.source),
        target: activeNodeMap.get(l.target.id || l.target)
    })).filter(l => l.source && l.target);

    const topologyChanged = nodesData.length !== nodeMap.size || processedLinks.length !== linksData.length;
    linksData = processedLinks;

    // ── Links ──
    const link = container.selectAll(".link")
        .data(linksData, d => {
            const ids = [d.source.id || d.source, d.target.id || d.target];
            return ids.sort().join('_');
        });

    link.exit().remove();

    const linkEnter = link.enter().append("line")
        .attr("class", d => `link ${d.active ? '' : 'inactive'}`)
        .on("click", (event, d) => toggleLink(d));

    const linkUpdate = link.merge(linkEnter)
        .attr("class", d => `link ${d.active ? '' : 'inactive'}`);

    // ── Nodes ──
    const node = container.selectAll(".node")
        .data(nodesData, d => d.id);

    node.exit().remove();

    const nodeEnter = node.enter().append("g")
        .attr("class", "node")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    nodeEnter.append("circle")
        .attr("r", d => d.type === 'PLC' ? 20 : 14)
        .attr("fill", d => {
            if (d.status === 'Offline') return "#666"; // Induced failure/Fault
            if (d.type === 'PLC') return "#fff";
            if (d.type === 'Drive') return "#ff2222";
            if (d.type === 'IO-Link') return "#22ff44";
            return "#58a6ff";
        })
        .style("filter", "drop-shadow(0 0 8px rgba(255,255,255,0.2))");

    nodeEnter.append("text")
        .attr("dy", 35)
        .attr("text-anchor", "middle")
        .attr("class", "node-label")
        .text(d => d.display_name || d.id);

    nodeEnter.append("text")
        .attr("dy", 48)
        .attr("text-anchor", "middle")
        .attr("class", "node-status")
        .style("font-size", "8px")
        .style("font-weight", "bold");

    const nodeUpdate = node.merge(nodeEnter);

    // Update colors and labels if status/name changed
    nodeUpdate.select("circle")
        .attr("fill", d => {
            if (d.status === 'Offline') return "#666";
            if (d.type === 'PLC') return "#fff";
            if (d.type === 'Drive') return "#ff2222";
            if (d.type === 'IO-Link') return "#22ff44";
            return "#58a6ff";
        });

    nodeUpdate.select(".node-label")
        .text(d => d.display_name || d.id);

    nodeUpdate.select(".node-status")
        .text(d => d.status === 'Online' ? '' : d.status.toUpperCase())
        .attr("fill", d => d.status === 'Offline' ? '#ff2222' : '#ffaa00');

    nodeEnter.on("dblclick", (event, d) => {
        event.stopPropagation();
        const newName = prompt(`Renombrar dispositivo ${d.id}:`, d.display_name || d.id);
        if (newName) {
            fetch(`/api/devices/${d.id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ display_name: newName })
            });
        }
    });

    nodeEnter.on("click", (event, d) => {
        // Toggle fault if it's already offline (Repair) or just confirm
        const action = d.status === 'Offline' ? 'Restaurar' : 'Inducir fallo en';
        if (confirm(`¿${action} ${d.display_name || d.id}?`)) {
            socket.emit('trigger_fault', { device_id: d.id });
        }
    });

    nodeEnter.on("contextmenu", (event, d) => {
        event.preventDefault();
        if (confirm(`¿Inducir/Restaurar fallo en ${d.display_name || d.id}?`)) {
            socket.emit('trigger_fault', { device_id: d.id });
        }
    });

    // ── Simulation Update ──
    simulation.nodes(nodesData);
    simulation.force("link").links(linksData);

    // Only "shake" the graph if something new was added
    if (topologyChanged) {
        simulation.alpha(0.3).restart();
    }

    simulation.on("tick", () => {
        linkUpdate
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        nodeUpdate
            .attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // ── Traffic Simulation ──
    startTrafficParticles();
}

function startTrafficParticles() {
    // Periodically spawn particles
    if (!window.trafficTimer) {
        window.trafficTimer = setInterval(() => {
            spawnParticles(linksData.filter(l => l.active));
        }, 800);
    }
}

function spawnParticles(activeLinks) {
    activeLinks.forEach(link => {
        const particle = container.append("circle")
            .attr("class", "traffic-particle")
            .attr("r", 4);

        const start = link.source;
        const end = link.target;

        particle.attr("cx", start.x).attr("cy", start.y)
            .transition()
            .duration(1000)
            .ease(d3.easeLinear)
            .attr("cx", end.x).attr("cy", end.y)
            .remove();
    });
}

function toggleLink(link) {
    const sourceId = link.source.id || link.source;
    const targetId = link.target.id || link.target;

    fetch('/api/link', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            u: sourceId,
            v: targetId,
            active: !link.active
        })
    });
}

// ── Drag Helpers ──
function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}
function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}
function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

window.addEventListener('resize', () => {
    // Basic resize handling
});
