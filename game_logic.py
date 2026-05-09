import uuid
import random
from geopy.distance import geodesic
import database
import questions
# minor update

# Valid lentokentät
VALID_AIRPORTS = ["EFHK", "EGLL", "LFPG", "RJTT", "OMDB", "EDDF",
                  "EHAM", "LEMD", "KLAX", "KJFK", "CYYZ", "KDFW",
                  "ZBAA", "RKSI", "YSSY", "NZAA", "SBGR", "FAOR",
                  "HECA", "SKBO"]

def get_all_airports_list():
    """Palauttaa listan kaikista pelin lentokentistä"""
    return VALID_AIRPORTS

def calculate_distance(lat1, lon1, lat2, lon2):
    """Laskee etäisyyden GeoPy:n avulla kilometreinä"""
    paikka1 = (lat1, lon1)
    paikka2 = (lat2, lon2)
    return geodesic(paikka1, paikka2).kilometers

def assign_treasure(pelaaja_id, yhteys):
    """Arpoo aarteen sijainnin pelaajalle"""
    kursori = yhteys.cursor()
    
    # Tarkistetaan onko pelaajalla jo aarre
    kursori.execute("SELECT airport_ident, found FROM treasure WHERE player_id = %s", (pelaaja_id,))
    tulos = kursori.fetchone()
    if tulos is not None:
        kursori.close()
        return tulos[0]  # Palautetaan olemassa oleva aarre
    
    # Hae pelaajan käydyt kentät
    kursori.execute("SELECT käyty_kentät FROM game WHERE id = %s", (pelaaja_id,))
    tulos = kursori.fetchone()
    käyty_kentät = tulos[0].split(",") if tulos and tulos[0] else []
    
    # Valitse aarre kentistä joissa ei ole vielä käyty
    mahdolliset = [k for k in VALID_AIRPORTS if k not in käyty_kentät]
    
    if not mahdolliset:
        mahdolliset = VALID_AIRPORTS  # jos kaikki käyty, valitaan satunnainen
    
    aarre_kenttä = random.choice(mahdolliset)
    
    # Tallennetaan treasure-tauluun
    kursori.execute("""
        INSERT INTO treasure (player_id, airport_ident, found)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE airport_ident = %s, found = %s
    """, (pelaaja_id, aarre_kenttä, False, aarre_kenttä, False))
    
    yhteys.commit()
    kursori.close()
    return aarre_kenttä
#..
def check_game_end(pelaaja_id, yhteys):
    """Tarkistaa pelin lopputilan ja palauttaa status-dictin"""
    kursori = yhteys.cursor()
    kursori.execute(
        "SELECT Motivaatio_taso, has_treasure, location FROM game WHERE id = %s",
        (pelaaja_id,)
    )
    tulos = kursori.fetchone()
    kursori.close()
    
    if not tulos:
        return {"status": "error", "message": "Pelaajaa ei löytynyt tietokannasta."}
    
    motivaatio_taso, has_treasure, location = tulos
    
    # Tappio: motivaatio loppui
    if motivaatio_taso is None or motivaatio_taso <= 0:
        return {
            "status": "lost",
            "message": "Menetit motivaationsi kokonaan ja masentuit. Peli päättyi."
        }
    
    # Voitto: superpallo löydetty, palattu Helsinkiin, motivaatio riittävä
    if motivaatio_taso >= 10 and has_treasure == 1 and location == "EFHK":
        return {
            "status": "won",
            "message": "Onnistuit tuomaan Sir Pommin takaisin kotiin! Sir Pomm oli aivan entisellään. Voitit pelin!"
        }
    
    return {"status": "playing"}

def fly_to(pelaaja_id, target_icao, yhteys):
    """Lentää pelaajan annettuun lentokenttään"""
    if target_icao not in VALID_AIRPORTS:
        return {
            "success": False,
            "message": "Tuntematon ICAO-koodi"
        }
    
    # Hae nykyinen sijainti ja kuljettu matka
    game_state = database.get_player_game_state(pelaaja_id, yhteys)
    if not game_state:
        return {
            "success": False,
            "message": "Pelaajaa ei löytynyt tietokannasta"
        }
    
    nykyinen_sijainti, matkustettu_matka, _, _, _, _ = game_state
    
    # Laske etäisyys
    lat1, lon1 = database.get_airport_coordinates(nykyinen_sijainti, yhteys)
    lat2, lon2 = database.get_airport_coordinates(target_icao, yhteys)

    if None in (lat1, lon1, lat2, lon2):
        # Tarkempi virheilmoitus, jotta nähdään kummalta kentältä koordinaatit puuttuvat
        missing = []
        if lat1 is None or lon1 is None:
            missing.append(nykyinen_sijainti)
        if lat2 is None or lon2 is None:
            missing.append(target_icao)

        return {
            "success": False,
            "message": f"Koordinaattitietoja ei löytynyt kentälle: {', '.join(missing)}"
        }
    
    etaisyys = calculate_distance(lat1, lon1, lat2, lon2)
    matkustettu_matka += etaisyys
    
    # Päivitä sijainti
    database.update_player_location(pelaaja_id, target_icao, matkustettu_matka, yhteys)
    
    # Päivitä käydyt kentät
    käyty_kentät_str = game_state[4] if game_state[4] else ""
    käyty_kentät = käyty_kentät_str.split(",") if käyty_kentät_str else []
    if target_icao not in käyty_kentät:
        käyty_kentät.append(target_icao)
        database.update_visited_airports(pelaaja_id, käyty_kentät, yhteys)
    
    # Tarkista aarre
    treasure_location = database.get_treasure_location(pelaaja_id, yhteys)
    found_treasure = (target_icao == treasure_location)
    
    if found_treasure:
        database.update_treasure_found(pelaaja_id, yhteys)
    
    # Tarkista voitto
    game_end = check_game_end(pelaaja_id, yhteys)
    
    return {
        "success": True,
        "location": target_icao,
        "distance": round(etaisyys, 0),
        "total_distance": round(matkustettu_matka, 0),
        "found_treasure": found_treasure,
        "game_end": game_end
    }

def update_motivation(pelaaja_id, määrä, yhteys):
    """Päivittää pelaajan motivaatiotason"""
    kursori = yhteys.cursor()
    kursori.execute("UPDATE game SET Motivaatio_taso = Motivaatio_taso + %s WHERE id = %s", (määrä, pelaaja_id))
    yhteys.commit()
    kursori.close()
    
    # Tarkista pelin loppu
    return check_game_end(pelaaja_id, yhteys)

def check_answer(icao, answer, pelaaja_id, yhteys):
    """Tarkistaa vastauksen ja päivittää motivaation"""
    question_data = questions.get_question(icao)
    
    if not question_data:
        return {
            "success": False,
            "message": "Tällä kentällä ei ole kysymystä"
        }
    
    correct_answer = question_data["correct"].strip().lower()
    user_answer = answer.strip().lower()
    
    if user_answer == correct_answer:
        game_end = update_motivation(pelaaja_id, 1, yhteys)
        return {
            "success": True,
            "correct": True,
            "message": "Oikein! Sait 1 pisteen.",
            "game_end": game_end
        }
    else:
        game_end = update_motivation(pelaaja_id, -1, yhteys)
        return {
            "success": True,
            "correct": False,
            "message": "Väärin! Menetit 1 pisteen.",
            "game_end": game_end
        }

def create_or_get_player(username, yhteys, reset=False):
    """Luo uuden pelaajan tai hakee olemassa olevan"""
    kursori = yhteys.cursor()
    
    # Tarkista onko käyttäjä jo olemassa
    kursori.execute("SELECT id, käyty_kentät FROM game WHERE screen_name = %s", (username,))
    tulos = kursori.fetchone()
    
    if tulos and not reset:
        # Pelaaja on olemassa, palautetaan ID
        pelaaja_id = tulos[0]
        käyty_kentät = tulos[1].split(",") if tulos[1] else []
        kursori.close()
        
        # Varmista että aarre on arvottu
        assign_treasure(pelaaja_id, yhteys)
        
        return {
            "player_id": pelaaja_id,
            "is_new": False,
            "visited_airports": käyty_kentät
        }
    
    # Luodaan uusi pelaaja tai nollataan vanha
    if tulos and reset:
        pelaaja_id = tulos[0]
        # Nollaa peli
        reset_sql = """
            UPDATE game
            SET location = %s,
                has_treasure = %s,
                Motivaatio_taso = %s,
                käyty_kentät = %s,
                matkustettu_matka = %s
            WHERE id = %s
        """
        kursori.execute(reset_sql, ('EFHK', False, 10, '', 0, pelaaja_id))
        yhteys.commit()
        
        # Poista vanha aarre
        kursori.execute("DELETE FROM treasure WHERE player_id = %s", (pelaaja_id,))
        yhteys.commit()
    else:
        # Uusi pelaaja
        pelaaja_id = str(uuid.uuid4())
        kursori.execute("""
            INSERT INTO game (id, screen_name, location, has_treasure, Motivaatio_taso, käyty_kentät, matkustettu_matka)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (pelaaja_id, username, 'EFHK', False, 10, '', 0))
        yhteys.commit()
    
    kursori.close()
    
    # Arvo aarre
    assign_treasure(pelaaja_id, yhteys)
    
    return {
        "player_id": pelaaja_id,
        "is_new": True,
        "visited_airports": []
    }

def get_available_airports(pelaaja_id, yhteys):
    """Palauttaa listan saatavilla olevista lentokentistä"""
    game_state = database.get_player_game_state(pelaaja_id, yhteys)
    if not game_state:
        return []
    
    käyty_kentät_str = game_state[4] if game_state[4] else ""
    käyty_kentät = käyty_kentät_str.split(",") if käyty_kentät_str else []
    
    all_airports = database.get_all_airports(yhteys)
    available = [(ident, name) for ident, name, _, _ in all_airports if ident not in käyty_kentät]
    
    return available
