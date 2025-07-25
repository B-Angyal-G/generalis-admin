# Generalis-admin
Beosztásgeneráló SBO adminisztrátoroknak.

Szükséges az openpyxl könyvtár telepítése pythonhoz:
1. pip install openpyxl
2. IDE saját rendszerén belül


Rövid ismertető XLSX kérések megadásához:
1. x  : adott napon sem nappalos, sem éjszakás, sem lelépős nem lehet
2. y  : adott napon sem nappalos, sem éjszakás nem lehet
3. nx : adott napon nem lehet nappalos, sem lelépős
4. ex : adott napon nem lehet éjszakás

Kérések megadásánál kis- és nagy betű nem számít, továbbá 'e'-t és 'é'-t is lehet írni. Valamint 'nx' helyett 'xn'-et is, ugyanígy éjszakáshoz.

Legfontosabb mező, hogy az adott hónap hány napos, valamint, hogy kinek mennyi nappalos illetve éjszakás műszakja legyen (lehet 0 is).
Szükséges még az első szombat megadása, mert beleszámít az értékelésbe.
Fehér C1 és C2 mezőben csak az ellenőrzést megkönnyítő számadatok vannak, melyek a nappalos ill. éjszakás műszakok összegét tartalmazzák. A program nem veszi őket figyelembe.

A generálás algoritmusa garantálja, hogy mindig egy érvényes beosztást kapjunk a végén, vagyis megfelelő gráfpárosítást. Viszont van egy olyan szabály, hogy 3 egyforma műszak nem követheti egymást, valamint 4 vagy annál több műszak semmilyen kombinációban sem lehet folyamatosan megadva. A program ezeknek a feltételeknek a teljesülését a végzett generálás után vizsgálja csak meg, ami azt eredményezi, hogy addig nem fogadja el a generálást, amíg ezeknek a feltételeknek meg nem felel. Emiatt stochasztikusan következik be sikeres generálás. A program default beállításában 3 érvényes generálás közül válaztja ki a legjobbat a megírt értékelőfüggvénynek megfelelően.
