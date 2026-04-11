# ============================================================
#  BOB GUI  –  graficzny interfejs chatbota Bob
#  Wymaga: Python 3.10+, tkinter (wbudowany), bob_core.py
#  Uruchomienie:  python bob_gui.py
# ============================================================
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import random
import string
import threading
import time
import datetime
import zoneinfo
import sys
import os

# Dodaj folder skryptu do path (żeby znalazł bob_core)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bob_core import (
    BobState, MOTYWY, KOLORY_PROSTE, KOMENDY_HELP, POWITANIA,
    PYTANIA_QUIZ, CYTATY, BOB_FAKTY, SLOWNIK_PL_EN, SLOWNIK_EN_PL,
    SLOWA_WISIELEC, WISIELEC_RYSUNKI, EMOJI_MEMORY, OSIAGNIECIA_DEF,
    znajdz_odpowiedz, kalkulator, tlumacz, pogoda,
    losuj_quiz, sprawdz_quiz, losuj_fiszke, sprawdz_fiszke,
    pokaz_imgs, teach,
)


# ============================================================
#  PALETY KOLORÓW DLA GUI (każdy motyw: bg, fg, input_bg, btn)
# ============================================================
PALETY = {
    "default": {"bg": "#1e1e1e", "fg": "#00ff00", "ibg": "#2a2a2a", "btn": "#333333", "hl": "#00ff00"},
    "matrix":  {"bg": "#0d0d0d", "fg": "#00ff41", "ibg": "#111111", "btn": "#003300", "hl": "#00ff41"},
    "ocean":   {"bg": "#001a2e", "fg": "#00e5ff", "ibg": "#002040", "btn": "#003355", "hl": "#00e5ff"},
    "sunset":  {"bg": "#1a0a00", "fg": "#ff6b35", "ibg": "#2a1000", "btn": "#441800", "hl": "#ff6b35"},
    "blood":   {"bg": "#110000", "fg": "#cc2200", "ibg": "#1a0000", "btn": "#330000", "hl": "#cc2200"},
    "candy":   {"bg": "#1a001a", "fg": "#ff79c6", "ibg": "#280028", "btn": "#440044", "hl": "#ff79c6"},
    "snow":    {"bg": "#1a1a2e", "fg": "#e8e8e8", "ibg": "#252540", "btn": "#303050", "hl": "#ffffff"},
}

FONT_CHAT  = ("Consolas", 11)
FONT_INPUT = ("Consolas", 11)
FONT_TITLE = ("Consolas", 13, "bold")
FONT_BTN   = ("Consolas", 10)


# ============================================================
#  GŁÓWNA KLASA GUI
# ============================================================
class BobGUI:
    def __init__(self, root: tk.Tk):
        self.root  = root
        self.state = BobState()
        self.root.title("Chatbot Bob 2.5")
        self.root.geometry("860x640")
        self.root.resizable(True, True)
        self.root.minsize(600, 400)

        # Stan mini-gier
        self._quiz_pytanie   = None
        self._fiszka_zrod    = None
        self._fiszka_cel     = None
        self._wisielec_slowo = None
        self._wisielec_odk   = None
        self._wisielec_bl    = None
        self._zgadnij_liczba = None
        self._zgadnij_proby  = 0
        self._kolko_plansza  = None
        self._memory_karty   = None
        self._memory_dop     = None
        self._memory_ruchy   = 0
        self._memory_pierwsza = None
        self._tryb = "chat"   # chat | quiz | fiszka | wisielec | zgadnij | kolko | memory

        self._zbuduj_ui()
        self._zastosuj_motyw()
        self._powitaj()

    # ----------------------------------------------------------
    #  BUDOWANIE UI
    # ----------------------------------------------------------
    def _zbuduj_ui(self):
        p = PALETY[self.state.motyw]

        # === TYTUŁ ===
        self.frame_top = tk.Frame(self.root)
        self.frame_top.pack(fill="x", padx=8, pady=(6, 0))

        self.lbl_title = tk.Label(self.frame_top, text="🤖  CHATBOT BOB 2.5",
                                  font=FONT_TITLE, anchor="w")
        self.lbl_title.pack(side="left")

        self.lbl_status = tk.Label(self.frame_top, text="", font=FONT_BTN, anchor="e")
        self.lbl_status.pack(side="right")

        # === PASEK BOCZNY (przyciski szybkich akcji) ===
        self.frame_side = tk.Frame(self.root, width=130)
        self.frame_side.pack(side="right", fill="y", padx=(0, 6), pady=6)
        self.frame_side.pack_propagate(False)

        self.lbl_side = tk.Label(self.frame_side, text="Szybkie akcje", font=FONT_BTN)
        self.lbl_side.pack(pady=(4, 2))

        akcje = [
            ("🌍 Język", self._toggle_jezyk),
            ("🎨 Motyw", self._pokaz_menu_motyw),
            ("❓ Quiz",   lambda: self._cmd("/quiz")),
            ("📚 Fiszka", lambda: self._cmd("/fiszka")),
            ("🎮 Wisielec", lambda: self._cmd("/wisielec")),
            ("❌⭕ Kółko",  lambda: self._cmd("/kolko")),
            ("🃏 Memory",  lambda: self._cmd("/memory")),
            ("🔢 Zgadnij", lambda: self._cmd("/zgadnij")),
            ("🌤️ Pogoda",  self._pokaz_dialog_pogoda),
            ("🔐 Hasło",   lambda: self._cmd("/haslo")),
            ("🎲 Lotto",   lambda: self._cmd("/lotto")),
            ("💬 Cytat",   lambda: self._cmd("/cytat")),
            ("📝 Memo",    lambda: self._cmd("/memo")),
            ("🏅 Punkty",  lambda: self._cmd("/punkty")),
            ("🏆 Osiągn.", lambda: self._cmd("/osiagniecia")),
            ("📖 Pomoc",   lambda: self._cmd("/help")),
            ("🗑️ Wyczyść", self._wyczysc_chat),
        ]
        for label, cmd in akcje:
            btn = tk.Button(self.frame_side, text=label, font=FONT_BTN,
                            command=cmd, relief="flat", cursor="hand2",
                            anchor="w", padx=6)
            btn.pack(fill="x", pady=1)
            btn.bind("<Enter>", lambda e, b=btn: self._btn_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._btn_hover(b, False))
            self.__dict__[f"_btn_{label}"] = btn

        self._side_btns = [w for w in self.frame_side.winfo_children()
                           if isinstance(w, tk.Button)]

        # === CHAT ===
        self.frame_chat = tk.Frame(self.root)
        self.frame_chat.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=6)

        self.chat = scrolledtext.ScrolledText(
            self.frame_chat, wrap=tk.WORD, state="disabled",
            font=FONT_CHAT, relief="flat", bd=0,
            padx=8, pady=6, cursor="arrow",
        )
        self.chat.pack(fill="both", expand=True)

        # Tagi kolorów dla chatu
        self.chat.tag_config("bob",    foreground="#aaaaaa")
        self.chat.tag_config("ty",     foreground="#ffffff")
        self.chat.tag_config("system", foreground="#888888", font=("Consolas", 9))
        self.chat.tag_config("ach",    foreground="#ffd700", font=("Consolas", 11, "bold"))
        self.chat.tag_config("error",  foreground="#ff5555")

        # === INPUT ===
        self.frame_input = tk.Frame(self.frame_chat)
        self.frame_input.pack(fill="x", pady=(4, 0))

        self.entry = tk.Entry(self.frame_input, font=FONT_INPUT, relief="flat", bd=0,
                              insertwidth=2)
        self.entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 4))
        self.entry.bind("<Return>", self._wyslij)
        self.entry.bind("<Up>",     self._historia_gora)
        self.entry.bind("<Down>",   self._historia_dol)
        self.entry.focus()

        self.btn_send = tk.Button(self.frame_input, text="Wyślij ▶",
                                  font=FONT_BTN, relief="flat", cursor="hand2",
                                  command=self._wyslij)
        self.btn_send.pack(side="right", ipady=6, ipadx=8)

        # Historia wejść (↑↓)
        self._hist_wejsc = []
        self._hist_idx   = -1

    # ----------------------------------------------------------
    #  MOTYWY
    # ----------------------------------------------------------
    def _zastosuj_motyw(self):
        p = PALETY[self.state.motyw]
        self.root.configure(bg=p["bg"])
        for w in (self.frame_top, self.frame_side, self.frame_chat, self.frame_input):
            w.configure(bg=p["bg"])
        self.lbl_title.configure(bg=p["bg"], fg=p["fg"])
        self.lbl_status.configure(bg=p["bg"], fg=p["fg"])
        self.lbl_side.configure(bg=p["bg"], fg=p["fg"])
        for btn in self._side_btns:
            btn.configure(bg=p["btn"], fg=p["fg"], activebackground=p["hl"],
                          activeforeground=p["bg"])
        self.chat.configure(bg=p["bg"], fg=p["fg"],
                            selectbackground=p["hl"], selectforeground=p["bg"],
                            insertbackground=p["fg"])
        self.entry.configure(bg=p["ibg"], fg=p["fg"], insertbackground=p["fg"])
        self.btn_send.configure(bg=p["btn"], fg=p["fg"],
                                activebackground=p["hl"], activeforeground=p["bg"])
        self.chat.tag_config("bob",    foreground=p["fg"])
        self.chat.tag_config("ty",     foreground="#ffffff")
        self.chat.tag_config("system", foreground=p["hl"])
        self._aktualizuj_status()

    def _btn_hover(self, btn, on):
        p = PALETY[self.state.motyw]
        btn.configure(bg=p["hl"] if on else p["btn"],
                      fg=p["bg"] if on else p["fg"])

    def _aktualizuj_status(self):
        j = "🇵🇱 PL" if self.state.jezyk == "pl" else "🇬🇧 EN"
        self.lbl_status.configure(
            text=f"{j}  |  motyw: {self.state.motyw}  |  🏅 {state_pts(self.state)}"
        )

    # ----------------------------------------------------------
    #  WYJŚCIE CHATU
    # ----------------------------------------------------------
    def _dopisz(self, tekst: str, tag="bob"):
        self.chat.configure(state="normal")
        self.chat.insert("end", tekst + "\n", tag)
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def _powitaj(self):
        self._dopisz(f"Bob: {self.state.powitanie()}", "bob")
        self._dopisz("Wpisz /help po listę komend lub użyj przycisków →", "system")

    # ----------------------------------------------------------
    #  WYSYŁANIE
    # ----------------------------------------------------------
    def _wyslij(self, event=None):
        tekst = self.entry.get().strip()
        if not tekst:
            return
        self.entry.delete(0, "end")
        self._hist_wejsc.append(tekst)
        self._hist_idx = -1

        self._dopisz(f"Ty: {tekst}", "ty")
        self.state.historia.append(f"Ty: {tekst}")
        self.state.licznik += 1

        self._przetworz(tekst.lower().strip(), tekst)

    def _historia_gora(self, event):
        if self._hist_wejsc:
            self._hist_idx = min(self._hist_idx + 1, len(self._hist_wejsc) - 1)
            self.entry.delete(0, "end")
            self.entry.insert(0, self._hist_wejsc[-(self._hist_idx + 1)])

    def _historia_dol(self, event):
        if self._hist_idx > 0:
            self._hist_idx -= 1
            self.entry.delete(0, "end")
            self.entry.insert(0, self._hist_wejsc[-(self._hist_idx + 1)])
        else:
            self._hist_idx = -1
            self.entry.delete(0, "end")

    # ----------------------------------------------------------
    #  LOGIKA KOMEND
    # ----------------------------------------------------------
    def _cmd(self, komenda: str):
        """Symuluje wpisanie komendy."""
        self.entry.delete(0, "end")
        self.entry.insert(0, komenda)
        self._wyslij()

    def _przetworz(self, p: str, oryginal: str):
        s = self.state

        # --- mini-gra w toku ---
        if self._tryb != "chat":
            self._odpowiedz_mini_gra(p)
            return

        # --- wyjście ---
        if p in ("koniec", "end"):
            self._dopisz(f"Bob: Do zobaczenia! Wiadomości: {s.licznik}", "bob")
            return

        # --- język ---
        if p == "/pl":
            s.jezyk = "pl"
            self._dopisz("Bob: Język polski ✓  Wszystkie komendy dostępne po polsku.", "system")
            self._aktualizuj_status()
            return
        if p == "/en":
            s.jezyk = "en"
            self._dopisz("Bob: English mode ✓  All commands available in English.", "system")
            self._aktualizuj_status()
            return

        # --- motyw ---
        if p.startswith("/motyw") or p.startswith("/theme"):
            nazwa = p.replace("/motyw", "").replace("/theme", "").strip()
            if nazwa in PALETY:
                s.motyw = nazwa
                self._zastosuj_motyw()
                self._dopisz(f"Bob: Motyw '{nazwa}' ustawiony!" if s.jezyk == "pl"
                             else f"Bob: Theme '{nazwa}' applied!", "system")
            else:
                lista = ", ".join(PALETY.keys())
                self._dopisz(f"Bob: Nieznany motyw. Dostępne: {lista}" if s.jezyk == "pl"
                             else f"Bob: Unknown theme. Available: {lista}", "error")
            return

        if p == "/rainbow":
            s.motyw = random.choice([k for k in PALETY if k != "default"])
            self._zastosuj_motyw()
            self._dopisz("Bob: 🌈 Losowy motyw!", "system")
            return

        if p in KOLORY_PROSTE:
            # W GUI mapujemy kolor prosty na motyw najbliższy
            _, hex_c = KOLORY_PROSTE[p]
            # Znajdź motyw o podobnym fg
            for nazwa, pal in PALETY.items():
                if pal["fg"] == hex_c:
                    s.motyw = nazwa
                    self._zastosuj_motyw()
                    break
            return

        # --- help ---
        if p in ("/help", "/pomoc"):
            self._dopisz(KOMENDY_HELP[s.jezyk], "system")
            return

        # --- historia ---
        if p in ("/historia", "/history"):
            self._dopisz("--- Historia ---", "system")
            for h in s.historia[-30:]:
                self._dopisz(h, "system")
            self._dopisz("----------------", "system")
            return

        # --- clear ---
        if p == "/clear":
            self.chat.configure(state="normal")
            self.chat.delete("1.0", "end")
            self.chat.configure(state="disabled")
            s.historia.clear()
            self._dopisz("Bob: Wyczyszczono." if s.jezyk == "pl" else "Bob: Cleared.", "system")
            return

        # --- imgs ---
        if p == "/imgs":
            self._dopisz(pokaz_imgs(s), "system")
            return

        # --- stats ---
        if p in ("/stats", "/statystyki"):
            self._dopisz(f"Bob: Wiadomości: {s.licznik}" if s.jezyk == "pl"
                         else f"Bob: Messages: {s.licznik}", "system")
            return

        # --- calc ---
        if p.startswith("/calc"):
            wyr = p.replace("/calc", "").strip()
            self._dopisz(f"Bob: {kalkulator(wyr, s)}" if wyr
                         else ("Bob: Użyj: /calc 2+2" if s.jezyk == "pl" else "Bob: Use: /calc 2+2"))
            return

        # --- czas / time ---
        if p in ("/czas", "/time"):
            strefa = zoneinfo.ZoneInfo("Europe/Warsaw")
            teraz  = datetime.datetime.now(strefa)
            if s.jezyk == "pl":
                self._dopisz(f"Bob: {teraz.strftime('%H:%M:%S, %d.%m.%Y')} (czas warszawski)", "bob")
            else:
                self._dopisz(f"Bob: {teraz.strftime('%H:%M:%S, %Y-%m-%d')} (Warsaw time)", "bob")
            return

        # --- pogoda / weather ---
        if p.startswith("/pogoda") or p.startswith("/weather"):
            miasto = p.replace("/pogoda", "").replace("/weather", "").strip()
            if miasto:
                self._dopisz("Bob: Pobieranie pogody..." if s.jezyk == "pl"
                             else "Bob: Fetching weather...", "system")
                threading.Thread(target=self._pogoda_async, args=(miasto,), daemon=True).start()
            else:
                self._dopisz("Bob: /pogoda Warszawa" if s.jezyk == "pl"
                             else "Bob: /weather London", "error")
            return

        # --- quiz ---
        if p == "/quiz":
            self._quiz_pytanie = losuj_quiz(s)
            q = self._quiz_pytanie
            if s.jezyk == "pl":
                self._dopisz(f"Bob: ❓ QUIZ! {q['pl']}", "bob")
                self._dopisz(f"       (podpowiedź: {q['hint_pl']})", "system")
            else:
                self._dopisz(f"Bob: ❓ QUIZ! {q['en']}", "bob")
                self._dopisz(f"       (hint: {q['hint_en']})", "system")
            self._tryb = "quiz"
            return

        # --- fiszka / flashcard ---
        if p in ("/fiszka", "/flashcard"):
            self._fiszka_zrod, self._fiszka_cel, pytanie = losuj_fiszke(s)
            self._dopisz(f"Bob: 📚 FISZKA! {pytanie}", "bob")
            self._tryb = "fiszka"
            return

        # --- zgadnij / guess ---
        if p in ("/zgadnij", "/guess"):
            self._zgadnij_liczba = random.randint(1, 100)
            self._zgadnij_proby  = 0
            self._dopisz("Bob: Myślę o liczbie 1–100. Zgadnij!" if s.jezyk == "pl"
                         else "Bob: I'm thinking of a number 1–100. Guess!", "bob")
            self._tryb = "zgadnij"
            return

        # --- wisielec / hangman ---
        if p in ("/wisielec", "/hangman"):
            self._wisielec_slowo = random.choice(SLOWA_WISIELEC)
            self._wisielec_odk   = set()
            self._wisielec_bl    = []
            self._dopisz("Bob: 🎮 WISIELEC! Podawaj litery." if s.jezyk == "pl"
                         else "Bob: 🎮 HANGMAN! Enter letters.", "bob")
            self._rysuj_wisielca()
            self._tryb = "wisielec"
            return

        # --- kółko / tictactoe ---
        if p in ("/kolko", "/tictactoe"):
            self._kolko_plansza = [" "] * 9
            self._dopisz("Bob: 🎮 KÓŁKO I KRZYŻYK! Ty = X, Bob = O. Podaj pole 1–9." if s.jezyk == "pl"
                         else "Bob: 🎮 TIC-TAC-TOE! You = X, Bob = O. Enter field 1–9.", "bob")
            self._rysuj_kolko()
            self._tryb = "kolko"
            return

        # --- memory ---
        if p == "/memory":
            karty = EMOJI_MEMORY * 2
            random.shuffle(karty)
            self._memory_karty   = karty
            self._memory_dop     = [False] * 16
            self._memory_ruchy   = 0
            self._memory_pierwsza = None
            self._dopisz("Bob: 🃏 MEMORY 4×4! Podaj dwa numery kart (np. 3 7)." if s.jezyk == "pl"
                         else "Bob: 🃏 MEMORY 4×4! Enter two card numbers (e.g. 3 7).", "bob")
            self._rysuj_memory()
            self._tryb = "memory"
            return

        # --- punkty / points ---
        if p in ("/punkty", "/points"):
            self._dopisz(f"Bob: 🏅 Punkty: {s.punkty}" if s.jezyk == "pl"
                         else f"Bob: 🏅 Points: {s.punkty}", "bob")
            self._aktualizuj_status()
            return

        # --- osiągnięcia / achievements ---
        if p in ("/osiagniecia", "/achievements"):
            if s.osiagniecia:
                self._dopisz("Bob: 🏆 Osiągnięcia:" if s.jezyk == "pl" else "Bob: 🏆 Achievements:", "bob")
                for aid in s.osiagniecia:
                    for a in OSIAGNIECIA_DEF:
                        if a["id"] == aid:
                            self._dopisz(f"  ✓ {a['pl'] if s.jezyk == 'pl' else a['en']}", "ach")
            else:
                self._dopisz("Bob: Brak osiągnięć – graj!" if s.jezyk == "pl"
                             else "Bob: No achievements yet – play!", "system")
            return

        # --- hasło / password ---
        if p in ("/haslo", "/password"):
            znaki = string.ascii_letters + string.digits + "!@#$%&*"
            haslo = "".join(random.choices(znaki, k=16))
            self._dopisz(f"Bob: 🔐 {haslo}", "bob")
            return

        # --- tłumacz / translate ---
        if p.startswith("/tlumacz") or p.startswith("/translate"):
            slowo = p.replace("/tlumacz", "").replace("/translate", "").strip()
            self._dopisz(f"Bob: {tlumacz(slowo, s)}" if slowo
                         else ("Bob: /tlumacz słowo" if s.jezyk == "pl" else "Bob: /translate word"), "bob")
            return

        # --- rzut / roll ---
        if p.startswith("/rzut") or p.startswith("/roll"):
            arg = p.replace("/rzut", "").replace("/roll", "").strip()
            try:
                sc = int(arg) if arg else 6
                if sc < 2: raise ValueError
                w = random.randint(1, sc)
                self._dopisz(f"Bob: 🎲 K{sc} → {w}" if s.jezyk == "pl"
                             else f"Bob: 🎲 D{sc} → {w}", "bob")
            except ValueError:
                self._dopisz("Bob: /rzut [N]" if s.jezyk == "pl" else "Bob: /roll [N]", "error")
            return

        # --- odliczaj / countdown ---
        if p.startswith("/odliczaj") or p.startswith("/countdown"):
            arg = p.replace("/odliczaj", "").replace("/countdown", "").strip()
            try:
                n = int(arg)
                if not 1 <= n <= 20: raise ValueError
                wynik = "  ".join(str(i) for i in range(n, -1, -1)) + "  🚀"
                self._dopisz(f"Bob: {wynik}", "bob")
            except ValueError:
                self._dopisz("Bob: /odliczaj N (1–20)" if s.jezyk == "pl"
                             else "Bob: /countdown N (1–20)", "error")
            return

        # --- lotto ---
        if p == "/lotto":
            liczby = sorted(random.sample(range(1, 50), 6))
            wynik  = "  ".join(f"{n:2}" for n in liczby)
            self._dopisz(f"Bob: 🎲 Lotto: [ {wynik} ]", "bob")
            return

        # --- losuj / pick ---
        if p.startswith("/losuj") or p.startswith("/pick"):
            arg = p.replace("/losuj", "").replace("/pick", "").strip()
            if arg:
                el = [e.strip() for e in arg.split(",") if e.strip()]
                self._dopisz(f"Bob: 🎯 {random.choice(el)}" if el
                             else ("Bob: Lista pusta!" if s.jezyk == "pl" else "Bob: Empty list!"), "bob")
            else:
                self._dopisz("Bob: /losuj a,b,c" if s.jezyk == "pl" else "Bob: /pick a,b,c", "error")
            return

        # --- anagram ---
        if p.startswith("/anagram"):
            slowo = p.replace("/anagram", "").strip()
            if slowo:
                l = list(slowo); random.shuffle(l)
                self._dopisz(f"Bob: 🔤 {slowo} → {''.join(l)}", "bob")
            else:
                self._dopisz("Bob: /anagram słowo" if s.jezyk == "pl" else "Bob: /anagram word", "error")
            return

        # --- cytat / quote ---
        if p in ("/cytat", "/quote"):
            self._dopisz(f"Bob: 💬 {random.choice(CYTATY[s.jezyk])}", "bob")
            return

        # --- memo ---
        if p.startswith("/memo"):
            arg = p.replace("/memo", "").strip()
            if not arg or arg in ("pokaz", "show"):
                if s.memo:
                    self._dopisz("Bob: 📝 Notatki:" if s.jezyk == "pl" else "Bob: 📝 Notes:", "bob")
                    for i, n in enumerate(s.memo, 1):
                        self._dopisz(f"  {i}. {n}", "system")
                else:
                    self._dopisz("Bob: Brak notatek." if s.jezyk == "pl" else "Bob: No notes.", "system")
            elif arg.startswith("usun ") or arg.startswith("delete "):
                try:
                    idx = int(arg.split()[1]) - 1
                    u = s.memo.pop(idx)
                    self._dopisz(f"Bob: Usunięto: {u}" if s.jezyk == "pl" else f"Bob: Deleted: {u}", "system")
                except (ValueError, IndexError):
                    self._dopisz("Bob: /memo usun N", "error")
            else:
                s.memo.append(arg)
                self._dopisz(f"Bob: ✓ Zapisano #{len(s.memo)}" if s.jezyk == "pl"
                             else f"Bob: ✓ Saved #{len(s.memo)}", "system")
            return

        # --- bob ---
        if p == "/bob":
            self._dopisz(f"Bob: {random.choice(BOB_FAKTY[s.jezyk])}", "bob")
            return

        # --- teach ---
        if p.startswith("/teach"):
            dane = oryginal.replace("/teach", "").replace("/TEACH", "").strip()
            self._dopisz(f"Bob: {teach(dane, s)}", "system")
            return

        # --- stoper / stopwatch (w GUI: prosty timer) ---
        if p in ("/stoper", "/stopwatch"):
            self._dopisz("Bob: ⏱️ Kliknij ponownie /stoper żeby zatrzymać." if s.jezyk == "pl"
                         else "Bob: ⏱️ Type /stoper again to stop.", "system")
            if not hasattr(self, "_stoper_start") or self._stoper_start is None:
                self._stoper_start = time.time()
                self._dopisz("Bob: Stoper uruchomiony!" if s.jezyk == "pl" else "Bob: Stopwatch started!", "system")
            else:
                el = time.time() - self._stoper_start
                self._stoper_start = None
                self._dopisz(f"Bob: ⏱️ Czas: {el:.2f}s" if s.jezyk == "pl"
                             else f"Bob: ⏱️ Time: {el:.2f}s", "bob")
            return

        # --- szukaj w bazie ---
        odp = znajdz_odpowiedz(p, s)
        if odp:
            self._dopisz(f"Bob: {odp}", "bob")
        else:
            self._dopisz("Bob: Nie znam odpowiedzi." if s.jezyk == "pl"
                         else "Bob: I don't know.", "bob")

    # ----------------------------------------------------------
    #  MINI-GRY  –  obsługa odpowiedzi
    # ----------------------------------------------------------
    def _odpowiedz_mini_gra(self, odp: str):
        s = self.state

        if self._tryb == "quiz":
            ok, msg, nowe = sprawdz_quiz(self._quiz_pytanie, odp, s)
            self._dopisz(f"Bob: {msg}", "bob" if ok else "error")
            self._pokaz_osiagniecia(nowe)
            self._tryb = "chat"
            self._aktualizuj_status()

        elif self._tryb == "fiszka":
            ok, msg, nowe = sprawdz_fiszke(self._fiszka_zrod, self._fiszka_cel, odp, s)
            self._dopisz(f"Bob: {msg}", "bob" if ok else "error")
            self._pokaz_osiagniecia(nowe)
            self._tryb = "chat"
            self._aktualizuj_status()

        elif self._tryb == "zgadnij":
            try:
                g = int(odp)
                self._zgadnij_proby += 1
                if g < self._zgadnij_liczba:
                    self._dopisz("Bob: Za mało!" if s.jezyk == "pl" else "Bob: Too low!", "bob")
                elif g > self._zgadnij_liczba:
                    self._dopisz("Bob: Za dużo!" if s.jezyk == "pl" else "Bob: Too high!", "bob")
                else:
                    bonus = max(1, 10 - self._zgadnij_proby)
                    nowe = s.dodaj_punkty(bonus)
                    self._dopisz(f"Bob: 🎉 Tak! {self._zgadnij_proby} prób.  (+{bonus} pkt, łącznie: {s.punkty})" if s.jezyk == "pl"
                                 else f"Bob: 🎉 Yes! {self._zgadnij_proby} tries.  (+{bonus} pts, total: {s.punkty})", "bob")
                    self._pokaz_osiagniecia(nowe)
                    self._tryb = "chat"
                    self._aktualizuj_status()
            except ValueError:
                self._dopisz("Bob: Podaj liczbę!" if s.jezyk == "pl" else "Bob: Enter a number!", "error")

        elif self._tryb == "wisielec":
            if len(odp) != 1 or not odp.isalpha():
                self._dopisz("Bob: Jedna litera!" if s.jezyk == "pl" else "Bob: One letter!", "error")
                return
            if odp in self._wisielec_odk or odp in self._wisielec_bl:
                self._dopisz("Bob: Już podana!" if s.jezyk == "pl" else "Bob: Already guessed!", "error")
                return
            if odp in self._wisielec_slowo:
                self._wisielec_odk.add(odp)
                self._dopisz("Bob: ✓ Dobra litera!" if s.jezyk == "pl" else "Bob: ✓ Good letter!", "bob")
            else:
                self._wisielec_bl.append(odp)
                self._dopisz("Bob: ✗ Nie ma tej litery." if s.jezyk == "pl" else "Bob: ✗ No such letter.", "error")
            self._rysuj_wisielca()
            if set(self._wisielec_slowo) <= self._wisielec_odk:
                nowe = s.dodaj_punkty(10)
                self._dopisz(f"Bob: 🎉 Wygrałeś! Słowo: '{self._wisielec_slowo}'  (+10 pkt)" if s.jezyk == "pl"
                             else f"Bob: 🎉 You won! Word: '{self._wisielec_slowo}'  (+10 pts)", "bob")
                self._pokaz_osiagniecia(nowe)
                self._tryb = "chat"
                self._aktualizuj_status()
            elif len(self._wisielec_bl) >= len(WISIELEC_RYSUNKI) - 1:
                self._dopisz(f"Bob: 💀 Przegrałeś! Słowo: '{self._wisielec_slowo}'" if s.jezyk == "pl"
                             else f"Bob: 💀 You lost! Word: '{self._wisielec_slowo}'", "error")
                self._tryb = "chat"

        elif self._tryb == "kolko":
            try:
                pole = int(odp) - 1
                if not 0 <= pole <= 8 or self._kolko_plansza[pole] != " ": raise ValueError
                self._kolko_plansza[pole] = "X"
            except (ValueError, IndexError):
                self._dopisz("Bob: Pole 1–9 (wolne)!" if s.jezyk == "pl" else "Bob: Field 1–9 (free)!", "error")
                return
            self._rysuj_kolko()
            if self._kolko_wygral("X"):
                self._dopisz("Bob: 🎉 Wygrałeś!" if s.jezyk == "pl" else "Bob: 🎉 You won!", "bob")
                self._tryb = "chat"; return
            # Ruch Boba
            wolne = [i for i, x in enumerate(self._kolko_plansza) if x == " "]
            if not wolne:
                self._dopisz("Bob: 🤝 Remis!" if s.jezyk == "pl" else "Bob: 🤝 Draw!", "bob")
                self._tryb = "chat"; return
            ruch = None
            for znak in ["O", "X"]:
                for i in wolne:
                    self._kolko_plansza[i] = znak
                    if self._kolko_wygral(znak): self._kolko_plansza[i] = " "; ruch = i; break
                    self._kolko_plansza[i] = " "
                if ruch is not None: break
            if ruch is None and 4 in wolne: ruch = 4
            if ruch is None: ruch = random.choice(wolne)
            self._kolko_plansza[ruch] = "O"
            self._rysuj_kolko()
            if self._kolko_wygral("O"):
                self._dopisz("Bob: 😏 Bob wygrał!" if s.jezyk == "pl" else "Bob: 😏 Bob won!", "bob")
                self._tryb = "chat"; return
            wolne2 = [i for i, x in enumerate(self._kolko_plansza) if x == " "]
            if not wolne2:
                self._dopisz("Bob: 🤝 Remis!" if s.jezyk == "pl" else "Bob: 🤝 Draw!", "bob")
                self._tryb = "chat"

        elif self._tryb == "memory":
            try:
                parts = odp.split()
                if len(parts) != 2: raise ValueError
                a, b = int(parts[0]) - 1, int(parts[1]) - 1
                if not (0 <= a <= 15 and 0 <= b <= 15) or a == b: raise ValueError
                if self._memory_dop[a] or self._memory_dop[b]:
                    self._dopisz("Bob: Ta karta już sparowana!" if s.jezyk == "pl"
                                 else "Bob: Already matched!", "error")
                    return
            except (ValueError, TypeError):
                self._dopisz("Bob: Podaj dwa numery, np. 3 7" if s.jezyk == "pl"
                             else "Bob: Enter two numbers, e.g. 3 7", "error")
                return
            self._memory_ruchy += 1
            self._dopisz(f"  [{a+1}] {self._memory_karty[a]}   [{b+1}] {self._memory_karty[b]}", "system")
            if self._memory_karty[a] == self._memory_karty[b]:
                self._memory_dop[a] = self._memory_dop[b] = True
                self._dopisz("Bob: ✓ Para!" if s.jezyk == "pl" else "Bob: ✓ Match!", "bob")
            else:
                self._dopisz("Bob: ✗ Nie pasuje." if s.jezyk == "pl" else "Bob: ✗ No match.", "error")
            self._rysuj_memory()
            if all(self._memory_dop):
                bonus = max(0, 50 - self._memory_ruchy * 2)
                nowe = s.dodaj_punkty(bonus)
                self._dopisz(f"Bob: 🎉 Ukończono w {self._memory_ruchy} ruchach!  (+{bonus} pkt)" if s.jezyk == "pl"
                             else f"Bob: 🎉 Finished in {self._memory_ruchy} moves!  (+{bonus} pts)", "bob")
                self._pokaz_osiagniecia(nowe)
                self._tryb = "chat"
                self._aktualizuj_status()

    # ----------------------------------------------------------
    #  RYSOWANIE MINI-GIER
    # ----------------------------------------------------------
    def _rysuj_wisielca(self):
        slowo = self._wisielec_slowo
        odk   = self._wisielec_odk
        bl    = self._wisielec_bl
        rys   = WISIELEC_RYSUNKI[min(len(bl), len(WISIELEC_RYSUNKI) - 1)]
        wyswietl = " ".join(c if c in odk else "_" for c in slowo)
        bledy    = ", ".join(bl) if bl else "-"
        self._dopisz(rys, "system")
        self._dopisz(f"  Słowo: {wyswietl}   Błędne: {bledy}  ({len(WISIELEC_RYSUNKI)-1-len(bl)} prób)", "system")

    def _rysuj_kolko(self):
        r = self._kolko_plansza
        self._dopisz(f"  {r[0]} | {r[1]} | {r[2]}", "system")
        self._dopisz("  ---------", "system")
        self._dopisz(f"  {r[3]} | {r[4]} | {r[5]}", "system")
        self._dopisz("  ---------", "system")
        self._dopisz(f"  {r[6]} | {r[7]} | {r[8]}   (1–9)", "system")

    def _kolko_wygral(self, z):
        r = self._kolko_plansza
        return any(r[a] == r[b] == r[c] == z
                   for a, b, c in [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)])

    def _rysuj_memory(self):
        karty = self._memory_karty
        dop   = self._memory_dop
        linie = []
        for i in range(16):
            linie.append(karty[i] if dop[i] else f"{i+1:2}")
            if (i + 1) % 4 == 0:
                self._dopisz("  " + "  ".join(linie), "system")
                linie = []

    # ----------------------------------------------------------
    #  OSIĄGNIĘCIA
    # ----------------------------------------------------------
    def _pokaz_osiagniecia(self, nowe):
        for n in nowe:
            self._dopisz(f"🏆 OSIĄGNIĘCIE: {n}", "ach")

    # ----------------------------------------------------------
    #  ASYNC POGODA
    # ----------------------------------------------------------
    def _pogoda_async(self, miasto):
        wynik = pogoda(miasto, self.state)
        self.root.after(0, lambda: self._dopisz(f"Bob: {wynik}", "bob"))

    # ----------------------------------------------------------
    #  DIALOGI
    # ----------------------------------------------------------
    def _pokaz_dialog_pogoda(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Pogoda / Weather")
        dialog.geometry("300x120")
        p = PALETY[self.state.motyw]
        dialog.configure(bg=p["bg"])
        tk.Label(dialog, text="Podaj miasto / Enter city:", font=FONT_INPUT,
                 bg=p["bg"], fg=p["fg"]).pack(pady=8)
        entry = tk.Entry(dialog, font=FONT_INPUT, bg=p["ibg"], fg=p["fg"],
                         insertbackground=p["fg"], relief="flat")
        entry.pack(padx=16, fill="x")
        entry.focus()
        def ok(e=None):
            m = entry.get().strip()
            dialog.destroy()
            if m: self._cmd(f"/pogoda {m}")
        entry.bind("<Return>", ok)
        tk.Button(dialog, text="OK", command=ok, font=FONT_BTN,
                  bg=p["btn"], fg=p["fg"], relief="flat").pack(pady=8)

    def _pokaz_menu_motyw(self):
        menu = tk.Menu(self.root, tearoff=0)
        p = PALETY[self.state.motyw]
        menu.configure(bg=p["btn"], fg=p["fg"])
        for m in PALETY:
            menu.add_command(label=m, command=lambda m=m: self._cmd(f"/motyw {m}"))
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def _toggle_jezyk(self):
        self._cmd("/en" if self.state.jezyk == "pl" else "/pl")

    def _wyczysc_chat(self):
        self._cmd("/clear")

    # ----------------------------------------------------------
    #  STOPER (GUI)
    # ----------------------------------------------------------
    def __init_stoper(self):
        self._stoper_start = None


# ============================================================
#  HELPER
# ============================================================
def state_pts(s: BobState) -> str:
    return f"{s.punkty} pkt" if s.jezyk == "pl" else f"{s.punkty} pts"


# ============================================================
#  MAIN
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app  = BobGUI(root)
    root.mainloop()
