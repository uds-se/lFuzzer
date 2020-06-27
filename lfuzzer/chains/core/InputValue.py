# coding=utf-8
"""
Contains the code that generates from an input and a given correction a new input.
"""
import random
import core.Utils as Utils
from core.TokenHandler import TokenHandler


class InputValue:
    """
    Generates from a given input based on operator, correcting string and the parent input a new input.
    """
    # the position at which the char subst starts
    at: int = 0
    # the start of the subst
    min: int = 0
    # the string to subst the char with
    correction: str = ""
    # the operator that caused the subst. strategy
    operator: str = ""
    # the input that was used in the execution
    inp: str = ""
    # the size of the stack at the comparison
    stack_size: int = 0
    # the id of the comparison which resulted in this input value
    id: int
    # defines if a random appending is done when the corrections are requested
    do_append: bool

    def __init__(self, at: int, min_pos: int, correction: str, operator: str, inp: str, stack_size: int, id: int, do_append: bool):
        self.at = at
        self.min = min_pos
        self.correction = correction
        self.operator = operator
        self.inp = inp
        self.stack_size = stack_size
        self.id = id
        self.do_append = do_append

    def __str__(self):
        return "inp: %s, at: %d, min: %d, correction: %s, operator: %s, stacksize: %d, id: %d" % (repr(self.inp), self.at, self.min, repr(self.correction), self.operator, self.stack_size, self.id)

    def __repr__(self):
        return self.__str__()

    def get_corrections(self):
        """
        Returns the new input string based on parent and other encapsulated parameters.
        :return:
        """
        new_char = self.correction
        subst_index = self.at - self.min
        inp = self.inp
        # replace char of last comparison with new continuation
        inp = inp[:subst_index] + new_char
        # append a new char, it might be that the program expects additional input
        # also if the newchar is not a char but a string it is likely a keyword, so we better add a whitespace
        if self.operator == "strcmp":
            inp_rand_new = inp + " " + random.choice(Utils.continuations)
        # for token compares the "random" next char has to be a token itself, otw. a lexing error might occur
        # and we will not see a token comparison. Also between two tokens a whitespace should be allowed.
        elif self.operator == "tokencomp":
            # for token substitutions add a whitespace as this is in general used to separate tokens
            inp = self.inp[:subst_index] + " " + new_char if not self.inp[:subst_index].endswith(" ") else self.inp[:subst_index] + new_char
            inp_rand_new = inp + " " + TokenHandler.random_token() if not inp.endswith(" ") else inp + new_char
        elif self.operator == "strlen":
            inp_rand_new = inp
        else:
            inp_rand_new = inp + random.choice(Utils.continuations)
        if self.do_append:
            return inp, inp_rand_new
        else:
            return inp, inp
