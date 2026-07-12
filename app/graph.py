from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.nodes import (
    cover_letter_node,
    gap_analysis_node,
    parse_node,
    tailor_node,
    validate_node,
)
from app.state import PipelineState

PIPELINE_STAGES = [
    ("parse", parse_node),
    ("gap_analysis", gap_analysis_node),
    ("tailor", tailor_node),
    ("cover_letter", cover_letter_node),
    ("validate", validate_node),
]


def build_graph() -> CompiledStateGraph:
    graph = StateGraph(PipelineState)

    for name, node_fn in PIPELINE_STAGES:
        graph.add_node(name, node_fn)

    graph.add_edge(START, PIPELINE_STAGES[0][0])
    for (prev_name, _), (next_name, _) in zip(PIPELINE_STAGES, PIPELINE_STAGES[1:]):
        graph.add_edge(prev_name, next_name)
    graph.add_edge(PIPELINE_STAGES[-1][0], END)

    return graph.compile()
