from flask import Flask, render_template, request, jsonify
import database
import game_logic
import questions

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game_page():
    return render_template('game.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Luo uuden pelin tai hakee olemassa olevan pelaajan"""
    try:
        # Turvallinen JSON-parsaus
        data = request.get_json(silent=True) or {}
        username = str(data.get('username', '')).strip()
        reset = bool(data.get('reset', False))

        if not username:
            return jsonify({"success": False, "message": "Käyttäjänimi vaaditaan"}), 400

        yhteys = database.get_connection()
        try:
            result = game_logic.create_or_get_player(username, yhteys, reset)
            game_state = database.get_player_game_state(result["player_id"], yhteys)

            return jsonify({
                "success": True,
                "player_id": result["player_id"],
                "is_new": result["is_new"],
                "location": game_state[0] if game_state else "EFHK",
                "motivation": game_state[2] if game_state else 10,
                "has_treasure": bool(game_state[3]) if game_state else False,
                "total_distance": game_state[1] if game_state else 0,
                "visited_airports": result["visited_airports"]
            })
        finally:
            yhteys.close()
    except Exception as e:
        # Varmistetaan, että palautetaan aina JSON, ei HTML-virhesivua
        return jsonify({"success": False, "message": f"Virhe new_game-reitillä: {e}"}), 500

@app.route('/api/fly', methods=['POST'])
def fly():
    """Lentää pelaajan annettuun lentokenttään"""
    data = request.json
    player_id = data.get('player_id')
    icao = data.get('icao', '').upper().strip()
    
    if not player_id or not icao:
        return jsonify({"success": False, "message": "player_id ja icao vaaditaan"}), 400
    
    yhteys = database.get_connection()
    try:
        result = game_logic.fly_to(player_id, icao, yhteys)
        
        if result["success"]:
            # Hae päivitetty pelitila
            game_state = database.get_player_game_state(player_id, yhteys)
            result["motivation"] = game_state[2] if game_state else 10
            result["has_treasure"] = bool(game_state[3]) if game_state else False
            
            # Tarkista onko kysymys saatavilla
            question_data = questions.get_question(icao)
            result["has_question"] = question_data is not None
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        yhteys.close()

@app.route('/api/get_question/<icao>', methods=['GET'])
def get_question(icao):
    """Hakee kysymyksen annetulle lentokentälle"""
    question_data = questions.get_question(icao.upper())
    
    if not question_data:
        return jsonify({"success": False, "message": "Tällä kentällä ei ole kysymystä"}), 404
    
    return jsonify({
        "success": True,
        "question": question_data["question"],
        "options": question_data["options"],
        "type": question_data.get("type", "multiple_choice")
    })

@app.route('/api/answer', methods=['POST'])
def answer():
    """Tarkistaa vastauksen ja päivittää motivaation"""
    data = request.json
    player_id = data.get('player_id')
    icao = data.get('icao', '').upper().strip()
    answer = data.get('answer', '').strip()
    
    if not all([player_id, icao, answer]):
        return jsonify({"success": False, "message": "player_id, icao ja answer vaaditaan"}), 400
    
    yhteys = database.get_connection()
    try:
        result = game_logic.check_answer(icao, answer, player_id, yhteys)
        
        if result["success"]:
            # Hae päivitetty pelitila
            game_state = database.get_player_game_state(player_id, yhteys)
            result["motivation"] = game_state[2] if game_state else 10
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        yhteys.close()

@app.route('/api/game_state', methods=['GET'])
def game_state():
    """Hakee pelaajan pelitilan"""
    player_id = request.args.get('player_id')
    
    if not player_id:
        return jsonify({"success": False, "message": "player_id vaaditaan"}), 400
    
    yhteys = database.get_connection()
    try:
        game_state = database.get_player_game_state(player_id, yhteys)
        
        if not game_state:
            return jsonify({"success": False, "message": "Pelaajaa ei löytynyt"}), 404
        
        käyty_kentät_str = game_state[4] if game_state[4] else ""
        käyty_kentät = käyty_kentät_str.split(",") if käyty_kentät_str else []
        
        return jsonify({
            "success": True,
            "location": game_state[0],
            "total_distance": game_state[1],
            "motivation": game_state[2],
            "has_treasure": bool(game_state[3]),
            "visited_airports": käyty_kentät,
            "player_name": game_state[5]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        yhteys.close()

@app.route('/api/airports', methods=['GET'])
def get_airports():
    """Hakee saatavilla olevat lentokentät"""
    player_id = request.args.get('player_id')
    
    if not player_id:
        return jsonify({"success": False, "message": "player_id vaaditaan"}), 400
    
    yhteys = database.get_connection()
    try:
        available = game_logic.get_available_airports(player_id, yhteys)
        all_airports = database.get_all_airports(yhteys)
        
        # Muotoile kaikki lentokentät koordinaatteineen..
        airports_data = []
        for ident, name, lat, lon in all_airports:
            airports_data.append({
                "icao": ident,
                "name": name,
                "latitude": float(lat) if lat else None,
                "longitude": float(lon) if lon else None,
                "available": ident in [a[0] for a in available]
            })
        
        return jsonify({
            "success": True,
            "airports": airports_data,
            "available": [{"icao": a[0], "name": a[1]} for a in available]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        yhteys.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
