import pulp
import copy as c
from openpyxl import load_workbook


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


def read_requests(ORIG_TABLE, day_requests, night_requests):
    day_exception_current = {'x', 'X', 'y', 'Y', 'xn', 'xN', 'XN', 'Xn', 'nx', 'nX', 'Nx', 'NX', 'e', 'E', 'é', 'É'}
    day_exception_prev = {'e', 'E', 'é', 'É'}

    night_exception_current = {'x', 'X', 'y', 'Y', 'xe', 'xE', 'XE', 'Xe', 'ex', 'eX', 'Ex', 'EX', 'n', 'N',
                               'xé', 'xÉ', 'XÉ', 'Xé', 'éx', 'éX', 'Éx', 'ÉX'}
    night_exception_next = {'x', 'X', 'xn', 'xN', 'XN', 'Xn', 'nx', 'nX', 'Nx', 'NX', 'n', 'N'}

    for row in ORIG_TABLE:
        day_req_list = set()
        night_req_list = set()
        for d in range(3, len(row)):
            if row[d] in day_exception_current:
                day_req_list.add(d - 2)
            if row[d] in night_exception_current:
                night_req_list.add(d - 2)

            if d < len(row) - 1:
                if row[d] in day_exception_prev:
                    day_req_list.add(d - 1)
            if d > 3:
                if row[d] in night_exception_next:
                    night_req_list.add(d - 3)

        day_requests[row[0]] = day_req_list
        night_requests[row[0]] = night_req_list


def main():
    ### XLSX IMPORTALASA
    workbook = load_workbook(filename="./requests_admin.xlsx")

    # ELSO SHEET
    worksheet = workbook.worksheets[0]

    # 2D-S LISTAVA KONVERTALAS
    row_list = []
    for r in worksheet.rows:
        column = [cell.value for cell in r]
        row_list.append(column)

    # NAPOK SZAMA
    DAYS = row_list[0][1]

    # BEOLVASOTT TABLAZAT
    ORIG_TABLE = [row[0:DAYS + 3] for row in row_list[3:len(row_list)]]

    # HETVEGEK DATUMAINAK GENERALESA KEZD.
    SATURDAY = row_list[1][1]
    sat = []
    sun = []
    if SATURDAY == 7:
        sun.append(1)
    while SATURDAY <= DAYS:
        sat.append(SATURDAY)
        if SATURDAY != DAYS:
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
    for d in range(len(ORIG_TABLE[0])):
        if ORIG_TABLE[-1][d] == None:
            if d - 2 not in sat_orig and d - 2 not in sun_orig:
                ORIG_TABLE[-1][d] = 'x'

    ### ELLENORZESEK
    if request_check(ORIG_TABLE) == 0:
        return 0

    ### MUSZAKSZAMOK LISTAJA
    day_shifts_read = [ORIG_TABLE[i][1] for i in range(len(ORIG_TABLE))]
    night_shifts_read = [ORIG_TABLE[i][2] for i in range(len(ORIG_TABLE))]

    # Dolgozók és dátumok
    days = list(range(1, DAYS + 1))
    admins = [row[0] for row in ORIG_TABLE]

    day_shifts = {}
    night_shifts = {}
    day_requests = {}
    night_requests = {}
    for i in range(len(admins)):
        day_shifts[admins[i]] = day_shifts_read[i]
        night_shifts[admins[i]] = night_shifts_read[i]

    read_requests(ORIG_TABLE, day_requests, night_requests)

    # Döntési változók: dolgozó-nap-műszak (0 = nem dolgozik, 1 = dolgozik)
    schedule = pulp.LpVariable.dicts( "admins", ((a, d, s) for a in admins for d in days for s in ["n", "e"]), cat="Binary" )

    # Modell
    model = pulp.LpProblem("Schedule", pulp.LpMaximize)

    # Célfüggvény: minimalizáljuk az eltérést az egyenletes elosztástól
    model += pulp.lpSum([schedule[a, d, s] for a in admins for d in days for s in ["n", "e"]])

    # Korlátozások:
    # 2 Nappalos es 1 ejszakas
    for d in days:
        model += pulp.lpSum([schedule[a, d, "n"] for a in admins]) == 2
        model += pulp.lpSum([schedule[a, d, "e"] for a in admins]) == 1

    # Nappalos es ejszakas muszakok szama
    for a in admins:
        model += pulp.lpSum([schedule[a, d, "n"] for d in days]) == day_shifts[a]
        model += pulp.lpSum([schedule[a, d, "e"] for d in days]) == night_shifts[a]

    # Egy ember max 1 műszak / nap
    for a in admins:
        for d in days:
            model += schedule[a, d, "n"] + schedule[a, d, "e"] <= 1
            # Szabadság kezelése
            if d in day_requests[a]:
                model += schedule[a, d, "n"] == 0
            if d in night_requests[a]:
                model += schedule[a, d, "e"] == 0

    # Ejszaka utan nappal nem lehet
    for a in admins:
        for d in range(1, len(days)):
            model += schedule[a, d, "e"] + schedule[a, d + 1, "n"] <= 1

    # Nem lehet 3 egyforma muszak egymas utan
    for a in admins:
        for d in range(1, len(days) - 1):
            model += pulp.lpSum([schedule[a, d + i, "n"] for i in range(3)]) <= 2
            model += pulp.lpSum([schedule[a, d + i, "e"] for i in range(3)]) <= 2

    # Nem lehet 4 muszak egymas utan
    for a in admins:
        for d in range(1, len(days) - 2):
            model += pulp.lpSum([schedule[a, d + i, s] for i in range(4) for s in ["n", "e"]]) <= 3

    # Megoldás
    model.solve()

    # Eredmény kiírása
    for d in days:
        print(f"{d}:")
        for s in ["n", "e"]:
            for a in admins:
                if pulp.value(schedule[a, d, s]) == 1:
                    print(f" {s.upper()}: {a}")

main()
