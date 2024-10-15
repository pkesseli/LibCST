from collections import defaultdict, OrderedDict
from libcst import Module
from libcst.codemod import Codemod, CodemodContext
from libcst.codemod.visitors._meta_code_repair_transformer import AttachCatchToTry, InlineStrayIndentedBlock
from libcst.codemod.visitors._find_all_stray_nodes import FindAllStrayNodes, StrayNodesDictionary
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
        dictionary: StrayNodesDictionary = findStrayNodes.dictionary
        if len(dictionary) == 0:
            self.solutions[num_steps].append(tree)
            return

        num_steps = num_steps + 1
        if dictionary.excepts:
            self.__build_solutions(
                tree.visit(AttachCatchToTry(
                    self.context,
                    dictionary.all_trys,
                    dictionary.excepts,
                )),
                num_steps,
            )
        elif dictionary.blocks:
            self.__build_solutions(
                tree.visit(InlineStrayIndentedBlock(
                    self.context,
                    dictionary.blocks[0].node,
                )),
                num_steps,
            )
