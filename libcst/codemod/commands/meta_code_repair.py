from collections import defaultdict, OrderedDict
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

    def __init__(self, context: CodemodContext) -> None:
        super().__init__(context)
        self.solutions: dict[int, list[tree]] = defaultdict(list)

    def transform_module_impl(self, tree: Module) -> Module:
        self.__build_solutions(tree, 0)
        self.solutions = dict(sorted(self.solutions.items()))
        return next(iter(self.solutions.values()))[0] if self.solutions else tree

    def __build_solutions(self, tree: Module, num_steps: int) -> None:
        findStrayNodes = FindAllStrayNodes(self.context)
        tree.visit(findStrayNodes)
        if len(findStrayNodes.dictionary) == 0:
            self.solutions[num_steps].append(tree)
            return

        num_steps = num_steps + 1
        if findStrayNodes.dictionary.blocks:
            inlineStrayIndentedBlock = InlineStrayIndentedBlock(
                self.context,
                findStrayNodes.dictionary.blocks[0].node,
            )
            self.__build_solutions(
                tree.visit(inlineStrayIndentedBlock),
                num_steps,
            )
