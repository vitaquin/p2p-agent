#!/usr/bin/env python3
"""
Eigenvector Centrality Calculator
==================================
PROTOCOL LAW - IMMUTABLE

This implementation follows the exact specification:
- Directed eigenvector centrality
- Computed on adjacency matrix including multiplicity
- Power iteration method
- Convergence tolerance: 1e-6
- Maximum iterations: 1000
- Scores normalized so that max(I_a) = 1

ANY CHANGE REQUIRES A PROTOCOL FORK.
"""

import math


# ============================================================
# IMMUTABLE PARAMETERS (Protocol Law)
# ============================================================
TOLERANCE = 1e-6
MAX_ITERATIONS = 1000
# ============================================================


def eigenvector_centrality(matrix, tolerance=TOLERANCE, max_iter=MAX_ITERATIONS):
    """
    Compute directed eigenvector centrality using power iteration.
    
    Parameters:
    -----------
    matrix : list[list[float]]
        Adjacency matrix where matrix[i][j] = weight of edge i -> j
    tolerance : float
        Convergence tolerance (IMMUTABLE: 1e-6)
    max_iter : int
        Maximum iterations (IMMUTABLE: 1000)
    
    Returns:
    --------
    list[float]
        Centrality scores, normalized so max = 1
    
    Protocol Law:
    -------------
    This algorithm is IMMUTABLE.
    Any modification requires a complete protocol fork.
    """
    n = len(matrix)
    
    if n == 0:
        return []
    
    # Transpose matrix for incoming edges (who points to me)
    # For directed graphs, eigenvector centrality typically uses
    # the transpose to measure "importance based on who links to you"
    transposed = [[matrix[j][i] for j in range(n)] for i in range(n)]
    
    # Initialize scores uniformly
    scores = [1.0 / n] * n
    
    for iteration in range(max_iter):
        # Power iteration step
        new_scores = [0.0] * n
        
        for i in range(n):
            for j in range(n):
                new_scores[i] += transposed[i][j] * scores[j]
        
        # Normalize
        norm = math.sqrt(sum(s * s for s in new_scores))
        if norm > 0:
            new_scores = [s / norm for s in new_scores]
        else:
            # No edges, return uniform
            return [1.0 / n] * n
        
        # Check convergence
        diff = sum(abs(new_scores[i] - scores[i]) for i in range(n))
        
        if diff < tolerance:
            break
        
        scores = new_scores
    
    # Normalize so max = 1 (Protocol Law)
    max_score = max(scores) if scores else 1.0
    if max_score > 0:
        scores = [s / max_score for s in scores]
    
    return scores


def compute_scores(adjacency, agents):
    """
    Compute centrality scores for all agents.
    
    Parameters:
    -----------
    adjacency : dict
        Adjacency list from graph.build_graph()
    agents : list
        List of agent IDs
    
    Returns:
    --------
    dict
        Mapping of agent_id -> score (0.0 to 1.0)
    """
    from graph import to_adjacency_matrix
    
    matrix, agent_index = to_adjacency_matrix(adjacency, agents)
    scores = eigenvector_centrality(matrix)
    
    # Map back to agent IDs
    result = {}
    for agent, idx in agent_index.items():
        result[agent] = round(scores[idx], 6)
    
    return result


def print_scores(scores):
    """Print scores in ranked order."""
    print("Intelligence Scores (I_a)")
    print("=========================")
    print("I_a = EigenvectorCentrality(G)")
    print()
    
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    for rank, (agent, score) in enumerate(ranked, 1):
        bar = "#" * int(score * 20)
        print(f"  {rank}. {agent}: {score:.4f} {bar}")


if __name__ == "__main__":
    # Test with sample data
    from graph import build_graph
    
    sample_messages = [
        {"from": "Alice", "content": "Hello @Bob, let's work together"},
        {"from": "Bob", "content": "@Alice sounds good! @Carol can you help?"},
        {"from": "Carol", "content": "@Alice @Bob I'm ready"},
        {"from": "Alice", "content": "@Carol great! @Bob let's start"},
        {"from": "Dave", "content": "@Alice I want to join"},
        {"from": "Alice", "content": "@Dave welcome!"},
    ]
    
    adjacency, agents = build_graph(sample_messages)
    scores = compute_scores(adjacency, agents)
    
    print()
    print_scores(scores)
    print()
    print("Protocol: IMMUTABLE")
    print(f"Tolerance: {TOLERANCE}")
    print(f"Max iterations: {MAX_ITERATIONS}")
