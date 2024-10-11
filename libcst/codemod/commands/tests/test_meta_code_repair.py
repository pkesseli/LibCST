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

    def test_stray_script(self) -> None:
        before = """
                value: int = 10
                 print(value)
        """
        after = """
                value: int = 10
                print(value)
        """

        self.assertCodemod(before, after)

    def test_nested_stray(self) -> None:
        before = """
                value: int = 10
                 print(value)
                  print(value)
        """
        after = """
                value: int = 10
                print(value)
                print(value)
        """

        self.assertCodemod(before, after)
