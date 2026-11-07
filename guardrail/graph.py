from collections.abc import Callable
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .model import GuardrailModel, LayaGate
from .schema import Classification

MAX_PROMPT_LENGTH = 8_000


class GuardrailState(TypedDict, total=False):
    prompt: str
    classification: Classification


def normalize_input(state: GuardrailState) -> GuardrailState:
    prompt = state.get("prompt", "").strip()
    return {"prompt": prompt[:MAX_PROMPT_LENGTH]}


def build_guardrail_graph(
    classifier: Callable[[str], Classification] | None = None,
    laya_gate: LayaGate | None = None,
):
    if classifier is not None:
        classify = classifier
    else:
        fast_gate = laya_gate or LayaGate()
        fallback = GuardrailModel()

        def classify(prompt: str) -> Classification:
            fast_result = fast_gate.classify(prompt)
            if fast_result.status.value == "ok" and fast_result.category.value != "unknown":
                return fast_result
            return fallback.classify(prompt)

    def classify_input(state: GuardrailState) -> GuardrailState:
        return {"classification": classify(state["prompt"])}

    graph = StateGraph(GuardrailState)
    graph.add_node("normalize_input", normalize_input)
    graph.add_node("classify_input", classify_input)
    graph.add_edge(START, "normalize_input")
    graph.add_edge("normalize_input", "classify_input")
    graph.add_edge("classify_input", END)
    return graph.compile()
