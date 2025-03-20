import sqlite3
import json
from pathlib import Path

class Database:
    def __init__(self):
        self.db_path = Path("game_data.db")
        self.connection = None
        if not self.db_path.exists():
            self.init_database()
        
    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection
        
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
        
    def reset_database(self):
        self.close()
        
        if self.db_path.exists():
            try:
                self.db_path.unlink()
            except PermissionError:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM matches")
                cursor.execute("DELETE FROM players")
                cursor.execute("DELETE FROM settings")
                conn.commit()
                return
        
        self.init_database()
        
    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    total_games INTEGER DEFAULT 0,
                    total_wins INTEGER DEFAULT 0,
                    best_score INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player1_id INTEGER,
                    player2_id INTEGER,
                    player1_score INTEGER,
                    player2_score INTEGER,
                    winner_id INTEGER,
                    player1_class TEXT,
                    player2_class TEXT,
                    duration INTEGER,
                    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player1_id) REFERENCES players (id),
                    FOREIGN KEY (player2_id) REFERENCES players (id),
                    FOREIGN KEY (winner_id) REFERENCES players (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    settings_data TEXT
                )
            ''')
            
            conn.commit()
            
    def add_player(self, name):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO players (name) VALUES (?)',
                    (name,)
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor.execute('SELECT id FROM players WHERE name = ?', (name,))
            return cursor.fetchone()[0]
            
    def get_player(self, player_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, total_games, total_wins, best_score
                FROM players WHERE id = ?
            ''', (player_id,))
            return cursor.fetchone()
            
    def get_player_by_name(self, name):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, total_games, total_wins, best_score
                FROM players WHERE name = ?
            ''', (name,))
            return cursor.fetchone()
            
    def save_match(self, match_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO matches (
                    player1_id, player2_id, player1_score, player2_score,
                    winner_id, player1_class, player2_class, duration
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match_data['player1_id'], match_data['player2_id'],
                match_data['player1_score'], match_data['player2_score'],
                match_data['winner_id'], match_data['player1_class'],
                match_data['player2_class'], match_data['duration']
            ))
            
            for player_id in [match_data['player1_id'], match_data['player2_id']]:
                cursor.execute('''
                    UPDATE players 
                    SET total_games = total_games + 1,
                        total_wins = total_wins + CASE 
                            WHEN id = ? THEN 1 
                            ELSE 0 
                        END,
                        best_score = CASE
                            WHEN id = ? AND ? > best_score THEN ?
                            ELSE best_score
                        END
                    WHERE id = ?
                ''', (
                    match_data['winner_id'],
                    player_id,
                    match_data['player1_score'] if player_id == match_data['player1_id'] else match_data['player2_score'],
                    match_data['player1_score'] if player_id == match_data['player1_id'] else match_data['player2_score'],
                    player_id
                ))
            
            conn.commit()
            
    def get_leaderboard(self, limit=10):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    name,
                    total_games,
                    total_wins,
                    best_score,
                    CASE 
                        WHEN total_games > 0 THEN ROUND(CAST(total_wins AS FLOAT) / total_games * 100, 1)
                        ELSE 0 
                    END as win_rate
                FROM players
                WHERE total_games > 0
                ORDER BY win_rate DESC, total_wins DESC
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
            
    def save_settings(self, settings):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            settings_json = json.dumps(settings)
            cursor.execute('''
                INSERT OR REPLACE INTO settings (id, settings_data)
                VALUES (1, ?)
            ''', (settings_json,))
            conn.commit()
            
    def load_settings(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT settings_data FROM settings WHERE id = 1')
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None 

    def get_all_players(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM players ORDER BY name')
            return cursor.fetchall() 

    def reset_scores(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE players 
                SET total_games = 0,
                    total_wins = 0,
                    best_score = 0
            ''')
            cursor.execute('DELETE FROM matches')
            conn.commit() 