from dataclasses import dataclass, field
from libcst._nodes.base import CSTNode
from libcst._nodes.statement import ExceptHandler, StrayIndentedBlock, Try
from libcst._nodes.module import Module
from libcst.codemod._context import CodemodContext
from libcst.codemod._visitor import ContextAwareVisitor
from libcst.metadata import CodePosition, CodeRange, ParentNodeProvider, PositionProvider, ProviderT
from typing import Generic, Optional, Tuple, TypeVar


GENERATED_NODE_CODE_RANGE = CodeRange(CodePosition(-1, -1), CodePosition(-1, -1))
NodeType = TypeVar("K", bound=CSTNode)


@dataclass(frozen=True)
class StrayNodeEntry(Generic[NodeType]):
    """
    Single entry with information about invalid nodes in a tree.
    """

    node: NodeType

    code_range: CodeRange

    def __lt__(self, other: "StrayNodeEntry[CSTNode]") -> bool:
        return self.__lt(self.code_range.start, other.code_range.start) or self.__lt(self.code_range.end, other.code_range.end)

    @staticmethod
    def __lt(lhs: CodePosition, rhs: CodePosition) -> bool:
        return lhs.line < rhs.line or lhs.column < rhs.column


@dataclass
class StrayNodesDictionary:
    """
    Data structure containing all invalid nodes in a tree.
    """

    blocks: list[StrayNodeEntry[StrayIndentedBlock]] = field(default_factory=list)

    all_trys: list[StrayNodeEntry[Try]] = field(default_factory=list)

    trys: list[StrayNodeEntry[Try]] = field(default_factory=list)

    excepts: list[StrayNodeEntry[ExceptHandler]] = field(default_factory=list)

    def __len__(self):
        return len(self.blocks) + len(self.trys) + len(self.excepts)


class FindAllStrayNodes(ContextAwareVisitor):
    """
    Helper to identify all invalid nodes which need to be mitigated.
    """

    METADATA_DEPENDENCIES: Tuple[ProviderT] = (ParentNodeProvider, PositionProvider,)

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.dictionary = StrayNodesDictionary()

    def leave_Module(self, original_node: Module) -> None:
        self.dictionary.all_trys.sort()

    def visit_ExceptHandler(self, node: ExceptHandler) -> Optional[bool]:
        parent: Optional[CSTNode] = self.get_metadata(ParentNodeProvider, node, None)
        if (parent is not None) and not isinstance(parent, Try):
            self.dictionary.excepts.append(self.__create_entry(node))
        return True

    def visit_StrayIndentedBlock(self, node: StrayIndentedBlock) -> Optional[bool]:
        self.dictionary.blocks.append(self.__create_entry(node))
        return True

    def visit_Try(self, node: Try) -> Optional[bool]:
        entry: StrayNodeEntry[Try] = self.__create_entry(node)
        self.dictionary.all_trys.append(entry)
        if not node.handlers and not node.finalbody:
            self.dictionary.trys.append(entry)
        return True

    def __create_entry(self, node: NodeType) -> NodeType:
        code_range: CodeRange = self.get_metadata(PositionProvider, node, GENERATED_NODE_CODE_RANGE)
        return StrayNodeEntry(node, code_range)
