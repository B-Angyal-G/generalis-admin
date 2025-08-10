from ortools.sat.python import cp_model

model = cp_model.CpModel()

for i in dir(model):
    print(i)
