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

    def test_stray_except(self) -> None:
        before = """
                try:
                    value: int = 10
                    except:
                        pass
        """
        after = """
                try:
                    value: int = 10
                except:
                    pass
        """

        self.assertCodemod(before, after)

    def test_stray_try(self) -> None:
        before = """
                    try:
                    value: int = 10
                except:
                        pass
        """
        # TODO: Move statements between try and except to try/except body.
        after = """
                try:pass
                except:
                        pass
                value: int = 10
        """

        self.assertCodemod(before, after)
