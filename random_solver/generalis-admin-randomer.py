from os import system, name
import random
import copy as c
from openpyxl import load_workbook

### TABLAZATKEZELESEK
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


def make_table(ORIG_TABLE, SHIFT):
    TABLE_MADE = c.deepcopy(ORIG_TABLE)

    day_exception_current = {'x', 'X', 'y', 'Y', 'xn', 'xN', 'XN', 'Xn', 'nx', 'nX', 'Nx', 'NX', 'e', 'E', 'é', 'É'}
    day_exception_prev = {'e', 'E', 'é', 'É'}

    night_exception_current = {'x', 'X', 'y', 'Y', 'xe', 'xE', 'XE', 'Xe', 'ex', 'eX', 'Ex', 'EX', 'n', 'N',
                               'xé', 'xÉ', 'XÉ', 'Xé', 'éx', 'éX', 'Éx', 'ÉX'}
    night_exception_next = {'x', 'X', 'xn', 'xN', 'XN', 'Xn', 'nx', 'nX', 'Nx', 'NX', 'n', 'N'}

    if SHIFT == 'DAY':
        for row in TABLE_MADE:
            for d in range(3, len(row)):
                if row[d] in day_exception_prev:
                    if d + 1 < len(row):
                        row[d + 1] = 0
                if row[d] in day_exception_current:
                    row[d] = 0
                elif row[d] in {'n', 'N'}:
                    row[d] = 'N'
                    row[1] -= 1
                elif row[d] != 0:
                    row[d] = 1
            if row[1] == 0:
                for d in range(3, len(row)):
                    if row[d] == 1:
                        row[d] = 0

    if SHIFT == 'NIGHT':
        for row in TABLE_MADE:
            for d in range(3, len(row)):
                if row[d] in night_exception_next:
                    if d - 1 > 3 and row[d - 1] != 4:
                        row[d - 1] = 0
                if row[d] in night_exception_current:
                    row[d] = 0
                elif row[d] in {'e', 'E', 'é', 'É'}:
                    row[d] = 'E'
                    row[2] -= 1
                elif row[d] != 0 and row[d] != 4:
                    row[d] = 1
            if row[2] == 0:
                for d in range(3, len(row)):
                    if row[d] == 1:
                        row[d] = 0

    return TABLE_MADE

def draw(current_day, NUM):
    ### AZ ADOTT NAPON A SULYOKNAK MEGFELELOEN KIVALASZT NUM SZAMU ADMINT,
    ### AKIK AZ ADOTT NAPI AKTUALIS MUSZAKNAK MEGFELELO BEOSZTAST KAPJAK
    ### HA NEM LEHET ANNYI KIVALASZTANI, AKKOR -1-GYEL TER VISSZA

    # ADMINOK SORSZAMANAK MEGFELELO LISTA
    admins_index = list(range(len(current_day)))

    # OSSZEHASONLITASHOZ, HOGY NEM MINDEN ADMINHOZ 0 TARTOZIK-E
    zeros = [0 for i in range(len(current_day))]

    # ATMENETI LISTA, HOGY NE AZ EREDETIT IRJA AT
    current_day_tmp = c.copy(current_day)

    # VISSZATERESI LISTA LESZ AZ AMDINOK SORSZAMAVAL
    admin = list(range(NUM))

    # FIX NAPOK VISSZAADASA
    index = 0
    for item in range(len(current_day_tmp)):
        if isinstance(current_day_tmp[item], str):
            admin[index] = item
            current_day_tmp[item] = 0
            index += 1
    
    # ANNYISZOR SORSOLUNK, AHANYSZOR A FUGGVENYNEK MEGADTUK
    # EGY-EGY ADMIN SORSOLASA, MAJD A HOZZA TARTOZO ELEM KINULLAZASA,
    # HOGY NE SORSOLJUK KI KETSZER
    for i in range(index, NUM):
        # HA AZONOSAN 0 A LISTA
        if current_day_tmp == zeros:
            return -1
        a = random.choices(admins_index, current_day_tmp, k = 1)
        admin[i] = a[0]
        current_day_tmp[a[0]] = 0

    return admin


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
            if table_fin[admin][day] == 0:
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


def gen_all(TABLE_DAY, TABLE_NIGHT):
    ### MEGPROBAL LEGENERALNI EGY BEOSZTAST
    max_day = len(TABLE_DAY[0])

    ### NAPPALOS MUSZAKOK GENERALASA
    for day in range(3, max_day):
        act_day = [row[day] for row in TABLE_DAY]
        ### HA VAN FIX MUSZAK BEIRVA AZ ADOTT NAPRA, AKKOR AZZAL FELFELE KORRIGALUNK,
        ### MERT EGYSZER MAR LE LETT VONVA A MUSZAKSZAMBOL
        for i in range(len(act_day)):
            if isinstance(act_day[i], str):
                TABLE_DAY[i][1] += 1
        admins = draw(act_day, 2)
        if admins != -1:
            for admin in admins:
                TABLE_DAY[admin][day] = 'N'
                ### EJSZAKAS MUSZAKOK LEHETOSEGEINEK MEGVALTOZTATASA
                TABLE_NIGHT[admin][day] = 0
                if day > 3:
                    TABLE_NIGHT[admin][day - 1] = 0
                ### 3 NAPPAL NEM LEHET ZSINORBAN
                if TABLE_DAY[admin][day - 1] == 'N' and day + 1 < max_day:
                    TABLE_DAY[admin][day + 1] = 0
                ### NAPPALOS MUSZAKOK SZAMANAK CSOKKENTESE
                TABLE_DAY[admin][1] -= 1
                ### ELLENORZES, HOGY KELL-E MEG ADNI MUSZAKOT
                if TABLE_DAY[admin][1] == 0:
                    for i in range(3, max_day):
                        if TABLE_DAY[admin][i] != 'N':
                            TABLE_DAY[admin][i] = 0
        else:
            return -1

    ### EJSZAKAS MUSZAKOK GENERALASA
    for day in range(3, max_day):
        act_day = [row[day] for row in TABLE_NIGHT]
        ### HA VAN FIX MUSZAK BEIRVA AZ ADOTT NAPRA, AKKOR AZZAL FELFELE KORRIGALUNK,
        ### MERT EGYSZER MAR LE LETT VONVA A MUSZAKSZAMBOL
        for i in range(len(act_day)):
            if isinstance(act_day[i], str):
                TABLE_NIGHT[i][2] += 1
        admin = draw(act_day, 1)
        if admin != -1:
            admin = admin[0]
            TABLE_NIGHT[admin][day] = 'E'
            ### 3 EJSZAKA NEM LEHET ZSINORBAN
            if TABLE_NIGHT[admin][day - 1] == 'E' and day + 1 < max_day:
                TABLE_NIGHT[admin][day + 1] = 0
            ### 4 MUSZAK NEM LEHET ZSINORBAN MEGADVA,
            ### AMI CSAK A KOVETKEZOKEPPEN LEHETSEGES: NNEE
            if day > 4 and day < max_day - 1:
                if TABLE_DAY[admin][day - 1] == 'N' and TABLE_DAY[admin][day - 2] == 'N':
                    TABLE_NIGHT[admin][day + 1] = 0
            ### EJSZAKAS MUSZAKOK SZAMANAK CSOKKENTESE
            TABLE_NIGHT[admin][2] -= 1
            ### ELLENORZES, HOGY KELL-E MEG ADNI MUSZAKOT
            if TABLE_NIGHT[admin][2] == 0:
                for i in range(3, max_day):
                    if TABLE_NIGHT[admin][i] != 'E':
                        TABLE_NIGHT[admin][i] = 0
        else:
            return -1
    return 1


def merge_table(TABLE_DAY, TABLE_NIGHT):
    final_table = [[row[0]] + row[3:len(TABLE_DAY[0])] for row in TABLE_DAY]
    for row in range(len(final_table)):
        for day in range(3, len(TABLE_NIGHT[0])):
            if TABLE_NIGHT[row][day] == 'E':
                final_table[row][day - 2] = 'E'
    return final_table


def main():
    ### XLSX IMPORTALASA
    workbook = load_workbook(filename="../requests_admin.xlsx")

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

    ### MUSZAKSZAMOK LISTAJA
    day_shifts = [ORIG_TABLE[i][1] for i in range(len(ORIG_TABLE))]
    night_shifts = [ORIG_TABLE[i][2] for i in range(len(ORIG_TABLE))]

    ### KERESEKET TARTALMAZO KULON NAPPALOS ES EJSZAKAS TABLAZATOK LETREHOZASA
    ORIG_TABLE_DAY = make_table(ORIG_TABLE, 'DAY')
    ORIG_TABLE_NIGHT = make_table(ORIG_TABLE, 'NIGHT')

    ### GENERALAS
    ### GENERALAS SORAN ATMENETI TABLAZATOKKAL DOLGOZUNK
    tmp_table_day = c.deepcopy(ORIG_TABLE_DAY)
    tmp_table_night = c.deepcopy(ORIG_TABLE_NIGHT)
    g = gen_all(tmp_table_day, tmp_table_night)
    s = 0
    MAX_GEN = 5
    best_gen_value = -100000
    i = 0
    print('Gen start')

    s = 0
    while i < MAX_GEN:
        tmp_table_day = c.deepcopy(ORIG_TABLE_DAY)
        tmp_table_night = c.deepcopy(ORIG_TABLE_NIGHT)
        g = gen_all(tmp_table_day, tmp_table_night)
        while g == -1:
            s += 1
            if s % 1000 == 0:
                print(s)
            tmp_table_day = c.deepcopy(ORIG_TABLE_DAY)
            tmp_table_night = c.deepcopy(ORIG_TABLE_NIGHT)
            g = gen_all(tmp_table_day, tmp_table_night)
        final_table = merge_table(tmp_table_day, tmp_table_night)
        if final_check(final_table, day_shifts, night_shifts) == 0:
            pass
        else:
            current_value = eval_table(final_table, sat_orig, sat_orig)
            print('Gen:', i + 1, 'val:', current_value)
            if current_value > best_gen_value:
                best_gen_value = current_value
                best_gen_table = c.deepcopy(final_table)
            i += 1
    print('Legjobb beosztas', MAX_GEN, 'generalasbol:')
    niceprint(best_gen_table, DAYS, 0)
    print('Ertekeles:', best_gen_value)


main()
