# coding=utf-8

"""
Handles the learning of tokens throughout the execution.
"""

from typing import Set, List
from core.ParsingStageExtractor import ParsingStageExtractor, Stage


class TokenLearningHandler:
    """
    Each right hand side (rhs) is stored in here. For each rhs we haven't yet tested we issue an execution to check if it induces a token which we can learn.
    """

    rhs_to_test: Set[str] = set()

    rhs_tested: Set[str] = set()

    @classmethod
    def add_rhs(cls, rhs_list: List[str]):
        """
        Adds rhs to the set of values to test if it was not already tested.
        :param rhs: The value to test.
        """
        for rhs in rhs_list:
            if rhs not in cls.rhs_tested:
                cls.rhs_to_test.add(rhs)

    @classmethod
    def tokens_to_learn(cls):
        """
        Check if any values exist that need to be tested.
        :return: True if there are values to be tested.
        """
        return cls.rhs_to_test != set()

    @classmethod
    def get_to_test(cls):
        """
        If there is any value to be tested one value is returned, otw. None.
        :return: None or a value that needs to be tested.
        """
        if cls.rhs_to_test:
            value = cls.rhs_to_test.pop()
            cls.rhs_tested.add(value)
            return value
        else:
            return None

    @classmethod
    def find_learning_patterns(cls, objs):
        accumulate = False
        comparisons = list()
        for obj in objs:
            if obj["type"] == "STACK_EVENT":
                accumulate = False
                cls._add_token_to_learn(comparisons)
                comparisons = list()
                if not obj["stack"]:
                    return
                function = obj["stack"][-1]
                if function in ParsingStageExtractor.stages and ParsingStageExtractor.stages[function] == Stage.LEXING:
                    accumulate = True
            elif accumulate and obj["type"] == "INPUT_COMPARISON":
                if obj["operator"] not in {"tokencomp", "tokenstore"}:
                    comparisons.append((obj["id"], obj["index"][0], obj["operand"]))

    @classmethod
    def _add_token_to_learn(cls, comparisons):
        """
        Check if the pattern matches for learning tokens (i.e. if consecutive characters are compared in different comparisons) and add those tokens to learn to the learning set.
        Different comparisons to avoid adding identifier lexing (here in a loop the identifier would be checked)
        Consecutive tokens as the tokens would be matched one after another. The rules can be relaxed which might increase the learning phase and possibly the learning noise.
        :param comparisons:
        :return:
        """
        # only interested in two or more comparisons
        if len(comparisons) < 2:
            return False
        # check if the comparison id or index is the same for two consecutive comparisons, if so, stop
        for i in range(1, len(comparisons)):
            if comparisons[i - 1][0] == comparisons[i][0] or comparisons[i - 1][1] >= comparisons[i][1]:
                return False
        strings = {""}
        new_strings = set()
        for val in comparisons:
            for string in strings:
                for char in val[2]:
                    new_strings.add(string + char)
            strings = new_strings
            new_strings = set()
        for string in strings:
            if string not in cls.rhs_tested:
                cls.rhs_to_test.add(string)
