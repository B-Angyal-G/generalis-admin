from os import system, name
import random
import copy as c

from simple_graph import *
from double_graph import *
from mutual_graph import *
from check_graph import *

### DOUBLE GRAF (NAPPALOS MUSZAKOK) GENERALASA
def graph_bipart_double_init(G, shifts, admins):
    for row in range(len(G)):
        SKIP = 0
        tmp = list()
        for col in range(len(G[0])):
            if G[row][col][1] in {1, 4}:
                SKIP = 1
                admins[col].add(whois(row, shifts))
            if len(admins[col]) < 2 and G[row][col] == [1, 0]:
                if whois(row, shifts) not in admins[col]:
                    tmp.append(col)
        if not SKIP:
            if len(tmp) != 0:
                day = random.choice(tmp)
                G[row][day][1] = 1
                admins[day].add(whois(row, shifts))

def hun_repair_double_init(G, A, B, shifts, admins):
    ### MAS MINT A SIMPLE ESET, MERT A KIMARADT 0-AS INDEXU CSUCSOKBOL
    ### OLYAN CSUCSBA NEM HUZHATUNK ELT, AMELYIKKEL OSSZE VAN KOTVE OLYAN EL,
    ### AMELYIK UGYANAHHOZ AZ ADMINHOZ TARTOZIK, VAGYIS WHOIS() BENNE VAN ADMINS-BAN
    OK = 0
    ### 0-AS INDEXU CSUCSOK KIJELOLESE
    for i in range(len(G)):
        if sum(item[1] for item in G[i]) == 0:
            A[i] = 0
            OK = 1

    ### 1-ES INDEXU CSUCSOK KIJELOLESE (MEG NEM LEHET JAVITO UT!)
    if OK:
        OK = 0
        for row in range(len(A)):
            if A[row] == 0:
                for col in range(len(G[0])):
                    if G[row][col] == [1, 0] and B[col] == -1 and whois(row, shifts) not in admins[col]:
                        B[col] = 1
                        OK = 1
    if OK:
        return 1
    else:
        return 0

def hun_repair_double(G, shifts, admins):
    A = list(-1 for i in range(len(G)))
    B = list(-1 for i in range(len(G[0])))

    ### UA MINT SIMPLE ESETBEN
    OK = hun_repair_double_init(G, A, B, shifts, admins)
    enum = 1
    FIND = 0

    ### MINDEN 2. LEPES UTAN VIZSGALUNK
    while OK:
        enum += 1
        OK = 0
        for j in range(len(B)):
            if B[j] == enum - 1:
                for i in range(len(G)):
                    ### VAN EL ES MEG NEM JELOLTUK MEG A HOZZA TARTOZO CSUCSOT
                    if G[i][j] == [1, 1] and A[i] == -1:
                        A[i] = enum
                        OK = 1

        if OK:
            enum += 1
            OK = 0
            for row in range(len(A)):
                if A[row] == enum - 1:
                    for col in range(len(G[0])):
                        ### VAN EL ES MEG NEM JELOLTUK MEG A HOZZA TARTOZO CSUCSOT
                        if G[row][col] == [1, 0] and B[col] == -1:
                            B[col] = enum
                            OK = 1

                            ### VIZSGALAT, HOGY VEGE LESZ-E AZ ALGORITMUSNAK
                            FIND = 0
                            s_edge = 0
                            for k in range(len(G)):
                                if G[k][col] == [1, 1] or G[k][col] == [1, 4]:
                                    s_edge += 1
                            if s_edge < 2:
                                FIND = 1
                                last = col
                                break
                    if FIND:
                        break

        ### LEALLAS
        if FIND == 1:
            break

    ### JAVITAS VEGREHAJTASA
    ### ### MIVEL PARATLAN SOK ELET KELL ATIRNI,
    ### ### EZERT AZ ELSOT KIVUL, MAJD WHILE CILUSBAN 2-ESEVEL
    ### ### ATIRANDO EL MEGTALALASA A TOMB SEGITSEGEVEL TORTENIK
    if FIND:
        enum -= 1
        for i in range(len(A)):
            if G[i][last] == [1, 0] and A[i] == enum:
                G[i][last][1] = 2
                last = i
                break

        while enum > 0:
            ### GRAF MATRIXABAN VIZSZINTESEN CSAK 1 EL LEHET KIVALASZTVA, AZT ATIRJUK
            for j in range(len(G[last])):
                if G[last][j] == [1, 1]:
                    G[last][j][1] = 0
                    last_new = j
                elif G[last][j] == [1, 2]:
                    G[last][j][1] = 1
            last = last_new

            ### AZ ELOBB MEGTALALT EL OSZLOPABAN MEGKERESSUK A JAVITOELT A TOMB SEGITSEGEVEL
            enum -= 2
            for i in range(len(A)):
                if G[i][last] == [1, 0] and A[i] == enum:
                    G[i][last][1] = 2
                    last = i
                    break

        for i in range(len(G[last])):
            if G[last][i] == [1, 2]:
                G[last][i][1] = 1
        return 1

    return 0

def graph_double_max_match(G, shifts, admins):
    graph_bipart_double_init(G, shifts, admins)
    while hun_repair_double(G, shifts, admins):
        pass

