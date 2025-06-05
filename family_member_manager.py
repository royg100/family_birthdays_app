# family_member_manager.py
import datetime
import json
from family_member import FamilyMember # Import the FamilyMember class

class FamilyMemberManager:
    """
    Manages FamilyMember objects, including adding, retrieving, updating, and deleting.
    Uses an in-memory list for storage initially, with basic save/load to JSON.
    """
    _instance = None # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FamilyMemberManager, cls).__new__(cls)
            cls._instance._members = []
            cls._instance._next_id = 1 # Simple ID generator
            cls._instance._data_file = 'family_members.json' # File for persistence
            cls._instance._load_data()
        return cls._instance

    def _generate_id(self) -> int:
        """Generates a unique ID for a new family member."""
        new_id = self._next_id
        self._next_id += 1
        return new_id

    def _save_data(self):
        """Saves the current family members data to a JSON file."""
        try:
            with open(self._data_file, 'w', encoding='utf-8') as f:
                # Convert list of FamilyMember objects to list of dictionaries
                json.dump([member.to_dict() for member in self._members], f, indent=4, ensure_ascii=False)
            print(f"Data saved to {self._data_file}")
        except Exception as e:
            print(f"Error saving data: {e}")

    def _load_data(self):
        """Loads family members data from a JSON file."""
        try:
            with open(self._data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert list of dictionaries back to list of FamilyMember objects
                self._members = [FamilyMember.from_dict(d) for d in data]
                # Ensure _next_id is higher than any existing ID
                if self._members:
                    self._next_id = max(member.id for member in self._members if member.id is not None) + 1
                print(f"Data loaded from {self._data_file}")
        except FileNotFoundError:
            print(f"No data file '{self._data_file}' found. Starting with empty data.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from '{self._data_file}'. Starting with empty data.")
            self._members = [] # Reset if file is corrupted
        except Exception as e:
            print(f"An unexpected error occurred while loading data: {e}")
            self._members = [] # Reset on unexpected errors

    def add_member(self, first_name: str, last_name: str, birth_date: datetime.date,
                   relationship: str = None, notes: str = None) -> FamilyMember:
        """Adds a new family member to the system."""
        member = FamilyMember(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            relationship=relationship,
            notes=notes,
            member_id=self._generate_id()
        )
        self._members.append(member)
        self._save_data() # Save after every change for simplicity
        return member

    def get_member(self, member_id: int) -> FamilyMember | None:
        """Retrieves a family member by their ID."""
        for member in self._members:
            if member.id == member_id:
                return member
        return None

    def get_all_members(self) -> list[FamilyMember]:
        """Returns a list of all family members."""
        return list(self._members) # Return a copy to prevent external modification of the internal list

    def update_member(self, member_id: int, **kwargs) -> FamilyMember | None:
        """
        Updates an existing family member's details.

        Args:
            member_id (int): The ID of the member to update.
            **kwargs: Keyword arguments for fields to update (e.g., first_name="חדש").
        Returns:
            FamilyMember | None: The updated FamilyMember object, or None if not found.
        """
        member = self.get_member(member_id)
        if member:
            for key, value in kwargs.items():
                if hasattr(member, key):
                    if key == "birth_date" and isinstance(value, str):
                        try:
                            value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                        except ValueError:
                            print(f"Warning: Could not parse birth_date '{value}'. Skipping update for this field.")
                            continue
                    setattr(member, key, value)
                else:
                    print(f"Warning: Field '{key}' does not exist on FamilyMember and cannot be updated.")
            self._save_data()
            return member
        return None

    def delete_member(self, member_id: int) -> bool:
        """Deletes a family member by their ID."""
        initial_count = len(self._members)
        self._members = [member for member in self._members if member.id != member_id]
        if len(self._members) < initial_count:
            self._save_data()
            return True
        return False

    def get_upcoming_birthdays(self, days_in_advance: int = 30, current_date: datetime.date = None) -> list[FamilyMember]:
        """
        Returns a list of family members with upcoming birthdays.

        Args:
            days_in_advance (int): How many days in advance to look for birthdays.
            current_date (datetime.date, optional): The date to calculate from. Defaults to today's date.

        Returns:
            list[FamilyMember]: A list of FamilyMember objects with upcoming birthdays, sorted by date.
        """
        if current_date is None:
            current_date = datetime.date.today()

        upcoming = []
        for member in self._members:
            days_until = member.get_days_until_next_birthday(current_date)
            # Include birthdays that are *today* (days_until == 0) up to days_in_advance
            if 0 <= days_until <= days_in_advance:
                upcoming.append((days_until, member)) # Store with days_until for sorting

        # Sort by days until birthday
        upcoming.sort(key=lambda x: x[0])
        return [member for days, member in upcoming] # Return just the member objects

    def search_members(self, query: str) -> list[FamilyMember]:
        """
        Searches for family members by first name, last name, or relationship.
        """
        query_lower = query.lower().strip()
        results = []
        for member in self._members:
            if (query_lower in member.first_name.lower() or
                query_lower in member.last_name.lower() or
                (member.relationship and query_lower in member.relationship.lower())):
                results.append(member)
        return results