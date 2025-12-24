"""Tests für die Move-Klasse."""

import json
import pytest
from move import Move
from pieces import Pawn, Rook, Queen, King


class TestMoveToJson:
    """Tests für die to_json-Methode der Move-Klasse."""
    
    def test_simple_move_to_json(self):
        """Test einfacher Zug ohne Schlagen."""
        # Erstelle einen Pawn
        pawn = Pawn('white', (6, 4))
        
        # Erstelle einen einfachen Move
        move = Move(
            from_pos=(6, 4),
            to_pos=(4, 4),
            piece=pawn
        )
        
        # Konvertiere zu JSON
        json_str = move.to_json()
        
        # Parse JSON zurück
        move_dict = json.loads(json_str)
        
        # Prüfe Attribute
        assert move_dict['from_pos'] == [6, 4]
        assert move_dict['to_pos'] == [4, 4]
        assert move_dict['piece']['type'] == 'Pawn'
        assert move_dict['piece']['color'] == 'white'
        assert move_dict['piece']['notation'] == 'P'
        assert move_dict['captured'] is None
        assert move_dict['promotion'] is None
        assert move_dict['castelling'] is None
        assert move_dict['en_passant'] is False
    
    def test_capture_move_to_json(self):
        """Test Schlagzug."""
        # Erstelle Figuren
        pawn = Pawn('white', (4, 4))
        captured_pawn = Pawn('black', (3, 5))
        
        # Erstelle Schlagzug
        move = Move(
            from_pos=(4, 4),
            to_pos=(3, 5),
            piece=pawn,
            captured=captured_pawn
        )
        
        # Konvertiere zu JSON
        json_str = move.to_json()
        move_dict = json.loads(json_str)
        
        # Prüfe captured Attribut
        assert move_dict['captured'] is not None
        assert move_dict['captured']['type'] == 'Pawn'
        assert move_dict['captured']['color'] == 'black'
        assert move_dict['captured']['notation'] == 'P'
    
    def test_promotion_move_to_json(self):
        """Test Bauernumwandlung."""
        # Erstelle Pawn
        pawn = Pawn('white', (1, 4))
        
        # Erstelle Promotion Move
        move = Move(
            from_pos=(1, 4),
            to_pos=(0, 4),
            piece=pawn,
            promotion='Q'
        )
        
        # Konvertiere zu JSON
        json_str = move.to_json()
        move_dict = json.loads(json_str)
        
        # Prüfe promotion
        assert move_dict['promotion'] == 'Q'
    
    def test_castling_move_to_json(self):
        """Test Rochade."""
        # Erstelle König und Turm
        king = King('white', (7, 4))
        rook = Rook('white', (7, 7))
        
        # Erstelle Rochade Move
        move = Move(
            from_pos=(7, 4),
            to_pos=(7, 6),
            piece=king,
            castelling=rook
        )
        
        # Konvertiere zu JSON
        json_str = move.to_json()
        move_dict = json.loads(json_str)
        
        # Prüfe castelling
        assert move_dict['castelling'] is not None
        assert move_dict['castelling']['type'] == 'Rook'
        assert move_dict['castelling']['color'] == 'white'
    
    def test_en_passant_move_to_json(self):
        """Test En Passant."""
        # Erstelle Pawns
        pawn = Pawn('white', (3, 4))
        captured_pawn = Pawn('black', (3, 5))
        
        # Erstelle En Passant Move
        move = Move(
            from_pos=(3, 4),
            to_pos=(2, 5),
            piece=pawn,
            captured=captured_pawn,
            en_passant=True
        )
        
        # Konvertiere zu JSON
        json_str = move.to_json()
        move_dict = json.loads(json_str)
        
        # Prüfe en_passant
        assert move_dict['en_passant'] is True
        assert move_dict['captured'] is not None
    
    def test_json_is_valid_string(self):
        """Test dass to_json einen validen JSON-String zurückgibt."""
        pawn = Pawn('white', (6, 4))
        move = Move(from_pos=(6, 4), to_pos=(4, 4), piece=pawn)
        
        json_str = move.to_json()
        
        # Sollte ein String sein
        assert isinstance(json_str, str)
        
        # Sollte valides JSON sein (wirft Exception falls nicht)
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
