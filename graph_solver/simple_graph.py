from os import system, name
import random
import copy as c

from simple_graph import *
from double_graph import *
from mutual_graph import *
from check_graph import *

### SIMPLE GRAF (EJJELES MUSZAKOK) GENERALASA
def graph_bipart_init(G):
    for i in range(len(G)):
        if sum(item[1] for item in G[i]) == 0:
            tmp = list()
            for j in range(len(G[i])):
                if G[i][j] == [1, 0] and sum(rows[j][1] for rows in G) == 0:
                    tmp.append(j)
            if len(tmp) > 0:
                rand_item = random.choice(tmp)
                G[i][rand_item][1] = 1

def hun_repair_init(G, A, B):
    ### UA SIMPLE ES DOUBLE ESETEKBEN
    OK = 0
    ### 0-AS INDEXU CSUCSOK KIJELOLESE
    for i in range(len(G)):
        if sum(item[1] for item in G[i]) == 0:
            A[i] = 0
            OK = 1

    ### 1-ES INDEXU CSUCSOK KIJELOLESE (MEG NEM LEHET JAVITO UT!)
    if OK:
        OK = 0
        for i in range(len(A)):
            if A[i] == 0:
                for j in range(len(G[0])):
                    if G[i][j] == [1, 0] and B[j] == -1:
                        B[j] = 1
                        OK = 1
    if OK:
        return 1
    else:
        return 0

def hun_repair(G):
    A = list(-1 for i in range(len(G)))
    B = list(-1 for i in range(len(G[0])))

    OK = hun_repair_init(G, A, B)
    IFEND = OK
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
            for i in range(len(A)):
                if A[i] == enum - 1:
                    for j in range(len(G[0])):
                        ### VAN EL ES MEG NEM JELOLTUK MEG A HOZZA TARTOZO CSUCSOT
                        if G[i][j] == [1, 0] and B[j] == -1:
                            B[j] = enum
                            OK = 1

                            ### VIZSGALAT, HOGY VEGE LESZ-E AZ ALGORITMUSNAK
                            FIND = 1
                            for k in range(len(G)):
                                if G[k][j] == [1, 1] or G[k][j] == [1, 4]:
                                    FIND = 0
                                    break
                            if FIND == 1:
                                last = j
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

    if IFEND:
        return -1
    else:
        return 0

def graph_max_match(G):
    graph_bipart_init(G)
    REPAIR = hun_repair(G)
    while REPAIR == 1:
        REPAIR = hun_repair(G)
    if REPAIR == -1:
        return 0
    return 1
