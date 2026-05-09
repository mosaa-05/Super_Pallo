import mysql.connector

def get_connection():
    """Luo tietokantayhteyden"""
    return mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        database='flight_game',
        user='root',
        password='1234',
        autocommit=True
    )

def get_all_airports(yhteys):
    """Hakee kaikki pelin lentokentät"""
    sql = ("SELECT ident, name, latitude_deg, longitude_deg FROM airport WHERE ident IN("
           "'EGLL', 'LFPG', 'RJTT', 'OMDB', 'EDDF', 'EHAM', 'LEMD', 'KLAX', "
           "'KJFK', 'CYYZ', 'KDFW', 'ZBAA', 'RKSI', 'YSSY', 'NZAA', 'SBGR', "
           "'FAOR', 'HECA', 'SKBO', 'EFHK'"
           ");")
    kursori = yhteys.cursor()
    kursori.execute(sql)
    airports = kursori.fetchall()
    kursori.close()
    return airports

def get_airport_coordinates(ICAO, yhteys):
    """Hakee lentokentän koordinaatit"""
    kursori = yhteys.cursor()
    kursori.execute("SELECT latitude_deg, longitude_deg FROM airport WHERE ident = %s", (ICAO,))
    tulos = kursori.fetchone()
    kursori.close()
    if tulos:
        return tulos[0], tulos[1]
    else:
        return None, None

def get_player_game_state(pelaaja_id, yhteys):
    """Hakee pelaajan pelitilan"""
    kursori = yhteys.cursor()
    kursori.execute(
        "SELECT location, matkustettu_matka, Motivaatio_taso, has_treasure, käyty_kentät, screen_name FROM game WHERE id = %s",
        (pelaaja_id,)
    )
    tulos = kursori.fetchone()
    kursori.close()
    return tulos

def update_player_location(pelaaja_id, icao, matkustettu_matka, yhteys):
    """Päivittää pelaajan sijainnin ja kuljetun matkan"""
    kursori = yhteys.cursor()
    sql = '''UPDATE game 
             SET location = %s, matkustettu_matka = %s 
             WHERE id = %s'''
    kursori.execute(sql, (icao, matkustettu_matka, pelaaja_id))
    yhteys.commit()
    kursori.close()

def update_visited_airports(pelaaja_id, käyty_kentät, yhteys):
    """Päivittää käydyt kentät"""
    kursori = yhteys.cursor()
    kursori.execute(
        "UPDATE game SET käyty_kentät = %s WHERE id = %s",
        (",".join(käyty_kentät), pelaaja_id)
    )
    yhteys.commit()
    kursori.close()

def update_treasure_found(pelaaja_id, yhteys):
    """Merkitsee aarteen löydetyksi"""
    kursori = yhteys.cursor()
    kursori.execute(
        "UPDATE game SET has_treasure = %s WHERE id = %s",
        (True, pelaaja_id)
    )
    yhteys.commit()
    kursori.close()

def get_treasure_location(pelaaja_id, yhteys):
    """Hakee aarteen sijainnin"""
    kursori = yhteys.cursor()
    kursori.execute("SELECT airport_ident FROM treasure WHERE player_id = %s", (pelaaja_id,))
    tulos = kursori.fetchone()
    kursori.close()
    return tulos[0] if tulos else None

