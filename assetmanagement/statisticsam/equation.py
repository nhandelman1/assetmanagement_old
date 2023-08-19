import re

import numpy as np
import pandas as pd


# variables must have first character r followed by a string of digits. First digit can only be 0 in the case of r0.
#   Correct: r0, r1, r111
#   Incorrect: r, r01, r00, x, x0, rx0, r0x
# variables, when evaluated, can be constants or pandas Series
# unary operators: operand must be enclosed with []
#   LN
#       Correct: LN[5], LN[r1+5], 5 + LN[r1]
#       Incorrect: LN[], LN(), LN5, LN 5, LN r1, 5LN(r1)
# binary operators: +, -, /, *, ^
# decimal numbers acceptable
# negative numbers:
#   -1 must be input as (0-1),
#   -.25 must be input as (0-.25), etc.
# no implied multiplication:
#   -(5+4) must be input as (0-1)*(5+4)
#   5r1 must be input as 5*r1
# TODO dataframe variables and related operations
class Equation:

    def __init__(self, equation_name=None, r0_allowed=True):
        self.equation_name = equation_name
        self.r0_allowed = r0_allowed

        self.infix_str = None
        self.postfix_list = None
        self.constant_list = None
        self.variable_list = None
        self.evaluated_result = None

    @staticmethod
    def is_unary_operator(s):
        return s in ["LN["]

    @staticmethod
    def is_right_bracket(c):
        return c == ']'

    @staticmethod
    def is_binary_operator(c):
        return c in ['+', '-', '/', '*', '^']

    @staticmethod
    def is_left_paren(c):
        return c == '('

    @staticmethod
    def is_right_paren(c):
        return c == ')'

    @staticmethod
    def has_high_eq_precedence(op1, op2):
        if op1 == '^':
            return True
        elif op1 in ['*', '/']:
            return op2 != '^'
        elif op1 in ['+', '-']:
            return op2 in ['+', '-']
        else:  # op1 is left paren or unary operator
            return False

    @staticmethod
    def is_constant(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    # has required variable form
    @staticmethod
    def is_variable(s):
        if Equation.is_constant(s):
            return False
        else:
            if len(s) < 2 or s[0] != 'r' or (len(s) > 2 and s[1] == '0'):
                return False
            for c in s[1:]:
                if c not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    return False
        return True

    def infix_str_to_postfix_list(self, infix_str):
        self.postfix_list = None
        operator_stack = []
        output_list = []

        infix_str = infix_str.replace(' ', '')
        self.infix_str = infix_str

        infix_list = re.split('(\(|\)|\+|\-|\*|/|\^|LN\[|\])', infix_str)
        infix_list = [s for s in infix_list if s != '']

        error_msg = None
        for s in infix_list:
            if self.is_left_paren(s) or self.is_unary_operator(s):
                operator_stack.append(s)
            elif self.is_right_paren(s):
                try:
                    operator = operator_stack.pop()
                    while not self.is_left_paren(operator):
                        output_list.append(operator)
                        operator = operator_stack.pop()
                except IndexError as e:
                    error_msg = str(e) + ". No left parenthesis for right parenthesis"
                    break
            elif self.is_right_bracket(s):
                try:
                    while True:
                        operator = operator_stack.pop()
                        output_list.append(operator)
                        if self.is_unary_operator(operator):
                            break
                except IndexError as e:
                    error_msg = str(e) + ". No unary operator for right bracket"
                    break
            elif self.is_binary_operator(s):
                try:
                    while len(operator_stack) > 0 and self.has_high_eq_precedence(operator_stack[-1], s):
                        output_list.append(operator_stack.pop())
                    operator_stack.append(s)
                except ValueError as e:
                    error_msg = str(e)
                    break
            else:  # is operand
                output_list.append(s)

        if error_msg is None:
            while len(operator_stack) > 0:
                s = operator_stack.pop()
                if self.is_left_paren(s):
                    error_msg = "No right parenthesis for left parenthesis"
                    break
                elif self.is_unary_operator(s):
                    error_msg = "No right bracket for unary operator"
                    break
                else:
                    output_list.append(s)

        if error_msg is None:
            error_msg = self.check_infix_to_postfix_conversion(output_list)

        if error_msg is None:
            error_msg = self.set_constants_variables(output_list)

        self.postfix_list = output_list if error_msg is None else None

        return None if error_msg is None else self.prepend_id_data([error_msg])[0]

    # # operands = # binary operators + 1
    #   exception: one operand and no binary operators is ok
    def check_infix_to_postfix_conversion(self, output_list):
        operator_count = 0
        operand_count = 0

        for s in output_list:
            if self.is_binary_operator(s):
                operator_count += 1
            elif self.is_unary_operator(s):
                pass
            else:  # is operand
                operand_count += 1

        if (operand_count == 1 and operator_count == 0) or operand_count == operator_count + 1:
            return None
        else:
            return "Number of operands should equal number of operators + 1"

    def set_constants_variables(self, output_list):
        self.constant_list = []
        self.variable_list = []

        error_msg = None
        for s in output_list:
            if self.is_binary_operator(s) or self.is_unary_operator(s):
                continue
            elif self.is_constant(s):
                self.constant_list.append(s)
            elif self.is_variable(s):
                if not self.r0_allowed and s == "r0":
                    error_msg = "Variable r0 not allowed"
                    break
                self.variable_list.append(s)
            else:
                error_msg = "'" + s + "' is not a correctly formatted constant or variable"
                break

        if error_msg is not None:
            self.constant_list = None
            self.variable_list = None

        return error_msg

    # return an empty set if no variables
    def variable_numbers(self):
        numbers = set()
        if self.variable_list is not None:
            for s in self.variable_list:
                numbers.add(int(s[1:]))
        return numbers

    def check_variable_count(self, num_vars_available):
        var_nums = self.variable_numbers()
        error_msg = None

        if len(var_nums) == 0:
            num_vars_req = 0
        else:
            num_vars_req = max(var_nums) + 1 if self.r0_allowed else max(var_nums)

        if num_vars_req > num_vars_available:
            error_msg = str(num_vars_available) + " variables available. " + str(num_vars_req) + " required."

        return error_msg

    def has_variable_r0(self):
        return 0 in self.variable_numbers()

    def prepend_id_data(self, msg_list):
        new_list = []
        for msg in msg_list:
            new_list.append(self.equation_name + " : " + msg)
        return new_list

    # elements of variable_value_list can be scalars or pandas series. they do not all have to be the same type
    # variable r0 assumed to refer to variable_value_list[0], r1 refers to variable_value_list[1], etc.
    # if r0 is not allowed, None is prepended to variable_value_list to keep the numbering
    # can raise ValueError
    def evaluate_equation(self, variable_value_list=[], inf_allowed=True, nan_allowed=True):
        error_msg_list = []

        if self.postfix_list is None:
            error_msg_list.append("Postfix equation not set")
        else:
            error_msg = self.check_variable_count(len(variable_value_list))
            if error_msg is not None:
                error_msg_list.append(error_msg)

        data_postfix_list = []
        if len(error_msg_list) == 0:
            if not self.r0_allowed:
                variable_value_list.insert(0, None)

            for term in self.postfix_list:
                if self.is_constant(term):
                    try:
                        term = int(term)
                    except ValueError:
                        try:
                            term = float(term)
                        except ValueError:
                            error_msg_list.append(str(term) + " is not an int or float")
                elif self.is_variable(term):
                    term = variable_value_list[int(term[1:])]

                data_postfix_list.append(term)

        operand_stack = []
        if len(error_msg_list) == 0:
            for term in data_postfix_list:
                if isinstance(term, str) and (self.is_unary_operator(term) or self.is_binary_operator(term)):
                    op_list = [operand_stack.pop()]

                    if self.is_binary_operator(term):
                        op_list.insert(0, operand_stack.pop())

                    try:
                        term = self.do_operation(op_list, term, inf_allowed, nan_allowed)
                    except ValueError as e:
                        error_msg_list.append(str(e))
                        break

                operand_stack.append(term)

        self.evaluated_result = None if len(operand_stack) == 0 else operand_stack[0]

        return self.prepend_id_data(error_msg_list)

    # implemented for unary and binary only
    # operands can be can be scalars or pandas series
    # operand_list contains the operands in prefix visual order
    #   unary operators: first element is operand
    #   binary operators: first element is left operand, second element is right operand
    #   functions: (when implemented), first element is first argument, second is second, etc.
    #   Note: technically all operators are functions. think of prefix notation (e.g. ln 5, + 5 2, func 5 2 3)
    # Pandas series:
    #   both series assumed to have same number of elements
    #   indexes are ignored. the result keeps the index of the visually leftmost series
    # can raise ValueError
    def do_operation(self, operand_list, operator_str, inf_allowed=True, nan_allowed=True):
        op1 = operand_list[0]
        op2 = None if self.is_unary_operator(operator_str) else operand_list[1]
        op1_is_series = isinstance(op1, pd.Series)
        op2_is_series = isinstance(op2, pd.Series)

        if op1_is_series and op2_is_series:
            op2 = op2.values

        if operator_str == "LN[":
            # np.log(0) = -inf and np.log(negative number) = NaN
            if (op1_is_series and op1.le(0).any()) or (not op1_is_series and op1 <= 0):
                raise ValueError("Non-positive number found before " + operator_str + " operation")
            result = np.log(op1)
        elif operator_str == "+":
            result = op1 + op2
        elif operator_str == "-":
            result = op1 - op2
        elif operator_str == "/":
            result = op1 / op2
        elif operator_str == "*":
            result = op1 * op2
        elif operator_str == "^":
            result = op1 ** op2
        else:
            raise ValueError("Unknown operator " + operator_str)

        if not isinstance(result, pd.Series):
            result = [result]

        if not inf_allowed and np.isinf(result).any():
            raise ValueError("Infinity not allowed in result of " + operator_str + " operation")
        if not nan_allowed and np.isnan(result).any():
            raise ValueError("NaN not allowed in result of " + operator_str + " operation")

        return result[0] if isinstance(result, list) else result
