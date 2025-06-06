import datetime
import base64

class GiftHistoryEntry:
    """
    מייצג רשומה בודדת בהיסטוריית המתנות.
    """
    def __init__(self, date_given: datetime.date, description: str, occasion: str = None):
        if not isinstance(date_given, datetime.date):
            raise TypeError("Date given must be a datetime.date object.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Gift description cannot be empty.")
        
        self.date_given = date_given
        self.description = description.strip()
        self.occasion = occasion.strip() if occasion else None

    def to_dict(self):
        """ממיר אובייקט GiftHistoryEntry למילון."""
        return {
            "date_given": self.date_given.strftime("%Y-%m-%d"),
            "description": self.description,
            "occasion": self.occasion
        }

    @staticmethod
    def from_dict(data: dict):
        """יוצר אובייקט GiftHistoryEntry ממילון."""
        return GiftHistoryEntry(
            date_given=datetime.datetime.strptime(data['date_given'], "%Y-%m-%d").date(),
            description=data['description'],
            occasion=data.get('occasion')
        )

    def __repr__(self):
        return f"GiftHistoryEntry(date={self.date_given}, desc='{self.description}')"


class FamilyMember:
    """
    מייצג בן משפחה בודד במערכת ניהול ימי הולדת.
    """
    def __init__(self, first_name: str, last_name: str, birth_date: datetime.date,
                 relationship: str = None, notes: str = None, member_id: int = None,
                 profile_picture_base64: str = None):
        """
        Initializes a FamilyMember object.

        Args:
            first_name (str): The first name of the family member.
            last_name (str): The last name of the family member.
            birth_date (datetime.date): The birth date of the family member.
            relationship (str, optional): The family relationship (e.g., "אח", "אמא"). Defaults to None.
            notes (str, optional): Any additional notes about the family member. Defaults to None.
            member_id (int, optional): Unique ID for the family member. If None, it will be generated.
            profile_picture_base64 (str, optional): Base64 encoded string of the profile picture. Defaults to None.
        """
        if not isinstance(first_name, str) or not first_name.strip():
            raise ValueError("First name cannot be empty.")
        if not isinstance(last_name, str) or not last_name.strip():
            raise ValueError("Last name cannot be empty.")
        if not isinstance(birth_date, datetime.date):
            raise TypeError("Birth date must be a datetime.date object.")

        self.id = member_id
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.birth_date = birth_date
        self.relationship = relationship.strip() if relationship else None
        self.notes = notes.strip() if notes else None
        self.gift_ideas = [] # List to store gift ideas
        self.gift_history = [] # Changed to store GiftHistoryEntry objects
        self.profile_picture_base64 = profile_picture_base64

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
        if idea and idea.strip() and idea.strip() not in self.gift_ideas:
            self.gift_ideas.append(idea.strip())

    def remove_gift_idea(self, idea: str):
        """Removes a gift idea from the member's list."""
        if idea in self.gift_ideas:
            self.gift_ideas.remove(idea)

    def add_gift_to_history(self, date_given: datetime.date, description: str, occasion: str = None):
        """מוסיף מתנה שניתנה להיסטוריה."""
        new_entry = GiftHistoryEntry(date_given, description, occasion)
        self.gift_history.append(new_entry)
        # ניתן למיין כאן את הרשימה לפי תאריך אם רוצים
        self.gift_history.sort(key=lambda x: x.date_given, reverse=True)

    def remove_gift_from_history(self, index: int):
        """מסיר מתנה מההיסטוריה לפי אינדקס."""
        if 0 <= index < len(self.gift_history):
            del self.gift_history[index]

    def update_gift_in_history(self, index: int, date_given: datetime.date, description: str, occasion: str = None):
        """מעדכן מתנה קיימת בהיסטוריה."""
        if 0 <= index < len(self.gift_history):
            self.gift_history[index].date_given = date_given
            self.gift_history[index].description = description
            self.gift_history[index].occasion = occasion
            self.gift_history.sort(key=lambda x: x.date_given, reverse=True)


    def __repr__(self):
        return f"FamilyMember(id={self.id}, name='{self.get_full_name()}', birth_date={self.birth_date})"

    def to_dict(self):
        """Converts the FamilyMember object to a dictionary for serialization."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birth_date": self.birth_date.strftime("%Y-%m-%d"),
            "relationship": self.relationship,
            "notes": self.notes,
            "gift_ideas": self.gift_ideas,
            "gift_history": [entry.to_dict() for entry in self.gift_history],
            "profile_picture_base64": self.profile_picture_base64
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
            member_id=data.get('id'),
            profile_picture_base64=data.get('profile_picture_base64')
        )
        member.gift_ideas = data.get('gift_ideas', [])
        member.gift_history = [GiftHistoryEntry.from_dict(d) for d in data.get('gift_history', [])]
        return member