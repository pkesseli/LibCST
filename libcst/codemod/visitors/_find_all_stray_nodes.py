from dataclasses import dataclass, field
from libcst._nodes.base import CSTNode
from libcst._nodes.statement import StrayIndentedBlock
from libcst.codemod._context import CodemodContext
from libcst.codemod._visitor import ContextAwareVisitor
from libcst.metadata import CodeRange, ParentNodeProvider, PositionProvider, ProviderT
from typing import Generic, Optional, Tuple, TypeVar


NodeType = TypeVar("K", bound=CSTNode)


@dataclass(frozen=True)
class StrayNodeEntry(Generic[NodeType]):
    """
    Single entry with information about invalid nodes in a tree.
    """

    node: NodeType

    parent: CSTNode

    code_range: CodeRange


@dataclass(frozen=True)
class StrayNodesDictionary:
    """
    Data structure containing all invalid nodes in a tree.
    """

    blocks: list[StrayNodeEntry[StrayIndentedBlock]] = field(default_factory=list)

    def __len__(self):
        return len(self.blocks)



class FindAllStrayNodes(ContextAwareVisitor):
    """
    Helper to identify all invalid nodes which need to be mitigated.
    """

    METADATA_DEPENDENCIES: Tuple[ProviderT] = (ParentNodeProvider, PositionProvider,)

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.dictionary = StrayNodesDictionary()

    def visit_StrayIndentedBlock(self, node: StrayIndentedBlock) -> Optional[bool]:
        code_range: CodeRange = self.get_metadata(PositionProvider, node)
        parent: CSTNode = self.get_metadata(ParentNodeProvider, node)
        entry = StrayNodeEntry(node, parent, code_range)
        self.dictionary.blocks.append(entry)
        return True
