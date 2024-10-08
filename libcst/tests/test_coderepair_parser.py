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
        self.__test_parse(
            """
try:
    value: int = 10
    except:
        pass
""",
            """Module(
  body=[
    Try(
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
          ExceptHandler(
            body=IndentedBlock(
              body=[
                SimpleStatementLine(
                  body=[
                    Pass(),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  ],
)""",
        )

    def test_stray_finally(self) -> None:
        self.__test_parse(
            """
try:
    value: int = 10
    finally:
        pass
""",
            """Module(
  body=[
    Try(
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
          Finally(
            body=IndentedBlock(
              body=[
                SimpleStatementLine(
                  body=[
                    Pass(),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  ],
)""",
        )

    def test_stray_if(self) -> None:
        self.__test_parse(
            """
value: int = 10
if value > 50:
    pass
    else:
    pass
""",
            """Module(
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
    If(
      test=Comparison(
        left=Name(
          value='value',
        ),
        comparisons=[
          ComparisonTarget(
            operator=GreaterThan(),
            comparator=Integer(
              value='50',
            ),
          ),
        ],
      ),
      body=IndentedBlock(
        body=[
          SimpleStatementLine(
            body=[
              Pass(),
            ],
          ),
          Else(
            body=SimpleStatementSuite(
              body=[],
            ),
          ),
          SimpleStatementLine(
            body=[
              Pass(),
            ],
          ),
        ],
      ),
    ),
  ],
)""",
        )

    def test_empty_with(self) -> None:
        self.__test_parse(
            """
with open('file_path', 'w') as file:
file.write('hello world !')
""",
            """Module(
  body=[
    With(
      items=[
        WithItem(
          item=Call(
            func=Name(
              value='open',
            ),
            args=[
              Arg(
                value=SimpleString(
                  value="'file_path'",
                ),
              ),
              Arg(
                value=SimpleString(
                  value="'w'",
                ),
              ),
            ],
          ),
          asname=AsName(
            name=Name(
              value='file',
            ),
          ),
        ),
      ],
      body=SimpleStatementSuite(
        body=[],
      ),
    ),
    SimpleStatementLine(
      body=[
        Expr(
          value=Call(
            func=Attribute(
              value=Name(
                value='file',
              ),
              attr=Name(
                value='write',
              ),
            ),
            args=[
              Arg(
                value=SimpleString(
                  value="'hello world !'",
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  ],
)""",
        )

    def test_empty_match(self) -> None:
        self.__test_parse(
            """
num: int = 10
match num:
case 1:
    pass
""",
            """Module(
  body=[
    SimpleStatementLine(
      body=[
        AnnAssign(
          target=Name(
            value='num',
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
    Match(
      subject=Name(
        value='num',
      ),
      cases=[],
    ),
    MatchCase(
      pattern=MatchValue(
        value=Integer(
          value='1',
        ),
      ),
      body=IndentedBlock(
        body=[
          SimpleStatementLine(
            body=[
              Pass(),
            ],
          ),
        ],
      ),
    ),
  ],
)""",
        )

    def test_stray_case(self) -> None:
        self.__test_parse(
            """
num: int = 10
match num:
    case 1:
        pass
case 2:
    pass
        case 3:
            pass
    case _:
        pass
""",
            """Module(
  body=[
    SimpleStatementLine(
      body=[
        AnnAssign(
          target=Name(
            value='num',
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
    Match(
      subject=Name(
        value='num',
      ),
      cases=[
        MatchCase(
          pattern=MatchValue(
            value=Integer(
              value='1',
            ),
          ),
          body=IndentedBlock(
            body=[
              SimpleStatementLine(
                body=[
                  Pass(),
                ],
              ),
            ],
          ),
        ),
      ],
    ),
    MatchCase(
      pattern=MatchValue(
        value=Integer(
          value='2',
        ),
      ),
      body=IndentedBlock(
        body=[
          SimpleStatementLine(
            body=[
              Pass(),
            ],
          ),
          StrayIndentedBlock(
            body=[
              MatchCase(
                pattern=MatchValue(
                  value=Integer(
                    value='3',
                  ),
                ),
                body=IndentedBlock(
                  body=[
                    SimpleStatementLine(
                      body=[
                        Pass(),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          MatchCase(
            pattern=MatchAs(),
            body=IndentedBlock(
              body=[
                SimpleStatementLine(
                  body=[
                    Pass(),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  ],
)""",
        )

    def __test_parse(self, code: str, expected_tree: str) -> None:
        source_tree: Module = parse_module(code)
        actual_tree: str = dump(source_tree)
        self.assertEqual(expected_tree, actual_tree)
