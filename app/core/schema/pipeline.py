"""
Pipeline Schema Module

This module defines the Pydantic schema classes used to configure pipeline structures.
It provides a type-safe way to represent node connections, execution order, and overall
pipeline configuration.
"""

from pydantic import BaseModel, Field

from app.core.node import Node


class NodeConfig(BaseModel):
    """Configuration model for pipeline nodes.

    NodeConfig defines the structure and behavior of a single node within
    a pipeline, including its connections to other nodes and routing properties.

    Attributes:
        node: The Node class to be instantiated
        connections: List of Node classes this node can connect to
        is_router: Flag indicating if this node performs routing logic
        description: Optional description of the node's purpose

    Example:
        config = NodeConfig(
            node=AnalyzeNode,
            connections=[RouterNode],
            is_router=False,
            description="Analyzes incoming requests"
        )
    """

    node: type[Node]
    connections: list[type[Node]] = Field(default_factory=list)
    is_router: bool = False
    description: str | None = None


class PipelineSchema(BaseModel):
    """Schema definition for a complete pipeline.

    PipelineSchema defines the overall structure of a processing pipeline,
    including its entry point and all constituent nodes.

    Attributes:
        description: Optional description of the pipeline's purpose
        start: The entry point Node class for the pipeline
        nodes: List of NodeConfig objects defining the pipeline structure

    Example:
        schema = PipelineSchema(
            description="Support ticket processing pipeline",
            start=AnalyzeNode,
            nodes=[
                NodeConfig(node=AnalyzeNode, connections=[RouterNode]),
                NodeConfig(node=RouterNode, connections=[ResponseNode, EscalateNode]),
            ]
        )
    """

    description: str | None = None
    start: type[Node]
    nodes: list[NodeConfig]
