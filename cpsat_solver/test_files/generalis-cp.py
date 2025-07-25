"""Nurse scheduling problem with shift requests."""
from typing import Union

from ortools.sat.python import cp_model


def niceprint(final_table, DAYS, SWITCH):
    if SWITCH == 0:
        print('NÉV'.center(21, ' '), end='\t ')
        for i in range(DAYS):
            if i < 9:
                print(i + 1, end='  ')
            else:
                print(i + 1, end=' ')
        print()
        for i in final_table:
            for j in range(len(i)):
                if j == 0:
                    print(i[j].ljust(21, ' '), end='\t|')
                else:
                    if i[j] != 0:
                        print(i[j], end='  ')
                    else:
                        print(' ', end='  ')
            print()

    elif SWITCH == 1:
        print('NÉV'.center(21, ' '), end='\t       ')
        for i in range(DAYS):
            if i < 9:
                print(i + 1, end='  ')
            else:
                print(i + 1, end=' ')
        print()
        for i in final_table:
            for j in range(len(i)):
                if j == 0:
                    print(i[j].ljust(21, ' '), end='\t|')
                else:
                    if i[j] != 0:
                        print(i[j], end='  ')
                    else:
                        print(' ', end='  ')
            print()

def main() -> None:
    # This program tries to find an optimal assignment of nurses to shifts
    # (3 shifts per day, for 7 days), subject to some constraints (see below).
    # Each nurse can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    num_nurses = 7
    num_shifts = 3
    num_days = 31
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    # shift_requests = [
    #     [[0, 0, 1], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 1]],
    #     [[0, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 0, 0], [0, 0, 0], [0, 0, 1]],
    #     [[0, 1, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0], [0, 1, 0], [0, 0, 0]],
    #     [[0, 0, 1], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0]],
    #     [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0]],
    # ]

    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.NewBoolVar(f"shift_n{n}_d{d}_s{s}")

    # Each shift is assigned to exactly one nurse in .
    for d in all_days:
        for s in all_shifts:
            model.AddExactlyOne(shifts[(n, d, s)] for n in all_nurses)

    # Each nurse works at most one shift per day.
    for n in all_nurses:
        for d in all_days:
            model.AddAtMostOne(shifts[(n, d, s)] for s in all_shifts)

    # Never work at day after night shift.
    for n in all_nurses:
        for d in range(num_days - 1):
            night_shift_today = shifts[(n, d, 2)]
            model.Add(shifts[(n, d + 1, 0)] == 0).OnlyEnforceIf(night_shift_today)
            model.Add(shifts[(n, d + 1, 1)] == 0).OnlyEnforceIf(night_shift_today)

    # No 3 similar shifts in a row
    # for n in all_nurses:
    #     for d in range(num_days - 2):
    #         day_shift_today = shifts[(n, d, 0)]


    # Try to distribute the shifts evenly, so that each nurse works
    # min_shifts_per_nurse shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of nurses, some nurses will
    # be assigned one more shift.
    min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
    if num_shifts * num_days % num_nurses == 0:
        max_shifts_per_nurse = min_shifts_per_nurse
    else:
        max_shifts_per_nurse = min_shifts_per_nurse + 1
    for n in all_nurses:
        num_shifts_worked: Union[cp_model.LinearExpr, int] = 0
        for d in all_days:
            for s in all_shifts:
                num_shifts_worked += shifts[(n, d, s)]
        model.Add(min_shifts_per_nurse <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_nurse)

    model.Maximize(0)
    # model.Maximize(
    #     sum(
    #         shift_requests[n][d][s] * shifts[(n, d, s)]
    #         for n in all_nurses
    #         for d in all_days
    #         for s in all_shifts
    #     )
    # )

    fin_table = [[i for _ in range(num_days + 1)]for i in range(num_nurses)]

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL:
        for d in range(num_days):
            for n in range(num_nurses):
                if solver.Value(shifts[(n, d, 0)]) == 1 or solver.Value(shifts[(n, d, 1)]) == 1:
                    fin_table[n][d + 1] = 'N'
                elif solver.Value(shifts[(n, d, 2)]) == 1:
                    fin_table[n][d + 1] = 'E'
                else:
                    fin_table[n][d + 1] = ' '
    else:
        print("No optimal solution found !")

    for i in fin_table:
        print(i)

    for i in fin_table:
        for j in range(len(i) - 1):
            if i[j] == 'E' and i[j + 1] == 'N':
                print('BAJ')

    return 0

    if status == cp_model.OPTIMAL:
        print("Solution:")
        for d in all_days:
            print("Day", d)
            for n in all_nurses:
                for s in all_shifts:
                    if solver.Value(shifts[(n, d, s)]) == 1:
                        if shift_requests[n][d][s] == 1:
                            print("Nurse", n, "works shift", s, "(requested).")
                        else:
                            print("Nurse", n, "works shift", s, "(not requested).")
            print()
        print(
            f"Number of shift requests met = {solver.ObjectiveValue}",
            f"(out of {num_nurses * min_shifts_per_nurse})",
        )
    else:
        print("No optimal solution found !")

    # Statistics.
    print("\nStatistics")
    print(f"  - conflicts: {solver.NumConflicts}")
    print(f"  - branches : {solver.NumBranches}")
    print(f"  - wall time: {solver.WallTime}s")


if __name__ == "__main__":
    main()
