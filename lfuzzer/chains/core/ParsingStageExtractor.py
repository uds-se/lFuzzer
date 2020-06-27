"""
Puts every function in a specific parsing stage (lexing, parsing). In future it might also help to extract function with semnatic checks and function including the actual program logic.
"""

from typing import Dict, Set, List, Any
from enum import IntEnum


class Stage(IntEnum):
    """
    Enum defining the different stages
    """
    LEXING = 0
    PARSING = 1
    UNDEF = 2


class ParsingStageExtractor:
    """
    Class computing and containing the current knowledge about the parsing stages of a program.
    """
    stages: Dict[str, Stage] = dict()

    call_tree: Dict[str, Set[str]] = dict()
    call_tree_root: str

    @classmethod
    def extract_stages(cls, objs: List[Any]):
        """
        Extract the parsing stages as defined by one run and add it to the overall knowledge.
        :param objs: The comparisons done throughout the execution.
        """
        # extract dynamic call graph
        # for each comparison check if it is a comparison on a real input character, if so put the function in the lexing set, otherwise in the parsing set
        tmp_stages = dict()
        for obj in objs:
            if obj["type"] == "INPUT_COMPARISON":
                function = obj["stack"][-1]
                if function not in cls.stages:
                    if function not in tmp_stages:
                        tmp_stages[function] = {Stage.LEXING: 0, Stage.PARSING: 0}
                    if obj["operator"] == "tokencomp":
                        tmp_stages[function][Stage.PARSING] += 1
                    elif obj["operator"] != "tokenstore":
                        tmp_stages[function][Stage.LEXING] += 1

        if tmp_stages:
            cls._extract_callgraph(objs)
            cls._get_stage_mapping(tmp_stages, cls.call_tree_root, set(), Stage.UNDEF)
        return True

    @classmethod
    def _extract_callgraph(cls, objs: List[Any]):
        last_size = 0
        # save the root of the tree
        cls.call_tree_root = objs[0]["stack"][0]
        for obj in objs:
            if obj["type"] == "STACK_EVENT":
                stack = obj["stack"]
                current_size = len(stack)
                if last_size < current_size and current_size > 1:
                    caller = stack[-2]
                    callee = stack[-1]
                    if caller not in cls.call_tree:
                        cls.call_tree[caller] = set()
                    cls.call_tree[caller].add(callee)
                last_size = current_size
        # dot = Digraph(comment="Caller Graph")
        # for key in cls.call_tree.keys():
        #     dot.node(key)
        # for key, values in cls.call_tree.items():
        #     for val in values:
        #         dot.edge(key, val)
        # dot.render("call_graph.pdf", view=True)

    @classmethod
    def _get_stage_mapping(cls, tmp_stages, current, seen, stage):
        # if we already defined a stage for the function and the stage is less or equal what we are about to define, we can skip
        # if the stage is for example parsing and the current stage is lexing we might want to lower the stage
        if current in seen and (current not in cls.stages or cls.stages[current] <= stage):
            return
        seen.add(current)
        current_stage = stage
        if current in tmp_stages:
            # if the function is declared as lexing or if one of the parents was a lexing function, define the function as a lexing function
            if tmp_stages[current][Stage.LEXING] > tmp_stages[current][Stage.PARSING] or stage == Stage.LEXING:
                cls.stages[current] = Stage.LEXING
                current_stage = Stage.LEXING
            else:
                cls.stages[current] = Stage.PARSING
                current_stage = Stage.PARSING
        elif current in cls.stages:
            current_stage = cls.stages[current]
        if current in cls.call_tree:
            for child in cls.call_tree[current]:
                cls._get_stage_mapping(tmp_stages, child, seen, current_stage)

    @classmethod
    def print_stages(cls):
        result = ""
        for key, value in cls.stages.items():
            result += '{0:30}  {1}\n'.format(key, value)
        return result
