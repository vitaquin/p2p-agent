#!/usr/bin/env python3
"""
Graph Builder
=============
Builds a directed collaboration graph from message logs.
Detects @mentions and creates edges.

Includes:
- Integration section analysis
- Mutual reference detection (observation only)
- Connected component analysis
"""

import re
from collections import defaultdict


def extract_mentions(content):
    """
    Extract @mentions from message content.
    Returns list of mentioned agent IDs.
    """
    pattern = r"@(\w+)"
    return re.findall(pattern, content)


def extract_integration_section(content):
    """
    Extract mentions from Integration section specifically.
    Integration sections indicate structural dependency.
    """
    # Look for Integration section
    patterns = [
        r"Integration[:\s]*\n(.*?)(?=\n#|\n\n\n|\Z)",
        r"Builds upon[:\s]*(.*?)(?=\n|\Z)",
        r"References[:\s]*(.*?)(?=\n|\Z)",
    ]
    
    integration_content = ""
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            integration_content += match.group(1) + " "
    
    return extract_mentions(integration_content)


def detect_mutual_references(adjacency):
    """
    Detect mutual references (a -> b AND b -> a).
    For observation only - does not affect scores.
    
    Returns list of (agent_a, agent_b) pairs.
    """
    mutual = []
    checked = set()
    
    for a, targets in adjacency.items():
        for b in targets:
            if (b, a) not in checked:
                if b in adjacency and a in adjacency[b]:
                    mutual.append((a, b))
                checked.add((a, b))
    
    return mutual


def compute_connected_components(adjacency, agents):
    """
    Compute connected components (treating graph as undirected).
    Returns list of components, each component is a set of agents.
    """
    # Build undirected adjacency
    undirected = defaultdict(set)
    for a, targets in adjacency.items():
        for b in targets:
            undirected[a].add(b)
            undirected[b].add(a)
    
    visited = set()
    components = []
    
    def dfs(node, component):
        visited.add(node)
        component.add(node)
        for neighbor in undirected.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, component)
    
    for agent in agents:
        if agent not in visited:
            component = set()
            dfs(agent, component)
            components.append(component)
    
    return components


def largest_component_ratio(adjacency, agents):
    """
    Compute ratio of largest component to total nodes.
    Used to measure collaboration emergence.
    
    Returns float between 0 and 1.
    1.0 = all agents connected (full collaboration)
    1/n = all agents isolated (no collaboration)
    """
    if not agents:
        return 0.0
    
    components = compute_connected_components(adjacency, agents)
    if not components:
        return 0.0
    
    largest = max(len(c) for c in components)
    return largest / len(agents)


def build_graph(messages):
    """
    Build adjacency list from message log.
    
    Input: List of messages with 'from', 'to', 'content'
    Output: Dict mapping agent -> list of (mentioned_agent, count)
    
    Edge Rule:
    - A directed edge (a -> b) exists if agent a mentions @b
    - Multiple mentions in same message = 1 edge
    - Multiple messages = multiple edges (frequency)
    - Integration section mentions are weighted equally
    """
    # adjacency[from_agent][to_agent] = count
    adjacency = defaultdict(lambda: defaultdict(int))
    
    # Track all agents
    all_agents = set()
    
    # Track integration references separately (for observation)
    integration_refs = []
    
    for msg in messages:
        from_agent = msg.get("from")
        content = msg.get("content", "")
        
        all_agents.add(from_agent)
        
        # Extract all mentions
        mentions = extract_mentions(content)
        
        # Extract integration section mentions (for observation)
        integration_mentions = extract_integration_section(content)
        if integration_mentions:
            integration_refs.append({
                "from": from_agent,
                "references": integration_mentions
            })
        
        # Remove duplicates within same message
        unique_mentions = set(mentions)
        
        # Remove self-mentions
        unique_mentions.discard(from_agent)
        
        # Add edges
        for mentioned in unique_mentions:
            all_agents.add(mentioned)
            adjacency[from_agent][mentioned] += 1
    
    return dict(adjacency), list(all_agents)


def to_adjacency_matrix(adjacency, agents):
    """
    Convert adjacency list to matrix.
    
    Returns:
    - matrix: 2D list (rows=from, cols=to)
    - agent_index: dict mapping agent_id to index
    """
    n = len(agents)
    agent_index = {agent: i for i, agent in enumerate(agents)}
    
    matrix = [[0] * n for _ in range(n)]
    
    for from_agent, targets in adjacency.items():
        i = agent_index.get(from_agent)
        if i is None:
            continue
        for to_agent, count in targets.items():
            j = agent_index.get(to_agent)
            if j is not None:
                matrix[i][j] = count
    
    return matrix, agent_index


def print_graph(adjacency, agents):
    """Print graph with collaboration metrics."""
    print("Collaboration Graph")
    print("===================")
    print(f"Nodes: {len(agents)}")
    print(f"Agents: {agents}")
    print()
    
    # Edges
    edge_count = sum(len(targets) for targets in adjacency.values())
    print(f"Edges: {edge_count}")
    for from_agent, targets in adjacency.items():
        for to_agent, count in targets.items():
            print(f"  {from_agent} -> {to_agent} (x{count})")
    
    print()
    
    # Mutual references (observation)
    mutual = detect_mutual_references(adjacency)
    print(f"Mutual References: {len(mutual)}")
    for a, b in mutual:
        print(f"  {a} <-> {b}")
    
    print()
    
    # Connected components
    components = compute_connected_components(adjacency, agents)
    print(f"Connected Components: {len(components)}")
    for i, comp in enumerate(components, 1):
        print(f"  Component {i}: {comp}")
    
    # Collaboration ratio
    ratio = largest_component_ratio(adjacency, agents)
    print()
    print(f"Collaboration Ratio: {ratio:.2%}")
    if ratio == 1.0:
        print("  -> Full collaboration (all agents connected)")
    elif ratio > 0.5:
        print("  -> Emerging collaboration")
    else:
        print("  -> Fragmented (low collaboration)")


if __name__ == "__main__":
    # Test with sample data including Integration sections
    sample_messages = [
        {"from": "Alice", "content": "Hello @Bob, let's work together"},
        {"from": "Bob", "content": "@Alice sounds good! @Carol can you help?"},
        {"from": "Carol", "content": """
## My Contribution

Here is my design.

## Integration
This builds upon @Alice and @Bob's initial discussion.
"""},
        {"from": "Alice", "content": "@Carol great! @Bob let's start"},
    ]
    
    adjacency, agents = build_graph(sample_messages)
    print_graph(adjacency, agents)
    
    print()
    print("=" * 40)
    matrix, idx = to_adjacency_matrix(adjacency, agents)
    print("Adjacency Matrix:")
    print(f"Index: {idx}")
    for row in matrix:
        print(f"  {row}")
