from libcst._nodes.module import Module
from libcst._nodes.statement import BaseStatement, BaseSuite, IndentedBlock, StrayIndentedBlock
from libcst.codemod._context import CodemodContext
from libcst.codemod._visitor import ContextAwareTransformer
from libcst.metadata import ParentNodeProvider, PositionProvider, ProviderT
from typing import Tuple


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
        index: int = -1
        for i, stmt in enumerate(original_node.body):
            if stmt is self.block:
                index = i
                break
        if index == -1:
            return updated_node

        new_body: list[BaseStatement] = list(updated_node.body[0:index])
        new_body.extend(self.block.body)
        new_body.extend(updated_node.body[index + 1:])
        return updated_node.with_changes(body=new_body)

    def leave_StrayIndentedBlock(
        self, original_node: StrayIndentedBlock, updated_node: StrayIndentedBlock
    ) -> BaseSuite:
        return updated_node

    def leave_Module(self, original_node: Module, updated_node: Module) -> Module:
        return updated_node
