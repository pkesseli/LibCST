from libcst._nodes.base import CSTNode
from libcst._nodes.module import Module
from libcst._nodes.statement import BaseStatement, BaseSuite, IndentedBlock, StrayIndentedBlock
from libcst.codemod._context import CodemodContext
from libcst.codemod._visitor import ContextAwareTransformer
from libcst.metadata import ParentNodeProvider, PositionProvider, ProviderT
from typing import Sequence, Tuple, TypeVar


NodeType = TypeVar("K", bound=CSTNode)


class InlineStrayIndentedBlock(ContextAwareTransformer):
    """
    Inlines a stray indented block into its parent. Currently only
    IndentedBlock parents are implemented.
    """

    METADATA_DEPENDENCIES: Tuple[ProviderT] = (ParentNodeProvider, PositionProvider,)

    def __init__(self, context: CodemodContext, strayIndentedBlock: StrayIndentedBlock) -> None:
        super().__init__(context)
        self.block = strayIndentedBlock

    def leave_IndentedBlock(
        self, original_node: IndentedBlock, updated_node: IndentedBlock
    ) -> BaseSuite:
        return self.__inline(original_node, original_node.body, updated_node, updated_node.body)

    def leave_StrayIndentedBlock(
        self, original_node: StrayIndentedBlock, updated_node: StrayIndentedBlock
    ) -> BaseSuite:
        return self.__inline(original_node, original_node.body, updated_node, updated_node.body)

    def leave_Module(self, original_node: Module, updated_node: Module) -> Module:
        return self.__inline(original_node, original_node.body, updated_node, updated_node.body)

    def __inline(self, original_node: NodeType, original_body: Sequence[BaseStatement], updated_node: NodeType, updated_body: Sequence[BaseStatement]) -> NodeType:
        index: int = -1
        for i, stmt in enumerate(original_body):
            if stmt is self.block:
                index = i
                break
        if index == -1:
            return updated_node

        new_body: list[BaseStatement] = list(updated_body[0:index])
        new_body.extend(self.block.body)
        new_body.extend(updated_body[index + 1:])
        return updated_node.with_changes(body=new_body)
