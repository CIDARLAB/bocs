from typing import Dict
import numpy as np

class LogicEquation(object):

    def __init__(self, equation, value):
        self.equation = equation
        self.value = value

class ConstraintMatrix:

    def __init__(self, size):
        self.header = []
        self.size = size
        self.matrix = np.zeros((1, size))

    def set_header(self, header):
        self.header = header

    def insert_row(self, row: LogicEquation):
        # TODO: insert the data into this
        sub_matrix = self.compile_logic(row)
        self.matrix = np.r_[self.matrix, sub_matrix]
        print(row.equation)
        print(self.matrix)

    def compile_logic(self, logic):
        sub_matrix = np.zeros((1, self.size))
        # compile the logic equation into a 0/1 table and return this matrix
        return sub_matrix

ControlPortNumber = 3
# The first element of each line is the array of all elements involved in this constraint
# For example, we have a constraint line as
# (elements involved) C1 C2 C3
#              [2,3]  0  1  1
# By adding this array can quickly locate the situation we want to check.
ConstraintMatrix_example = ConstraintMatrix(ControlPortNumber+1)

# C2 and C3 always in the same state, open together and close together
# {'AND(C1,C3)', 0} in LaTEX: ${C_2}={C_3}$
Logic1 = LogicEquation('EQUAL(C2,C3)', 1)
ConstraintMatrix_example.insert_row(Logic1)
# Here we only focus on the relationship sub-table of C2 and C3
# C2 C3
# 0  0
# 1  1
# Final table will look like
# (elements involved) C1 C2 C3
#              [2,3]  0  0  0
#              [2,3]  0  1  1

# In addition to the upper constraint, C1 and C3 cannot be opened together, but they can be closed at the same time
# {'AND(C1,C3)', 0} in LaTEX [${C_1}\land{C_3}=0$]
Logic2 = LogicEquation('AND(C1,C3)', 0)
ConstraintMatrix_example.insert_row(Logic2)
# Here we only focus on the relationship sub-table of C1 and C3
# C1 C3
# 0  0
# 1  0
# 0  1
# Table will be changed as
# (elements involved) C1 C2 C3
#              [2,3]  0  0  0
#              [2,3]  0  1  1
#              [1,3]  0  0  0
#              [1,3]  0  1  0
#              [1,3]  1  0  0
#              [1,3]  1  1  0
#              [1,3]  0  0  1
#              [1,3]  0  1  1
# But we cannot have conflict constraint, so after adding new rows, we should have a check and remove the ones causing conflicts and repeats
# Because we have the $element involved$ for each row, we can only check the rows contributed by at least one of the current involved elements, which
# faster our checking procedure.
# (elements involved) C1 C2 C3
#              [2,3]  0  0  0
#              [2,3]  0  1  1
#              [1,3]  1  0  0
#              [1,3]  0  1  1

# In addition to the upper constraint, C1 and C2 cannot be opened together, but they can be closed at the same time
Logic3 = LogicEquation('AND(C1,C2)', 0)
ConstraintMatrix_example.insert_row(Logic3)
# Here we only focus on the relationship sub-table of C1 and C2
# C1 C2
# 0  0
# 1  0
# 0  1
# Table will be changed as
# (elements involved) C1 C2 C3
#              [2,3]  0  0  0
#              [2,3]  0  1  1
#              [1,3]  1  0  0
#              [1,3]  0  1  1
#              [1,2]  0  0  0
#              [1,2]  0  0  1
#              [1,2]  1  0  0
#              [1,2]  1  0  1
#              [1,2]  0  1  0
#              [1,2]  0  1  1

# After checking the repeats and conflicts in the constraint matrix, the final table will be changed as
# (elements involved) C1 C2 C3
#              [2,3]  0  0  0
#              [2,3]  0  1  1
#              [1,3]  1  0  0
#              [1,3]  0  1  1

# Nothing new!
