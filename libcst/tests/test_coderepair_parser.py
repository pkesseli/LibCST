from libcst import Module, parse_module
from libcst._exceptions import ParserSyntaxError
from libcst.display import dump
from libcst.testing.utils import UnitTest


class TestCodeRepairParser(UnitTest):

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.maxDiff = None

    def test_stray_return(self) -> None:
        self.__test_parse(
            """
def invalid() -> int:
    value: int = 10
     return value
""",
            """Module(
  body=[
    FunctionDef(
      name=Name(
        value='invalid',
      ),
      params=Parameters(),
      body=IndentedBlock(
        body=[
          SimpleStatementLine(
            body=[
              AnnAssign(
                target=Name(
                  value='value',
                ),
                annotation=Annotation(
                  annotation=Name(
                    value='int',
                  ),
                ),
                value=Integer(
                  value='10',
                ),
              ),
            ],
          ),
          StrayIndentedBlock(
            body=[
              SimpleStatementLine(
                body=[
                  Return(
                    value=Name(
                      value='value',
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
      returns=Annotation(
        annotation=Name(
          value='int',
        ),
      ),
    ),
  ],
)""",
        )

    def test_stray_return_dedent(self) -> None:
        self.__test_parse(
            """
def invalid() -> int:
    value: int = 10
   value = 11
  return value
""",
            """Module(
  body=[
    FunctionDef(
      name=Name(
        value='invalid',
      ),
      params=Parameters(),
      body=IndentedBlock(
        body=[
          SimpleStatementLine(
            body=[
              AnnAssign(
                target=Name(
                  value='value',
                ),
                annotation=Annotation(
                  annotation=Name(
                    value='int',
                  ),
                ),
                value=Integer(
                  value='10',
                ),
              ),
            ],
          ),
          UnmatchedDedent(),
        ],
      ),
      returns=Annotation(
        annotation=Name(
          value='int',
        ),
      ),
    ),
    SimpleStatementLine(
      body=[
        Assign(
          targets=[
            AssignTarget(
              target=Name(
                value='value',
              ),
            ),
          ],
          value=Integer(
            value='11',
          ),
        ),
      ],
    ),
    StrayIndentedBlock(
      body=[
        SimpleStatementLine(
          body=[
            Return(
              value=Name(
                value='value',
              ),
            ),
          ],
        ),
      ],
    ),
  ],
)""",
        )

    def test_stray_method(self) -> None:
        self.__test_parse(
            """
    def invalid() -> int:
        value: int = 10
        return value
""",
            """Module(
  body=[
    StrayIndentedBlock(
      body=[
        FunctionDef(
          name=Name(
            value='invalid',
          ),
          params=Parameters(),
          body=IndentedBlock(
            body=[
              SimpleStatementLine(
                body=[
                  AnnAssign(
                    target=Name(
                      value='value',
                    ),
                    annotation=Annotation(
                      annotation=Name(
                        value='int',
                      ),
                    ),
                    value=Integer(
                      value='10',
                    ),
                  ),
                ],
              ),
              SimpleStatementLine(
                body=[
                  Return(
                    value=Name(
                      value='value',
                    ),
                  ),
                ],
              ),
            ],
          ),
          returns=Annotation(
            annotation=Name(
              value='int',
            ),
          ),
        ),
      ],
    ),
  ],
)""",
        )

    def test_stray_except(self) -> None:
        self.assertRaises(
            ParserSyntaxError,
            self.__test_parse,
            """
try:
    value: int = 10
    except:
        pass
""",
            "",
        )

    def test_stray_if(self) -> None:
        self.assertRaises(
            ParserSyntaxError,
            self.__test_parse,
            """
value: int = 10
if value > 50:
    pass
    else:
    pass
""",
            "",
        )

    def __test_parse(self, code: str, expected_tree: str) -> None:
        source_tree: Module = parse_module(code)
        actual_tree: str = dump(source_tree)
        self.assertEqual(expected_tree, actual_tree)
