"""Test script to show what character stats the AI DM will see"""
import sys
import os

# Run from backend directory
if __name__ == "__main__":
    # Add parent directory to path for imports
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, parent_dir)

def main():
    from backend.database import SessionLocal
    from backend.models import GameSession
    from backend.game.dm_chat_handler import DMChatHandler
    
    db = SessionLocal()
    try:
        # Get most recent game session
        game_session = db.query(GameSession).order_by(GameSession.id.desc()).first()
        
        if not game_session:
            print("No game sessions found in database.")
            return
        
        print(f"Testing context for Game Session #{game_session.id}")
        print(f"Campaign: {game_session.campaign_name}\n")
        
        # Create DM handler
        handler = DMChatHandler(db)
        
        # Build and display context
        context = handler._build_game_context(game_session)
        
        print("=" * 60)
        print("GAME CONTEXT SENT TO AI DM")
        print("=" * 60)
        print(context)
        print("=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
