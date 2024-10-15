from bisect import bisect_left
from libcst._nodes.base import CSTNode
from libcst._nodes.module import Module
from libcst._nodes.statement import BaseStatement, BaseSuite, ExceptHandler, IndentedBlock, StrayIndentedBlock, Try
from libcst.codemod._context import CodemodContext
from libcst.codemod._visitor import ContextAwareTransformer
from libcst.codemod.visitors._find_all_stray_nodes import StrayNodeEntry
from libcst.metadata import ParentNodeProvider, PositionProvider, ProviderT
from typing import Optional, Sequence, Tuple, TypeVar


NodeType = TypeVar("K", bound=CSTNode)


class InlineStrayIndentedBlock(ContextAwareTransformer):
    """
    Inlines a stray indented block into its parent.
    """

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
        """
        If self.block is contained in original_body, we remove it from
        updated_node.
        """
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


class AttachCatchToTry(ContextAwareTransformer):
    """
    Attaches stray except blocks to the closest preceding try.
    """

    def __init__(self, context: CodemodContext, all_trys: list[StrayNodeEntry[Try]], excepts: list[StrayNodeEntry[ExceptHandler]]) -> None:
        super().__init__(context)
        self.all_trys = all_trys
        self.excepts = excepts
        self.excepts_per_try: dict[int, list[ExceptHandler]] = {}
        self.except_ids_to_remove: set[int] = set()
        for stray_except in excepts:
            index: int = bisect_left(self.all_trys, stray_except)
            if index > 0:
                new_parent: Try = self.all_trys[index - 1].node
                excepts_for_parent: list[ExceptHandler] = self.excepts_per_try.setdefault(id(new_parent), [])
                excepts_for_parent.append(stray_except.node)
                self.except_ids_to_remove.add(id(stray_except.node))

    def leave_IndentedBlock(
        self, original_node: IndentedBlock, updated_node: IndentedBlock
    ) -> BaseSuite:
        return self.__remove(original_node, original_node.body, updated_node, updated_node.body)

    def leave_Module(self, original_node: Module, updated_node: Module) -> Module:
        return self.__remove(original_node, original_node.body, updated_node, updated_node.body)

    def leave_StrayIndentedBlock(
        self, original_node: StrayIndentedBlock, updated_node: StrayIndentedBlock
    ) -> BaseSuite:
        return self.__remove(original_node, original_node.body, updated_node, updated_node.body)

    def leave_Try(self, original_node: Try, updated_node: Try) -> Try:
        excepts_for_parent: Optional[list[ExceptHandler]] = self.excepts_per_try.get(id(original_node))
        if not excepts_for_parent:
            return updated_node

        new_handlers: list[ExceptHandler] = list(updated_node.handlers)
        for stray_except in excepts_for_parent:
            new_handlers.append(stray_except.deep_clone())
        return updated_node.with_changes(handlers=new_handlers)

    def __remove(
        self,
        original_node: NodeType,
        original_body: Sequence[BaseStatement],
        updated_node: NodeType,
        updated_body: Sequence[BaseStatement]) -> NodeType:
        """
        Removes all nodes from updated_node whose id is in
        self.except_ids_to_remove.
        """
        new_body: list[BaseStatement] = []
        for i, stmt in enumerate(original_body):
            if id(stmt) not in self.except_ids_to_remove:
                new_body.append(updated_body[i])
        if len(new_body) == len(updated_body):
            return updated_node

        return updated_node.with_changes(body=new_body)
