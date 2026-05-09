# Kysymysfunktiot eri lentokentille

def get_question(icao):
    """Palauttaa kysymyksen ja oikean vastauksen annetulle ICAO-koodille"""
    questions = {
        "EGLL": {
            "question": "Mikä on Lontoon tunnettu historiallinen kellotorni, jota kutsutaan Elizabeth Toweriksi?",
            "options": ["A) Big Ben", "B) Ben Ten", "C) Big Ten", "D) London Eye"],
            "correct": "A"
        },
        "CYYZ": {
            "question": "Mikä on Kanadan Pääkaupunki?",
            "options": ["A) Toronto", "B) Edmonton", "C) Vancouver", "D) Ottawa"],
            "correct": "D"
        },
        "EDDF": {
            "question": "Mikä joki virtaa Saksan läpi ja on yksi Euroopan pisimmistä?",
            "options": ["A) Rein", "B) Tonava", "C) Seine", "D) Thames"],
            "correct": "A"
        },
        "EHAM": {
            "question": "Kuka tunnetuista taiteilijoista on Alankomaista kotoisin?",
            "options": ["A) Leonardo Da Vinci", "B) Ludwig van Beethoven", "C) Vincent van Gogh"],
            "correct": "C"
        },
        "FAOR": {
            "question": "Mikä vuori sijaitsee Etelä-Afrikassa?",
            "options": ["A) Pöytävuori", "B) Kilimanjaro", "C) Mount Kenya", "D) Drakensberg"],
            "correct": "A"
        },
        "HECA": {
            "question": "Mikä oli muinaisen Egyptin kirjoitusjärjestelmä?",
            "options": ["A) Kyrillinen", "B) Latinan kirjaimet", "C) Hieroglyfit"],
            "correct": "C"
        },
        "KDFW": {
            "question": "Mikä on Texasin osavaltion lempinimi?",
            "options": ["A) The Golden State", "B) The Sunshine State", "C) The Lone Star State", "D) The Empire State"],
            "correct": "C"
        },
        "KJFK": {
            "question": "Mikä oli New Yorkin alkuperäinen nimi, ennen kuin englantilaiset valtasivat kaupungin?",
            "options": ["A) York", "B) New Amsterdam", "C) Gotham"],
            "correct": "B"
        },
        "KLAX": {
            "question": "Mikä kuuluisa Los Angelesissa sijaitseva katu on tunnettu elokuvateollisuudestaan ja tähtien nimillä koristellusta jalkakäytävästään?",
            "options": ["A) Sunset Boulevard", "B) Mulholland Drive", "C) Hollywood Boulevard", "D) Rodeo Drive"],
            "correct": "C"
        },
        "LEMD": {
            "question": "Missä Espanjan kaupungissa järjestetään kuuluisa La Tomatina, tomaattisota?",
            "options": ["A) Valencia", "B) Zaragoza", "C) Sevilla", "D) Buñol"],
            "correct": "D"
        },
        "LFPG": {
            "question": "Mikä näistä nähtävyyksistä ei ole Pariisissa?",
            "options": ["A) Notre Dame", "B) Riemukaari", "C) Louvre", "D) Mont Blanc"],
            "correct": "D"
        },
        "NZAA": {
            "question": "Mikä Uuden-Seelannin alkuperäiskansa on nimeltään?",
            "options": ["A) Maori", "B) Aboriginaalit", "C) Inuit", "D) Samoalaiset"],
            "correct": "A"
        },
        "OMDB": {
            "question": "Mikä on maailman korkeimman rakennuksen nimi, joka sijaitsee Dubaissa?",
            "options": [],
            "correct": "burj khalifa",
            "type": "text"
        },
        "RJTT": {
            "question": "Minkä vuoren voi nähdä Tokiosta?",
            "options": ["A) Hakkoda", "B) Fuji", "C) Everest", "D) Hekla"],
            "correct": "B"
        },
        "RKSI": {
            "question": "Mikä on Etelä-Korean kansallisruoka?",
            "options": ["A) Sushi", "B) Pho", "C) Ramen", "D) Kimchi"],
            "correct": "D"
        },
        "SBGR": {
            "question": "Mikä on Brasilian suurin ja tunnetuin sademetsä, joka tunnetaan suuresta monimuotoisuudestaan?",
            "options": [],
            "correct": "amazon",
            "type": "text"
        },
        "SKBO": {
            "question": "Mikä on Kolumbian virallinen kieli?",
            "options": ["A) Portugali", "B) Ranska", "C) Englanti", "D) Espanja"],
            "correct": "D"
        },
        "YSSY": {
            "question": "Mikä on Australian Pääkaupunki?",
            "options": ["A) Sydney", "B) Canberra", "C) Melbourne", "D) Brisbane"],
            "correct": "B"
        },
        "ZBAA": {
            "question": "Mikä kuuluisa historiallinen palatsialue sijaitsee Pekingissä?",
            "options": ["A) Kesäpalatsi", "B) Kielletty kaupunki", "C) Taivaallisen rauhan aukio", "D) Ming-haudat"],
            "correct": "B"
        }
    }
    
    return questions.get(icao, None)
# minor update

