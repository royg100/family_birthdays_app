# app.py
import streamlit as st
import datetime
from family_member_manager import FamilyMemberManager
from family_member import FamilyMember # חשוב לוודא ש FamilyMember מיובא כאן גם

# אתחול המנהל (זה יטען נתונים מקובץ family_members.json)
manager = FamilyMemberManager()

def display_member_card(member: FamilyMember):
    """מציג פרטים של בן משפחה בודד בפורמט כרטיס."""
    st.subheader(f"🎉 {member.get_full_name()}")
    st.write(f"**תאריך לידה:** {member.birth_date.strftime('%d/%m/%Y')}")
    st.write(f"**קשר משפפתי:** {member.relationship if member.relationship else 'לא הוגדר'}")

    next_birthday = member.get_next_birthday()
    days_until = member.get_days_until_next_birthday()

    if days_until == 0:
        st.success(f"🎊 **יום הולדת היום!**")
    elif days_until == 1:
        st.warning(f"🎂 **יום הולדת מחר!**")
    else:
        st.info(f"🎈 יום הולדת ב- {next_birthday.strftime('%d/%m')} (עוד {days_until} ימים)")

    st.write(f"**הערות:** {member.notes if member.notes else 'אין'}")

    st.write("**רעיונות למתנות:**")
    if member.gift_ideas:
        for idea in member.gift_ideas:
            st.markdown(f"- {idea}")
    else:
        st.write("אין רעיונות למתנות כרגע.")

    if st.button(f"ערוך פרטים / מתנות של {member.first_name}", key=f"edit_member_{member.id}"):
        st.session_state.current_page = "edit_member"
        st.session_state.editing_member_id = member.id
        st.rerun() # הפעלה מחדש כדי להחליף עמוד


def add_edit_member_form():
    """טופס להוספה או עריכה של בן משפחה."""
    editing_id = st.session_state.get("editing_member_id", None)
    member_to_edit = None
    
    # אתחול רעיונות למתנות ב-session state אם לא קיימים
    if editing_id and f"gift_ideas_for_edit_{editing_id}" not in st.session_state:
        member_to_edit = manager.get_member(editing_id)
        st.session_state[f"gift_ideas_for_edit_{editing_id}"] = list(member_to_edit.gift_ideas) if member_to_edit else []
    elif not editing_id and "gift_ideas_for_new_member" not in st.session_state:
        st.session_state["gift_ideas_for_new_member"] = []
    
    # קביעת רשימת רעיונות למתנות לשימוש בהתאם למצב הוספה/עריכה
    current_gift_ideas_key = f"gift_ideas_for_edit_{editing_id}" if editing_id else "gift_ideas_for_new_member"
    current_gift_ideas = st.session_state[current_gift_ideas_key]

    if editing_id:
        member_to_edit = manager.get_member(editing_id)
        st.title(f"ערוך את {member_to_edit.get_full_name()}")
    else:
        st.title("הוסף בן משפפה חדש")

    # זהו הטופס החיצוני לפרטי בן המשפחה
    with st.form("member_details_form"): # נתנו לו שם ייחודי
        first_name = st.text_input("שם פרטי", value=member_to_edit.first_name if member_to_edit else "")
        last_name = st.text_input("שם משפחה", value=member_to_edit.last_name if member_to_edit else "")
        
        default_birth_date = member_to_edit.birth_date if member_to_edit else datetime.date(2000, 1, 1)
        # שימו לב: השתמשתי ב-key קבוע עבור בורר התאריך
        birth_date = st.date_input("תאריך לידה", value=default_birth_date, min_value=datetime.date(1900,1,1), key="birth_date_input")
        
        relationship = st.text_input("קשר משפחתי (אופציונלי)", value=member_to_edit.relationship if member_to_edit else "")
        notes = st.text_area("הערות (אופציונלי)", value=member_to_edit.notes if member_to_edit else "")

        st.subheader("רעיונות למתנות")
        # שימו לב: השתמשתי ב-key קבוע עבור שדה קלט הרעיון החדש
        new_gift_idea = st.text_input("הוסף רעיון חדש למתנה", key="new_gift_idea_input")
        
        # הצגת רעיונות מתנה קיימים עם אפשרות הסרה
        if current_gift_ideas:
            st.write("רעיונות קיימים:")
            for i, idea in enumerate(current_gift_ideas):
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.write(f"- {idea}")
                with col2:
                    # תיבת סימון להסרה, עם key ייחודי המבוסס על האינדקס ו-ID החבר/חדש
                    st.session_state[f"remove_idea_checkbox_{i}_{editing_id or 'new'}"] = st.checkbox(
                        "הסר", 
                        value=st.session_state.get(f"remove_idea_checkbox_{i}_{editing_id or 'new'}", False),
                        key=f"remove_idea_checkbox_{i}_{editing_id or 'new'}"
                    )
        st.markdown("---") # מפריד

        # כפתור השליחה הראשי לכל טופס הפרטים של בן המשפחה
        submitted = st.form_submit_button("שמור בן משפחה")

        if submitted:
            # שלב 1: הסרת רעיונות מתנה מסומנים
            ideas_after_removal = []
            for i, idea in enumerate(current_gift_ideas):
                # בדוק את המצב של תיבת הסימון ב-session_state
                if not st.session_state.get(f"remove_idea_checkbox_{i}_{editing_id or 'new'}", False):
                    ideas_after_removal.append(idea)
            
            # שלב 2: הוספת רעיון מתנה חדש אם הוזן
            if new_gift_idea and new_gift_idea.strip() and new_gift_idea.strip() not in ideas_after_removal:
                ideas_after_removal.append(new_gift_idea.strip())
            
            try:
                if editing_id:
                    # עדכון חבר קיים
                    manager.update_member(
                        editing_id,
                        first_name=first_name,
                        last_name=last_name,
                        birth_date=birth_date,
                        relationship=relationship,
                        notes=notes
                    )
                    # עדכון רעיונות למתנות על ידי הגדרה ישירה של הרשימה על אובייקט החבר
                    updated_member_obj = manager.get_member(editing_id)
                    if updated_member_obj:
                        updated_member_obj.gift_ideas = ideas_after_removal # עדכון הרשימה אחרי הסרה והוספה
                        manager._save_data() # שמירה ידנית לאחר שינוי רשימת רעיונות מתנה
                    st.success(f"הפרטים של {first_name} עודכנו בהצלחה!")
                else:
                    # הוספת חבר חדש
                    new_member = manager.add_member(
                        first_name=first_name,
                        last_name=last_name,
                        birth_date=birth_date,
                        relationship=relationship,
                        notes=notes
                    )
                    # הוספת רעיונות למתנות לחבר החדש אם ישנם
                    if ideas_after_removal: # אם יש רעיונות אחרי הוספה/הסרה
                        for idea in ideas_after_removal:
                            new_member.add_gift_idea(idea) # add_gift_idea כבר דואג לא להוסיף כפילויות
                        manager._save_data() # שמירה לאחר הוספת רעיונות למתנות
                    st.success(f"{first_name} {last_name} נוסף בהצלחה!")

                # ניקוי מצב ה-session עבור עריכה וחזרה לדף הראשי
                st.session_state.current_page = "home"
                st.session_state.editing_member_id = None
                
                # ניקוי משתני ה-session state של רעיונות מתנה ספציפיים לטופס
                if f"gift_ideas_for_edit_{editing_id}" in st.session_state:
                    del st.session_state[f"gift_ideas_for_edit_{editing_id}"]
                if "gift_ideas_for_new_member" in st.session_state:
                    del st.session_state["gift_ideas_for_new_member"]
                
                # ניקוי תיבות הסימון של הסרת רעיונות
                # חשוב לנקות את ה-session state של כל ה-checkboxes שהיו בטופס
                for i, _ in enumerate(current_gift_ideas): # השתמש ברשימה המקורית כי ייתכן שהיא לא השתנתה
                    key_to_clear = f"remove_idea_checkbox_{i}_{editing_id or 'new'}"
                    if key_to_clear in st.session_state:
                        del st.session_state[key_to_clear]


                st.rerun() # הפעלה מחדש להצגת הרשימה המעודכנת
            except ValueError as e:
                st.error(f"שגיאה: {e}")
            except TypeError as e:
                st.error(f"שגיאה: {e}")


def list_all_members_page():
    """מציג עמוד עם כל בני המשפחה, עם חיפוש וסינון."""
    st.title("כל בני המשפפה")

    search_query = st.text_input("חפש לפי שם או קשר משפחתי", "")

    all_members = manager.get_all_members()

    if search_query:
        members_to_display = manager.search_members(search_query)
    else:
        members_to_display = sorted(all_members, key=lambda m: m.get_full_name()) # מיין אלפביתית

    if not members_to_display:
        st.info("לא נמצאו בני משפחה התואמים לחיפוש.")
        return

    for member in members_to_display:
        with st.expander(f"{member.get_full_name()} ({member.relationship})"):
            st.write(f"**תאריך לידה:** {member.birth_date.strftime('%d/%m/%Y')}")
            st.write(f"**יום הולדת הבא:** {member.get_next_birthday().strftime('%d/%m/%Y')} (עוד {member.get_days_until_next_birthday()} ימים)")
            st.write(f"**הערות:** {member.notes if member.notes else 'אין'}")
            
            st.write("**רעיונות למתנות:**")
            if member.gift_ideas:
                for idea in member.gift_ideas:
                    st.markdown(f"- {idea}")
            else:
                st.write("אין רעיונות למתנות כרגע.")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"ערוך", key=f"edit_all_{member.id}"):
                    st.session_state.current_page = "edit_member"
                    st.session_state.editing_member_id = member.id
                    st.rerun()
            with col2:
                # בעת מחיקה, כדאי להוסיף אישור כדי למנוע מחיקה בשוגג
                if st.button(f"מחק", key=f"delete_all_{member.id}"):
                    # הוספת תיבת אישור למחיקה
                    st.session_state[f"confirm_delete_{member.id}"] = True # שמור ב-session state את הצורך באישור
                    st.rerun() # הפעלה מחדש כדי להציג את הודעת האישור

    # לולאה נפרדת לטיפול באישור מחיקה כדי לא להפריע ללולאת התצוגה
    for member in members_to_display:
        if st.session_state.get(f"confirm_delete_{member.id}", False):
            st.warning(f"האם אתה בטוח שברצונך למחוק את {member.get_full_name()}?")
            col_confirm1, col_confirm2 = st.columns(2)
            with col_confirm1:
                if st.button("כן, מחק!", key=f"execute_delete_{member.id}"):
                    manager.delete_member(member.id)
                    st.success(f"{member.get_full_name()} נמחק בהצלחה.")
                    del st.session_state[f"confirm_delete_{member.id}"] # נקה את דגל האישור
                    st.rerun() # הפעלה מחדש כדי לרענן את הרשימה
            with col_confirm2:
                if st.button("בטל", key=f"cancel_delete_{member.id}"):
                    del st.session_state[f"confirm_delete_{member.id}"] # נקה את דגל האישור
                    st.rerun()


def settings_page():
    """עמוד להגדרות תזכורות (מקום מילוי כרגע)."""
    st.title("הגדרות תזכורות")
    st.warning("פונקציונליות התזכורות האוטומטיות עדיין בפיתוח! (דורש פתרון צד שרת)")
    st.write("כאן תוכל להגדיר מתי ואיך תרצה לקבל תזכורות על ימי הולדת.")
    
    st.checkbox("הפעל תזכורות לאימייל", value=False)
    st.number_input("שלח תזכורת X ימים לפני יום ההולדת", min_value=1, max_value=30, value=7)
    st.checkbox("שלח תזכורת ביום יום ההולדת", value=True)
    
    st.button("שמור הגדרות")


# --- לוגיקת האפליקציה הראשית ---
st.sidebar.title("ניווט")
if st.sidebar.button("🏠 דף הבית"):
    st.session_state.current_page = "home"
    st.session_state.editing_member_id = None
    # נקה שדות טופס פוטנציאליים ב-session state
    if "new_gift_idea_input" in st.session_state: del st.session_state["new_gift_idea_input"]
    if "birth_date_input" in st.session_state: del st.session_state["birth_date_input"]
    st.rerun()

if st.sidebar.button("➕ הוסף בן משפחה"):
    st.session_state.current_page = "add_member"
    st.session_state.editing_member_id = None
    # נקה שדות טופס פוטנציאליים ב-session state
    if "new_gift_idea_input" in st.session_state: del st.session_state["new_gift_idea_input"]
    if "birth_date_input" in st.session_state: del st.session_state["birth_date_input"]
    st.rerun()

if st.sidebar.button("👥 כל בני המשפחה"):
    st.session_state.current_page = "list_all"
    st.session_state.editing_member_id = None
    # נקה שדות טופס פוטנציאליים ב-session state
    if "new_gift_idea_input" in st.session_state: del st.session_state["new_gift_idea_input"]
    if "birth_date_input" in st.session_state: del st.session_state["birth_date_input"]
    st.rerun()

if st.sidebar.button("⚙️ הגדרות"):
    st.session_state.current_page = "settings"
    st.session_state.editing_member_id = None
    # נקה שדות טופס פוטנציאליים ב-session state
    if "new_gift_idea_input" in st.session_state: del st.session_state["new_gift_idea_input"]
    if "birth_date_input" in st.session_state: del st.session_state["birth_date_input"]
    st.rerun()


# אתחל את מצב ה-session עבור ניווט בעמודים אם עדיין לא הוגדר
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# --- ניתוב עמודים ---
if st.session_state.current_page == "home":
    st.title("🎂 מנהל ימי הולדת משפפתיים")
    
    st.subheader("ימי הולדת קרובים")
    current_date_for_display = datetime.date.today() # תמיד השתמש בתאריך של היום לתצוגה
    upcoming = manager.get_upcoming_birthdays(days_in_advance=90, current_date=current_date_for_display)

    if upcoming:
        for member in upcoming:
            days_left = member.get_days_until_next_birthday(current_date_for_display)
            if days_left == 0:
                st.write(f"**🎉 {member.get_full_name()}** - **יום הולדת היום!** 🥳")
            elif days_left == 1:
                st.write(f"**🎂 {member.get_full_name()}** - **יום הולדת מחר!**")
            else:
                st.write(f"**🎈 {member.get_full_name()}** - יום הולדת ב- {member.get_next_birthday(current_date_for_display).strftime('%d/%m')} (עוד {days_left} ימים)")
            
            # כפתור לצפייה/עריכת פרטים ישירות מדף הבית עבור כל יום הולדת קרוב
            if st.button(f"פרטים / ערוך {member.first_name}", key=f"home_edit_{member.id}"):
                st.session_state.current_page = "edit_member"
                st.session_state.editing_member_id = member.id
                st.rerun()
            st.markdown("---") # מפריד

    else:
        st.info("אין ימי הולדת קרובים ב-90 הימים הבאים. הוסף בני משפחה כדי להתחיל!")

elif st.session_state.current_page == "add_member" or st.session_state.current_page == "edit_member":
    add_edit_member_form()
elif st.session_state.current_page == "list_all":
    list_all_members_page()
elif st.session_state.current_page == "settings":
    settings_page()