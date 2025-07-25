from ortools.sat.python import cp_model
from openpyxl import *


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

def request_check(ORIG_TABLE):
    DAYS = len(ORIG_TABLE[0]) - 3
    ERROR = 0

    ### ### ELLENORZES, HOGY PONTOSAN ANNYI KIOSZTANDO MUSZAK VAN-E AHANY NAP
    day_shift = 0
    night_shift = 0
    for i in range(len(ORIG_TABLE)):
        day_shift += ORIG_TABLE[i][1]
        night_shift += ORIG_TABLE[i][2]

    ### ### FELTETELEK NAPPALRA ES EJSZAKARA KULON
    if day_shift < 2 * DAYS:
        print('ALERT!!! Nappalra kevesebb műszak van beírva, mint szükséges!')
        ERROR = 1
    elif day_shift > 2 * DAYS:
        print('ALERT!!! Nappalra több műszak van beírva, mint szükséges!')
        ERROR = 1

    if night_shift < DAYS:
        print('ALERT!!! Éjszakára kevesebb műszak van beírva, mint szükséges!')
        ERROR = 1
    elif night_shift > DAYS:
        print('ALERT!!! Éjszakára több műszak van beírva, mint szükséges!')
        ERROR = 1

    ### ### ELLENORZES, HOGY NEM ADTAK-E EGY EMBERNEK TOBB FIX NAPOT
    ### ### NAPPALRA VAGY EJSZAKARA, MINT AMENNYIT LEHETNE
    ### ### ES
    ### ### ELLENORZES, HOGY NEM ADTAK-E VALAKINEK
    ### ### EJSZAKA UTAN NAPPALT
    for row in range(len(ORIG_TABLE)):
        s = 0
        for day in range(DAYS):
            if ORIG_TABLE[row][day + 3] in {'n', 'N'}:
                s += 1
                if ORIG_TABLE[row][day + 2] in {'é', 'É'}:
                    ERROR = 1
                    print(ORIG_TABLE[row][0], day + 1, 'DATE: ALERT DAY AFTER NIGHT!!!')
        if s > ORIG_TABLE[row][1]:
            ERROR = 1
            print(ORIG_TABLE[row][0], ': ALERT DAY!!!')

        s = 0
        for night in range(DAYS):
            if ORIG_TABLE[row][night + 3] in {'é', 'É'}:
                s += 1
        if s > ORIG_TABLE[row][2]:
            ERROR = 1
            print(ORIG_TABLE[row][0], ': ALERT NIGHT!!!')

    ### ### ELLENORZES, HOGY NEM OSZTOTTAK-E BE TOBB EMBERT EGY NAPON
    ### ### NAPPALRA VAGY EJSZAKARA, MINT AMENNYIT LEHETNE
    for day in range(3, len(ORIG_TABLE[0])):
        s_day = 0
        s_night = 0
        for people in range(len(ORIG_TABLE)):
            if ORIG_TABLE[people][day] in {'n', 'N'}:
                s_day += 1
            if ORIG_TABLE[people][day] in {'é', 'É'}:
                s_night += 1
        if s_day > 2:
            ERROR = 1
            print(day - 2, 'ALERT DAY SHIFT!!!')
        if s_night > 1:
            ERROR = 1
            print(day - 2, 'ALERT NIGHT SHIFT!!!')

    if ERROR:
        return 0
    return 1


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Megoldás visszahívó osztály, amely kiírja a talált megoldásokat."""

    def __init__(self, shifts, all_admins, num_days, all_shifts, solution_limit=None):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._all_admins = all_admins
        self._num_days = num_days
        self._all_shifts = all_shifts
        self._solution_count = 0
        self._solution_limit = solution_limit
        self.all_found_schedules = [] # Itt tároljuk az összes talált beosztást

    def OnSolutionCallback(self):
        """Ezt a metódust hívja meg a solver minden talált megoldáskor."""
        self._solution_count += 1
        print(f"\n--- Megoldás {self._solution_count} ---")
        current_schedule = []

        for a in self._all_admins:
            admins_shifts_today = [a]
            for d in range(self._num_days):
                OK = 0
                for s in self._all_shifts:
                    if self.Value(self._shifts[(a, d, s)]) == 1:
                        if s == 0:
                            admins_shifts_today.append('N')
                            OK = 1
                        elif s == 1:
                            admins_shifts_today.append('E')
                            OK= 1
                if not OK:
                    admins_shifts_today.append(' ')
            print(admins_shifts_today)
        print()

        self.all_found_schedules.append(current_schedule)

        # Ha be van állítva megoldás limit, és elértük, állítsuk le a keresést
        if self._solution_limit is not None and self._solution_count >= self._solution_limit:
            print(f"Elértük a {self._solution_limit} megoldás limitet. Leállítás.")
            self.StopSearch()

    def solution_count(self):
        return self._solution_count


def read_requests(ORIG_TABLE, all_admins, all_days, all_shifts):
    shift_requests = [[[1 for s in all_shifts] for d in all_days] for a in all_admins]

    all_exception = {'x', 'X', 'y', 'Y'}
    day_exception_current = {'xn', 'xN', 'XN', 'Xn', 'nx', 'nX', 'Nx', 'NX', 'e', 'E', 'é', 'É'}
    day_current = {'n', 'N'}

    night_exception_current = {'xe', 'xE', 'XE', 'Xe', 'ex', 'eX', 'Ex', 'EX', 'n', 'N',
                               'xé', 'xÉ', 'XÉ', 'Xé', 'éx', 'éX', 'Éx', 'ÉX'}
    night_exception_next = {'x', 'X', 'xn', 'xN', 'XN', 'Xn', 'nx', 'nX', 'Nx', 'NX', 'n', 'N'}
    night_current = {'e', 'E', 'é', 'É'}

    for a in all_admins:
        for d in all_days:
            if ORIG_TABLE[a][d] in day_current:
                shift_requests[a][d][0] = 2
                shift_requests[a][d][1] = 0
            elif ORIG_TABLE[a][d] in night_current:
                shift_requests[a][d][0] = 0
                shift_requests[a][d][1] = 2
            elif ORIG_TABLE[a][d] in all_exception:
                shift_requests[a][d][0] = 0
                shift_requests[a][d][1] = 0
            elif ORIG_TABLE[a][d] in day_exception_current:
                shift_requests[a][d][0] = 0
            elif ORIG_TABLE[a][d] in night_exception_current:
                shift_requests[a][d][1] = 0

            if d < len(all_days) - 1:
                if ORIG_TABLE[a][d] in night_current:
                    shift_requests[a][d + 1][0] = 0
            if d > 0:
                if ORIG_TABLE[a][d] in night_exception_next:
                    shift_requests[a][d - 1][1] = 0

    return shift_requests

def main() -> None:
    ### XLSX IMPORTALASA
    workbook = load_workbook(filename="./requests_admin_cp.xlsx", data_only = True)

    # ELSO SHEET
    worksheet = workbook.worksheets[0]

    # 2D-S LISTAVA KONVERTALAS
    row_list = []
    for r in worksheet.rows:
        column = [cell.value for cell in r]
        row_list.append(column)

    # NAPOK SZAMA
    num_days = row_list[0][1]
    solution_limit = row_list[2][1]

    # BEOLVASOTT TABLAZAT
    # num_days + 6: OSZLOPOK SZAMA A KERESEK TABLAZAT ELOTT
    # row in row_list[4:len(row_list)]]-ban 4: TABLAZAT ELOTTI SOROK SZAMA
    ORIG_TABLE = [row[0:num_days + 6] for row in row_list[5:len(row_list)]]

    # ADMINOK
    admins_name = [row[0] for row in ORIG_TABLE]
    
    ### MUSZAKSZAMOK LISTAJA
    day_shifts_min = [row[1] for row in ORIG_TABLE]
    day_shifts_max = [row[2] for row in ORIG_TABLE]
    night_shifts_min = [row[3] for row in ORIG_TABLE]
    night_shifts_max = [row[4] for row in ORIG_TABLE]
    shifts_sum = [row[5] for row in ORIG_TABLE]

    # HETVEGEK DATUMAINAK GENERALESA KEZD.
    SATURDAY = row_list[1][1]
    sat = []
    sun = []
    if SATURDAY == 7:
        sun.append(1)
    while SATURDAY <= num_days:
        sat.append(SATURDAY)
        if SATURDAY != num_days:
            sun.append(SATURDAY + 1)
        SATURDAY += 7

    # HETVEGEK EREDETI DATUMAHOZ!!! HALMAZOK LETREHOZASA
    sat_orig = set(sat)
    sun_orig = set(sun)

    # TIME (DATUMOK) LISTABAN INDEXELES!!! MIATT 1-GYEL CSOKKENTES
    for i in range(len(sat)):
        sat[i] -= 1
    for i in range(len(sun)):
        sun[i] -= 1
    # HETVEGEK DATUMAINAK GENERALASA VEGE

    # KULSOSOK MUSZAKJAI
    s = 0
    for d in range(6, len(ORIG_TABLE[-1])):
        if ORIG_TABLE[-1][d] == None:
            if d - 6 not in sat and d - 6 not in sun:
                ORIG_TABLE[-1][d] = 'y'

    ### ELLENORZESEK
    ### TODO
    # if request_check(ORIG_TABLE) == 0:
    #     return 0

    # This program tries to find an optimal assignment of nurses to shifts
    # (3 shifts per day, for 7 days), subject to some constraints (see below).
    # Each nurse can request to be assigned to specific shifts.
    # The optimal assignment maximizes the number of fulfilled shift requests.
    num_admins = len(admins_name)
    num_shifts = 2
    all_admins = range(num_admins)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    shift_requests = read_requests([row[6:] for row in ORIG_TABLE], all_admins, all_days, all_shifts)

    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
    shifts = {}
    for a in all_admins:
        for d in all_days:
            for s in all_shifts:
                shifts[(a, d, s)] = model.NewBoolVar(f"shift_a{a}_d{d}_s{s}")

    # Every day shifts has exactly 2 nurses and night shifts exactly 1
    for d in all_days:
        model.Add(sum([shifts[(a, d, 0)] for a in all_admins]) == 2)

    for d in all_days:
        model.AddExactlyOne([shifts[(a, d, 1)] for a in all_admins])


    # Each nurse works at most one shift per day.
    for a in all_admins:
        for d in all_days:
            model.AddAtMostOne([shifts[(a, d, s)] for s in all_shifts])

    # Never work at day after night shift.
    for a in all_admins:
        for d in range(num_days - 1):
            model.Add(shifts[(a, d + 1, 0)] == 0).OnlyEnforceIf(shifts[(a, d, 1)])

    # No 3 similar shifts in a row
    for a in all_admins:
        for d in range(num_days - 2):
            model.Add(shifts[(a, d + 2, 0)] == 0).OnlyEnforceIf([shifts[(a, d, 0)], shifts[(a, d + 1, 0)]])
            model.Add(shifts[(a, d + 2, 1)] == 0).OnlyEnforceIf([shifts[(a, d, 1)], shifts[(a, d + 1, 1)]])

    # No 4 shifts in a row
    for a in all_admins:
        for d in range(num_days - 3):
            model.Add(shifts[(a, d + 3, 1)] == 0).OnlyEnforceIf([shifts[(a, d, 0)], shifts[(a, d + 1, 0)], shifts[(a, d + 2, 1)]])

    # Set day and night shift nums
    ### Soft constrains
    # Day and night shifts min, max and sum constrains
    for a in all_admins:
        model.Add(sum( [shifts[(a, d, 0)] for d in all_days] ) >= day_shifts_min[a])
        model.Add(sum( [shifts[(a, d, 0)] for d in all_days] ) <= day_shifts_max[a])
        model.Add(sum( [shifts[(a, d, 1)] for d in all_days] ) >= night_shifts_min[a])
        model.Add(sum( [shifts[(a, d, 1)] for d in all_days] ) <= night_shifts_max[a])
        model.Add(sum( [shifts[(a, d, s)] for d in all_days for s in all_shifts] ) == shifts_sum[a])

    
    # Requests
    for a in all_admins:
        for d in all_days:
            for s in all_shifts:
                if shift_requests[a][d][s] < 2:
                    model.Add(shifts[(a, d, s)] <= shift_requests[a][d][s])
                else:
                    model.Add(shifts[(a, d, s)] == 1)

    # for a in all_admins:
    #     for d in all_days:
    #         for s in all_shifts:
    #             if shift_requests[a][d][s] == 0:
    #                 model.Add(shifts[(a, d, s)] == 0)


    # model.Maximize(1)
    # model.Maximize(
    #         sum(
    #             shift_requests[n][d][s] * shifts[(n, d, s)]
    #             for n in all_nurses
    #             for d in all_days
    #             for s in all_shifts
    #             )
    #         )

    fin_table = [[i for _ in range(num_days + 1)] for i in range(num_admins)]


    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter(shifts, all_admins, num_days, all_shifts, solution_limit)

    solver.parameters.enumerate_all_solutions = True
    # Solve.
    status = solver.SearchForAllSolutions(model, solution_printer)

    print(f"Status = {solver.StatusName(status)}")
    print(f"Number of solutions found: {solution_printer.solution_count}")


    return 0

    # OLD!!!
    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL:
        for a in range(num_admins):
            sd = 0
            sn = 0
            for d in range(num_days):
                if solver.Value(shifts[(a, d, 0)]) == 1:
                    fin_table[a][d + 1] = 'N'
                    sd += 1
                elif solver.Value(shifts[(a, d, 1)]) == 1:
                    fin_table[a][d + 1] = 'E'
                    sn += 1
                else:
                    fin_table[a][d + 1] = ' '
            fin_table[a].append(sd)
            fin_table[a].append(sn)
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
            for a in all_admins:
                for s in all_shifts:
                    if solver.Value(shifts[(a, d, s)]) == 1:
                        if shift_requests[a][d][s] == 1:
                            print("Nurse", a, "works shift", s, "(requested).")
                        else:
                            print("Nurse", a, "works shift", s, "(not requested).")
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
