# main.py
import datetime
from family_member_manager import FamilyMemberManager

# --- Main execution block for testing ---
if __name__ == "__main__":
    manager = FamilyMemberManager() # Get the singleton instance

    print("\n--- Adding Family Members ---")
    member1 = manager.add_member("משה", "כהן", datetime.date(1980, 5, 15), "אבא")
    member2 = manager.add_member("שרה", "לוי", datetime.date(1982, 6, 10), "אמא")
    member3 = manager.add_member("דוד", "ישראלי", datetime.date(2010, 1, 25), "בן")
    member4 = manager.add_member("חנה", "אברהם", datetime.date(1955, 6, 7), "דודה")
    member5 = manager.add_member("יוסף", "חיים", datetime.date(1995, 12, 1), "בן דוד")

    print(f"Added: {member1.get_full_name()} (ID: {member1.id})")
    print(f"Added: {member2.get_full_name()} (ID: {member2.id})")
    print(f"Added: {member3.get_full_name()} (ID: {member3.id})")
    print(f"Added: {member4.get_full_name()} (ID: {member4.id})")
    print(f"Added: {member5.get_full_name()} (ID: {member5.id})")

    print("\n--- All Family Members ---")
    for member in manager.get_all_members():
        print(f"{member.id}: {member.get_full_name()}, Born: {member.birth_date}, Relationship: {member.relationship}")

    print("\n--- Getting a specific member (ID 1) ---")
    retrieved_member = manager.get_member(1)
    if retrieved_member:
        print(f"Retrieved: {retrieved_member.get_full_name()}")
        print(f"Birthday: {retrieved_member.get_next_birthday()}")
        print(f"Days until next birthday: {retrieved_member.get_days_until_next_birthday()}")
    else:
        print("Member with ID 1 not found.")

    print("\n--- Updating a member (ID 1 - Moshe) ---")
    updated_member = manager.update_member(1, first_name="משה-אלי", notes="אוהב שוקולד")
    if updated_member:
        print(f"Updated member: {updated_member.get_full_name()}, Notes: {updated_member.notes}")
    else:
        print("Member with ID 1 not found for update.")

    print("\n--- Adding gift ideas for Sarah (ID 2) ---")
    sarah = manager.get_member(2)
    if sarah:
        sarah.add_gift_idea("ספר חדש")
        sarah.add_gift_idea("צמיד כסף")
        # Since add_gift_idea modifies the member object directly,
        # we need to ensure the manager saves the updated state.
        # The manager's update_member method handles saving,
        # but for simple direct modifications to the object,
        # we might need a specific 'save_member_changes' or rely on other operations.
        # For this in-memory JSON example, calling _save_data() directly is an option
        # or better, consider adding a save_member(member_object) method to manager.
        # For simplicity, if add_gift_idea was a method on manager, it would handle saving.
        # For now, rely on other operations or a direct save for testing.
        manager._save_data() # Manually trigger a save to persist gift ideas

        print(f"{sarah.get_full_name()}'s gift ideas: {sarah.gift_ideas}")
    else:
        print("Sarah not found.")

    print("\n--- Upcoming Birthdays (next 60 days) ---")
    # Simulate a specific date for testing upcoming birthdays.
    # Current date in Israel is June 5, 2025.
    # So we'll use a date close to existing birthdays for demonstration.
    test_date = datetime.date(2025, 6, 5) # Today's date for consistent testing
    upcoming_birthdays = manager.get_upcoming_birthdays(days_in_advance=60, current_date=test_date)
    print(f"Current date for testing: {test_date}")
    if upcoming_birthdays:
        for member in upcoming_birthdays:
            days_left = member.get_days_until_next_birthday(test_date)
            # Handle cases where birthday is today (0 days left) or in the future
            days_text = "היום!" if days_left == 0 else f"עוד {days_left} ימים"
            print(f"- {member.get_full_name()} ({member.relationship})'s birthday is on {member.birth_date.strftime('%d/%m')}. ({days_text})")
    else:
        print("No upcoming birthdays in the next 60 days.")

    print("\n--- Searching for 'לוי' ---")
    search_results = manager.search_members("לוי")
    for member in search_results:
        print(f"Found: {member.get_full_name()}, Relationship: {member.relationship}")

    print("\n--- Deleting a member (ID 3 - David) ---")
    if manager.delete_member(3):
        print("David (ID 3) deleted successfully.")
    else:
        print("David (ID 3) not found for deletion.")

    print("\n--- All Family Members after deletion ---")
    for member in manager.get_all_members():
        print(f"{member.id}: {member.get_full_name()}")

    # To demonstrate loading data again, create a new manager instance
    # This will load from the family_members.json file
    print("\n--- Creating a new manager instance to load data ---")
    new_manager = FamilyMemberManager()
    print("Members after loading (should reflect previous saves):")
    for member in new_manager.get_all_members():
        print(f"{member.id}: {member.get_full_name()}")