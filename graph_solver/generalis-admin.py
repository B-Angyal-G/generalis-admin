from os import system, name
import random
import copy as c
from openpyxl import load_workbook

from simple_graph import *
from double_graph import *
from mutual_graph import *
from check_graph import *


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
    admins_name = [row[0] for row in ORIG_TABLE]

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

    ### GRAFOK LETREHOZASA
    ORIG_ADMINS = [set() for i in range(DAYS)]
    day_shifts = [ORIG_TABLE[i][1] for i in range(len(ORIG_TABLE))]
    night_shifts = [ORIG_TABLE[i][2] for i in range(len(ORIG_TABLE))]
    ORIG_GRAPH_DAY = make_graph(ORIG_TABLE, ORIG_ADMINS, day_shifts,  'DAY', DAYS)
    ORIG_GRAPH_NIGHT = make_graph(ORIG_TABLE, ORIG_ADMINS, night_shifts,  'NIGHT', DAYS)

    ### GENERALAS KEZDESE
    SZUMMA = 0
    best_gen_value = -100000
    best_gen_table = list()
    SUM_GEN = 3
    GEN = 0
    for i in range(SUM_GEN):
        GENERATION = 1
        while GENERATION:
            GEN += 1
            GENERATION = 0
            admins = c.deepcopy(ORIG_ADMINS)
            ### EREDETI GRAFOKAT NEM MODOSITJUK,
            ### AZ ALABBI GRAFOKKAL FOGUNK TOVABB DOLGOZNI
            graph_day = c.deepcopy(ORIG_GRAPH_DAY)
            graph_night = c.deepcopy(ORIG_GRAPH_NIGHT)

            ### NAPPALI BEOSZTAS GENERALASA
            graph_double_max_match(graph_day, day_shifts, admins)

            ### EJSZAKAI MUSZAKOKHOZ TARTOZO GRAF MODOSITASA
            ### A GENERALASNAK MEGFELELOEN
            for row in range(len(graph_day)):
                for col in range(len(graph_day[row])):
                    if graph_day[row][col][1] == 1:
                        admin = whois(row, day_shifts)
                        admin_index = sum(night_shifts[:admin])
                        for row_mod in range(admin_index, admin_index + night_shifts[admin]):
                            graph_night[row_mod][col][0] = 0
                            if col - 1 >= 0:
                                graph_night[row_mod][col - 1][0] = 0
                        break

            ### EJSZAKAI MUSZAKOK GENERALASA
            gen_night = graph_max_match(graph_night)
            if gen_night == 0:
                GENERATION = 1
            else:
                final_table = graph_merge(graph_day, graph_night, day_shifts, night_shifts, admins_name, DAYS)
                if final_check(final_table, day_shifts, night_shifts):
                    GENERATION = 0
                    current_value = eval_table(final_table, sat_orig, sun_orig)
                    if current_value > best_gen_value:
                        best_gen_value = current_value
                        best_gen_table = c.deepcopy(final_table)
                else:
                    GENERATION = 1
            if GEN % 100 == 0:
                if name == 'nt':
                    _ = system('cls')
                else:
                    _ = system('clear')
                print('Eddigi próbálkozások száma:', GEN)
                print('Sikeresen elkészített beosztások:', i, '/', SUM_GEN)

    print()
    print(SUM_GEN, 'generálásból a legjobbnak vélt beosztás:')
    print()
    niceprint(best_gen_table, DAYS)
    print()
    print('Értékelés:', best_gen_value)
    print('Generálások száma:', GEN)

main()
