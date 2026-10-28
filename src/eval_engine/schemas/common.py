from enum import StrEnum


class TaskType(StrEnum):
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    EXPLANATORY = "explanatory"
    CREATIVE = "creative"


class Dimension(StrEnum):
    CORRECTNESS = "correctness"
    COMPLETENESS = "completeness"
    REASONING = "reasoning"
    EXPRESSION = "expression"


class RubricShape(StrEnum):
    CHECKLIST = "checklist"
    MULTI_PATH_CLAIM_EVIDENCE = "multi_path_claim_evidence"
    MULTI_PATH = "multi_path"
    CRAFT_TESTS = "craft_tests"


# The rubric shape is dictated by the task type (design doc §3).
SHAPE_FOR_TASK: dict[TaskType, RubricShape] = {
    TaskType.FACTUAL: RubricShape.CHECKLIST,
    TaskType.ANALYTICAL: RubricShape.MULTI_PATH_CLAIM_EVIDENCE,
    TaskType.EXPLANATORY: RubricShape.MULTI_PATH,
    TaskType.CREATIVE: RubricShape.CRAFT_TESTS,
}

SINGLE_PATH_SHAPES = frozenset({RubricShape.CHECKLIST, RubricShape.CRAFT_TESTS})

OBVIOUS_ANSWER_COUNT = 5
