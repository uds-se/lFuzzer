# coding=utf-8

"""
Handles the usages of tokens, i.e. it contains the mapping of tokens to specific values as well as methods to organize
the tokens throughout the execution.
"""

from typing import Dict, Set, List, Any, Tuple
from core import Utils
import os.path as path
import random
import sys
import string
from core.ParsingStageExtractor import ParsingStageExtractor, Stage


class TokenHandler:
    """
    Handles the token streams of the executions and collects information about the tokens.
    """

    # stores for each token the strings that generated those tokens and a flag that marks some values as fixed
    # fixed values are values that stem from an execution with just one token, then the token counts as learned
    token_map: Dict[int, Dict[str, bool]] = dict()

    # stores for each run the last time the str was converted to a token
    tmp_index_token_map: Dict[int, Tuple[int, str]] = dict()

    # a mapping from the stacksize to a set of token values
    stack_comp_map: Dict[Tuple, Set[Tuple]] = dict()

    # index tokenvalue majority dict: stores for each index the token value that ocurred the most for it during one execution
    majority_dict: Dict[int, int] = dict()

    # stores the index of the largest found token in this run
    largest_index = -1

    @classmethod
    def iterate_objs(cls, objs: List[Dict[str, Any]], inpt: str):
        """
        Iterate over all INPUT_COMPARISONS and link the tokens.
        :param inpt: The input with which the subject was run.
        :param objs: All input comparisons of one run.
        """
        cls.stack_comp_map = dict()
        token_list = list()
        # max_index contains the maximum character seen in any input comparison throughout the execution
        max_index = -1
        # first get all token compares and store them together with their index
        for obj in objs:
            if obj["operator"] == "tokencomp" and  \
                    (obj["stack"][-1] not in ParsingStageExtractor.stages or ParsingStageExtractor.stages[obj["stack"][-1]] != Stage.LEXING):
                value = (int(obj["index"][0]), int(obj["value"]), int(obj["operand"][0]), tuple(obj["stack"]), obj["id"])
                if not token_list or token_list[-1] != value:
                    token_list.append(value)
            if obj["operator"] not in {"tokencomp", "strlen", "eof", "tokenstore"}:
                max_index = max(obj["index"][-1], max_index)




        # TODO filtering out loop conditions is not necessary as long as we take the largest and last tokencomp later
        # filtering out loop conditions with loop counters: if consecutive tokencomps have increasing/decreasing values and compare against the same constant, they are filtered
        # i = 0
        # while i < len(token_list) - 1:
        #     tok1 = token_list[i]
        #     tok2 = token_list[i + 1]
        #     # if the difference between the two values is 1 and the operand is the same, check if there is a third value or delete the two
        #     if (abs(tok1[1] - tok2[1]) == 1) and (tok1[2] == tok2[2]):
        #         # if there is a third value check if it holds the same condition to the second value, if so delete only the first value
        #         # thus, the whole comparison chain can be deleted
        #         if i < len(token_list) - 2:
        #             tok3 = token_list[i + 2]
        #             if (abs(tok2[1] - tok3[1]) == 1) and (tok2[2] == tok3[2]):
        #                 del token_list[i]
        #             else:
        #                 del token_list[i]
        #                 del token_list[i]
        #         else:
        #             del token_list[i]
        #             del token_list[i]
        #     else:
        #         i += 1
        # the last value could be caused by an lookahaead, in this case the safest way is deleting it as we cannot know if it was an eof check or a lookahead
        if token_list:
            token_list[0] = (Utils.min_index, token_list[0][1], token_list[0][2], token_list[0][3], token_list[0][4])
        # while token_list and (cls._get_substring(inpt, token_list[-1][0], 1) == '' or
        #                       (len(token_list) > 1 and token_list[-1][0] == Utils.max_index and
        #                        token_list[-2][0] < token_list[-1][0] - 1 and token_list[-1][1] != token_list[-1][2])):
        #     del token_list[-1]

        # TODO lookahead correction removed for the moment, need better heuristics here to fix those
        # then fix the list entries, e.g. bc of lookaheads in the lexer some indices are not linked correctly to the token value
        # for i in range(len(token_list) - 1):
        #     # check if two consecutive comparisons have the same index but different values
        #     if token_list[i][0] == token_list[i+1][0]:
        #         # then check if the index of the element in front of the current element is smaller, this indicates that a character was skipped
        #         if i > 0 and token_list[i][0] - 1 > token_list[i-1][0]:
        #             diff = token_list[i][0] - 1 - token_list[i-1][0]
        #             token_list[i] = (token_list[i][0] - diff, token_list[i][1])
        #         elif len(token_list) < i + 2 and token_list[i][0] + 1 < token_list[i+2][0]:
        #             diff = token_list[i+2][0] - token_list[i][0] + 1
        #             token_list[i+1] = (token_list[i+1][0] + diff, token_list[i+1][1])
        #         # TODO could also happen at the beginning or end of the compares, then Utils.maxindex and Utils.minindex needs to be used

        # extract list of ranges
        # use list to keep order as this is important for the deletion of subsuming ranges later (only the last range is kept if several values have the same range)
        if not token_list:
            return
        cls._make_majority_vote(token_list)
        rangelist = list()
        value = token_list[0]
        value2 = 0
        for i in range(len(token_list) - 1):
            value = token_list[i]
            value2 = token_list[i + 1]
            if value2[0] > value[0]:
                to_add = (value[0], value2[0] - value[0], value[1], value[3], value[4])
                if to_add not in rangelist:
                    rangelist.append(to_add)

        # add the last characters to the set
        # tuple format is: (startindex, length, token value, stacksize)
        if value2 != 0:
            to_add = (value2[0], max_index - value2[0] + 1, value2[1], value2[3], value2[4])
        else:
            to_add = (value[0], max_index - value[0] + 1, value[1], value[3], value[4])
        if to_add not in rangelist:
            rangelist.append(to_add)  # TODO objs[0]["length"] -1 to ignore the random appended char as this one likely not belongs to the token, but possibly can, so this assumption has to be handled carefully in future

        cls._clean_rangelist(rangelist)
        # extract and save the token string mapping
        for val in rangelist:
            # link stacks with tokencomps
            if val[3] not in cls.stack_comp_map:
                cls.stack_comp_map[val[3]] = set()
            cls.stack_comp_map[val[3]].add((val[0], val[2], val[4]))

            string = cls._get_substring(inpt, val[0], val[1])
            if string == "":
                continue
            if val[2] in cls.token_map:
                map_entry = cls.token_map[val[2]]
            else:
                map_entry = dict()
                cls.token_map[val[2]] = map_entry
            # check if the string is a safe string, i.e. the input consisted only of this one token
            if string == inpt:
                if False in map_entry.values():
                    for key, value in list(map_entry.items()):
                        if not value:
                            del map_entry[key]
                map_entry[string] = True
            elif not True in map_entry.values():
                string = cls._find_common(map_entry, string)
                map_entry[string] = False


        # for key, value in cls.stack_comp_map.items():
        #     print(value, key)
        # print(cls.print_tokenmap())
        return True

    @classmethod
    def _clean_rangelist(cls, rangelist):
        """
        Delete values in rangeset that are subsumed by larger values. (i.e. a value with range 0-2 is deleted if a value with range 0-6 is in the set.
        :param rangelist:
        :return:
        """
        to_delete = set()
        for val in reversed(rangelist):
            if val not in to_delete:
                for comp in rangelist:
                    if val is not comp and comp not in to_delete:
                        if val[0] <= comp[0] and val[0] + val[1] >= comp[0] + comp[1]:
                            to_delete.add(comp)
        for delete in to_delete:
            rangelist.remove(delete)

    @classmethod
    def _make_majority_vote(cls, token_list: List[Tuple[Any]]):
        """
        For each index get the token value that appeared the most. All other values are deleted from the token_list.
        :param token_list:
        :return:
        """
        cls.largest_index = -1
        index_token_count_map: Dict[int, Dict[int, int]] = dict()
        # count the number of token values per index
        for val in token_list:
            if val[0] in index_token_count_map:
                count_item = index_token_count_map[val[0]]
                if val[1] in count_item:
                    count_item[val[1]] += 1
                else:
                    count_item[val[1]] = 1
            else:
                index_token_count_map[val[0]] = {val[1]: 1}

        counter_set = set()
        cls. majority_dict = dict()
        # get for each index the token value that appeared the most
        for idx, counts in index_token_count_map.items():
            max_val = max([(val[1], val[0]) for val in counts.items()])
            counter_set.add((idx, max_val[1]))
            cls.majority_dict[idx] = max_val[1]
            cls.largest_index = max(cls.largest_index, idx)


        # delete all entries in the token_list which are not in the counter list
        # also delete in between entries (if we already had a higher value, delete the lower one
        current = 0
        for val in list(token_list):
            if (val[0], val[1]) not in counter_set or current > val[0]:
                token_list.remove(val)
            else:
                current = val[0]

    @classmethod
    def print_tokenmap(cls)-> str:
        """
        Print out all tokens known up to size 500.
        :return:
        """
        result = ""
        for i in range(0, 500):
            if i in cls.token_map:
                result += "%d %s\n" % (i, str(cls.token_map[i]))
        return result

    @classmethod
    def _find_common(cls, map_entry: Dict[str, int], string: str):
        string = string.strip()
        for key in map_entry.keys():
            key_str = key.strip()
            commonprefix = path.commonprefix([string, key_str])
            if commonprefix != '':
                del map_entry[key]
                return commonprefix
        return string

    @classmethod
    def _get_substring(cls, inpt: str, idx: int, size: int):
        """
        Get substring starting at idx with specified size.
        :param inpt: The input used to run the program.
        :param idx: The idx at which the substraction starts.
        :param size: The number of chars that should be substracted.
        :return:
        """
        return inpt[idx - Utils.min_index: idx - Utils.min_index + size].strip()

    # @classmethod
    # def iterate_objs(cls, objs: List[Dict[str, Any]]):
    #     """
    #     Iterate over all INPUT_COMPARISONS and link the tokens.
    #     :param objs: All input comparisons of one run.
    #     """
    #     for obj in objs:
    #         if obj["operator"] == "tokenstore":
    #             TokenHandler._link_token(obj["index"][0], obj["value"], obj["operand"][0])
    #     TokenHandler._flush_tokens()

    @classmethod
    def _link_token(cls, idx, value, token_number):
        """
        Links the token number to the value. This information is later important to generate the possible substitutions.
        :param value: The value which caused the token generation.
        :param token_number: The numeric representation of the token.
        :return:
        """
        try:
            tok_num = int(token_number)
        except ValueError:
            return
        cls.tmp_index_token_map[idx] = (max(tok_num, cls.tmp_index_token_map[idx][0]), value) if idx in cls.tmp_index_token_map else (tok_num, value)

    @classmethod
    def _flush_tokens(cls):
        """
        Writes the tokens temporarily stored in the tokenhandler to the actual storage and clears the temp.
        """
        for idx, (tok_num, value) in dict(cls.tmp_index_token_map).items():
            # for each index check if the length of the value is larger than one (so a keyword)
            if len(value) > 1:
                # if so check for each character if it was bound to a token
                for i in range(idx + 1, idx + len(value)):
                    val = cls.tmp_index_token_map.get(i)
                    # if a character was bound to a token, delete the index from the temp list if the entry to be deleted does not reach farther than the entry we are currently looking at
                    if val and i + len(val[1]) <= idx + len(value):
                        del cls.tmp_index_token_map[i]
        for idx, (tok_num, value) in cls.tmp_index_token_map.items():
            if tok_num in cls.token_map:
                if value in cls.token_map[tok_num]:
                    cls.token_map[tok_num][value] += 1
                else:
                    cls.token_map[tok_num][value] = 1
            else:
                cls.token_map[tok_num] = {value: 1}
        cls.tmp_index_token_map = dict()

        # for i in range(0, 15):
        #     if i in cls.token_map:
        #         print(i, cls.token_map[i])

    @classmethod
    def get_possible_substitutions(cls, token_number: str, stack: List[str]) -> Set[str]:
        """
        For a token value return the linked values.
        :param token_number:
        :return: the values linked to the token number
        """
        # for lexing function tokencompares are not allowed, so prune those comparisons
        if stack and stack[-1] in ParsingStageExtractor.stages and ParsingStageExtractor.stages[stack[-1]] == Stage.LEXING:
            return set()
        try:
            tok_num = int(token_number)
        except ValueError:
            return set()

        stack_tuple = tuple(stack)
        if stack_tuple in cls.stack_comp_map:
            if cls.check_tokenpruning(tok_num, cls.stack_comp_map[stack_tuple]):
                return set()

        if tok_num in cls.token_map:
            token_dict = cls.token_map[tok_num]
            if len(token_dict) >= 5:
                return set(random.sample(set(token_dict.keys()), 5))
            else:
                return set(token_dict.keys())
        else:
            return set()

    @classmethod
    def get_tokencompare_stack_tuple(cls, index: int, correction: str, stack_size: int, id: int, cover_counter: int) -> Tuple[Tuple[int]]:
        """
        Based on the number of token comparisons done at each level of the stack a heuristic value is calculated.
        Many different comparisons on a low level are favorable. Capped at 30 comparisons per level.
        :return:
        """
        # add all token right hand sides for comparisons of chars not at the given index
        key_value_dict: Dict[int, Set[Tuple[int, int]]] = dict()
        for key, value in cls.stack_comp_map.items():
            for val in value:
                if val[0] != index:
                    length = len(key)
                    if length in key_value_dict:
                        key_value_dict[length].add((val[1], val[2]))
                    else:
                        key_value_dict[length] = {(val[1], val[2])}

        # add the value that the index is compared to
        if stack_size in key_value_dict:
            value_set = key_value_dict[stack_size]
            # check if the same comparison was already performed on another index, if so do not add the correction
            if not any(val[1] == id for val in value_set):
                value_set.add((correction, id))
        else:
            key_value_dict[stack_size] = {(correction, id)}
        result_list = list()
        for key, value in sorted(key_value_dict.items()):
            # take the negative length as smaller values are ranked higher in the prio queue
            result_list.append((key, -len(value)))
        # append coverage as metric, if the comparisons are the same, the value with the highest coverage should be preferred
        # also if progress can only be achieved on a higher value in the stack, this value is preferred
        result_list.append((sys.maxsize, -cover_counter))
        return tuple(result_list)

    @classmethod
    def check_tokenpruning(cls, token_number: int, compare_set: Set[Tuple]):
        """
        For the given tokennumber check if it appears several times on different indices. This would mean the comparison is in a loop, one loop iteration is sufficient for the moment.
        :param token_number: The number of the token.
        :param compare_set: The tuples defining the index and tokenvalue used in the comparison.
        :return: True if the tokenvalue was used several times on different indices.
        """
        return sum(token_number == val[1] for val in compare_set) > 1

    @classmethod
    def random_token(cls) -> str:
        """
        :return: a random token if tokens are present, a random alphanumeric character otw.
        """
        values = list(cls.token_map.values())
        if values:
            keys = list(random.choice(values).keys())
            if keys:
                return random.choice(keys)
        # if no tokens are available, return a random alphanumeric character
        return random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)

    @classmethod
    def get_majority_token(cls, index: int) -> int:
        """
        :param index: Index for which the majority token is queried
        :return: the value of the majority token
        """
        return cls.majority_dict.get(index)


    @classmethod
    def is_largest_token(cls, index: int) -> bool:
        """
        Reports if the given index is the start of the largest token found in this run
        :param index: the index to check for maximality
        :return: True if the given index is the start of the largest token of this subject execution.
        """
        return cls.largest_index == index


    @classmethod
    def get_different_correct_token(cls, tok_comp_values: Set) -> Set[str]:
        tokens = set(cls.token_map.keys())
        diff_set = tokens.difference(tok_comp_values)
        if diff_set:
            return {random.choice(list(cls.token_map[random.choice(list(diff_set))].keys()))}
        else:
            return set()

    @classmethod
    def tokens(cls):
        result = set()
        for tokens in cls.token_map.values():
            keys = set()
            for token in tokens.keys():  # make sure that only the common prefixes of tokens are used
                if not keys:
                    keys.add(token)
                    continue
                for el in keys:
                    if el.startswith(token) and len(token) > 3:  # only delete a value if the token that causes the delete is larger than 3
                        keys.remove(el)
                        break
                    if token.startswith(el) and len(el) > 3:  # only do not add a token if the token that hinders the add is larger than 3
                        token = el
                        break
                keys.add(token)
            result.update(keys)

        return result

