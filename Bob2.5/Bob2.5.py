# ============================================================
#  CHATBOT BOB 2.5  –  by X
#  Zmiany względem 2.4:
#   - Logika wydzielona do bob_core.py (importowana tu)
#   - Motywy zmieniają CAŁY tekst konsoli (nie tylko wiadomości Boba)
#   - Po /pl i /en odświeża ekran + wypisuje powitanie i komendy
#   - Każda komenda ma wersję PL i EN (np. /pogoda = /weather)
#   - Rozbudowany translator (~120 słów)
# ============================================================
import random
import string
import time
import datetime
import zoneinfo
import os
import sys

from bob_core import (
    BobState, MOTYWY, KOLORY_PROSTE, KOMENDY_HELP, POWITANIA,
    PYTANIA_QUIZ, CYTATY, BOB_FAKTY, SLOWNIK_PL_EN, SLOWNIK_EN_PL,
    SLOWA_WISIELEC, WISIELEC_RYSUNKI, EMOJI_MEMORY, OSIAGNIECIA_DEF,
    znajdz_odpowiedz, kalkulator, tlumacz, pogoda,
    losuj_quiz, sprawdz_quiz, losuj_fiszke, sprawdz_fiszke,
    pokaz_imgs, teach,
)

# ============================================================
#  STAN GLOBALNY
# ============================================================
state = BobState()


# ============================================================
#  HELPER KONSOLI
# ============================================================
def zastosuj_motyw_caly_terminal():
    """Wypisuje kod ANSI motywu tak, że cały terminal zmienia kolor."""
    sys.stdout.write(state.kolor_ansi)
    sys.stdout.flush()

def resetuj_kolor():
    sys.stdout.write("\033[0m")
    sys.stdout.flush()

def wyczysc_ekran():
    os.system("cls" if os.name == "nt" else "clear")

def wypisz_naglowek():
    wyczysc_ekran()
    zastosuj_motyw_caly_terminal()
    print(f"=== CHATBOT BOB 2.5  |  język: {'Polski 🇵🇱' if state.jezyk == 'pl' else 'English 🇬🇧'}  |  motyw: {state.motyw} ===")
    print(f"Bob: {state.powitanie()}\n")

def p(tekst):
    """Print z aktywnym motywem."""
    print(f"{state.kolor_ansi}{tekst}\033[0m")
    state.historia.append(tekst)

def echo(tekst):
    """Print BEZ zapisu do historii (pomocnicze)."""
    print(f"{state.kolor_ansi}{tekst}\033[0m")

def pokaz_osiagniecia(nowe):
    for n in nowe:
        echo(f"\n🏆 OSIĄGNIĘCIE ODBLOKOWANE: {n}\n")


# ============================================================
#  MINI-GRY  (konsola)
# ============================================================
def gra_wisielec():
    slowo     = random.choice(SLOWA_WISIELEC)
    odkryte   = set()
    bledne    = []
    max_bl    = len(WISIELEC_RYSUNKI) - 1

    echo("\nProgram: 🎮 WISIELEC! Odgadnij słowo." if state.jezyk == "pl"
         else "\nProgram: 🎮 HANGMAN! Guess the word.")

    while True:
        wyswietl  = " ".join(c if c in odkryte else "_" for c in slowo)
        bledy_str = ", ".join(bledne) if bledne else "-"
        echo(WISIELEC_RYSUNKI[len(bledne)])
        echo(f"\n  Słowo:  {wyswietl}" if state.jezyk == "pl" else f"\n  Word:  {wyswietl}")
        echo(f"  Błędne: {bledy_str}   Prób zostało: {max_bl - len(bledne)}\n" if state.jezyk == "pl"
             else f"  Wrong:  {bledy_str}   Tries left: {max_bl - len(bledne)}\n")

        if set(slowo) <= odkryte:
            nowe = state.dodaj_punkty(10)
            echo(f"Program: 🎉 Wygrałeś! Słowo: '{slowo}'  (+10 pkt, łącznie: {state.punkty})" if state.jezyk == "pl"
                 else f"Program: 🎉 You won! Word: '{slowo}'  (+10 pts, total: {state.punkty})")
            pokaz_osiagniecia(nowe)
            break

        if len(bledne) >= max_bl:
            echo(WISIELEC_RYSUNKI[-1])
            echo(f"Program: 💀 Przegrałeś! Słowo: '{slowo}'" if state.jezyk == "pl"
                 else f"Program: 💀 You lost! Word: '{slowo}'")
            break

        odp = input("Podaj literę: " if state.jezyk == "pl" else "Enter a letter: ").strip().lower()
        state.historia.append(f"Ty: {odp}")
        if len(odp) != 1 or not odp.isalpha():
            echo("Program: Podaj jedną literę!" if state.jezyk == "pl" else "Program: One letter!")
            continue
        if odp in odkryte or odp in bledne:
            echo("Program: Już podałeś tę literę!" if state.jezyk == "pl" else "Program: Already guessed!")
            continue
        if odp in slowo:
            odkryte.add(odp)
            echo("Program: ✓ Dobra litera!" if state.jezyk == "pl" else "Program: ✓ Good letter!")
        else:
            bledne.append(odp)
            echo("Program: ✗ Nie ma takiej litery." if state.jezyk == "pl" else "Program: ✗ No such letter.")


def gra_kolko():
    plansza = [" "] * 9

    def rysuj():
        r = plansza
        echo(f"\n  {r[0]} | {r[1]} | {r[2]}")
        echo("  ---------")
        echo(f"  {r[3]} | {r[4]} | {r[5]}")
        echo("  ---------")
        echo(f"  {r[6]} | {r[7]} | {r[8]}")
        echo("  (1-9)\n")

    def wygral(z):
        return any(plansza[a] == plansza[b] == plansza[c] == z
                   for a, b, c in [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)])

    echo("\nProgram: 🎮 KÓŁKO I KRZYŻYK! Ty = X, Bob = O." if state.jezyk == "pl"
         else "\nProgram: 🎮 TIC-TAC-TOE! You = X, Bob = O.")

    for tura in range(9):
        rysuj()
        if tura % 2 == 0:
            while True:
                odp = input("Ty (1-9): " if state.jezyk == "pl" else "You (1-9): ").strip()
                state.historia.append(f"Ty: {odp}")
                try:
                    pole = int(odp) - 1
                    if 0 <= pole <= 8 and plansza[pole] == " ":
                        plansza[pole] = "X"; break
                    echo("Program: Pole zajęte!" if state.jezyk == "pl" else "Program: Field taken!")
                except ValueError:
                    echo("Program: Podaj 1-9!" if state.jezyk == "pl" else "Program: Enter 1-9!")
            if wygral("X"):
                rysuj(); echo("Program: 🎉 Wygrałeś!" if state.jezyk == "pl" else "Program: 🎉 You won!"); return
        else:
            wolne = [i for i, x in enumerate(plansza) if x == " "]
            ruch = None
            for znak in ["O", "X"]:
                for i in wolne:
                    plansza[i] = znak
                    if wygral(znak): plansza[i] = " "; ruch = i; break
                    plansza[i] = " "
                if ruch is not None: break
            if ruch is None and 4 in wolne: ruch = 4
            if ruch is None: ruch = random.choice(wolne)
            plansza[ruch] = "O"
            echo(f"Program: Bob → pole {ruch+1}." if state.jezyk == "pl" else f"Program: Bob → field {ruch+1}.")
            if wygral("O"):
                rysuj(); echo("Program: 😏 Bob wygrał!" if state.jezyk == "pl" else "Program: 😏 Bob won!"); return

    rysuj()
    echo("Program: 🤝 Remis!" if state.jezyk == "pl" else "Program: 🤝 Draw!")


def gra_memory():
    karty      = EMOJI_MEMORY * 2
    random.shuffle(karty)
    dopasowane = [False] * 16
    ruchy      = 0

    def rysuj():
        echo("")
        for i in range(16):
            if dopasowane[i]:
                print(f" {karty[i]} ", end="")
            else:
                print(f" {i+1:2} ", end="")
            if (i + 1) % 4 == 0: print()
        echo("")

    echo("\nProgram: 🎮 MEMORY! Znajdź pary 4×4 (podaj dwa numery, np. 3 7)." if state.jezyk == "pl"
         else "\nProgram: 🎮 MEMORY! Find pairs 4×4 (enter two numbers, e.g. 3 7).")

    odkryte_tmp = {}
    while not all(dopasowane):
        rysuj()
        odp = input("Ty (dwie liczby): " if state.jezyk == "pl" else "You (two numbers): ").strip()
        state.historia.append(f"Ty: {odp}")
        try:
            a, b = map(int, odp.split())
            a -= 1; b -= 1
            if not (0 <= a <= 15 and 0 <= b <= 15) or a == b: raise ValueError
            if dopasowane[a] or dopasowane[b]:
                echo("Program: Ta karta już sparowana!" if state.jezyk == "pl" else "Program: Already matched!")
                continue
        except (ValueError, TypeError):
            echo("Program: Użyj np.: 3 7" if state.jezyk == "pl" else "Program: Use e.g.: 3 7")
            continue

        ruchy += 1
        # pokaż obie karty chwilowo
        echo(f"  [{a+1}]={karty[a]}   [{b+1}]={karty[b]}")
        if karty[a] == karty[b]:
            dopasowane[a] = dopasowane[b] = True
            echo("Program: ✓ Para!" if state.jezyk == "pl" else "Program: ✓ Match!")
        else:
            echo("Program: ✗ Nie pasuje." if state.jezyk == "pl" else "Program: ✗ No match.")

    bonus = max(0, 50 - ruchy * 2)
    nowe = state.dodaj_punkty(bonus)
    echo(f"\nProgram: 🎉 Ukończono w {ruchy} ruchach! (+{bonus} pkt, łącznie: {state.punkty})" if state.jezyk == "pl"
         else f"\nProgram: 🎉 Finished in {ruchy} moves! (+{bonus} pts, total: {state.punkty})")
    pokaz_osiagniecia(nowe)


def gra_quiz():
    q = losuj_quiz(state)
    if state.jezyk == "pl":
        echo(f"\nProgram: QUIZ! {q['pl']}")
        echo(f"Program: (podpowiedź: {q['hint_pl']})")
    else:
        echo(f"\nProgram: QUIZ! {q['en']}")
        echo(f"Program: (hint: {q['hint_en']})")
    odp = input("Ty: ").lower().strip()
    state.historia.append(f"Ty: {odp}")
    _, msg, nowe = sprawdz_quiz(q, odp, state)
    echo(f"Program: {msg}")
    pokaz_osiagniecia(nowe)


def gra_fiszka():
    zrod, cel, pytanie = losuj_fiszke(state)
    echo(f"\nProgram: FISZKA! {pytanie}" if state.jezyk == "pl" else f"\nProgram: FLASHCARD! {pytanie}")
    odp = input("Ty: ").strip().lower()
    state.historia.append(f"Ty: {odp}")
    _, msg, nowe = sprawdz_fiszke(zrod, cel, odp, state)
    echo(f"Program: {msg}")
    pokaz_osiagniecia(nowe)


def gra_zgadnij():
    echo("Program: Myślę o liczbie od 1 do 100. Zgadnij!" if state.jezyk == "pl"
         else "Program: I'm thinking of a number from 1 to 100. Guess!")
    liczba = random.randint(1, 100)
    proby  = 0
    while True:
        odp = input("Ty: ").strip()
        state.historia.append(f"Ty: {odp}")
        proby += 1
        try:
            g = int(odp)
            if g < liczba:
                echo("Program: Za mało!" if state.jezyk == "pl" else "Program: Too low!")
            elif g > liczba:
                echo("Program: Za dużo!" if state.jezyk == "pl" else "Program: Too high!")
            else:
                bonus = max(1, 10 - proby)
                nowe = state.dodaj_punkty(bonus)
                echo(f"Program: Brawo! {proby} prób.  (+{bonus} pkt, łącznie: {state.punkty})" if state.jezyk == "pl"
                     else f"Program: Well done! {proby} tries.  (+{bonus} pts, total: {state.punkty})")
                pokaz_osiagniecia(nowe)
                break
        except ValueError:
            echo("Program: Podaj liczbę!" if state.jezyk == "pl" else "Program: Enter a number!")


# ============================================================
#  STARTUP
# ============================================================
zastosuj_motyw_caly_terminal()
print("=== CHATBOT BOB 2.5 ===")
print(KOMENDY_HELP[state.jezyk])
print(f"\nBob: {state.powitanie()}\n")


# ============================================================
#  GŁÓWNA PĘTLA
# ============================================================
while True:
    try:
        wejscie = input("Ty: ")
    except (EOFError, KeyboardInterrupt):
        echo("\nProgram: Do zobaczenia!" if state.jezyk == "pl" else "\nProgram: Goodbye!")
        resetuj_kolor()
        break

    pytanie = wejscie.lower().strip()
    state.historia.append(f"Ty: {pytanie}")
    state.licznik += 1

    # --- wyjście ---
    if pytanie in ("koniec", "end"):
        echo(f"Program: Do zobaczenia! Wysłano {state.licznik} wiadomości." if state.jezyk == "pl"
             else f"Program: Goodbye! You sent {state.licznik} messages.")
        resetuj_kolor()
        break

    # --- zmiana języka (odświeża ekran) ---
    if pytanie == "/pl":
        state.jezyk = "pl"
        wypisz_naglowek()
        print(KOMENDY_HELP["pl"])
        print()
        continue

    if pytanie == "/en":
        state.jezyk = "en"
        wypisz_naglowek()
        print(KOMENDY_HELP["en"])
        print()
        continue

    # --- motyw ---
    if pytanie.startswith("/motyw") or pytanie.startswith("/theme"):
        nazwa = pytanie.replace("/motyw", "").replace("/theme", "").strip()
        if nazwa in MOTYWY:
            state.motyw = nazwa
            zastosuj_motyw_caly_terminal()
            echo(f"Program: Motyw '{nazwa}' ustawiony — cały terminal zmieniony!" if state.jezyk == "pl"
                 else f"Program: Theme '{nazwa}' applied — full terminal changed!")
        else:
            lista = ", ".join(MOTYWY.keys())
            echo(f"Program: Nieznany motyw. Dostępne: {lista}" if state.jezyk == "pl"
                 else f"Program: Unknown theme. Available: {lista}")
        continue

    # --- kolory proste ---
    if pytanie == "/rainbow":
        state.motyw = random.choice([k for k in MOTYWY if k != "default"])
        zastosuj_motyw_caly_terminal()
        echo("Program: Losowy motyw!" if state.jezyk == "pl" else "Program: Random theme!")
        continue

    if pytanie in KOLORY_PROSTE:
        ansi, _ = KOLORY_PROSTE[pytanie]
        sys.stdout.write(ansi); sys.stdout.flush()
        continue

    # --- help ---
    if pytanie in ("/help", "/pomoc"):
        echo(KOMENDY_HELP[state.jezyk])
        continue

    # --- historia ---
    if pytanie in ("/historia", "/history"):
        echo("\n--- Historia ---")
        for h in state.historia:
            echo(h)
        echo("----------------\n")
        continue

    # --- clear ---
    if pytanie == "/clear":
        state.historia.clear()
        echo("Program: Historia wyczyszczona!" if state.jezyk == "pl" else "Program: History cleared!")
        continue

    # --- imgs ---
    if pytanie == "/imgs":
        echo(pokaz_imgs(state))
        continue

    # --- stats ---
    if pytanie in ("/stats", "/statystyki"):
        echo(f"Program: Wysłano {state.licznik} wiadomości." if state.jezyk == "pl"
             else f"Program: {state.licznik} messages sent.")
        continue

    # --- kalkulator ---
    if pytanie.startswith("/calc"):
        wyr = pytanie.replace("/calc", "").strip()
        echo(f"Program: {kalkulator(wyr, state)}" if wyr
             else ("Program: Użyj: /calc 2+2" if state.jezyk == "pl" else "Program: Use: /calc 2+2"))
        continue

    # --- czas / time ---
    if pytanie in ("/czas", "/time"):
        strefa = zoneinfo.ZoneInfo("Europe/Warsaw")
        teraz  = datetime.datetime.now(strefa)
        if state.jezyk == "pl":
            p(f"Program: Teraz jest {teraz.strftime('%H:%M:%S, %d.%m.%Y')} (czas warszawski)")
        else:
            p(f"Program: Current time is {teraz.strftime('%H:%M:%S, %Y-%m-%d')} (Warsaw time)")
        continue

    # --- pogoda / weather ---
    if pytanie.startswith("/pogoda") or pytanie.startswith("/weather"):
        miasto = pytanie.replace("/pogoda", "").replace("/weather", "").strip()
        if miasto:
            echo(f"Program: {pogoda(miasto, state)}")
        else:
            echo("Program: Użyj: /pogoda Warszawa" if state.jezyk == "pl"
                 else "Program: Use: /weather London")
        continue

    # --- quiz ---
    if pytanie in ("/quiz"):
        gra_quiz()
        continue

    # --- fiszka / flashcard ---
    if pytanie in ("/fiszka", "/flashcard"):
        gra_fiszka()
        continue

    # --- zgadnij / guess ---
    if pytanie in ("/zgadnij", "/guess"):
        gra_zgadnij()
        continue

    # --- wisielec / hangman ---
    if pytanie in ("/wisielec", "/hangman"):
        gra_wisielec()
        continue

    # --- kółko / tictactoe ---
    if pytanie in ("/kolko", "/tictactoe"):
        gra_kolko()
        continue

    # --- memory ---
    if pytanie == "/memory":
        gra_memory()
        continue

    # --- punkty / points ---
    if pytanie in ("/punkty", "/points"):
        p(f"Program: 🏅 Twoje punkty: {state.punkty}" if state.jezyk == "pl"
          else f"Program: 🏅 Your points: {state.punkty}")
        continue

    # --- osiągnięcia / achievements ---
    if pytanie in ("/osiagniecia", "/achievements"):
        if state.osiagniecia:
            echo("Program: 🏆 Twoje osiągnięcia:" if state.jezyk == "pl" else "Program: 🏆 Your achievements:")
            for aid in state.osiagniecia:
                for a in OSIAGNIECIA_DEF:
                    if a["id"] == aid:
                        echo(f"  ✓ {a['pl'] if state.jezyk == 'pl' else a['en']}")
        else:
            echo("Program: Brak osiągnięć – graj, żeby zdobywać punkty!" if state.jezyk == "pl"
                 else "Program: No achievements yet – play to earn points!")
        continue

    # --- hasło / password ---
    if pytanie in ("/haslo", "/password"):
        znaki = string.ascii_letters + string.digits + "!@#$%&*"
        haslo = "".join(random.choices(znaki, k=16))
        p(f"Program: 🔐 Twoje hasło: {haslo}" if state.jezyk == "pl"
          else f"Program: 🔐 Your password: {haslo}")
        continue

    # --- tłumacz / translate ---
    if pytanie.startswith("/tlumacz") or pytanie.startswith("/translate"):
        slowo = pytanie.replace("/tlumacz", "").replace("/translate", "").strip()
        echo(f"Program: {tlumacz(slowo, state)}" if slowo
             else ("Program: Użyj: /tlumacz kot" if state.jezyk == "pl"
                   else "Program: Use: /translate cat"))
        continue

    # --- rzut / roll ---
    if pytanie.startswith("/rzut") or pytanie.startswith("/roll"):
        arg = pytanie.replace("/rzut", "").replace("/roll", "").strip()
        try:
            s = int(arg) if arg else 6
            if s < 2: raise ValueError
            w = random.randint(1, s)
            p(f"Program: 🎲 K{s} → {w}" if state.jezyk == "pl" else f"Program: 🎲 D{s} → {w}")
        except ValueError:
            echo("Program: /rzut [N]" if state.jezyk == "pl" else "Program: /roll [N]")
        continue

    # --- odliczaj / countdown ---
    if pytanie.startswith("/odliczaj") or pytanie.startswith("/countdown"):
        arg = pytanie.replace("/odliczaj", "").replace("/countdown", "").strip()
        try:
            n = int(arg)
            if not 1 <= n <= 100: raise ValueError
            for i in range(n, -1, -1):
                echo(f"  {i}{'...' if i > 0 else ' 🚀 Start!'}")
        except ValueError:
            echo("Program: /odliczaj N (1-100)" if state.jezyk == "pl" else "Program: /countdown N (1-100)")
        continue

    # --- lotto ---
    if pytanie == "/lotto":
        liczby = sorted(random.sample(range(1, 50), 6))
        wynik  = "  ".join(f"{n:2}" for n in liczby)
        p(f"Program: 🎲 Lotto: [ {wynik} ]")
        continue

    # --- losuj / pick ---
    if pytanie.startswith("/losuj") or pytanie.startswith("/pick"):
        arg = pytanie.replace("/losuj", "").replace("/pick", "").strip()
        if arg:
            el = [e.strip() for e in arg.split(",") if e.strip()]
            p(f"Program: 🎯 {random.choice(el)}" if el
              else ("Program: Lista pusta!" if state.jezyk == "pl" else "Program: Empty list!"))
        else:
            echo("Program: /losuj a,b,c" if state.jezyk == "pl" else "Program: /pick a,b,c")
        continue

    # --- anagram ---
    if pytanie.startswith("/anagram"):
        slowo = pytanie.replace("/anagram", "").strip()
        if slowo:
            l = list(slowo); random.shuffle(l)
            p(f"Program: 🔤 {slowo} → {''.join(l)}")
        else:
            echo("Program: /anagram słowo" if state.jezyk == "pl" else "Program: /anagram word")
        continue

    # --- stoper / stopwatch ---
    if pytanie in ("/stoper", "/stopwatch"):
        echo("Program: ⏱️ Start! Naciśnij Enter..." if state.jezyk == "pl"
             else "Program: ⏱️ Started! Press Enter...")
        t0 = time.time()
        input()
        el = time.time() - t0
        p(f"Program: Czas: {el:.2f}s" if state.jezyk == "pl" else f"Program: Time: {el:.2f}s")
        continue

    # --- cytat / quote ---
    if pytanie in ("/cytat", "/quote"):
        p(f"Program: 💬 {random.choice(CYTATY[state.jezyk])}")
        continue

    # --- memo ---
    if pytanie.startswith("/memo"):
        arg = pytanie.replace("/memo", "").strip()
        if not arg or arg in ("pokaz", "show"):
            if state.memo:
                echo("Program: Notatki:" if state.jezyk == "pl" else "Program: Notes:")
                for i, n in enumerate(state.memo, 1):
                    echo(f"  {i}. {n}")
            else:
                echo("Program: Brak notatek." if state.jezyk == "pl" else "Program: No notes.")
        elif arg.startswith("usun ") or arg.startswith("delete "):
            try:
                idx = int(arg.split()[1]) - 1
                u = state.memo.pop(idx)
                echo(f"Program: Usunięto: {u}" if state.jezyk == "pl" else f"Program: Deleted: {u}")
            except (ValueError, IndexError):
                echo("Program: /memo usun N" if state.jezyk == "pl" else "Program: /memo delete N")
        else:
            state.memo.append(arg)
            echo(f"Program: Zapisano #{len(state.memo)}!" if state.jezyk == "pl"
                 else f"Program: Saved #{len(state.memo)}!")
        continue

    # --- bob ---
    if pytanie == "/bob":
        p(f"Program: {random.choice(BOB_FAKTY[state.jezyk])}")
        continue

    # --- teach ---
    if pytanie.startswith("/teach"):
        dane = pytanie.replace("/teach", "").strip()
        echo(f"Program: {teach(dane, state)}")
        continue

    # --- szukanie w bazie ---
    odp = znajdz_odpowiedz(pytanie, state)
    if odp:
        p(f"Program: {odp}")
    else:
        p("Program: Nie znam odpowiedzi." if state.jezyk == "pl" else "Program: I don't know.")
