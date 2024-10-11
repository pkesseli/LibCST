from libcst import Module
from libcst.codemod import Codemod, CodemodContext
from libcst.codemod.visitors._meta_code_repair_transformer import InlineStrayIndentedBlock
from libcst.codemod.visitors._find_all_stray_nodes import FindAllStrayNodes
from libcst.metadata import ParentNodeProvider, PositionProvider, ProviderT
from typing import Tuple


class MetaCodeRepairCommand(Codemod):
    """
    Basic Codemod implementation to repair trees with invalid nodes.
    """

    METADATA_DEPENDENCIES: Tuple[ProviderT] = (ParentNodeProvider, PositionProvider,)

    def transform_module_impl(self, tree: Module) -> Module:
        # TODO: Convert to backtracking fixed point loop
        for _ in range(2):
            findStrayNodes = FindAllStrayNodes(self.context)
            tree.visit(findStrayNodes)
            if findStrayNodes.dictionary.blocks:
                inlineStrayIndentedBlock = InlineStrayIndentedBlock(
                    self.context,
                    findStrayNodes.dictionary.blocks[0].node,
                )
            tree = tree.visit(inlineStrayIndentedBlock)
        return tree
