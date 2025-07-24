"""
This code is based on content found in the LangGraph documentation: https://python.langchain.com/docs/tutorials/graph/#advanced-implementation-with-langgraph
"""

from typing import Any, Callable, Coroutine, Dict, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables.base import Runnable
from langchain_neo4j import Neo4jGraph


from app.lg_agent.kg_sub_graph.agentic_rag_agents.components.guardrails.models import GuardrailsOutput
from app.lg_agent.kg_sub_graph.agentic_rag_agents.components.guardrails.prompts import create_guardrails_prompt_template
from app.lg_agent.kg_sub_graph.agentic_rag_agents.components.state import InputState
from app.core.logger import get_logger

# 获取日志记录器
logger = get_logger(service="guardrails_node")


def create_guardrails_node(
    llm: BaseChatModel,
    graph: Optional[Neo4jGraph] = None,
    scope_description: Optional[str] = None,
) -> Callable[[InputState], Coroutine[Any, Any, dict[str, Any]]]:
    """
    Create a guardrails node to be used in a LangGraph workflow.

    Parameters
    ----------
    llm : BaseChatModel
        The LLM used to process data.
    graph: Optional[Neo4jGraph], optional
        The `Neo4jGraph` object used to generated a schema definition, by default None
    scope_description : Optional[str], optional
        A description of the application scope, by default None

    Returns
    -------
    Callable[[InputState], OverallState]
        The LangGraph node.
    """

    # 获取包含了图表结构和范围描述的guardrails完整提示词
    guardrails_prompt = create_guardrails_prompt_template(
        graph=graph, scope_description=scope_description
    )

    # 使用LLM进行结构化输出
    guardrails_chain: Runnable[Dict[str, Any], Any] = (
        guardrails_prompt | llm.with_structured_output(GuardrailsOutput)
    )

    async def guardrails(state: InputState) -> Dict[str, Any]:
        """
        Decides if the question is in scope.
        """

        # 提取到输入的问题
        question = state.get("question", "")

        # 使用LLM进行结构化输出
        guardrails_output: GuardrailsOutput = await guardrails_chain.ainvoke(
            {"question": question}
        )
        
        summary = None

        if guardrails_output.decision == "end":
            summary = "抱歉，我家暂时没有这方面的商品，可以在别家看看哦~"

        decision_info = {
            "next_action": guardrails_output.decision,
            "summary": summary,
            "steps": ["guardrails"],
        }
        
        logger.info(f"Guardrails Decision Info: {decision_info}")

        return decision_info


    return guardrails
