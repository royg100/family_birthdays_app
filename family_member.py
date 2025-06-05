# family_member.py
import datetime

class FamilyMember:
    """
    Represents a single family member in the birthday management system.
    """
    def __init__(self, first_name: str, last_name: str, birth_date: datetime.date,
                 relationship: str = None, notes: str = None, member_id: int = None):
        """
        Initializes a FamilyMember object.

        Args:
            first_name (str): The first name of the family member.
            last_name (str): The last name of the family member.
            birth_date (datetime.date): The birth date of the family member.
            relationship (str, optional): The family relationship (e.g., "אח", "אמא"). Defaults to None.
            notes (str, optional): Any additional notes about the family member. Defaults to None.
            member_id (int, optional): Unique ID for the family member. If None, it will be generated.
        """
        if not isinstance(first_name, str) or not first_name.strip():
            raise ValueError("First name cannot be empty.")
        if not isinstance(last_name, str) or not last_name.strip():
            raise ValueError("Last name cannot be empty.")
        if not isinstance(birth_date, datetime.date):
            raise TypeError("Birth date must be a datetime.date object.")

        self.id = member_id # Will be set by our data store later, or generated upon creation
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.birth_date = birth_date
        self.relationship = relationship.strip() if relationship else None
        self.notes = notes.strip() if notes else None
        self.gift_ideas = [] # List to store gift ideas
        self.gift_history = [] # List to store past gifts (optional for now)

    def get_full_name(self) -> str:
        """Returns the full name of the family member."""
        return f"{self.first_name} {self.last_name}"

    def get_next_birthday(self, current_date: datetime.date = None) -> datetime.date:
        """
        Calculates the date of the next birthday for the family member.

        Args:
            current_date (datetime.date, optional): The date to calculate from.
                                                    Defaults to today's date if None.
        Returns:
            datetime.date: The date of the next birthday.
        """
        if current_date is None:
            current_date = datetime.date.today()

        birth_month = self.birth_date.month
        birth_day = self.birth_date.day

        # Try this year's birthday
        next_birthday_this_year = datetime.date(current_date.year, birth_month, birth_day)

        if next_birthday_this_year >= current_date:
            return next_birthday_this_year
        else:
            # Birthday has already passed this year, so it's next year
            return datetime.date(current_date.year + 1, birth_month, birth_day)

    def get_days_until_next_birthday(self, current_date: datetime.date = None) -> int:
        """
        Calculates the number of days until the next birthday.

        Args:
            current_date (datetime.date, optional): The date to calculate from.
                                                    Defaults to today's date if None.
        Returns:
            int: Number of days until the next birthday.
        """
        if current_date is None:
            current_date = datetime.date.today()

        next_birthday = self.get_next_birthday(current_date)
        time_until_birthday = next_birthday - current_date
        return time_until_birthday.days

    def add_gift_idea(self, idea: str):
        """Adds a gift idea to the member's list."""
        if idea and idea.strip() not in self.gift_ideas:
            self.gift_ideas.append(idea.strip())

    def remove_gift_idea(self, idea: str):
        """Removes a gift idea from the member's list."""
        if idea in self.gift_ideas:
            self.gift_ideas.remove(idea)

    def __repr__(self):
        return f"FamilyMember(id={self.id}, name='{self.get_full_name()}', birth_date={self.birth_date})"

    def to_dict(self):
        """Converts the FamilyMember object to a dictionary for serialization."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birth_date": self.birth_date.strftime("%Y-%m-%d"), # Convert date to string
            "relationship": self.relationship,
            "notes": self.notes,
            "gift_ideas": self.gift_ideas,
            "gift_history": self.gift_history # If we implement this
        }

    @staticmethod
    def from_dict(data: dict):
        """Creates a FamilyMember object from a dictionary."""
        member = FamilyMember(
            first_name=data['first_name'],
            last_name=data['last_name'],
            birth_date=datetime.datetime.strptime(data['birth_date'], "%Y-%m-%d").date(),
            relationship=data.get('relationship'),
            notes=data.get('notes'),
            member_id=data.get('id')
        )
        member.gift_ideas = data.get('gift_ideas', [])
        member.gift_history = data.get('gift_history', [])
        return member