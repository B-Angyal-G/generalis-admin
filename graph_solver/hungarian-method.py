import random 
import copy as c


def graph_bipart_init (G, RANDOM):
    if RANDOM:
        for i in range(len(G)):
            if sum(item[1] for item in G[i]) == 0:
                tmp = list()
                for j in range(len(G[i])):
                    if G[i][j] == [1, 0] and sum(rows[j][1] for rows in G) == 0:
                        tmp.append(j)
                if len(tmp) > 0:
                    rand_item = random.choice(tmp)
                    G[i][rand_item][1] = 1
    else:
        for i in range(len(G)):
            if sum(item[1] for item in G[i]) == 0:
                for j in range(len(G[i])):
                    if G[i][j] == [1, 0] and sum(rows[j][1] for rows in G) == 0:
                        G[i][j][1] = 1
                        break


def hun_repair_init (G, A, B):
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


def hun_repair (G):
    A = list(-1 for i in range(len(G)))
    B = list(-1 for i in range(len(G[0])))

    OK = hun_repair_init(G, A, B)
    enum = 1
    FIND = 0

    ### MINDEN 2. LEPES UTAN VIZSGALUNK
    while OK:
        enum += 1
        OK = 0
        for j in range(len(B)):
            if B[j] == enum - 1:
                for i in range(len(G)):
                    if G[i][j] == [1, 1] and A[i] == -1:
                        A[i] = enum
                        OK = 1

        if OK:
            enum += 1
            OK = 0
            for i in range(len(A)):
                if A[i] == enum - 1:
                    for j in range(len(G[0])):
                        if G[i][j] == [1, 0] and B[j] == -1:
                            B[j] = enum
                            OK = 1

                            ### VIZSGALAT, HOGY VEGE LESZ-E AZ ALGORITMUSNAK
                            FIND = 1
                            for k in range(len(G)):
                                if G[k][j] == [1,1]:
                                    FIND = 0
                                    break
                            if FIND == 1:
                                last = j
        
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


def graph_max_match (G, RANDOM):
    graph_bipart_init(G, RANDOM)
    print("INIT")
    for i in G:
        print(i)
    print()
    while hun_repair(G):
        pass


def main():
    # # SOR OSSZEG
    # s = sum(item[0] for item in G[0])
    # # OSZLOP OSSZEG
    # s = sum(row[3][0] for row in G)
    # print(s)
    
    # G = [[[0, 0], [1, 0], [0, 0], [0, 0], [0, 0], [1, 0]],
    #      [[0, 0], [1, 0], [0, 0], [0, 0], [0, 0], [1, 0]],
    #      [[0, 0], [0, 0], [1, 0], [0, 0], [1, 0], [0, 0]],
    #      [[1, 0], [1, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
    #      [[0, 0], [0, 0], [0, 0], [1, 0], [1, 0], [0, 0]],
    #      [[1, 0], [0, 0], [0, 0], [1, 0], [0, 0], [0, 0]]]

    # WALDHAUSER 1
    # G = [[[0, 0], [1, 0], [0, 0], [0, 0], [0, 0]],
    #      [[1, 0], [1, 0], [1, 0], [0, 0], [0, 0]],
    #      [[0, 0], [0, 0], [1, 0], [1, 0], [0, 0]],
    #      [[0, 0], [0, 0], [0, 0], [1, 0], [1, 0]],
    #      [[0, 0], [1, 0], [0, 0], [0, 0], [0, 0]]]

    # WALDHAUSER 2
    # G = [[[1, 0], [0, 0], [0, 0], [0, 0]],
    #      [[1, 0], [1, 0], [0, 0], [0, 0]],
    #      [[0, 0], [1, 0], [0, 0], [0, 0]],
    #      [[0, 0], [1, 0], [1, 0], [1, 0]]]

    # WALDHAUSER 3
    G = [[[0, 0], [1, 1], [0, 0], [0, 0], [0, 0], [1, 0]], 
         [[0, 0], [1, 0], [0, 0], [0, 0], [0, 0], [1, 0]], 
         [[0, 0], [0, 0], [1, 0], [0, 0], [1, 0], [0, 0]], 
         [[1, 0], [1, 0], [0, 0], [0, 0], [0, 0], [0, 0]], 
         [[0, 0], [0, 0], [0, 0], [1, 0], [1, 0], [0, 0]], 
         [[1, 0], [0, 0], [0, 0], [1, 0], [0, 0], [0, 0]]] 


    G_work = c.deepcopy(G)
    summ_set = set()
    for i in range(10):
        print(i, "Kezdes")
        tmp = list()
        graph_max_match(G_work, 1)
        for i in range(len(G_work)):
            for j in range(len(G_work[i])):
                if G_work[i][j] == [1, 1]:
                    tmp.append(j)
                    G_work[i][j][1] = 0
                    break
        tmp = tuple(tmp)
        summ_set.add(tmp)
        for i in G_work:
            print(i)
        print(tmp)
        print()
        G_work = c.deepcopy(G)
    print(summ_set)
    print(len(summ_set))



main()
