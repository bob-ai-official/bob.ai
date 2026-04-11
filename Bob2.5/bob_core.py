# ============================================================
#  BOB CORE  –  wspólna logika chatbota
#  Importowany przez Bob2_5_EasyMod.py oraz bob_gui.py
# ============================================================
import random
import datetime
import string
import urllib.parse
import urllib.request
import json

# ============================================================
#  STAŁE  –  klucz API
# ============================================================
WEATHER_API_KEY = "1ed7fe74508acb030459d3785912c008"

# ============================================================
#  MOTYWY  –  słownik: nazwa → (kolor_fg_ansi, hex_dla_gui, bg_hex)
#  Motywy zmieniają CAŁY tekst w konsoli (nie tylko wiadomości Boba)
# ============================================================
MOTYWY = {
    "matrix":  ("\033[92m",  "#00ff41", "#0d0d0d"),
    "ocean":   ("\033[96m",  "#00e5ff", "#001a2e"),
    "sunset":  ("\033[91m",  "#ff6b35", "#1a0a00"),
    "blood":   ("\033[31m",  "#cc0000", "#110000"),
    "candy":   ("\033[95m",  "#ff79c6", "#1a001a"),
    "snow":    ("\033[97m",  "#e8e8e8", "#1a1a2e"),
    "default": ("\033[0m",   "#00ff00", "#1e1e1e"),
}

KOLORY_PROSTE = {
    "/red":    ("\033[91m",  "#ff5555"),
    "/green":  ("\033[92m",  "#50fa7b"),
    "/yellow": ("\033[93m",  "#f1fa8c"),
    "/blue":   ("\033[94m",  "#6272a4"),
    "/purple": ("\033[95m",  "#bd93f9"),
    "/cyan":   ("\033[96m",  "#8be9fd"),
}

# ============================================================
#  POWITANIA
# ============================================================
POWITANIA = {
    "pl": [
        "Hej! Jestem Bob, twój chatbot. Czym mogę służyć?",
        "Witaj! Bob do usług. O czym pogadamy?",
        "Cześć! Miło cię widzieć. Jestem Bob!",
        "Hejka! Tutaj Bob. Zadaj mi jakieś pytanie!",
    ],
    "en": [
        "Hey! I'm Bob, your chatbot. How can I help?",
        "Hello! Bob at your service. What shall we talk about?",
        "Hi there! Nice to see you. I'm Bob!",
        "Howdy! Bob here. Ask me something!",
    ],
}

# ============================================================
#  KOMENDY  –  mapa PL ↔ EN (każda komenda działa w obu językach)
# ============================================================
KOMENDY_HELP = {
    "pl": """=== DOSTĘPNE KOMENDY ===
/pl /en                  - zmiana języka (po zmianie odświeża ekran)
/motyw nazwa             - motyw: matrix / ocean / sunset / blood / candy / snow / default
/red /green /yellow /blue /purple /cyan /rainbow
/teach pyt | odp         - naucz bota (lub: pyt_pl | odp_pl | pyt_en | odp_en)
/historia                - historia rozmowy
/clear                   - wyczyść historię
/imgs                    - lista obrazków ASCII
/stats                   - licznik wiadomości
/calc wyrażenie          - kalkulator (np. /calc 2+2)
/czas                    - aktualna data i godzina
/pogoda miasto           - pogoda (np. /pogoda Warszawa)
/quiz                    - quiz wiedzy ogólnej  [+5 pkt]
/fiszka                  - nauka słówek PL↔EN  [+3 pkt]
/zgadnij                 - zgadywanie liczby  [+pkt]
/wisielec                - wisielec  [+10 pkt]
/kolko                   - kółko i krzyżyk vs Bob
/memory                  - memory 4×4  [+pkt]
/punkty                  - twoje punkty sesji
/osiagniecia             - odblokowane osiągnięcia
/haslo                   - generator hasła
/tlumacz słowo           - tłumacz PL↔EN
/rzut [N]                - rzut kością (domyślnie K6)
/odliczaj N              - odliczanie od N do 0
/lotto                   - losowanie Lotto 6/49
/losuj a,b,c             - losuje element z listy
/anagram słowo           - anagram słowa
/stoper                  - stoper (Enter = stop)
/cytat                   - cytat motywacyjny
/memo [tekst]            - notatki: dodaj / pokaż / /memo usun N
/bob                     - ciekawostki o Bobie
/help                    - ta pomoc
koniec                   - zakończ""",

    "en": """=== AVAILABLE COMMANDS ===
/pl /en                  - change language (refreshes screen on change)
/theme name              - theme: matrix / ocean / sunset / blood / candy / snow / default
/red /green /yellow /blue /purple /cyan /rainbow
/teach q | a             - teach bot (or: q_pl | a_pl | q_en | a_en)
/history                 - conversation history
/clear                   - clear history
/imgs                    - ASCII art list
/stats                   - message counter
/calc expression         - calculator (e.g. /calc 2+2)
/time                    - current date and time
/weather city            - weather (e.g. /weather London)
/quiz                    - general knowledge quiz  [+5 pts]
/flashcard               - vocabulary PL↔EN  [+3 pts]
/guess                   - number guessing game  [+pts]
/hangman                 - hangman game  [+10 pts]
/tictactoe               - tic-tac-toe vs Bob
/memory                  - memory 4×4  [+pts]
/points                  - your session points
/achievements            - unlocked achievements
/password                - password generator
/translate word          - PL↔EN translator
/roll [N]                - dice roll (default D6)
/countdown N             - countdown from N to 0
/lotto                   - Lotto draw 6/49
/pick a,b,c              - pick from list
/anagram word            - scramble a word
/stopwatch               - stopwatch (Enter = stop)
/quote                   - motivational quote
/memo [text]             - notes: add / show / /memo delete N
/bob                     - facts about Bob
/help                    - this help
end                      - quit""",
}

# ============================================================
#  ASCII ART
# ============================================================
kot = r"""
   _.---.._             _.---...__
.-'   /\   \          .'  /\     /
`.   (  )   \        /   (  )   /
  `.  \/   .'\\      /`.  \/  .'
    ``---''   )    (   ``---''
            .';.--.;`.
          .' /_...._\ `.
        .'   `.a  a.'   `.
       (        \/        )
        `.___..-'`-..___.'
           \          /
            `-.____.-'
"""

pies = r"""
                    ;i.
                     M$L                    .;i.
                     M$Y;                .;iii;;.
                   ;$YY$i._            .iiii;;;;;
                   iiiYYYYYYiiii;;;;;i;iii;;  ;;;
                 .;iYYYYYiiiiiYYYiiiiiiii;;   ;;;
              .YYYY$$$$YYYYYYYYYYYYYYYiii;;  ;;;;
             .YYY$$$$$$YYYYYY$$$$iiY$$$$$$$ii;;;;
            :YYYF`,  TYYYYY$$$$$YYYYYYYi$$$$$iiii;
            Y$MM: \  :YYYY$$P"````"T$YYMMMMMMMiiYY.
         `.;$$M$b.,dYY$$Yi; .(     .YYMM$$$MMMMMYY
        .._$MMMMM$!YYYYYYYi;.`"  .;iiMMM$MMMMMMMYY
         ._$MMMP` ```""4$$$$$iiiiii$MMMMMMMMMMMMMY;
          MMMM$:       :$$$$$$$MMMMMMMMM$$MMMMMMMYYL
         :MMMM$$.    .;PPb$$$$MMMMMMMM$$$$MMMMMMiYYU:
          iMM$$;;. ;;;;i$$$$$$$MMMM$$$$MMMMMMMMMYYYYY
          `$$$$i .. ``:iiii!*"``.$$$$$$$$MMMMMM$YiYYY
           :Y$$iii;;;.. ` ..;;i$$$$$$$MMMMMM$$YYYYiYY:
            :$$$$$iiiiii$$$$$$$$$MMMMMMMMMMMYYYYiYYYY.
             `$$$$$$$$$$$$$$$$$MMMMMMMM$YYYYYiiiYYYYYY
              YY$$$$$$$$$$$$$MMMMMMM$$YYYiiiiiiYYYYYYY
             :YYYYYY$$$$$$$$$$$$$$$YYYYYYYiiiiYYYYYYi'
"""

dragon = r"""
                             ___====-_  _-====___
                       _--~~~#####// '  ` \\#####~~~--_
                     -~##########// (    ) \\##########~-_
                   -############//  |\^^/|  \\############-
                 _~############//   (O||O)   \\############~_
                ~#############((     \\//     ))#############~
               -###############\\    (oo)    //###############-
              -#################\\  / `' \  //#################-
             -###################\\/  ()  \//###################-
            _#/|##########/\######(  (())  )######/\##########|\#_
            |/ |#/\#/\#/\/  \#/\##|  \()/  |##/\#/  \/\#/\#/\#| \|
            `  |/  V  V  `   V  )||  |()|  ||(  V   '  V /\  \|  '
               `   `  `      `  / |  |()|  | \  '      '<||>  '
                               (  |  |()|  |  )\        /|/
                              __\ |__|()|__| /__\______/|/
                             (vvv(vvvv)(vvvv)vvv)______|/
"""

ghostbusters = r"""
                       ---
                    -        --
                --( /     \ )XXXXXXXXXXXXX
            --XXX(   O   O  )XXXXXXXXXXXXXXX-
           /XXX(       U     )        XXXXXXX\
         /XXXXX(              )--   XXXXXXXXXXX\
        /XXXXX/ (      O     )   XXXXXX   \XXXXX\
        XXXXX/   /            XXXXXX   \   \XXXXX----
        XXXXXX  /          XXXXXX         \  ----  -
---     XXX  /          XXXXXX      \           ---
  --  --  /      /\  XXXXXX            /     ---=
    -        /    XXXXXX              '--- XXXXXX
      --\/XXX\ XXXXXX                      /XXXXX
        \XXXXXXXXX                        /XXXXX/
         \XXXXXX                         /XXXXX/
           \XXXXX--  /                -- XXXX/
            --XXXXXXX---------------  XXXXX--
               \XXXXXXXXXXXXXXXXXXXXXXXX-
                 --XXXXXXXXXXXXXXXXXX-
"""

robot = r"""
                     ____________
                    /____________\
                   / /  _\__/_  \ \
                   || // \\// \\ ||
                   || \\_//\\_//.||
                   |_\__/_<>_\__/_|
                      /        \
                     /  ||  ||  \
                  ///            \\\
                 //|              |\\
                 / \\     Bob     // \
                |U'U|'---____---'|U'U|
                |____________________|
                     \          /
                      |        |
                      |        |
                  ____|        |____
                 |\__/|        |\__/|
                 |    /        \    |
                 |  /            \  |
                 |/________________\|
                 |__________________|
"""

knight = r"""
                             _____
              ,             /@@@@@=-
              \\            @@@@@@@@@@=-
              \\          _\@/\@@@@@=-
  \\        /_ +\ \@@@@@=-
         ,      \\      (_/   )  \@@@@=-
         \\      \\     (_____)    \@@=-
         _\\_/\_ _\\__  /     \     ~~
   ____,/+-  `/\\  { \_|___(__ )
  >             \\  )_|/  ___  \
  \_/--\___/     \\.` / <-q-p-> \
     _//   )      \(\/\ <-d-b-> /___
  _____  /         \/ \  \|/  //   \__
  /     \/          /   \_____//     \_\
  | /\_  |         (_  /______\\     |||
  | \_ | |         | \|   <    \\    /||
  \_\_\ \/     ____\  |____\    \)  / ||
        /    _/  <____)\    (      / //\\
       /   _/           \    \    (  \\//
      (   /              )  / \    \  \/
      /  /              /  /   \    )
  ---/  /--------------/  /-----)  /-----
   _/__/             _/__/     /  /
   /__/              /__/    _/__/
                             /__/
"""

castle = r"""
                        _.---.                            _.---.
                       |_..--'                           |_..--'
                       |                               __|__
                       |                              |_|_|_|
                      /:\                              /:::\
                     /:::\                            /:::::\
                    /:::::\                          /:::::::\
                   /:::::::\                .---.   /:::::::::\
                  /:::::::::\               |_.-'  /:::::::::::\
                 /:::::::::::\  _..--.      |     /:::::::::::::\
                '-'-'-'-'-'-'-'|_..--'     /:\   '-'-'-'-'-'-'-'-'
           .---. |.-. .-. .-.| |          /:::\   \ .-. .-. .-. /
           |_.-' ||_| |_| |_|| |         /:::::\   ||_| |_| |_||
           |     |           |/:\       /:::::::\  |           |
           |     '-----------/:::\     /:::::::::\ '-----------'
          /:\     |.-.  __| /:::::\   /:::::::::::\ |_  .-.  .---.
         /:::\    ||_|     /:::::::\ '-'-'-'-'-'-'-'|   |_|_ |_.-'
        /:::::\   |   .-. /:::::::::\ |.-. .-. .-.| |-.      ||
       /:::::::\  |   |_|'-'-'-'-'-'-'||_| |_| |_|| |_| _   /:\
      /:::::::::\ |       |-. .-. .-| |___________| |     _/:::\ 
     '-'-'-'-'-'-'| |__   |_| |_| |_|  | __   _  |  |_    /:::::\
      | .-. .-. | |       |_________|  |__   -   | /////|/:::::::\
      | |_| |_| |/////|\\\\\_______/  //////|\\\\\\ |   /:::::::::\
      |_________| |.-. .-. |     _ |   |-. .-. .-|  |_ /:::::::::::\
       \_______/  ||_| |_| |    |  |   |_| |_| |_|  | '-'-'-'-'-'-'-'
       |    .  |  |  |   _ | _|    |   |  |      |  |  \_\_\_|_/_/_/
       |_  /:\ | _|  _   _ | _   _ | _ | _   _|  |  |_  |---------|  _
       |  /:::\ |-|_|-|_|-|_|-|_|-|_|-|_|-|_|-|_|-|_|-|_|-|_|-|_|-|_|-|
 _   _ | /:::::\|=====================================================|
|-|_|-|_/:::::::\\___________________________________________________/
|======/-. .-. .-\             .---------------------.     | .-. .-|
 \_____|_| |_| |_|_   _   _   _| .-. _       _   .-. |   _ | |_| |_|
 |     |---------|-|_|-|_|-|_|-| |_|   .-.-.-.   |_| |  _  |  _   _|
 | _    \     _ /==============|     .'   |   '.     |     |   |   |
 |    _ |       |     _    __  |    /     |     \   _|     |    __ |
 |   _  |_      |  _           | _  |     |     |    |     |       |
 '--..__|      _|______________|    |_____|_____|    |_____|__...--'
        '-------'              '----'           '----'
"""

sword = r"""
                            /()
                           / /
                          / /
             /============| |------------------------------------------,
           {=| / / / / / /|()}     }     }     }                        >
             \============| |------------------------------------------'
                          \ \
                           \ \
                            \()
"""

rubberduck = r"""
           ,-.
       ,--' ~.).
     ,'         `.
    ; (((__   __)))
    ;  ( (#) ( (#)
    |   \_/___\_/|
   ,"  ,-'    `__".
  (   ( ._   ____`.)--._
   `._ `-.`-' \(`-'  _  `-. _,-' `-/`.
    ,')   `.`._))  ,' `.   `.  ,','  ;
  .'   .    `--'  /     ).   `.      ;
 ;      `-       /     '  )         ;
 \                       ')       ,'
  \                     ,'       ;
   \               `~~~'       ,'
    `.                      _,'
      `.                ,--'
        `-._________,--'
"""

owl = r"""
                   __              __
                   \ `-._......_.-` /
                    `.  '.    .'  .'
                     //  _`\/`_  \\
                    ||  /\O||O/\  ||
                    |\  \_/||\_/  /|
                    \ '.   \/   .' /
                    / ^ `'~  ~'`   \
                   /  _-^_~ -^_ ~-  |
                   | / ^_ -^_- ~_^\ |
                   | |~_ ^- _-^_ -| |
                   | \  ^-~_ ~-_^ / |
                   \_/;-.,____,.-;\_/
            =========(_(_(==)_)_)=========
           ==================================
"""

rakieta = r"""
              /\
             /  \
            |    |
            |    |
           /|    |\
          / |    | \
         /  | /\ |  \
        /   |/  \|   \
       /    /    \    \
      /    / /--\ \    \
     |    | | () | |    |
     |    | |    | |    |
      \   |  \--/  |   /
       \  |        |  /
        \_|________|_/
           |      |
           |  /\  |
           | /  \ |
           |/    \|
            \    /
             \  /
              \/
         ~~~~~~~~~~
"""

auto = r"""
       ______
     /|_||_\`.__
    (   _    _ _\
    =`-(_)--(_)-'  ><>
"""

slimak = r"""
     .----.   @   @
    / .-"-.`.  \v/
    | | '\ \ \_/ )
  ,-\ `-.' /.'  /
 '---`----'----'
"""

# ============================================================
#  BAZA WIEDZY
# ============================================================
baza = [
{"pl_pytania": ["jak masz na imie", "twoje imie", "jak ci na imie"],
 "pl_odpowiedzi": ["Mam na imię Bob.", "Możesz mówić mi Bob.", "Jestem Bob, twój chatbot."],
 "en_pytania": ["what is your name", "your name", "what's your name"],
 "en_odpowiedzi": ["My name is Bob.", "You can call me Bob.", "I'm Bob, your chatbot."]},

{"pl_pytania": ["ile masz lat", "twoj wiek", "kiedy powstales"],
 "pl_odpowiedzi": ["Mam 0 lat, dopiero powstałem :)", "Jestem całkiem nowy!"],
 "en_pytania": ["how old are you", "your age", "when were you created"],
 "en_odpowiedzi": ["I'm 0 years old, just created :)", "I'm brand new!"]},

{"pl_pytania": ["co robisz", "czym sie zajmujesz"],
 "pl_odpowiedzi": ["Rozmawiam z tobą.", "Odpowiadam na pytania i pomagam."],
 "en_pytania": ["what are you doing", "what do you do"],
 "en_odpowiedzi": ["I'm talking with you.", "I answer questions and help out."]},

{"pl_pytania": ["lubisz programowanie", "czy lubisz python"],
 "pl_odpowiedzi": ["Tak, programowanie jest ciekawe!", "Bardzo lubię Python — to mój ojczysty język!"],
 "en_pytania": ["do you like programming", "do you like python"],
 "en_odpowiedzi": ["Yes, programming is fascinating!", "I love Python — it's my native language!"]},

# ŻARTY
{"pl_pytania": ["powiedz zart", "opowiedz zart", "zart", "kawal", "rozśmiesz mnie", "rozsmiесz mnie"],
 "pl_odpowiedzi": [
    "Dlaczego programiści mylą Halloween z Bożym Narodzeniem? Bo OCT 31 = DEC 25!",
    "Co mówi jeden bit do drugiego? Masz klasę!",
    "Dlaczego kot usiadł na komputerze? Żeby mieć oko na mysz!",
    "Co robi rybak w internecie? Łowi phishing!",
    "Jak programista mówi dobranoc? Niech ci się śni bez błędów!",
    "Ile programistów trzeba żeby wymienić żarówkę? Żadnego, to problem sprzętowy!",
    "Nauczyciel: Podaj liczbę. Uczeń: 3. Nauczyciel: Błąd! Uczeń: Ale dopiero co ją zdefiniowałem!",
 ],
 "en_pytania": ["tell me a joke", "joke", "make me laugh", "funny"],
 "en_odpowiedzi": [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why don't scientists trust atoms? Because they make up everything!",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
    "A SQL query walks into a bar and asks two tables: Can I join you?",
    "Why do Java developers wear glasses? Because they don't C#!",
    "I would tell you a UDP joke, but you might not get it.",
 ]},

# CIEKAWOSTKI
{"pl_pytania": ["ciekawostka", "powiedz cos ciekawego", "zaskocz mnie", "ciekawostke"],
 "pl_odpowiedzi": [
    "Miód nigdy się nie psuje — w egipskich grobowcach znaleziono 3000-letni miód, który był nadal jadalny!",
    "Ośmiornice mają trzy serca i niebieską krew!",
    "Python został nazwany na cześć serialu Monty Python, a nie węża!",
    "Na Saturnie i Jowiszu pada deszcz z diamentów!",
    "Ludzkie oko może rozróżnić około 10 milionów różnych kolorów.",
    "Rekiny istnieją dłużej niż drzewa — pojawiły się 400 mln lat temu!",
    "Pierwszy komputer ważył ponad 27 ton i zajmował całe piętro budynku!",
    "Mrówka może unieść ciężar 50 razy większy od swojego własnego.",
 ],
 "en_pytania": ["fun fact", "tell me something interesting", "surprise me", "did you know"],
 "en_odpowiedzi": [
    "Honey never spoils — archaeologists found 3000-year-old honey still edible!",
    "Octopuses have three hearts and blue blood!",
    "Python was named after Monty Python's Flying Circus, not the snake!",
    "On Saturn and Jupiter it rains diamonds!",
    "The human eye can distinguish about 10 million different colors.",
    "Sharks are older than trees — they appeared 400 million years ago!",
    "The first computer weighed over 27 tons and occupied an entire floor!",
    "An ant can carry 50 times its own body weight.",
 ]},

# OBRAZKI
{"pl_pytania": ["/img kot"],          "pl_odpowiedzi": [kot],         "en_pytania": ["/img cat"],         "en_odpowiedzi": [kot]},
{"pl_pytania": ["/img pies"],         "pl_odpowiedzi": [pies],        "en_pytania": ["/img dog"],         "en_odpowiedzi": [pies]},
{"pl_pytania": ["/img smok","/img dragon"],"pl_odpowiedzi": [dragon], "en_pytania": ["/img dragon"],      "en_odpowiedzi": [dragon]},
{"pl_pytania": ["/img ghostbusters"], "pl_odpowiedzi": [ghostbusters],"en_pytania": ["/img ghostbusters"],"en_odpowiedzi": [ghostbusters]},
{"pl_pytania": ["/img robot"],        "pl_odpowiedzi": [robot],       "en_pytania": ["/img robot"],       "en_odpowiedzi": [robot]},
{"pl_pytania": ["/img rycerz"],       "pl_odpowiedzi": [knight],      "en_pytania": ["/img knight"],      "en_odpowiedzi": [knight]},
{"pl_pytania": ["/img zamek"],        "pl_odpowiedzi": [castle],      "en_pytania": ["/img castle"],      "en_odpowiedzi": [castle]},
{"pl_pytania": ["/img miecz"],        "pl_odpowiedzi": [sword],       "en_pytania": ["/img sword"],       "en_odpowiedzi": [sword]},
{"pl_pytania": ["/img gumowa kaczka"],"pl_odpowiedzi": [rubberduck],  "en_pytania": ["/img rubberduck"],  "en_odpowiedzi": [rubberduck]},
{"pl_pytania": ["/img sowa"],         "pl_odpowiedzi": [owl],         "en_pytania": ["/img owl"],         "en_odpowiedzi": [owl]},
{"pl_pytania": ["/img rakieta"],      "pl_odpowiedzi": [rakieta],     "en_pytania": ["/img rocket"],      "en_odpowiedzi": [rakieta]},
{"pl_pytania": ["/img auto"],         "pl_odpowiedzi": [auto],        "en_pytania": ["/img auto"],        "en_odpowiedzi": [auto]},
{"pl_pytania": ["/img slimak"],       "pl_odpowiedzi": [slimak],      "en_pytania": ["/img snail"],       "en_odpowiedzi": [slimak]},
]

# ============================================================
#  QUIZ
# ============================================================
PYTANIA_QUIZ = [
    {"pl": "Ile nóg ma pająk?",                         "en": "How many legs does a spider have?",             "ans": "8",        "hint_pl": "Więcej niż u owadów...",           "hint_en": "More than insects..."},
    {"pl": "Jaka jest stolica Australii?",               "en": "What is the capital of Australia?",             "ans": "canberra", "hint_pl": "Nie Sydney ani Melbourne!",         "hint_en": "Not Sydney or Melbourne!"},
    {"pl": "Ile pierwiastków jest w wodzie (H2O)?",      "en": "How many elements are in water (H2O)?",         "ans": "2",        "hint_pl": "H i O...",                         "hint_en": "H and O..."},
    {"pl": "W którym roku człowiek stanął na Księżycu?", "en": "In what year did humans first land on the Moon?","ans": "1969",    "hint_pl": "Misja Apollo 11",                  "hint_en": "Apollo 11 mission"},
    {"pl": "Ile kości ma dorosły człowiek?",             "en": "How many bones does an adult human have?",      "ans": "206",      "hint_pl": "Dzieci mają ich więcej!",           "hint_en": "Children have more!"},
    {"pl": "Który planet jest największy w Układzie Słonecznym?", "en": "Largest planet in the Solar System?",  "ans": "jowisz",   "hint_pl": "Zaczyna się na J...",              "hint_en": "Starts with J..."},
    {"pl": "Jaki język stworzył Guido van Rossum?",     "en": "What language did Guido van Rossum create?",    "ans": "python",   "hint_pl": "Używasz go teraz!",                "hint_en": "You're using it now!"},
    {"pl": "Ile kontynentów jest na Ziemi?",             "en": "How many continents are there on Earth?",       "ans": "7",        "hint_pl": "Azja, Afryka, Ameryki...",         "hint_en": "Asia, Africa, Americas..."},
    {"pl": "Jaki jest najszybszy zwierzę na lądzie?",   "en": "What is the fastest land animal?",              "ans": "gepard",   "hint_pl": "Osiąga ponad 100 km/h!",            "hint_en": "Over 100 km/h! (gepard)"},
    {"pl": "Ile minut ma godzina?",                      "en": "How many minutes are in an hour?",              "ans": "60",       "hint_pl": "Podstawa czasu...",                "hint_en": "Basic unit of time..."},
    {"pl": "Największy ocean na świecie?",               "en": "What is the largest ocean?",                    "ans": "spokojny", "hint_pl": "Nazwa oznacza spokój...",           "hint_en": "In Polish: spokojny (peaceful)"},
    {"pl": "Ile boków ma sześciokąt?",                  "en": "How many sides does a hexagon have?",           "ans": "6",        "hint_pl": "Jak plaster miodu!",               "hint_en": "Like a honeycomb!"},
    {"pl": "Stolica Japonii?",                          "en": "What is the capital of Japan?",                 "ans": "tokio",    "hint_pl": "Jedno z największych miast...",     "hint_en": "One of the largest cities..."},
    {"pl": "Pierwiastek kwadratowy z 144?",             "en": "What is the square root of 144?",               "ans": "12",       "hint_pl": "12 × 12 = ?",                      "hint_en": "12 × 12 = ?"},
    {"pl": "Symbol chemiczny Au to jaki metal?",        "en": "Chemical element with symbol Au?",              "ans": "zloto",    "hint_pl": "Bardzo cenny metal...",             "hint_en": "Very precious metal... (zloto)"},
    {"pl": "W jakim kraju wynaleziono internet?",       "en": "In which country was the internet invented?",   "ans": "usa",      "hint_pl": "Projekt ARPANET...",               "hint_en": "ARPANET project..."},
    {"pl": "Ile planet ma Układ Słoneczny?",            "en": "How many planets are in the Solar System?",     "ans": "8",        "hint_pl": "Pluton już nie jest planetą!",      "hint_en": "Pluto is no longer a planet!"},
    {"pl": "Kto namalował Monę Lisę?",                 "en": "Who painted the Mona Lisa?",                    "ans": "da vinci", "hint_pl": "Leonardo...",                       "hint_en": "Leonardo..."},
]

# ============================================================
#  CYTATY
# ============================================================
CYTATY = {
    "pl": [
        "\"Nie musisz być świetny, żeby zacząć – ale musisz zacząć, żeby być świetny.\" – Zig Ziglar",
        "\"Jedynym sposobem na wykonanie świetnej pracy jest kochać to, co się robi.\" – Steve Jobs",
        "\"W środku każdej trudności tkwi możliwość.\" – Albert Einstein",
        "\"Sukces to suma małych wysiłków, powtarzanych dzień po dniu.\" – Robert Collier",
        "\"Kod to poezja.\" – WordPress",
        "\"Każdy ekspert był kiedyś początkującym.\" – Helen Hayes",
        "\"Programowanie to nie wiedza, to sposób myślenia.\" – anonimowe",
        "\"Dzisiaj jest dobry dzień, żeby nauczyć się czegoś nowego!\" – Bob",
    ],
    "en": [
        "\"You don't have to be great to start, but you have to start to be great.\" – Zig Ziglar",
        "\"The only way to do great work is to love what you do.\" – Steve Jobs",
        "\"In the middle of every difficulty lies opportunity.\" – Albert Einstein",
        "\"Success is the sum of small efforts, repeated day in and day out.\" – Robert Collier",
        "\"Code is poetry.\" – WordPress",
        "\"Every expert was once a beginner.\" – Helen Hayes",
        "\"Programming is not about knowledge, it's about thinking.\" – anonymous",
        "\"Today is a great day to learn something new!\" – Bob",
    ],
}

# ============================================================
#  CIEKAWOSTKI O BOBIE
# ============================================================
BOB_FAKTY = {
    "pl": [
        "Jestem napisany w Pythonie — języku nazwanym po Monty Python, nie po wężu!",
        "Mój kod rósł od wersji 1.8 aż do 2.5 — mój twórca dużo pracuje!",
        "Znam ponad 10 ASCII artów — od kota po smoka!",
        "Działam w dwóch językach: polskim i angielskim, a komendy mam w obu!",
        "W wersji 2.5 dostałem GUI, pełne EN komendy i rozbudowany translator!",
        "Zbieram punkty za każdą dobrą odpowiedź — spróbuj /punkty!",
        "Mam 5 poziomów osiągnięć do odblokowania!",
    ],
    "en": [
        "I'm written in Python — a language named after Monty Python, not the snake!",
        "My code grew from version 1.8 to 2.5 — my creator works hard!",
        "I know over 10 ASCII arts — from a cat to a dragon!",
        "I work in two languages and all commands have both PL and EN versions!",
        "In version 2.5 I got a GUI, full EN commands and an expanded translator!",
        "I track your points for correct answers — try /points!",
        "I have 5 achievement levels to unlock!",
    ],
}

# ============================================================
#  SŁOWNIK TŁUMACZA  (rozbudowany)
# ============================================================
SLOWNIK_PL_EN = {
    # podstawowe
    "czesc": "hello", "hej": "hey", "dzien dobry": "good morning",
    "dobry wieczor": "good evening", "dobranoc": "good night",
    "dziekuje": "thank you", "prosze": "please", "przepraszam": "sorry",
    "tak": "yes", "nie": "no", "moze": "maybe", "nigdy": "never",
    "zawsze": "always", "czasem": "sometimes",
    # rzeczy
    "kot": "cat", "pies": "dog", "dom": "house", "auto": "car",
    "woda": "water", "jedzenie": "food", "czas": "time",
    "komputer": "computer", "telefon": "phone", "ksiazka": "book",
    "szkola": "school", "praca": "work", "rodzina": "family",
    "mama": "mom", "tata": "dad", "brat": "brother", "siostra": "sister",
    "okno": "window", "drzwi": "door", "stol": "table", "krzeslo": "chair",
    "samolot": "airplane", "pociag": "train", "rower": "bicycle",
    "miasto": "city", "wies": "village", "kraj": "country", "rzeka": "river",
    "morze": "sea", "ocean": "ocean", "gora": "mountain", "las": "forest",
    # przymiotniki
    "dobry": "good", "zly": "bad", "duzy": "big", "maly": "small",
    "szybki": "fast", "wolny": "slow", "piekny": "beautiful", "brzydki": "ugly",
    "madry": "smart", "glupí": "stupid", "silny": "strong", "slaby": "weak",
    "stary": "old", "mlody": "young", "drogi": "expensive", "tani": "cheap",
    "cieply": "warm", "zimny": "cold", "gorący": "hot", "mokry": "wet",
    "suchy": "dry", "czysty": "clean", "brudny": "dirty", "pusty": "empty",
    "pelny": "full", "nowy": "new", "wazny": "important", "trudny": "difficult",
    "latwy": "easy", "dlugí": "long", "krotki": "short", "szeroki": "wide",
    # liczby
    "jeden": "one", "dwa": "two", "trzy": "three", "cztery": "four",
    "piec": "five", "szesc": "six", "siedem": "seven", "osiem": "eight",
    "dziewiec": "nine", "dziesiec": "ten", "sto": "hundred", "tysiac": "thousand",
    # uczucia
    "milosc": "love", "przyjazn": "friendship", "szczescie": "happiness",
    "smutek": "sadness", "radosc": "joy", "strach": "fear", "zlosc": "anger",
    "nadzieja": "hope", "wiara": "faith", "spokój": "peace",
    # IT / programowanie
    "python": "python", "program": "program", "kod": "code",
    "funkcja": "function", "zmienna": "variable", "petla": "loop",
    "warunek": "condition", "klasa": "class", "obiekt": "object",
    "baza danych": "database", "serwer": "server", "klient": "client",
    "algorytm": "algorithm", "interfejs": "interface", "modul": "module",
    "biblioteka": "library", "blad": "error", "debugowanie": "debugging",
    "kompilator": "compiler", "interpreter": "interpreter",
    # nauka / szkoła
    "matematyka": "mathematics", "fizyka": "physics", "chemia": "chemistry",
    "biologia": "biology", "historia": "history", "geografia": "geography",
    "jezyk": "language", "literatura": "literature", "sztuka": "art",
    "muzyka": "music", "sport": "sport", "nauka": "science",
    # jedzenie
    "chleb": "bread", "mleko": "milk", "jajko": "egg", "mieso": "meat",
    "ryba": "fish", "warzywo": "vegetable", "owoc": "fruit", "zupa": "soup",
    "herbata": "tea", "kawa": "coffee", "sok": "juice", "cukier": "sugar",
    # czas
    "dzien": "day", "noc": "night", "tydzien": "week", "miesiac": "month",
    "rok": "year", "godzina": "hour", "minuta": "minute", "sekunda": "second",
    "rano": "morning", "poludnie": "noon", "wieczor": "evening",
    "wczoraj": "yesterday", "dzisiaj": "today", "jutro": "tomorrow",
    # ciało
    "glowa": "head", "reka": "hand", "noga": "leg", "oko": "eye",
    "ucho": "ear", "nos": "nose", "usta": "mouth", "serce": "heart",
    # różne trudniejsze
    "rzeczywistosc": "reality", "swiadomosc": "consciousness",
    "odpowiedzialnosc": "responsibility", "spoleczenstwo": "society",
    "gospodarka": "economy", "demokracja": "democracy", "wolnosc": "freedom",
    "sprawiedliwosc": "justice", "rownosc": "equality", "postep": "progress",
    "innowacja": "innovation", "technologia": "technology", "sztuczna inteligencja": "artificial intelligence",
    "zrownowazony": "sustainable", "klimat": "climate", "srodowisko": "environment",
}
SLOWNIK_EN_PL = {v: k for k, v in SLOWNIK_PL_EN.items()}

# ============================================================
#  OSIĄGNIĘCIA
# ============================================================
OSIAGNIECIA_DEF = [
    {"id": "first",   "pl": "🥉 Pierwsze punkty!",  "en": "🥉 First points!",    "min": 1},
    {"id": "student", "pl": "📚 Uczeń (10 pkt)",    "en": "📚 Student (10 pts)", "min": 10},
    {"id": "scholar", "pl": "🎓 Scholarz (50 pkt)", "en": "🎓 Scholar (50 pts)", "min": 50},
    {"id": "master",  "pl": "🏅 Mistrz (100 pkt)",  "en": "🏅 Master (100 pts)", "min": 100},
    {"id": "legend",  "pl": "👑 Legenda (250 pkt)", "en": "👑 Legend (250 pts)", "min": 250},
]

# ============================================================
#  SŁOWA DO WISIELCA
# ============================================================
SLOWA_WISIELEC = [
    "python", "chatbot", "komputer", "programowanie", "klawiatura",
    "monitor", "internet", "algorytm", "zmienna", "funkcja",
    "baza", "serwer", "piksel", "ekran", "mysz",
    "robot", "inteligencja", "smartfon", "tablet", "procesor",
    "pamiec", "dysk", "siec", "protokol", "interfejs",
]

WISIELEC_RYSUNKI = [
    "  +---+\n      |\n      |\n      |\n      |\n      |\n=========",
    "  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========",
    "  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========",
    "  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========",
    "  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========",
    "  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========",
    "  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========",
    "  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n=========",
]

# ============================================================
#  EMOJI DO MEMORY
# ============================================================
EMOJI_MEMORY = ["🐱", "🐶", "🐸", "🦊", "🐼", "🐨", "🦁", "🐯"]


# ============================================================
#  KLASA STANU  –  cały stan bota w jednym obiekcie
# ============================================================
class BobState:
    def __init__(self):
        self.jezyk      = "pl"
        self.motyw      = "default"
        self.historia   = []
        self.licznik    = 0
        self.memo       = []
        self.punkty     = 0
        self.osiagniecia = []
        # baza jest globalna i mutowalna (tak jak było)
        self.baza = baza

    @property
    def kolor_ansi(self):
        return MOTYWY[self.motyw][0]

    @property
    def kolor_hex(self):
        return MOTYWY[self.motyw][1]

    @property
    def bg_hex(self):
        return MOTYWY[self.motyw][2]

    def powitanie(self):
        return random.choice(POWITANIA[self.jezyk])

    def dodaj_punkty(self, n):
        self.punkty += n
        nowe = []
        for ach in OSIAGNIECIA_DEF:
            if ach["id"] not in self.osiagniecia and self.punkty >= ach["min"]:
                self.osiagniecia.append(ach["id"])
                nowe.append(ach["pl"] if self.jezyk == "pl" else ach["en"])
        return nowe  # lista nowych osiągnięć do wyświetlenia


# ============================================================
#  FUNKCJE LOGIKI
# ============================================================

def znajdz_odpowiedz(pytanie: str, state: BobState):
    j = state.jezyk
    for temat in state.baza:
        klucz_p = "pl_pytania" if j == "pl" else "en_pytania"
        klucz_o = "pl_odpowiedzi" if j == "pl" else "en_odpowiedzi"
        for p in temat.get(klucz_p, []):
            if p in pytanie:
                odp = temat.get(klucz_o, [])
                return random.choice(odp) if odp else None
    return None


def kalkulator(wyrazenie: str, state: BobState) -> str:
    try:
        dozwolone = set("0123456789+-*/(). ")
        if not all(c in dozwolone for c in wyrazenie):
            raise ValueError
        wynik = eval(wyrazenie)
        return f"{wyrazenie} = {round(wynik, 10)}"
    except ZeroDivisionError:
        return "Błąd: dzielenie przez zero!" if state.jezyk == "pl" else "Error: division by zero!"
    except Exception:
        return "Błąd: nieprawidłowe wyrażenie!" if state.jezyk == "pl" else "Error: invalid expression!"


def tlumacz(tekst: str, state: BobState) -> str:
    t = tekst.strip().lower()
    if t in SLOWNIK_PL_EN:
        return f"{t}  →  {SLOWNIK_PL_EN[t]}  (PL→EN)"
    elif t in SLOWNIK_EN_PL:
        return f"{t}  →  {SLOWNIK_EN_PL[t]}  (EN→PL)"
    else:
        return ("Nie znam tego słowa." if state.jezyk == "pl"
                else "I don't know this word.")


def pogoda(miasto: str, state: BobState) -> str:
    try:
        miasto_enc = urllib.parse.quote(miasto)
        url = (f"https://api.openweathermap.org/data/2.5/weather"
               f"?q={miasto_enc}&appid={WEATHER_API_KEY}&units=metric&lang=pl")
        with urllib.request.urlopen(url, timeout=6) as r:
            dane = json.loads(r.read().decode())
        opis  = dane["weather"][0]["description"].capitalize()
        temp  = dane["main"]["temp"]
        odcz  = dane["main"]["feels_like"]
        wilg  = dane["main"]["humidity"]
        wiatr = dane["wind"]["speed"]
        nazwa = dane["name"]
        if state.jezyk == "pl":
            return (f"☁️ Pogoda w {nazwa}:\n"
                    f"  {opis}, 🌡️ {temp:.1f}°C (odczuwalna {odcz:.1f}°C)\n"
                    f"  💧 Wilgotność: {wilg}%   💨 Wiatr: {wiatr} m/s")
        else:
            opis_en = dane["weather"][0]["description"].capitalize()
            return (f"☁️ Weather in {nazwa}:\n"
                    f"  {opis_en}, 🌡️ {temp:.1f}°C (feels like {odcz:.1f}°C)\n"
                    f"  💧 Humidity: {wilg}%   💨 Wind: {wiatr} m/s")
    except Exception:
        return ("Nie mogę pobrać pogody. Sprawdź nazwę miasta lub połączenie."
                if state.jezyk == "pl"
                else "Cannot fetch weather. Check city name or connection.")


def losuj_quiz(state: BobState) -> dict:
    return random.choice(PYTANIA_QUIZ)


def sprawdz_quiz(pytanie_dict: dict, odpowiedz: str, state: BobState):
    """Zwraca (bool, komunikat, nowe_osiagniecia)"""
    ok = odpowiedz.strip().lower() == pytanie_dict["ans"]
    if ok:
        nowe = state.dodaj_punkty(5)
        msg = (f"Brawo! Poprawna odpowiedź! (+5 pkt, łącznie: {state.punkty})"
               if state.jezyk == "pl"
               else f"Correct! (+5 pts, total: {state.punkty})")
    else:
        nowe = []
        pop = pytanie_dict["ans"]
        msg = (f"Niestety źle. Poprawna odpowiedź: {pop}"
               if state.jezyk == "pl"
               else f"Wrong! Correct answer: {pop}")
    return ok, msg, nowe


def sprawdz_fiszke(slowo_zrodlowe: str, slowo_docelowe: str, odpowiedz: str, state: BobState):
    ok = odpowiedz.strip().lower() == slowo_docelowe
    if ok:
        nowe = state.dodaj_punkty(3)
        msg = (f"Brawo! '{slowo_zrodlowe}' = '{slowo_docelowe}' ✓  (+3 pkt, łącznie: {state.punkty})"
               if state.jezyk == "pl"
               else f"Correct! '{slowo_zrodlowe}' = '{slowo_docelowe}' ✓  (+3 pts, total: {state.punkty})")
    else:
        nowe = []
        msg = (f"Niestety! Poprawna odpowiedź: '{slowo_docelowe}'"
               if state.jezyk == "pl"
               else f"Wrong! Correct answer: '{slowo_docelowe}'")
    return ok, msg, nowe


def losuj_fiszke(state: BobState):
    """Zwraca (slowo_zrodlowe, slowo_docelowe, pytanie_str)"""
    if state.jezyk == "pl":
        pl, en = random.choice(list(SLOWNIK_PL_EN.items()))
        q = f"Jak powiedzieć po angielsku: '{pl}'?"
        return pl, en, q
    else:
        en, pl = random.choice(list(SLOWNIK_EN_PL.items()))
        q = f"How do you say in Polish: '{en}'?"
        return en, pl, q


def pokaz_imgs(state: BobState) -> str:
    obrazki = []
    klucz = "pl_pytania" if state.jezyk == "pl" else "en_pytania"
    for temat in state.baza:
        for p in temat.get(klucz, []):
            if p.startswith("/img"):
                obrazki.append(p)
    label = "Dostępne obrazki:" if state.jezyk == "pl" else "Available images:"
    return label + "\n" + "\n".join(f"  {img}" for img in obrazki)


def teach(dane: str, state: BobState) -> str:
    czesci = [c.strip() for c in dane.split("|")]
    if len(czesci) == 4:
        state.baza.append({
            "pl_pytania": [czesci[0]], "pl_odpowiedzi": [czesci[1]],
            "en_pytania": [czesci[2]], "en_odpowiedzi": [czesci[3]],
        })
        return ("Nauczyłem się nowej odpowiedzi (PL + EN)!" if state.jezyk == "pl"
                else "Learned a new answer (PL + EN)!")
    elif len(czesci) == 2:
        if state.jezyk == "pl":
            state.baza.append({"pl_pytania": [czesci[0]], "pl_odpowiedzi": [czesci[1]],
                                "en_pytania": [], "en_odpowiedzi": []})
        else:
            state.baza.append({"pl_pytania": [], "pl_odpowiedzi": [],
                                "en_pytania": [czesci[0]], "en_odpowiedzi": [czesci[1]]})
        return ("Nauczyłem się nowej odpowiedzi!" if state.jezyk == "pl"
                else "Learned a new answer!")
    else:
        return ("Zły format. Użyj: pytanie | odpowiedź" if state.jezyk == "pl"
                else "Bad format. Use: question | answer")
