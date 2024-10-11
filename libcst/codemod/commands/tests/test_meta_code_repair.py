# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
# pyre-strict

from libcst.codemod import CodemodTest
from libcst.codemod.commands.meta_code_repair import MetaCodeRepairCommand


class TestRenameCommand(CodemodTest):
    TRANSFORM = MetaCodeRepairCommand

    def test_stray_return(self) -> None:
        before = """
            def invalid() -> int:
                value: int = 10
                 return value
        """
        after = """
            def invalid() -> int:
                value: int = 10
                return value
        """

        self.assertCodemod(before, after)
