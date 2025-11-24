"""
Property-Based Tests: Complex Circular Dependency Detection

Generated from Requirement 3: Complex Circular Dependency Detection
Tests cycles of any length (3+ tasks).
"""
import pytest
from hypothesis import given, assume
from hypothesis import strategies as st
from services.task_service.domain.business_rules import has_circular_dependency


# Strategy for generating valid task IDs (matching production: str(uuid.uuid4()))
task_ids = st.uuids().map(str)


class TestComplexCircularDependencyProperties:
    """Property-based tests for complex circular dependencies (Requirement 3)."""
    
    @given(task_a=task_ids, task_b=task_ids, task_c=task_ids)
    def test_three_task_cycle(self, task_a, task_b, task_c):
        """
        Property: Three-task cycles are detected (A→B→C→A).
        
        Requirement 3.1: WHEN a dependency chain exists from Task A through
        multiple tasks back to Task A, THE System SHALL identify this as
        a circular dependency.
        """
        assume(len({task_a, task_b, task_c}) == 3)  # All different
        
        # Create cycle: task_a→task_b→task_c
        graph = {
            task_a: [task_b],
            task_b: [task_c]
        }
        
        # Check if task_c→task_a would complete the cycle
        result = has_circular_dependency(task_c, task_a, graph)
        
        assert result is True, f"Three-task cycle {task_a}→{task_b}→{task_c}→{task_a} should be detected"
    
    @given(tasks=st.lists(task_ids, min_size=4, max_size=10, unique=True))
    def test_long_chain_cycle(self, tasks):
        """
        Property: Cycles of any length are detected.
        
        Requirement 3.2: THE System SHALL traverse the entire dependency graph
        to detect cycles of any length.
        """
        assume(len(tasks) >= 4)
        
        # Create chain: tasks[0]→tasks[1]→tasks[2]→...→tasks[n-1]
        graph = {}
        for i in range(len(tasks) - 1):
            graph[tasks[i]] = [tasks[i + 1]]
        
        # Check if tasks[n-1]→tasks[0] would complete the cycle
        result = has_circular_dependency(tasks[-1], tasks[0], graph)
        
        assert result is True, f"Cycle of length {len(tasks)} should be detected"
    
    @given(task_a=task_ids, task_b=task_ids, task_c=task_ids, task_d=task_ids)
    def test_four_task_cycle(self, task_a, task_b, task_c, task_d):
        """
        Property: Four-task cycles are detected (A→B→C→D→A).
        
        Requirement 3.4: THE System SHALL handle dependency chains of three
        or more tasks.
        """
        assume(len({task_a, task_b, task_c, task_d}) == 4)  # All different
        
        # Create cycle: task_a→task_b→task_c→task_d
        graph = {
            task_a: [task_b],
            task_b: [task_c],
            task_c: [task_d]
        }
        
        # Check if task_d→task_a would complete the cycle
        result = has_circular_dependency(task_d, task_a, graph)
        
        assert result is True, f"Four-task cycle should be detected"
    
    @given(tasks=st.lists(task_ids, min_size=3, max_size=8, unique=True))
    def test_cycle_detection_uses_dfs(self, tasks):
        """
        Property: Cycle detection traverses the graph (DFS behavior).
        
        Requirement 3.3: THE System SHALL use depth-first search to efficiently
        detect cycles in the dependency graph.
        """
        assume(len(tasks) >= 3)
        
        # Create a chain
        graph = {}
        for i in range(len(tasks) - 1):
            graph[tasks[i]] = [tasks[i + 1]]
        
        # Adding back-edge creates cycle
        result_with_cycle = has_circular_dependency(tasks[-1], tasks[0], graph)
        
        # Not adding back-edge means no cycle
        result_without_cycle = has_circular_dependency(tasks[-1], tasks[-1] + "_new", graph)
        
        assert result_with_cycle is True, "Should detect cycle when back-edge exists"
        assert result_without_cycle is False, "Should not detect cycle without back-edge"
    
    @given(
        main_chain=st.lists(task_ids, min_size=3, max_size=5, unique=True),
        branch_chain=st.lists(task_ids, min_size=2, max_size=4, unique=True),
        branch_point=st.integers(min_value=0, max_value=10)
    )
    def test_cycle_in_graph_with_branches(self, main_chain, branch_chain, branch_point):
        """
        Property: Cycles are detected when nodes have multiple dependencies (branches).
        
        Requirement 3.2: THE System SHALL traverse the entire dependency graph.
        
        Tests a graph where a node has multiple dependencies, requiring DFS to
        explore multiple paths to find the cycle.
        
        Example structure:
        main_chain[0] → [main_chain[1], branch_chain[0]]  (branches to two paths)
        main_chain[1] → main_chain[2]
        branch_chain[0] → branch_chain[1]
        main_chain[2] → main_chain[0]  (creates cycle back to start)
        
        Visual:
        ┌─────────────┐
        ↓             │
      main[0]         |
       / \\           |
      /   \\          |
   main[1] branch[0]  |
      |       |       |
   main[2] branch[1]  |
      └───────────────┘
        """
        assume(len(main_chain) >= 3)
        assume(len(branch_chain) >= 2)
        assume(not set(main_chain).intersection(set(branch_chain)))
        
        graph = {}

        # Create main chain
        for i in range(len(main_chain) - 1):
            graph[main_chain[i]] = [main_chain[i + 1]]
        
        # Create branch chain
        for i in range(len(branch_chain) - 1):
            graph[branch_chain[i]] = [branch_chain[i + 1]]
        
        # Pick random point in main chain to add the branch
        branch_idx = branch_point % len(main_chain)
        existing_deps = graph.get(main_chain[branch_idx], [])
        graph[main_chain[branch_idx]] = existing_deps + [branch_chain[0]]
        
        # Target end of main chain to beginning so we are forced to traverse branch
        target = main_chain[0]
        
        # Check if completing cycle on main chain returns True
        result = has_circular_dependency(main_chain[-1], target, graph)

        assert result is True, "Cycle should be detected in graph with branches"
    
    @given(tasks=st.lists(task_ids, min_size=5, max_size=10, unique=True))
    def test_partial_cycle_not_detected(self, tasks):
        """
        Property: Partial chains that don't loop back are not cycles.
        
        Requirement 3.1: Only when chain loops back to starting task.
        """
        assume(len(tasks) >= 5)
        
        # Create chain: tasks[0]→tasks[1]→tasks[2]→tasks[3]
        graph = {}
        for i in range(3):
            graph[tasks[i]] = [tasks[i + 1]]
        
        # Check if tasks[3]→tasks[4] creates cycle (it shouldn't - doesn't loop back)
        result = has_circular_dependency(tasks[3], tasks[4], graph)
        
        assert result is False, "Partial chain without loop back should not be circular"
