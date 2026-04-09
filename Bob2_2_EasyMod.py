import random
import datetime
import string

# ============================================================
#  CHATBOT BOB 2.2  –  by Adam
#  Zmiany względem 2.1:
#   - BUGFIX: funkcje zdefiniowane PRZED główną pętlą
#   - BUGFIX: /teach zapisuje osobno PL i EN (jeśli podano | rozdzielnik)
#   - BUGFIX: znajdz_odpowiedz – poprawione elif dla EN (było drugie if)
#   - REFAKTORING: f-stringi zamiast konkatenacji (+)
#   - REFAKTORING: funkcja pomocnicza msg() eliminuje powtórzenia print/historia
#   - REFAKTORING: zmiana koloru w jednym słowniku zamiast 5 osobnych if-ów
#   - NOWE: /memo – notatki w sesji (dodaj / pokaż / usuń)
#   - NOWE: /rzut – rzut kością (domyślnie K6, można podać /rzut 20)
#   - NOWE: /odliczaj N – odlicza od N do 0
# ============================================================

# === KONFIGURACJA POWITAŃ ===
powitania_pl = [
    "Hej! Jestem Bob, twój chatbot. Czym mogę służyć?",
    "Witaj! Bob do usług. O czym pogadamy?",
    "Cześć! Miło cię widzieć. Jestem Bob!",
    "Hejka! Tutaj Bob. Zadaj mi jakieś pytanie!",
]
powitania_en = [
    "Hey! I'm Bob, your chatbot. How can I help?",
    "Hello! Bob at your service. What shall we talk about?",
    "Hi there! Nice to see you. I'm Bob!",
    "Howdy! Bob here. Ask me something!",
]

# === ZMIENNE GLOBALNE (STAN PROGRAMU) ===
jezyk   = "pl"
kolor   = "\033[0m"
historia = []
licznik  = 0
memo     = []   # NOWE: lista notatek sesji

# Mapa komend kolorów → kody ANSI  (refaktoring: zamiast 5 osobnych if-ów)
KOLORY = {
    "/red":    "\033[91m",
    "/green":  "\033[92m",
    "/yellow": "\033[93m",
    "/blue":   "\033[94m",
    "/purple": "\033[95m",
    "/cyan":   "\033[96m",
}

# ============================================================
#  ASCII ART
# ============================================================
kot = r"""
   _.---.._             _.---...__
.-'   /\   \          .'  /\     /
`.   (  )   \        /   (  )   /
  `.  \/   .'\\      /`.   \/  .'
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

{
"pl_pytania": ["jak masz na imie", "twoje imie"],
"pl_odpowiedzi": ["Mam na imię Bob.", "Możesz mówić mi Bob.", "Jestem Bob, twój chatbot."],
"en_pytania": ["what is your name", "your name"],
"en_odpowiedzi": ["My name is Bob.", "You can call me Bob.", "I'm Bob, your chatbot."]
},

{
"pl_pytania": ["ile masz lat", "twoj wiek"],
"pl_odpowiedzi": ["Mam 0 lat.", "Dopiero powstałem :)"],
"en_pytania": ["how old are you", "your age"],
"en_odpowiedzi": ["I am 0 years old, I was created recently."]
},

{
"pl_pytania": ["co robisz"],
"pl_odpowiedzi": ["Rozmawiam z tobą.", "Odpowiadam na pytania."],
"en_pytania": ["what are you doing"],
"en_odpowiedzi": ["I'm talking with you.", "I answer questions."]
},

{
"pl_pytania": ["lubisz programowanie"],
"pl_odpowiedzi": ["Tak, programowanie jest ciekawe.", "Bardzo lubię Python."],
"en_pytania": ["do you like programming"],
"en_odpowiedzi": ["Yes, programming is interesting.", "I like Python."]
},

# === ŻARTY ===
{
"pl_pytania": ["powiedz zart", "opowiedz zart", "rozsmiесz mnie", "zart", "kawal", "rozśmiesz mnie"],
"pl_odpowiedzi": [
    "Dlaczego programiści mylą Halloween z Bożym Narodzeniem? Bo OCT 31 = DEC 25!",
    "Jak nazywa się niewidomy dinozaur? Doyouthinkhesaurus!",
    "Co mówi jeden bit do drugiego? Masz klasę!",
    "Dlaczego kot usiadł na komputerze? Żeby mieć oko na mysz!",
    "Co robi rybak w internecie? Łowi phishing!",
    "Jak programista mówi dobranoc? Niech ci się śni bez błędów!",
    "Co powiedział zero do ósemki? Fajny pasek!",
    "Dlaczego szkielet nie poszedł na imprezę? Bo nie miał nikogo, kogo mógłby zabrać!",
    "Nauczyciel: Podaj liczbę. Uczeń: 3. Nauczyciel: Błąd! Uczeń: Ale dopiero co ją zdefiniowałem!",
    "Ile programistów trzeba żeby wymienić żarówkę? Żadnego, to problem sprzętowy!",
],
"en_pytania": ["tell me a joke", "joke", "make me laugh", "funny"],
"en_odpowiedzi": [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "Why don't scientists trust atoms? Because they make up everything!",
    "What do you call a fish without eyes? A fsh!",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
    "Why was the math book sad? It had too many problems.",
    "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
    "Why do Java developers wear glasses? Because they don't C#!",
    "I would tell you a UDP joke, but you might not get it.",
]
},

# === CIEKAWOSTKI OGÓLNE ===
{
"pl_pytania": ["ciekawostka", "powiedz cos ciekawego", "zaskocz mnie", "cos ciekawego", "ciekawostke"],
"pl_odpowiedzi": [
    "Miód nigdy się nie psuje - w egipskich grobowcach znaleziono 3000-letni miód, który był nadal jadalny!",
    "Ośmiornice mają trzy serca i niebieską krew!",
    "Mrówki nigdy nie śpią i nie mają płuc.",
    "Banany są lekko radioaktywne ze względu na zawartość potasu-40.",
    "Ludzki mózg generuje tyle energii elektrycznej, że mógłby zasilić małą żarówkę!",
    "Python został nazwany na cześć serialu komediowego Monty Python, a nie węża!",
    "Pierwsze zdjęcie zostało wykonane w 1826 roku i wymagało 8 godzin naświetlania!",
    "Rekiny istnieją dłużej niż drzewa - rekinopodobne stworzenia pojawiły się 400 mln lat temu!",
    "Na Saturnie i Jowiszu pada deszcz z diamentów!",
    "Mrówka może unieść ciężar 50 razy większy od swojego własnego.",
    "Ludzkie oko może rozróżnić około 10 milionów różnych kolorów.",
    "Pierwszy komputer ważył ponad 27 ton i zajmował całe piętro budynku!",
],
"en_pytania": ["fun fact", "tell me something interesting", "surprise me", "interesting fact", "did you know"],
"en_odpowiedzi": [
    "Honey never spoils - archaeologists found 3000-year-old honey in Egyptian tombs that was still edible!",
    "Octopuses have three hearts and blue blood!",
    "Ants never sleep and don't have lungs.",
    "Bananas are slightly radioactive due to their potassium-40 content.",
    "The human brain generates enough electricity to power a small light bulb!",
    "Python was named after Monty Python's Flying Circus, not the snake!",
    "The first photo ever taken was in 1826 and required 8 hours of exposure!",
    "Sharks are older than trees - shark-like creatures appeared 400 million years ago!",
    "On Saturn and Jupiter it rains diamonds!",
    "An ant can carry 50 times its own body weight.",
    "The first computer weighed over 27 tons and occupied an entire floor of a building!",
]
},

# === PRZYPISANIE OBRAZKÓW DO KOMEND ===
{"pl_pytania": ["/img kot"],          "pl_odpowiedzi": [kot],         "en_pytania": ["/img cat"],         "en_odpowiedzi": [kot]},
{"pl_pytania": ["/img pies"],         "pl_odpowiedzi": [pies],        "en_pytania": ["/img dog"],         "en_odpowiedzi": [pies]},
{"pl_pytania": ["/img smok", "/img dragon"], "pl_odpowiedzi": [dragon], "en_pytania": ["/img dragon"],   "en_odpowiedzi": [dragon]},
{"pl_pytania": ["/img ghostbusters"], "pl_odpowiedzi": [ghostbusters], "en_pytania": ["/img ghostbusters"], "en_odpowiedzi": [ghostbusters]},
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
pytania_quiz = [
    {"pytanie_pl": "Ile nóg ma pająk?",              "pytanie_en": "How many legs does a spider have?",         "odpowiedz": "8",        "podpowiedz_pl": "To więcej niż u owadów...",           "podpowiedz_en": "More than insects have..."},
    {"pytanie_pl": "Jaka jest stolica Australii?",   "pytanie_en": "What is the capital of Australia?",         "odpowiedz": "canberra", "podpowiedz_pl": "Nie Sydney ani Melbourne!",            "podpowiedz_en": "Not Sydney or Melbourne!"},
    {"pytanie_pl": "Ile pierwiastków jest w wodzie (H2O)?", "pytanie_en": "How many elements are in water (H2O)?", "odpowiedz": "2",    "podpowiedz_pl": "H i O...",                            "podpowiedz_en": "H and O..."},
    {"pytanie_pl": "W którym roku człowiek po raz pierwszy stanął na Księżycu?", "pytanie_en": "In what year did humans first land on the Moon?", "odpowiedz": "1969", "podpowiedz_pl": "Misja Apollo 11", "podpowiedz_en": "Apollo 11 mission"},
    {"pytanie_pl": "Ile kości ma dorosły człowiek?", "pytanie_en": "How many bones does an adult human have?",   "odpowiedz": "206",      "podpowiedz_pl": "Dzieci mają ich więcej!",             "podpowiedz_en": "Children have more!"},
    {"pytanie_pl": "Który planet jest największy w Układzie Słonecznym?", "pytanie_en": "Which planet is the largest in the Solar System?", "odpowiedz": "jowisz", "podpowiedz_pl": "Zaczyna się na J...", "podpowiedz_en": "It starts with J..."},
    {"pytanie_pl": "Jaki język programowania stworzył Guido van Rossum?", "pytanie_en": "What programming language did Guido van Rossum create?", "odpowiedz": "python", "podpowiedz_pl": "Używasz go teraz!", "podpowiedz_en": "You're using it right now!"},
    {"pytanie_pl": "Ile kontynentów jest na Ziemi?", "pytanie_en": "How many continents are there on Earth?",    "odpowiedz": "7",        "podpowiedz_pl": "Azja, Afryka, Ameryki, Europa...",    "podpowiedz_en": "Asia, Africa, Americas, Europe..."},
    {"pytanie_pl": "Jaki jest najszybszy zwierzę na lądzie?", "pytanie_en": "What is the fastest land animal?", "odpowiedz": "gepard",   "podpowiedz_pl": "Osiąga ponad 100 km/h!",              "podpowiedz_en": "It can reach over 100 km/h! (gepard)"},
    {"pytanie_pl": "Ile minut ma godzina?",          "pytanie_en": "How many minutes are in an hour?",           "odpowiedz": "60",       "podpowiedz_pl": "Podstawowa jednostka czasu...",       "podpowiedz_en": "Basic unit of time..."},
    {"pytanie_pl": "Jak nazywa się największy ocean?","pytanie_en": "What is the largest ocean?",                "odpowiedz": "spokojny", "podpowiedz_pl": "Jego nazwa oznacza spokój...",        "podpowiedz_en": "In Polish it means peaceful... (spokojny)"},
    {"pytanie_pl": "Ile boków ma sześciokąt?",       "pytanie_en": "How many sides does a hexagon have?",        "odpowiedz": "6",        "podpowiedz_pl": "Tyle samo co plaster miodu!",         "podpowiedz_en": "Same as a honeycomb cell!"},
    {"pytanie_pl": "Jak się nazywa stolica Japonii?","pytanie_en": "What is the capital of Japan?",              "odpowiedz": "tokio",    "podpowiedz_pl": "Jedno z największych miast świata...", "podpowiedz_en": "One of the largest cities in the world..."},
    {"pytanie_pl": "Ile wynosi pierwiastek kwadratowy z 144?", "pytanie_en": "What is the square root of 144?", "odpowiedz": "12",       "podpowiedz_pl": "12 x 12 = ?",                         "podpowiedz_en": "12 x 12 = ?"},
    {"pytanie_pl": "Który pierwiastek chemiczny ma symbol Au?", "pytanie_en": "Which chemical element has the symbol Au?", "odpowiedz": "zloto", "podpowiedz_pl": "Bardzo cenny metal...",      "podpowiedz_en": "A very precious metal... (in Polish: zloto)"},
    {"pytanie_pl": "W jakim kraju wynaleziono internet?", "pytanie_en": "In which country was the internet invented?", "odpowiedz": "usa", "podpowiedz_pl": "Projekt ARPANET...",               "podpowiedz_en": "ARPANET project..."},
]

# ============================================================
#  CIEKAWOSTKI O BOBIE
# ============================================================
bob_fakty_pl = [
    "Jestem napisany w Pythonie - języku nazwanym po Monty Python, nie po wężu!",
    "Mój kod rósł od wersji 1.8 aż do 2.2 - to znaczy, że mój twórca dużo pracuje!",
    "Znam ponad 10 ASCII artów - od kota po smoka!",
    "Potrafię liczyć, tłumaczyć, zadawać pytania quizowe i generować hasła!",
    "Moje imię to Bob. Proste, łatwe do zapamiętania. :)",
    "Za każdym razem gdy uruchamiasz program, witam się trochę inaczej!",
    "Można mnie nauczyć nowych odpowiedzi przez /teach - jestem pojętny!",
    "Działam w dwóch językach: polskim i angielskim!",
    "W wersji 2.2 dostałem notatki (/memo), rzut kością (/rzut) i odliczanie (/odliczaj)!",
]

bob_fakty_en = [
    "I'm written in Python - a language named after Monty Python, not the snake!",
    "My code grew from version 1.8 all the way to 2.2 - my creator works hard!",
    "I know over 10 ASCII arts - from a cat to a dragon!",
    "I can calculate, translate, ask quiz questions and generate passwords!",
    "My name is Bob. Simple, easy to remember. :)",
    "Every time you run the program, I greet you a little differently!",
    "You can teach me new answers with /teach - I'm a quick learner!",
    "I work in two languages: Polish and English!",
    "In version 2.2 I got notes (/memo), dice rolls (/rzut) and countdown (/odliczaj)!",
]

# ============================================================
#  SŁOWNIK TŁUMACZA
# ============================================================
slownik_pl_en = {
    "czesc": "hello", "hej": "hey", "dzien dobry": "good morning",
    "dobry wieczor": "good evening", "dobranoc": "good night",
    "dziekuje": "thank you", "prosze": "please", "przepraszam": "sorry",
    "tak": "yes", "nie": "no", "moze": "maybe",
    "kot": "cat", "pies": "dog", "dom": "house", "auto": "car",
    "woda": "water", "jedzenie": "food", "czas": "time",
    "komputer": "computer", "telefon": "phone", "ksiazka": "book",
    "szkola": "school", "praca": "work", "rodzina": "family",
    "mama": "mom", "tata": "dad", "brat": "brother", "siostra": "sister",
    "dobry": "good", "zly": "bad", "duzy": "big", "maly": "small",
    "szybki": "fast", "wolny": "slow", "piekny": "beautiful",
    "jeden": "one", "dwa": "two", "trzy": "three", "cztery": "four", "piec": "five",
    "milosc": "love", "przyjazn": "friendship", "szczescie": "happiness",
    "python": "python", "program": "program", "kod": "code",
}
slownik_en_pl = {v: k for k, v in slownik_pl_en.items()}


# ============================================================
#  FUNKCJE  –  zdefiniowane PRZED główną pętlą (BUGFIX)
# ============================================================

def msg(tekst, do_historii=True):
    """Wypisuje tekst z aktywnym kolorem i opcjonalnie zapisuje do historii."""
    print(f"{kolor}{tekst}\033[0m")
    if do_historii:
        historia.append(tekst)


def tlumacz(tekst):
    tekst = tekst.strip().lower()
    if tekst in slownik_pl_en:
        return f"{tekst} = {slownik_pl_en[tekst]} (PL->EN)"
    elif tekst in slownik_en_pl:
        return f"{tekst} = {slownik_en_pl[tekst]} (EN->PL)"
    else:
        return ("Nie znam tego słowa. Znam podstawowe słowa PL<->EN."
                if jezyk == "pl" else
                "I don't know this word. I know basic PL<->EN words.")


def quiz():
    pytanie = random.choice(pytania_quiz)
    if jezyk == "pl":
        print(f"\nProgram: QUIZ! {pytanie['pytanie_pl']}")
        print(f"Program: (podpowiedź: {pytanie['podpowiedz_pl']})")
    else:
        print(f"\nProgram: QUIZ! {pytanie['pytanie_en']}")
        print(f"Program: (hint: {pytanie['podpowiedz_en']})")

    odp = input("Ty: ").lower().strip()
    historia.append(f"Ty: {odp}")

    if odp == pytanie["odpowiedz"]:
        print("Program: Brawo! Poprawna odpowiedź!" if jezyk == "pl" else "Program: Well done! Correct answer!")
    else:
        pop = pytanie["odpowiedz"]
        print(f"Program: Niestety źle. Poprawna odpowiedź to: {pop}" if jezyk == "pl"
              else f"Program: Wrong! The correct answer is: {pop}")


def kalkulator(wyrazenie):
    try:
        dozwolone = set("0123456789+-*/(). ")
        if not all(c in dozwolone for c in wyrazenie):
            raise ValueError("Niedozwolone znaki")
        wynik = eval(wyrazenie)
        return f"{wyrazenie} = {round(wynik, 10)}"
    except ZeroDivisionError:
        return "Błąd: dzielenie przez zero!" if jezyk == "pl" else "Error: division by zero!"
    except Exception:
        return "Błąd: nieprawidłowe wyrażenie!" if jezyk == "pl" else "Error: invalid expression!"


def pokaz_imgs():
    obrazki = []
    for temat in baza:
        klucz = "pl_pytania" if jezyk == "pl" else "en_pytania"
        for p in temat.get(klucz, []):
            if p.startswith("/img"):
                obrazki.append(p)
    label = "Dostępne obrazki:" if jezyk == "pl" else "Available images:"
    print(f"\n{label}")
    for img in obrazki:
        print(f"  {img}")
    print()


def znajdz_odpowiedz(pytanie):
    """BUGFIX: elif dla EN (było drugie 'if', więc PL zawsze sprawdzało się podwójnie)."""
    for temat in baza:
        if jezyk == "pl":
            for p in temat["pl_pytania"]:
                if p in pytanie:
                    return random.choice(temat["pl_odpowiedzi"])
        elif jezyk == "en":                         # ← było: if jezyk == "en"
            for p in temat["en_pytania"]:
                if p in pytanie:
                    return random.choice(temat["en_odpowiedzi"])
    return None


# ============================================================
#  INTERFEJS STARTOWY
# ============================================================
print("=== CHATBOT BOB 2.2 ===")
print("Komendy:")
print("/pl /en              - zmiana języka")
print("/red /green /yellow /blue /purple /cyan /rainbow - zmiana koloru")
print("/teach pyt | odp     - naucz bota (opcjonalnie: pyt_pl | odp_pl | pyt_en | odp_en)")
print("/history             - historia rozmowy")
print("/clear               - wyczyść historię")
print("/imgs                - lista obrazków")
print("/stats               - licznik wiadomości")
print("/calc wyrazenie      - kalkulator (np. /calc 2+2)")
print("/czas                - aktualna data i godzina")
print("/quiz                - quiz wiedzy ogólnej")
print("/zgadnij             - gra w zgadywanie liczby")
print("/haslo               - generator losowego hasła")
print("/tlumacz tekst       - tłumacz PL<->EN")
print("/rzut [N]            - rzut kością N-ścienną (domyślnie K6)")
print("/odliczaj N          - odlicza od N do 0")
print("/memo                - notatki sesji (dodaj / pokaż / usuń)")
print("/bob                 - ciekawostki o Bobie")
print("/help                - pomoc")
print("koniec / end         - zakończ\n")

print("Bob: " + random.choice(powitania_pl) + "\n")


# ============================================================
#  GŁÓWNA PĘTLA
# ============================================================
while True:

    pytanie = input("Ty: ").lower().strip()
    historia.append(f"Ty: {pytanie}")
    licznik += 1

    # --- wyjście ---
    if pytanie in ["koniec", "end"]:
        print(f"Program: Do zobaczenia! Wysłano {licznik} wiadomości." if jezyk == "pl"
              else f"Program: Goodbye! You sent {licznik} messages.")
        break

    # --- pomoc ---
    if pytanie == "/help":
        print("Dostępne komendy:")
        print("/pl /en")
        print("/red /green /yellow /blue /purple /cyan /rainbow")
        print("/teach pytanie | odpowiedz")
        print("/history  /clear  /imgs  /stats")
        print("/calc  /czas  /quiz  /zgadnij  /haslo")
        print("/tlumacz  /rzut [N]  /odliczaj N  /memo")
        print("/bob")
        continue

    # --- historia ---
    if pytanie == "/history":
        print("\n--- Historia ---")
        for h in historia:
            print(h)
        print("---------------\n")
        continue

    # --- wyczyść historię ---
    if pytanie == "/clear":
        historia.clear()
        print("Program: Historia wyczyszczona!" if jezyk == "pl" else "Program: History cleared!")
        continue

    # --- obrazki ---
    if pytanie == "/imgs":
        pokaz_imgs()
        continue

    # --- statystyki ---
    if pytanie == "/stats":
        msg(f"Program: Wysłano {licznik} wiadomości w tej sesji." if jezyk == "pl"
            else f"Program: You have sent {licznik} messages this session.")
        continue

    # --- kalkulator ---
    if pytanie.startswith("/calc"):
        wyrazenie = pytanie.replace("/calc", "").strip()
        if wyrazenie:
            msg(f"Program: {kalkulator(wyrazenie)}")
        else:
            print("Program: Użyj: /calc 2+2" if jezyk == "pl" else "Program: Use: /calc 2+2")
        continue

    # --- czas ---
    if pytanie in ("/czas", "/time"):
        import zoneinfo
        strefa = zoneinfo.ZoneInfo("Europe/Warsaw")
        teraz = datetime.datetime.now(strefa)
        if jezyk == "pl":
            msg(f"Program: Teraz jest {teraz.strftime('%H:%M:%S, %d.%m.%Y')} (czas warszawski)")
        else:
            msg(f"Program: Current time is {teraz.strftime('%H:%M:%S, %Y-%m-%d')} (Warsaw time)")
        continue

    # --- quiz ---
    if pytanie == "/quiz":
        quiz()
        continue

    # --- NOWE: rzut kością ---
    if pytanie.startswith("/rzut"):
        arg = pytanie.replace("/rzut", "").strip()
        try:
            sciany = int(arg) if arg else 6
            if sciany < 2:
                raise ValueError
            wynik = random.randint(1, sciany)
            msg(f"Program: Rzucam K{sciany}... wypadło {wynik}!" if jezyk == "pl"
                else f"Program: Rolling D{sciany}... you got {wynik}!")
        except ValueError:
            print("Program: Użyj: /rzut lub /rzut 20" if jezyk == "pl" else "Program: Use: /rzut or /rzut 20")
        continue

    # --- NOWE: odliczanie ---
    if pytanie.startswith("/odliczaj"):
        arg = pytanie.replace("/odliczaj", "").strip()
        try:
            n = int(arg)
            if n < 1 or n > 100:
                raise ValueError
            for i in range(n, -1, -1):
                print(f"Program: {i}{'...' if i > 0 else ' - Start! 🚀'}")
        except ValueError:
            print("Program: Użyj: /odliczaj 10 (liczba 1-100)" if jezyk == "pl"
                  else "Program: Use: /odliczaj 10 (number 1-100)")
        continue

    # --- NOWE: notatki memo ---
    if pytanie.startswith("/memo"):
        arg = pytanie.replace("/memo", "").strip()
        if not arg or arg == "pokaz" or arg == "show":
            if memo:
                print("Program: Twoje notatki:" if jezyk == "pl" else "Program: Your notes:")
                for i, n in enumerate(memo, 1):
                    print(f"  {i}. {n}")
            else:
                print("Program: Brak notatek." if jezyk == "pl" else "Program: No notes yet.")
        elif arg.startswith("usun ") or arg.startswith("delete "):
            try:
                idx = int(arg.split()[1]) - 1
                usunieta = memo.pop(idx)
                print(f"Program: Usunięto: {usunieta}" if jezyk == "pl" else f"Program: Deleted: {usunieta}")
            except (ValueError, IndexError):
                print("Program: Użyj: /memo usun 1" if jezyk == "pl" else "Program: Use: /memo delete 1")
        else:
            memo.append(arg)
            print(f"Program: Zapisano notatkę #{len(memo)}!" if jezyk == "pl"
                  else f"Program: Note #{len(memo)} saved!")
        continue

    # --- rainbow ---
    if pytanie == "/rainbow":
        kolor = random.choice(list(KOLORY.values()))
        print("Program: Losowy kolor ustawiony!" if jezyk == "pl" else "Program: Random color set!")
        continue

    # --- zmiana koloru (refaktoring: słownik zamiast 5 osobnych if-ów) ---
    if pytanie in KOLORY:
        kolor = KOLORY[pytanie]
        continue

    # --- ciekawostki o Bobie ---
    if pytanie == "/bob":
        msg("Program: " + random.choice(bob_fakty_pl if jezyk == "pl" else bob_fakty_en))
        continue

    # --- generator hasła ---
    if pytanie == "/haslo":
        znaki = string.ascii_letters + string.digits + "!@#$%&*"
        haslo = "".join(random.choices(znaki, k=16))
        msg(f"Program: Twoje losowe hasło: {haslo}" if jezyk == "pl"
            else f"Program: Your random password: {haslo}")
        continue

    # --- tłumacz ---
    if pytanie.startswith("/tlumacz"):
        slowo = pytanie.replace("/tlumacz", "").strip()
        if slowo:
            msg(f"Program: {tlumacz(slowo)}")
        else:
            print("Program: Użyj: /tlumacz kot" if jezyk == "pl" else "Program: Use: /tlumacz cat")
        continue

    # --- zgadywanka ---
    if pytanie == "/zgadnij":
        print("Program: Myślę o liczbie od 1 do 100. Zgadnij!" if jezyk == "pl"
              else "Program: I'm thinking of a number from 1 to 100. Guess!")
        liczba = random.randint(1, 100)
        proby = 0
        while True:
            odp = input("Ty: ").strip()
            historia.append(f"Ty: {odp}")
            proby += 1
            try:
                guess = int(odp)
                if guess < liczba:
                    print("Program: Za mało! Spróbuj większej liczby." if jezyk == "pl"
                          else "Program: Too low! Try a bigger number.")
                elif guess > liczba:
                    print("Program: Za dużo! Spróbuj mniejszej liczby." if jezyk == "pl"
                          else "Program: Too high! Try a smaller number.")
                else:
                    print(f"Program: Brawo! Zgadłeś w {proby} próbach!" if jezyk == "pl"
                          else f"Program: Well done! You guessed in {proby} tries!")
                    break
            except ValueError:
                print("Program: Podaj liczbę!" if jezyk == "pl" else "Program: Enter a number!")
        continue

    # --- zmiana języka ---
    if pytanie == "/pl":
        jezyk = "pl"
        print("Program: Język polski")
        continue

    if pytanie == "/en":
        jezyk = "en"
        print("Program: English language")
        continue

    # --- BUGFIX /teach: obsługa 4-częściowego formatu PL|odp_PL|EN|odp_EN ---
    if pytanie.startswith("/teach"):
        try:
            dane = pytanie.replace("/teach", "").strip()
            czesci = [c.strip() for c in dane.split("|")]
            if len(czesci) == 4:
                # format: pytanie_pl | odpowiedz_pl | pytanie_en | odpowiedz_en
                nowy = {
                    "pl_pytania":   [czesci[0]],
                    "pl_odpowiedzi":[czesci[1]],
                    "en_pytania":   [czesci[2]],
                    "en_odpowiedzi":[czesci[3]],
                }
                baza.append(nowy)
                print("Program: Nauczyłem się nowej odpowiedzi (PL + EN)!" if jezyk == "pl"
                      else "Program: Learned a new answer (PL + EN)!")
            elif len(czesci) == 2:
                # format uproszczony: pytanie | odpowiedz (trafia do aktywnego języka)
                if jezyk == "pl":
                    nowy = {"pl_pytania": [czesci[0]], "pl_odpowiedzi": [czesci[1]],
                            "en_pytania": [],           "en_odpowiedzi": []}
                else:
                    nowy = {"pl_pytania": [],           "pl_odpowiedzi": [],
                            "en_pytania": [czesci[0]],  "en_odpowiedzi": [czesci[1]]}
                baza.append(nowy)
                print("Program: Nauczyłem się nowej odpowiedzi!" if jezyk == "pl"
                      else "Program: Learned a new answer!")
            else:
                raise ValueError("Zły format")
        except Exception:
            print("Program: Użyj: /teach pytanie | odpowiedz" if jezyk == "pl"
                  else "Program: Use: /teach question | answer")
        continue

    # --- szukanie odpowiedzi w bazie ---
    odpowiedz = znajdz_odpowiedz(pytanie)

    if odpowiedz:
        msg(f"Program: {odpowiedz}")
    else:
        msg("Program: Nie znam odpowiedzi." if jezyk == "pl" else "Program: I don't know.")
