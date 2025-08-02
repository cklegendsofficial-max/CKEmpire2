#!/usr/bin/env python3
"""
Alembic migration runner for CK Empire Builder
"""

import os
import sys
import subprocess
from pathlib import Path

def run_migration_command(command: str) -> bool:
    """Run an Alembic command"""
    try:
        # Change to backend directory
        backend_dir = Path(__file__).parent
        os.chdir(backend_dir)
        
        # Run alembic command
        result = subprocess.run(
            ["alembic"] + command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✅ {command} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {command} failed:")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Please install it with: pip install alembic")
        return False

def main():
    """Main migration runner"""
    print("🏛️ CK Empire Builder - Database Migration Tool")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("alembic.ini").exists():
        print("❌ alembic.ini not found. Please run this script from the backend directory.")
        return
    
    # Show current status
    print("\n📊 Current migration status:")
    run_migration_command("current")
    
    # Show available migrations
    print("\n📋 Available migrations:")
    run_migration_command("history")
    
    # Ask user what to do
    print("\n🔧 Migration options:")
    print("1. Run all pending migrations (upgrade)")
    print("2. Create a new migration (revision --autogenerate)")
    print("3. Downgrade to previous version (downgrade)")
    print("4. Show current status (current)")
    print("5. Show migration history (history)")
    print("6. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            print("\n🔄 Running pending migrations...")
            if run_migration_command("upgrade head"):
                print("✅ All migrations completed successfully!")
            break
        elif choice == "2":
            message = input("Enter migration message: ").strip()
            if message:
                print(f"\n📝 Creating new migration: {message}")
                run_migration_command(f'revision --autogenerate -m "{message}"')
            else:
                print("❌ Migration message is required")
            break
        elif choice == "3":
            print("\n⬇️ Downgrading to previous version...")
            run_migration_command("downgrade -1")
            break
        elif choice == "4":
            print("\n📊 Current migration status:")
            run_migration_command("current")
            break
        elif choice == "5":
            print("\n📋 Migration history:")
            run_migration_command("history")
            break
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main() 