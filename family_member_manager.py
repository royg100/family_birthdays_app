import datetime
import json
from family_member import FamilyMember, GiftHistoryEntry

class FamilyMemberManager:
    """
    מנהל אובייקטי FamilyMember, כולל הוספה, שליפה, עדכון ומחיקה.
    משתמש ברשימה בזיכרון לאחסון ראשוני, עם שמירה/טעינה בסיסית ל-JSON.
    """
    _instance = None # מופע Singleton

    # ודא ששורה זו נראית כך:
    def __new__(cls, data_file='family_members.json'): 
        if cls._instance is None:
            cls._instance = super(FamilyMemberManager, cls).__new__(cls)
            cls._instance._members = []
            cls._instance._next_id = 1
            # ודא ששורה זו קיימת ומגדירה את _data_file
            cls._instance._data_file = data_file 
            cls._instance._load_data()
        return cls._instance

    def _generate_id(self) -> int:
        """יוצר מזהה ייחודי עבור בן משפחה חדש."""
        new_id = self._next_id
        self._next_id += 1
        return new_id

    def _save_data(self):
        """שומר את נתוני בני המשפחה הנוכחיים לקובץ JSON."""
        try:
            with open(self._data_file, 'w', encoding='utf-8') as f:
                json.dump([member.to_dict() for member in self._members], f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"שגיאה בשמירת נתונים: {e}")

    def _load_data(self):
        """טוען נתוני בני משפחה מקובץ JSON."""
        try:
            with open(self._data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._members = [FamilyMember.from_dict(d) for d in data]
                if self._members:
                    self._next_id = max(member.id for member in self._members if member.id is not None) + 1
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            print(f"שגיאת פענוח JSON מ- '{self._data_file}'. מתחיל עם נתונים ריקים.")
            self._members = []
        except Exception as e:
            print(f"אירעה שגיאה בלתי צפויה בטעינת נתונים: {e}")
            self._members = []

    def add_member(self, first_name: str, last_name: str, birth_date: datetime.date,
                   relationship: str = None, notes: str = None) -> FamilyMember:
        """מוסיף בן משפחה חדש למערכת."""
        member = FamilyMember(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            relationship=relationship,
            notes=notes,
            member_id=self._generate_id()
        )
        self._members.append(member)
        self._save_data()
        return member

    def get_member(self, member_id: int) -> FamilyMember | None:
        """שולף בן משפחה לפי המזהה שלו."""
        for member in self._members:
            if member.id == member_id:
                return member
        return None

    def get_all_members(self) -> list[FamilyMember]:
        """מחזיר רשימה של כל בני המשפחה."""
        return list(self._members)

    def update_member(self, member_id: int, **kwargs) -> FamilyMember | None:
        """
        מעדכן פרטים של בן משפחה קיים.

        Args:
            member_id (int): המזהה של החבר לעדכון.
            **kwargs: ארגומנטים מילוניים עבור שדות לעדכון (לדוגמה, first_name="חדש").
        Returns:
            FamilyMember | None: אובייקט FamilyMember המעודכן, או None אם לא נמצא.
        """
        member = self.get_member(member_id)
        if member:
            for key, value in kwargs.items():
                if hasattr(member, key):
                    if key == "birth_date" and isinstance(value, str):
                        try:
                            value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                        except ValueError:
                            print(f"אזהרה: לא ניתן לנתח תאריך לידה '{value}'. מדלג על עדכון שדה זה.")
                            continue
                    setattr(member, key, value)
            self._save_data()
            return member
        return None

    def delete_member(self, member_id: int) -> bool:
        """מוחק בן משפחה לפי המזהה שלו."""
        initial_count = len(self._members)
        self._members = [member for member in self._members if member.id != member_id]
        if len(self._members) < initial_count:
            self._save_data()
            return True
        return False

    def get_upcoming_birthdays(self, days_in_advance: int = 30, current_date: datetime.date = None) -> list[FamilyMember]:
        """
        מחזיר רשימה של בני משפחה עם ימי הולדת קרובים.

        Args:
            days_in_advance (int): כמה ימים מראש לחפש ימי הולדת.
            current_date (datetime.date, optional): התאריך שממנו יש לחשב. ברירת מחדל: התאריך של היום.

        Returns:
            list[FamilyMember]: רשימה של אובייקטי FamilyMember עם ימי הולדת קרובים, ממוינים לפי תאריך.
        """
        if current_date is None:
            current_date = datetime.date.today()

        upcoming = []
        for member in self._members:
            days_until = member.get_days_until_next_birthday(current_date)
            if 0 <= days_until <= days_in_advance:
                upcoming.append((days_until, member))

        upcoming.sort(key=lambda x: x[0])
        return [member for days, member in upcoming]

    def search_members(self, query: str) -> list[FamilyMember]:
        """
        מחפש בני משפחה לפי שם פרטי, שם משפחה, קשר משפחתי, הערות, או רעיונות למתנות.
        """
        query_lower = query.lower().strip()
        results = []
        for member in self._members:
            search_string = f"{member.first_name} {member.last_name} {member.relationship or ''} {member.notes or ''} {' '.join(member.gift_ideas or '')}".lower()
            if query_lower in search_string:
                results.append(member)
        return results