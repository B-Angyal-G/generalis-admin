from os import system, name
import random
import copy as c

from simple_graph import *
from double_graph import *
from mutual_graph import *
from check_graph import *

### KOZOS HASZNALATU FUGGVENYEK
def make_graph(ORIG_TABLE, admins, shifts, SHIFT, DAYS):
    ### GRAFOK LETREHOZASA
    ### ### TABLAZATBA IRHATO JELEK CSOPORTOSITASA
    day_exception_current = {'x', 'X', 'y', 'Y', 'xn', 'xN', 'XN', 'Xn', 'nx', 'nX', 'Nx', 'NX', 'e', 'E', 'é', 'É'}
    day_exception_prev = {'e', 'E', 'é', 'É'}
    night_exception_current = {'x', 'X', 'y', 'Y', 'xe', 'xE', 'XE', 'Xe', 'ex', 'eX', 'Ex', 'EX', 'n', 'N',
                               'xé', 'xÉ', 'XÉ', 'Xé', 'éx', 'éX', 'Éx', 'ÉX'}
    night_exception_next = {'x', 'X', 'xn', 'xN', 'XN', 'Xn', 'nx', 'nX', 'Nx', 'NX', 'n', 'N'}

    ### ORIG_TABLE_REQ AZ ADOTT MUSZAKRA VONATKOZO KERESEKET TARTALMAZZA
    ### ### NEM LEHET NAPPALOS, HA AZNAP VAGY ELOTTE NAP EJSZAKAS
    ### ### NEM LEHET EJSZAKAS, HA AZNAP VAGY UTANA NAP NAPPALOS
    ORIG_TABLE_REQ = list(range(len(ORIG_TABLE)))
    if SHIFT == 'DAY':
        for row in range(len(ORIG_TABLE_REQ)):
            ORIG_TABLE_REQ[row] = [[1, 0] for j in range(DAYS)]
            for col in range(DAYS):
                if ORIG_TABLE[row][col + 3] in day_exception_current:
                    ORIG_TABLE_REQ[row][col][0] = 0
                if ORIG_TABLE[row][col + 3] in {'n', 'N'}:
                    ORIG_TABLE_REQ[row][col][1] = 4
                    admins[col].add(row)
                if ORIG_TABLE[row][col + 2] in day_exception_prev:
                    ORIG_TABLE_REQ[row][col][0] = 0
    if SHIFT == 'NIGHT':
        for i in range(len(ORIG_TABLE_REQ)):
            ORIG_TABLE_REQ[i] = [[1, 0] for j in range(DAYS)]
            for j in range(DAYS):
                if ORIG_TABLE[i][j + 3] in night_exception_current:
                    ORIG_TABLE_REQ[i][j][0] = 0
                if ORIG_TABLE[i][j + 3] in {'e', 'E'}:
                    ORIG_TABLE_REQ[i][j][1] = 4
                if j + 4 < len(ORIG_TABLE[0]):
                    if ORIG_TABLE[i][j + 4] in night_exception_next:
                        ORIG_TABLE_REQ[i][j][0] = 0

    ### ORIG_GRAPH AZ ADOTT MUSZAKNAK MEGFELELO GRAF
    ### AMIBEN MINDEN EMBER ANNYISZOR SZEREPEL MAR, AHANY MUSZAKJA VAN
    ### ### shifts A MUSZAKNAK MEGFELELO BEOSZTASSZAMOKAT TARTALMAZZA
    index = 0
    ORIG_GRAPH = list(range(sum(shifts)))
    for i in range(len(ORIG_TABLE_REQ)):
        for j in range(shifts[i]):
            ORIG_GRAPH[index] = c.deepcopy(ORIG_TABLE_REQ[i])
            index += 1

    ### ### FIX NAPOK BEIRASA/JAVITASA
    admin_index = 0
    for s in range(len(shifts)):
        serial_num = 0
        for col in range(len(ORIG_GRAPH[0])):
            if ORIG_GRAPH[admin_index][col][1] == 4:
                for row in range(admin_index, admin_index + shifts[s]):
                    if row != serial_num + admin_index:
                        ORIG_GRAPH[row][col][1] = 0
                serial_num += 1
        ### ### HA A LEGUTOLSO ADMINNAL 0 SZEREPEL MUSZAKSZAMNAK,
        ### ### AKKOR MAR NEM KELL NOVELNI, KULONBEN KIINDEXEL A GRAFBOL
        if s < len(shifts) - 1:
            if shifts[s + 1] != 0:
                admin_index += shifts[s]

    return ORIG_GRAPH

def graph_merge(graph_day, graph_night, day_shifts, night_shifts, admins, DAYS):
    ### VEGSO TABLAZAT, ELSO OSZLOPA AZ ADMINOK NEVEI
    final_table = [[admin] for admin in admins]
    for i in range(len(final_table)):
        final_table[i] += (list('' for j in range(DAYS)))

    ### NAPPALOS MUSZAKOK EGYBE IRASA
    for row in range(len(graph_day)):
        for col in range(len(graph_day[row])):
            if graph_day[row][col][1] in {1, 4}:
                final_table[whois(row, day_shifts)][col + 1] = 'N'

    ### EJSZAKAS MUSZAKOK EGYBE IRASA
    for row in range(len(graph_night)):
        for col in range(len(graph_night[row])):
            if graph_night[row][col][1] in {1, 4}:
                final_table[whois(row, night_shifts)][col + 1] = 'E'

    return final_table

def whois(row, shifts):
    s = 0
    for i in range(len(shifts)):
        s += shifts[i]
        if s > row:
            return i

