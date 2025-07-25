from os import system, name
import random
import copy as c

from simple_graph import *
from double_graph import *
from mutual_graph import *
from check_graph import *

### ELLENORZESEK
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

def result_check(GRAPH, SCALE):
    OK = 1
    for row in range(len(GRAPH)):
        s = 0
        for col in GRAPH[row]:
            if col[1] != 0:
                s += 1
        if s > 1:
            OK = 0
            print('ALERT:', row, 'sorban tobb el lett kivalasztva', s)
        elif s < 1:
            OK = 0
            print('ALERT:', row, 'sorban kevesebb lett kivalasztva', s)

    for col in range(len(GRAPH[0])):
        s = 0
        for row in GRAPH:
            if row[col][1] != 0:
                s += 1
        if s > SCALE:
            OK = 0
            print('ALERT:', col, 'col tobb el lett kivalasztva', s)
        elif s < SCALE:
            OK = 0
            print('ALERT:', col, 'col kevesebb lett kivalasztva', s)

    if OK:
        if SCALE == 2:
            print('ELLENORZES RENDBEN: DAYS')
        if SCALE == 1:
            print('ELLENORZES RENDBEN: NIGHTS')

def final_check(table_fin, day_shifts, night_shifts):
    OK = 1
    for col in range(1, len(table_fin[0])):
        d = 0
        e = 0
        for row in range(len(table_fin)):
            if table_fin[row][col] == 'N':
                d += 1
            elif table_fin[row][col] == 'E':
                e += 1
        if d < 2:
            OK = 0
            # print('ALERT', col, 'napon nincs eleg nappalos!')
        elif d > 2:
            OK = 0
            # print('ALERT', col, 'napon tul sok a nappalos!')
        if e < 1:
            OK = 0
            # print('ALERT', col, 'napon nincs eleg ejszakas!')
        elif e > 1:
            OK = 0
            # print('ALERT', col, 'napon tul sok az ejszakas!')
    for row in range(len(table_fin)):
        d = 0
        e = 0
        for col in range(1, len(table_fin[0])):
            if table_fin[row][col] == 'N':
                d += 1
            elif table_fin[row][col] == 'E':
                e += 1
        if d != day_shifts[row]:
            # print('ALERT', table_fin[row][0], 'adminnak kevesebb lett a nappalja.')
            OK = 0
        if e != night_shifts[row]:
            # print('ALERT', table_fin[row][0], 'adminnak kevesebb lett az ejszakaja.')
            OK = 0

    ### SZABALYOK: NEM LEHET 3 EGYFORMA MUSZAK EGYMAS UTAN,
    ### VALAMINT NEM LEHET 4 VAN ANNAL NAP MUSZAKBAN EGYMAS UTAN
    for st in table_fin:
        s = 1
        d = 0
        n = 0
        while s < len(st):
            if st[s] == 'N':
                d += 1
            elif st[s] == 'E':
                n += 1
            else:
                d = 0
                n = 0
            if d == 3 or n == 3:
                # print()
                # niceprint(table_fin, len(table_fin[0]) - 1)
                # input()
                return 0
            if d + n == 4:
                # print()
                # niceprint(table_fin, len(table_fin[0]) - 1)
                # input()
                return 0
            s += 1

    if OK:
        # print('Minden rendben!')
        return 1
    else:
        return 0

def pattern_count(row, pattern):
    row_tmp = c.deepcopy(row)
    row_tmp = row_tmp.replace('N', '*')
    row_tmp = row_tmp.replace('E', '*')
    l = len(pattern)

    s = 0
    current = ''
    for i in range(l):
        current += row_tmp[1 + i]
    if current == pattern:
        s += 1

    # print(current)
    for i in range(1 + l, len(row_tmp)):
        current = current[1:]
        current += row_tmp[i]
        if current == pattern:
            s += 1
    return s

def eval_table(table_fin, sat_orig, sun_orig):
    PRINT = 0

    VALUE = 10000
    pattern = [['.**.', 35], ['.***.', 170], ['.**.*.', 40], ['.**.**.', 80], ['.***..**.', 115]]

    ### MINDEN EGYES ADMINHOZ TARTOZIK EGY KETELEMU LISTA,
    ### MELYNEK AZ ELSO ELEME AZ OSSZES MUSZAKJA, A MASODIK A HETVEGERE ESO MUSZAKJAI
    admin_shifts = [ [0, 0] for i in range(len(table_fin)) ]

    table_string = ['.' for i in range(len(table_fin))]
    for admin in range(len(table_fin)):
        s = 0
        w = 0
        for day in range(1, len(table_fin[0])):
            if table_fin[admin][day] == '':
                table_string[admin] += '.'
            elif table_fin[admin][day] in {'N', 'E'}:
                s += 1
                table_string[admin] += table_fin[admin][day]
                if day in sat_orig or day in sun_orig:
                    w += 1
        admin_shifts[admin][0] = s
        admin_shifts[admin][1] = w
        table_string[admin] += '.'

    weekend = 0
    weekend += len(sat_orig)
    weekend += len(sun_orig)
    weekend *= 3
    sum_shifts = 3 * (len(table_fin[0]) - 1)
    for admin in admin_shifts:
        opt_weekend = admin[0]*weekend/sum_shifts
        w = abs(admin[1] - opt_weekend)
        if w > 2:
            VALUE -= 120
        elif w > 1:
            VALUE -= 50
        elif w > 0:
            VALUE -= 20

    for row in table_string:
        for p in pattern:
            VALUE -= pattern_count(row, p[0])*p[1]

    if PRINT:
        for i in table_fin:
            print(i)
        print()
        print(VALUE)
        print()
        for i in admin_shifts:
            print(i)
        print()
        print('-'*100)
        print()

    return VALUE

def niceprint(final_table, DAYS):
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
                if i[j] != '':
                    print(i[j], end='  ')
                else:
                    print(' ', end='  ')
        print()

