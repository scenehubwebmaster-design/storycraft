"""
Quick setup script for Campaign Journal System

Runs all setup steps in order:
1. Database migration
2. Portrait batch generation (optional)
3. Instructions for starting backend
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and show progress."""
    print(f"\n{'='*80}")
    print(f"  {description}")
    print('='*80)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.returncode != 0:
            print(f"❌ Command failed with code {result.returncode}")
            return False
        print(f"✅ {description} - Success!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "="*80)
    print("  🚀 CAMPAIGN JOURNAL SYSTEM - QUICK SETUP")
    print("="*80)
    print("\nThis script will:")
    print("  1. Run database migrations")
    print("  2. Optionally generate NPC portraits")
    print("  3. Show next steps")
    
    # Step 1: Check if we're in backend directory
    backend_dir = Path(__file__).parent
    if not (backend_dir / "database.py").exists():
        print("\n❌ Error: Not in backend directory!")
        print(f"Current directory: {backend_dir}")
        print("Please run this from: e:\\storycraft\\backend\\")
        sys.exit(1)
    
    # Step 2: Run migration
    print("\n" + "="*80)
    print("  STEP 1: Database Migration")
    print("="*80)
    
    proceed = input("\nRun database migration? [Y/n]: ").strip().lower()
    if proceed != 'n':
        # Change to parent directory and run as module
        import os
        os.chdir(backend_dir.parent)
        run_command(
            "python -m backend.migrate_add_journal_and_npc_enhancements",
            "Running database migration"
        )
        os.chdir(backend_dir)
    else:
        print("⏭️  Skipping migration")
    
    # Step 3: Portrait generation
    print("\n" + "="*80)
    print("  STEP 2: NPC Portrait Generation (Optional)")
    print("="*80)
    
    portraits = input("\nGenerate NPC portraits? [y/N]: ").strip().lower()
    if portraits == 'y':
        # Ask for options
        print("\nOptions:")
        print("  1. Dry run (show what would be generated)")
        print("  2. Generate all")
        print("  3. Generate for specific campaign")
        print("  4. Generate with limit")
        
        choice = input("Choice [1]: ").strip() or "1"
        
        if choice == "1":
            run_command(
                "python -m backend.batch_generate_npc_portraits --dry-run",
                "Dry run - showing NPCs to process"
            )
        elif choice == "2":
            confirm = input("This may take a while. Continue? [y/N]: ").strip().lower()
            if confirm == 'y':
                run_command(
                    "python -m backend.batch_generate_npc_portraits",
                    "Generating all NPC portraits"
                )
        elif choice == "3":
            campaign_id = input("Campaign ID: ").strip()
            run_command(
                f"python -m backend.batch_generate_npc_portraits --campaign-id {campaign_id}",
                f"Generating portraits for campaign {campaign_id}"
            )
        elif choice == "4":
            limit = input("Limit (e.g., 5): ").strip()
            run_command(
                f"python -m backend.batch_generate_npc_portraits --limit {limit}",
                f"Generating up to {limit} portraits"
            )
    else:
        print("⏭️  Skipping portrait generation")
    
    # Step 4: Show next steps
    print("\n" + "="*80)
    print("  🎉 SETUP COMPLETE!")
    print("="*80)
    
    print("\n📋 Next Steps:")
    print("\n1. Restart your backend server:")
    print("   cd e:\\storycraft\\backend")
    print("   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    
    print("\n2. Open DMChat in your browser")
    
    print("\n3. Test the Journal:")
    print("   • Start or select a campaign")
    print("   • Click the Journal icon (📖) in the toolbar")
    print("   • Browse NPCs, quests, locations, and timeline")
    
    print("\n4. (Optional) Review/regenerate portraits:")
    print("   cd e:\\storycraft")
    print("   python -m backend.review_npc_portraits --campaign-id 1")
    
    print("\n5. Test auto-logging:")
    print("   • Send a message with NPC introductions")
    print("   • Check journal for auto-created entries")
    
    print("\n6. Test checkpoint previews:")
    print("   • Create a checkpoint")
    print("   • View details to see journal information")
    
    print("\n📚 Documentation:")
    print("   • JOURNAL_SCRIPTS_README.md - Script usage guide")
    print("   • CAMPAIGN_JOURNAL_SYSTEM.md - Full architecture guide")
    print("   • CAMPAIGN_JOURNAL_IMPLEMENTATION.md - What was built")
    
    print("\n✨ Enjoy your enhanced campaign journal system!")


if __name__ == "__main__":
    main()
