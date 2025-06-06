# app.py
import streamlit as st
import datetime
import calendar
from family_member_manager import FamilyMemberManager
from family_member import FamilyMember, GiftHistoryEntry
import base64

# אתחול המנהל (זה יטען נתונים מ-family_members.json)
manager = FamilyMemberManager(data_file='family_members.json') #

# פונקציות עזר לטיפול בתמונות (המרה ל-Base64 ובחזרה)
def get_image_as_base64(image_bytes): #
    """ממיר בייטים של תמונה למחרוזת Base64.""" #
    if image_bytes: #
        try: #
            return base64.b64encode(image_bytes).decode('utf-8') #
        except Exception as e: #
            st.error(f"שגיאה בהמרת תמונה ל-Base64: {e}") #
            return None #
    return None #

def get_base64_as_image(base64_string): #
    """ממיר מחרוזת Base64 לבייטים של תמונה.""" #
    if base64_string: #
        try: #
            return base64.b64decode(base64_string) #
        except Exception as e: #
            st.error(f"שגיאה בהמרת Base64 לתמונה. ייתכן שהתמונה פגומה. {e}") #
            return None #
    return None #

def display_member_card(member: FamilyMember): #
    """מציג פרטים של בן משפחה בודד בפורמט כרטיס.""" #
    st.subheader(f"🎉 {member.get_full_name()}") #
    
    if member.profile_picture_base64: #
        image_data = get_base64_as_image(member.profile_picture_base64) #
        if image_data: #
            st.image(image_data, width=150) #

    st.write(f"**תאריך לידה:** {member.birth_date.strftime('%d/%m/%Y')}") #
    st.write(f"**קשר משפפתי:** {member.relationship if member.relationship else 'לא הוגדר'}") #

    next_birthday = member.get_next_birthday() #
    days_until = member.get_days_until_next_birthday() #

    if days_until == 0: #
        st.success(f"🎊 **יום הולדת היום!**") #
    elif days_until == 1: #
        st.warning(f"🎂 **יום הולדת מחר!**") #
    else: #
        st.info(f"🎈 יום הולדת ב- {next_birthday.strftime('%d/%m')} (עוד {days_until} ימים)") #

    st.write(f"**הערות:** {member.notes if member.notes else 'אין'}") #

    st.write("**רעיונות למתנות:**") #
    if member.gift_ideas: #
        for idea in member.gift_ideas: #
            st.markdown(f"- {idea}") #
    else: #
        st.write("אין רעיונות למתנות כרגע.") #

    st.write("**היסטוריית מתנות שניתנו:**") #
    if member.gift_history: #
        for entry in member.gift_history: #
            st.markdown(f"- {entry.date_given.strftime('%d/%m/%Y')} ({entry.occasion if entry.occasion else 'לא מוגדר'}): {entry.description}") #
    else: #
        st.write("אין היסטוריית מתנות.") #

    if st.button(f"ערוך פרטים / מתנות של {member.first_name}", key=f"edit_member_{member.id}"): #
        st.session_state.current_page = "edit_member" #
        st.session_state.editing_member_id = member.id #
        clear_form_session_state(editing_id=member.id) #
        st.rerun() #


def clear_form_session_state(editing_id=None): #
    """מנקה משתני session state הקשורים לטפסים באופן יעיל.""" #
    general_keys = ["new_gift_idea_input", "birth_date_input", "new_gift_history_desc", "new_gift_history_date", "new_gift_history_occasion"] #

    for key in general_keys: #
        if key in st.session_state: #
            del st.session_state[key] #

    if editing_id is not None: #
        prefix = f"for_edit_{editing_id}" #
    else: #
        prefix = "for_new_member" #
    
    specific_keys = [ #
        f"gift_ideas_{prefix}", #
        f"profile_picture_{prefix}", #
        f"new_gift_idea_input_{prefix}", #
        f"gift_history_{prefix}", #
        f"edit_gift_history_form_key_{editing_id}", #
    ]
    
    for key in specific_keys: #
        if key in st.session_state: #
            del st.session_state[key] #
            
    keys_to_delete = [key for key in st.session_state.keys() if key.startswith("remove_gift_idea_button_") or key.startswith("remove_gift_history_button_")] #
    for key in keys_to_delete: #
        del st.session_state[key] #


def add_edit_member_form():
    """טופס להוספה או עריכה של בן משפחה, עכשיו עם קצת הומור ושאלון שנון!"""
    editing_id = st.session_state.get("editing_member_id", None) #
    member_to_edit = None #
    
    if editing_id: #
        member_to_edit = manager.get_member(editing_id) #
        if member_to_edit is None: #
            st.error("אוי לא! בן משפחה לעריכה לא נמצא. נא לחזור לדף הבית.") #
            st.session_state.current_page = "home" #
            st.session_state.editing_member_id = None #
            clear_form_session_state() #
            st.rerun() #
    
    current_gift_ideas_key = f"gift_ideas_for_edit_{editing_id}" if editing_id else "gift_ideas_for_new_member" #
    profile_picture_key = f"profile_picture_for_edit_{editing_id}" if editing_id else "profile_picture_for_new_member" #
    current_gift_history_key = f"gift_history_for_edit_{editing_id}" if editing_id else "gift_history_for_new_member" #


    if current_gift_ideas_key not in st.session_state: #
        st.session_state[current_gift_ideas_key] = list(member_to_edit.gift_ideas) if member_to_edit else [] #
    current_gift_ideas = st.session_state[current_gift_ideas_key] #

    if profile_picture_key not in st.session_state: #
        st.session_state[profile_picture_key] = member_to_edit.profile_picture_base64 if member_to_edit else None #
    current_profile_picture_base64 = st.session_state[profile_picture_key] #

    if current_gift_history_key not in st.session_state: #
        st.session_state[current_gift_history_key] = [entry.to_dict() for entry in member_to_edit.gift_history] if member_to_edit else [] #
    current_gift_history_dicts = st.session_state[current_gift_history_key] #


    if editing_id: #
        st.title(f"ערוך את יצור יום ההולדת הנדיר ששמו {member_to_edit.get_full_name()}!") #
        st.markdown("_נכון, קצת התבלבלנו, אבל אנחנו מבטיחים לתקן!_") #
    else: #
        st.title("ברוך הבא למפקד! 🧐") #
        st.markdown("_נא למלא את הפרטים הבאים ביסודיות, גורל המתנות תלוי בזה!_") #

    # Main form for member details
    with st.form("member_details_form"): #
        st.header("פרטי הזיהוי הסודיים שלך:") #
        first_name_val = member_to_edit.first_name if member_to_edit else "" #
        last_name_val = member_to_edit.last_name if member_to_edit else "" #
        birth_date_val = member_to_edit.birth_date if member_to_edit else datetime.date(2000, 1, 1) #
        relationship_val = member_to_edit.relationship if member_to_edit else "" #
        notes_val = member_to_edit.notes if member_to_edit else "" #

        first_name = st.text_input("איך יקראו לך כשיהיו עוגה ובלונים? (חובה)", value=first_name_val, placeholder="לדוגמה: פיצה🍕") #
        last_name = st.text_input("ומה השם שהמשפחה תמיד שוכחת לזכור? (חובה)", value=last_name_val, placeholder="לדוגמה: משפחת פרי") #
        
        birth_date = st.date_input("מתי התחלת לשמח את העולם? (DD/MM/YYYY) (חובה)", #
                                  value=birth_date_val, #
                                  min_value=datetime.date(1900, 1, 1), #
                                  max_value=datetime.date.today(), #
                                  key="birth_date_input") #
        
        relationship = st.text_input("מה הקשר שלך למשפחה? (לדוגמה: מלך הבית, המלכה האם, הנסיך המקסים, הבת המפונקת)", value=relationship_val) #
        notes = st.text_area("יש לך איזה סוד קטן שנשמח לגלות? (לדוגמה: אוהב/ת שוקולד, אלרגי/ת לדרקונים, חולם/ת על טיול לירח)", value=notes_val) #

        st.header("פניך המרהיבים לעתיד:") #
        uploaded_file = st.file_uploader("העלה תמונה עדכנית של ה'אני' המקסים שלך (כי אנחנו ויזואליים, ורוצים להיות בטוחים שזו לא תמונה מהגן)", type=["jpg", "jpeg", "png"]) #
        
        if uploaded_file is not None: #
            image_bytes = uploaded_file.read() #
            st.session_state[profile_picture_key] = get_image_as_base64(image_bytes) #
        
        if st.session_state.get(profile_picture_key): #
            image_data = get_base64_as_image(st.session_state[profile_picture_key]) #
            if image_data: #
                st.image(image_data, caption="התמונה הנוכחית/חדשה שלך!", width=200) #

        # Moved "Add Gift Idea" and "Gift History" sections outside the main form
        # The main form only contains the member's core details and the submit button for *those* details.
        
        submitted = st.form_submit_button("שלח את הגורל שלי! (ושמור)") #

        if submitted: #
            final_gift_ideas = st.session_state[current_gift_ideas_key] #
            final_gift_history = [GiftHistoryEntry.from_dict(d) for d in st.session_state[current_gift_history_key]] #

            if not first_name.strip(): #
                st.error("שם פרטי הוא שדה חובה, בבקשה מלא אותו. איך נדע למי לאחל מזל טוב?") #
                st.stop() #
            if not last_name.strip(): #
                st.error("שם משפחה הוא שדה חובה. אנחנו חייבים לדעת לאיזו קהילה אתה שייך!") #
                st.stop() #
            if birth_date is None: #
                 st.error("תאריך לידה הוא שדה חובה. בלעדיו אין יום הולדת!") #
                 st.stop() #

            try: #
                final_profile_picture_base64 = st.session_state.get(profile_picture_key, None) #

                if editing_id: #
                    member_to_update = manager.get_member(editing_id) #
                    if member_to_update: #
                        member_to_update.first_name = first_name #
                        member_to_update.last_name = last_name #
                        member_to_update.birth_date = birth_date #
                        member_to_update.relationship = relationship #
                        member_to_update.notes = notes #
                        member_to_update.profile_picture_base64 = final_profile_picture_base64 #
                        member_to_update.gift_ideas = final_gift_ideas #
                        member_to_update.gift_history = final_gift_history #
                        manager._save_data() #
                    st.success(f"הפרטים של {first_name} עודכנו בהצלחה! יאללה בלאגן!") #
                else: #
                    new_member = manager.add_member( #
                        first_name=first_name, #
                        last_name=last_name, #
                        birth_date=birth_date, #
                        relationship=relationship, #
                        notes=notes #
                    ) #
                    new_member.gift_ideas = final_gift_ideas #
                    new_member.gift_history = final_gift_history #
                    new_member.profile_picture_base64 = final_profile_picture_base64 #
                    manager._save_data() #
                    st.success(f"{first_name} {last_name} נוסף בהצלחה! תתכונן למסיבה!") #

                st.session_state.current_page = "home" #
                st.session_state.editing_member_id = None #
                clear_form_session_state(editing_id=editing_id) #
                st.rerun() #
            except ValueError as e: #
                st.error(f"אוי לא! {e} - נראה שמישהו שכח למלא משהו חשוב. נסה שוב!") #
            except TypeError as e: #
                st.error(f"שגיאה טכנית! {e} - אולי המחשב התרגש מרוב חגיגות?") #

    # Sections for Gift Ideas and Gift History are now outside the main form
    st.header("רעיונות למתנות (כי אנחנו לא קוראי מחשבות... עדיין):")
    with st.container():
        new_gift_col, add_gift_col = st.columns([0.8, 0.2])
        with new_gift_col:
            # Use a unique key for the text input that is not dependent on the form
            new_gift_idea_input = st.text_input(
                "מה חסר באוסף שלך? (אפשר להוסיף כמה רעיונות)",
                key=f"new_gift_idea_input_outside_form_{editing_id or 'new'}",
                placeholder="לדוגמה: שובר למסאז', טיסה לחו'ל, גרביים מצחיקות",
                value=st.session_state.get(f"new_gift_idea_input_outside_form_{editing_id or 'new'}", "")
            )
        with add_gift_col:
            st.markdown("<br>", unsafe_allow_html=True)
            # This button is now outside the form, so it can trigger a rerun directly
            if st.button("➕ הוסף רעיון", key=f"add_gift_btn_outside_form_{editing_id or 'new'}"):
                if new_gift_idea_input and new_gift_idea_input.strip() and new_gift_idea_input.strip() not in current_gift_ideas:
                    current_gift_ideas.append(new_gift_idea_input.strip())
                    st.session_state[current_gift_ideas_key] = current_gift_ideas
                    st.session_state[f"new_gift_idea_input_outside_form_{editing_id or 'new'}"] = "" # Clear the input
                    st.rerun()

    if current_gift_ideas: #
        st.write("רעיונות שרשמנו (לחץ על הפח כדי להסיר):") #
        for i, idea in enumerate(current_gift_ideas): #
            col1, col2 = st.columns([0.8, 0.2]) #
            with col1: #
                st.write(f"- {idea}") #
            with col2: #
                if st.button("🗑️", key=f"remove_gift_idea_button_outside_form_{editing_id or 'new'}_{i}"):
                    current_gift_ideas.pop(i) #
                    st.session_state[current_gift_ideas_key] = current_gift_ideas #
                    st.rerun() #
    else: #
         st.info("אין רעיונות למתנות כרגע. תוכל להוסיף כמה!") #

    st.header("היסטוריית מתנות שניתנו (כדי שלא נקנה בטעות פעמיים!):") #
    with st.expander("הוסף מתנה שניתנה בעבר"): #
        # This form is specifically for adding gift history and is separate from the main member details form
        with st.form(key=f"add_gift_history_form_{editing_id or 'new'}_standalone"):
            history_date = st.date_input("תאריך מתן המתנה", value=datetime.date.today(), max_value=datetime.date.today(), key=f"new_gift_history_date_{editing_id or 'new'}") #
            history_description = st.text_input("תיאור המתנה (מה קניתם?)", key=f"new_gift_history_desc_{editing_id or 'new'}", placeholder="לדוגמה: ספר טוב, חולצה, טיול ספא") #
            history_occasion = st.text_input("אירוע (באיזה יום הולדת/חג?)", key=f"new_gift_history_occasion_{editing_id or 'new'}", placeholder="לדוגמה: יום הולדת 2023") #
            add_history_submitted = st.form_submit_button("הוסף מתנה להיסטוריה") #
            if add_history_submitted: #
                if history_description.strip(): #
                    st.session_state[current_gift_history_key].append( #
                        GiftHistoryEntry(history_date, history_description, history_occasion).to_dict() #
                    ) #
                    st.session_state[current_gift_history_key].sort(key=lambda x: x['date_given'], reverse=True) #
                    st.success("מתנה נוספה להיסטוריה!") #
                    st.session_state[f"new_gift_history_desc_{editing_id or 'new'}"] = "" #
                    st.session_state[f"new_gift_history_occasion_{editing_id or 'new'}"] = "" #
                    st.rerun() #

    if current_gift_history_dicts: #
        st.write("היסטוריית מתנות (ערוך או מחק):") #
        for i, entry_dict in enumerate(current_gift_history_dicts): #
            entry_obj = GiftHistoryEntry.from_dict(entry_dict) #
            with st.expander(f"מתנה ב-{entry_obj.date_given.strftime('%d/%m/%Y')} - {entry_obj.description}"): #
                # Each gift history entry can also be edited within its own form for independent submission
                with st.form(key=f"edit_gift_history_form_{editing_id}_{i}_standalone"):
                    edited_date = st.date_input( #
                        "תאריך", #
                        value=entry_obj.date_given, #
                        key=f"edit_history_date_{editing_id}_{i}", #
                        max_value=datetime.date.today() #
                    ) #
                    edited_description = st.text_input( #
                        "תיאור", #
                        value=entry_obj.description, #
                        key=f"edit_history_desc_{editing_id}_{i}" #
                    ) #
                    edited_occasion = st.text_input( #
                        "אירוע", #
                        value=entry_obj.occasion if entry_obj.occasion else "", #
                        key=f"edit_history_occasion_{editing_id}_{i}" #
                    ) #

                    col_update, col_delete = st.columns(2) #
                    with col_update: #
                        if st.form_submit_button("עדכן מתנה זו", key=f"update_gift_history_button_{editing_id}_{i}"): # Changed to form_submit_button
                            try: #
                                updated_entry = GiftHistoryEntry(edited_date, edited_description, edited_occasion) #
                                st.session_state[current_gift_history_key][i] = updated_entry.to_dict() #
                                st.session_state[current_gift_history_key].sort(key=lambda x: x['date_given'], reverse=True) #
                                st.success("היסטוריית מתנה עודכנה!") #
                                st.rerun() #
                            except (ValueError, TypeError) as e: #
                                st.error(f"שגיאת עדכון מתנה: {e}") #
                    with col_delete: #
                        if st.form_submit_button("🗑️ מחק מתנה זו", key=f"delete_gift_history_button_{editing_id}_{i}_delete"): # Changed to form_submit_button, unique key
                            st.session_state[current_gift_history_key].pop(i) #
                            st.success("מתנה נמחקה מההיסטוריה!") #
                            st.rerun() #
    else: #
        st.info("אין היסטוריית מתנות עבור בן משפחה זה. התחילו להוסיף!") #


def list_all_members_page(): #
    """מציג עמוד עם כל בני המשפחה, עם חיפוש וסינון.""" #
    st.title("כל האורחים הפוטנציאליים למסיבה!") #

    col_search, col_sort, col_filter = st.columns([0.4, 0.3, 0.3]) #
    with col_search: #
        search_query = st.text_input("חפש (שם, קשר, הערות, מתנות)", "") #
    with col_sort: #
        sort_by = st.selectbox( #
            "מיין לפי", #
            ["שם מלא (א-ב)", "תאריך לידה (עולה)", "תאריך לידה (יורד)", "ימי הולדת קרובים"], #
            key="sort_members_by" #
        ) #
    with col_filter: #
        all_relationships = sorted(list(set([m.relationship for m in manager.get_all_members() if m.relationship]))) #
        selected_relationship = st.selectbox( #
            "סנן לפי קשר משפחתי", #
            ["הכל"] + all_relationships, #
            key="filter_relationship" #
        ) #


    all_members = manager.get_all_members() #
    members_to_display = [] #

    if search_query: #
        all_members = manager.search_members(search_query) #
    
    if selected_relationship != "הכל": #
        all_members = [m for m in all_members if m.relationship == selected_relationship] #

    if sort_by == "שם מלא (א-ב)": #
        members_to_display = sorted(all_members, key=lambda m: m.get_full_name()) #
    elif sort_by == "תאריך לידה (עולה)": #
        members_to_display = sorted(all_members, key=lambda m: m.birth_date) #
    elif sort_by == "תאריך לידה (יורד)": #
        members_to_display = sorted(all_members, key=lambda m: m.birth_date, reverse=True) #
    elif sort_by == "ימי הולדת קרובים": #
        members_to_display = sorted(all_members, key=lambda m: m.get_days_until_next_birthday()) #


    if not members_to_display: #
        st.info("אוי, אין כאן אף אחד. כנראה כולם ביום הולדת במקום אחר. בוא נוסיף אותם!") #
        return #

    for member in members_to_display: #
        with st.expander(f"🥳 {member.get_full_name()} ({member.relationship if member.relationship else 'לא מוגדר'})"): #
            if member.profile_picture_base64: #
                image_data = get_base64_as_image(member.profile_picture_base64) #
                if image_data: #
                    st.image(image_data, width=200, caption=f"האורח המכובד {member.first_name}") #

            st.write(f"**תאריך לידה:** {member.birth_date.strftime('%d/%m/%Y')}") #
            st.write(f"**יום הולדת הבא:** {member.get_next_birthday().strftime('%d/%m/%Y')} (עוד {member.get_days_until_next_birthday()} ימים)") #
            st.write(f"**גיל:** {datetime.date.today().year - member.birth_date.year} (יחגוג {datetime.date.today().year - member.birth_date.year + 1} ביום הולדת הבא)") #
            st.write(f"**הערות:** {member.notes if member.notes else 'אין הערות, כנראה הוא אדם מאוד פשוט...'}") #
            
            st.write("**רעיונות למתנות (כי למתנות תמיד יש מקום):**") #
            if member.gift_ideas: #
                for idea in member.gift_ideas: #
                    st.markdown(f"- {idea}") #
            else: #
                st.write("אין רעיונות למתנות כרגע. תהיה יצירתי!") #

            st.write("**היסטוריית מתנות שניתנו:**") #
            if member.gift_history: #
                for entry in member.gift_history: #
                    st.markdown(f"- {entry.date_given.strftime('%d/%m/%Y')} ({entry.occasion if entry.occasion else 'לא מוגדר'}): {entry.description}") #
            else: #
                st.write("אין היסטוריית מתנות.") #


            col1, col2 = st.columns(2) #
            with col1: #
                if st.button(f"ערוך את {member.first_name}", key=f"edit_all_{member.id}"): #
                    st.session_state.current_page = "edit_member" #
                    st.session_state.editing_member_id = member.id #
                    clear_form_session_state(editing_id=member.id) #
                    st.rerun() #
            with col2: #
                if st.button(f"זרוק מסיבה (מחק) {member.first_name}", key=f"delete_all_{member.id}"): #
                    st.session_state[f"confirm_delete_{member.id}"] = True #
                    st.rerun() #

    for member in all_members: #
        if st.session_state.get(f"confirm_delete_{member.id}", False): #
            st.warning(f"**אזהרה קיומית!** האם אתה בטוח שברצונך למחוק את {member.get_full_name()}? זה ימחוק את כל הנתונים שלו לנצח נצחים (או עד שתזין מחדש).") #
            col_confirm1, col_confirm2 = st.columns(2) #
            with col_confirm1: #
                if st.button("כן, מחק ותפסיק לבלבל לי את המוח!", key=f"execute_delete_{member.id}"): #
                    manager.delete_member(member.id) #
                    st.success(f"{member.get_full_name()} נמחק בהצלחה. ביי ביי חמוד!") #
                    del st.session_state[f"confirm_delete_{member.id}"] #
                    st.rerun() #
            with col_confirm2: #
                if st.button("רגע, התחרטתי! בטל!", key=f"cancel_delete_{member.id}"): #
                    del st.session_state[f"confirm_delete_{member.id}"] #
                    st.rerun() #

def calendar_page(): #
    """מציג לוח שנה חודשי עם סימון ימי הולדת.""" #
    st.title("לוח שנה של ימי הולדת") #

    current_year = datetime.date.today().year #
    current_month = datetime.date.today().month #

    selected_month = st.selectbox("בחר חודש", range(1, 13), index=current_month - 1, format_func=lambda x: datetime.date(1, x, 1).strftime('%B')) #
    selected_year = st.selectbox("בחר שנה", range(current_year - 5, current_year + 5), index=5) #

    cal = calendar.Calendar() #
    month_days = cal.monthdayscalendar(selected_year, selected_month) #

    st.markdown(f"### {datetime.date(selected_year, selected_month, 1).strftime('%B %Y')}") #

    birthdays_in_month = {} #
    for member in manager.get_all_members(): #
        if member.birth_date.month == selected_month: #
            day = member.birth_date.day #
            if day not in birthdays_in_month: #
                birthdays_in_month[day] = [] #
            birthdays_in_month[day].append(member) #

    st.markdown(""" #
        <style> #
            .calendar-grid { #
                display: grid; #
                grid-template-columns: repeat(7, 1fr); #
                gap: 5px; #
                border: 1px solid #ddd; #
                padding: 10px; #
                background-color: #f0f2f6; #
            } #
            .calendar-header { #
                font-weight: bold; #
                text-align: center; #
                padding: 5px; #
                background-color: #e6e6e6; #
            } #
            .calendar-day { #
                border: 1px solid #eee; #
                padding: 10px; #
                min-height: 80px; #
                background-color: white; #
                font-size: 0.9em; #
                position: relative; #
            } #
            .calendar-day.today { #
                border: 2px solid #4CAF50; #
                background-color: #e8f5e9; #
            } #
            .calendar-day.birthday { #
                background-color: #ffe0b2; #
                border: 2px solid #FF9800; #
            } #
            .day-number { #
                font-weight: bold; #
                margin-bottom: 5px; #
                display: block; #
            } #
            .birthday-names { #
                font-size: 0.8em; #
                color: #555; #
            } #
            .birthday-name-item { #
                margin-top: 3px; #
                background-color: #FFEBEE; #
                padding: 2px 5px; #
                border-radius: 3px; #
                font-weight: bold; #
                color: #D32F2F; #
            } #
        </style> #
    """, unsafe_allow_html=True) #

    day_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"] #
    header_cols = st.columns(7) #
    for i, day_name in enumerate(day_names): #
        with header_cols[i]: #
            st.markdown(f"<div class='calendar-header'>{day_name}</div>", unsafe_allow_html=True) #
    
    st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True) #

    today = datetime.date.today() #

    for week in month_days: #
        cols = st.columns(7) #
        for i, day in enumerate(week): #
            with cols[i]: #
                if day == 0: #
                    st.markdown("<div class='calendar-day'></div>", unsafe_allow_html=True) #
                else: #
                    current_day_date = datetime.date(selected_year, selected_month, day) #
                    day_class = "calendar-day" #
                    if current_day_date == today: #
                        day_class += " today" #
                    if day in birthdays_in_month: #
                        day_class += " birthday" #
                    
                    day_content = f"<span class='day-number'>{day}</span>" #
                    if day in birthdays_in_month: #
                        for member in birthdays_in_month[day]: #
                            day_content += f"<div class='birthday-name-item'>{member.first_name}</div>" #
                    
                    st.markdown(f"<div class='{day_class}'>{day_content}</div>", unsafe_allow_html=True) #
    st.markdown("</div>", unsafe_allow_html=True) #


def settings_page(): #
    """עמוד להגדרות תזכורות (מקום מילוי כרגע).""" #
    st.title("חוקי המסיבה: הגדרות תזכורות") #
    st.warning("פונקציונליות התזכורות האוטומטיות עדיין בפיתוח! (דורש מוח על בשרת)") #
    st.write("כאן תוכל להגדיר מתי ואיך תרצה לקבל תזכורות על ימי הולדת (ברגע שזה יהיה מוכן, כמובן).") #
    
    st.checkbox("הפעל תזכורות לאימייל (כי מי לא אוהב מיילים על יום הולדת?)", value=False) #
    st.number_input("שלח תזכורת X ימים לפני יום ההולדת (כדי שתספיק לקנות מתנה הגונה)", min_value=1, max_value=30, value=7) #
    st.checkbox("שלח תזכורת ביום יום ההולדת (למקרה ששכחת, וזה קורה!)", value=True) #
    
    st.button("שמור הגדרות (אולי זה יעבוד ביום מן הימים...)") #


# --- לוגיקת האפליקציה הראשית --- #
st.sidebar.title("ניווט בממלכה") #
if st.sidebar.button("🏠 הטירה שלי (דף הבית)"): #
    st.session_state.current_page = "home" #
    st.session_state.editing_member_id = None #
    clear_form_session_state() #
    st.rerun() #

if st.sidebar.button("➕ צור מסיבה חדשה (הוסף בן משפחה)"): #
    st.session_state.current_page = "add_member" #
    st.session_state.editing_member_id = None #
    clear_form_session_state() #
    st.rerun() #

if st.sidebar.button("👥 כל האורחים הפוטנציאליים"): #
    st.session_state.current_page = "list_all" #
    st.session_state.editing_member_id = None #
    clear_form_session_state() #
    st.rerun() #

if st.sidebar.button("📅 לוח שנה"): #
    st.session_state.current_page = "calendar" #
    st.session_state.editing_member_id = None #
    clear_form_session_state() #
    st.rerun() #

if st.sidebar.button("⚙️ חוקי המסיבה (הגדרות)"): #
    st.session_state.current_page = "settings" #
    st.session_state.editing_member_id = None #
    clear_form_session_state() #
    st.rerun() #


if "current_page" not in st.session_state: #
    st.session_state.current_page = "home" #

query_params = st.query_params #
if "page" in query_params: #
    requested_page = query_params.get("page") #
    if isinstance(requested_page, list): #
        requested_page = requested_page[0] #

    if requested_page in ["home", "add_member", "list_all", "settings", "edit_member", "calendar"]: #
        if st.session_state.current_page != requested_page or \
        (requested_page == "add_member" and st.session_state.get("editing_member_id") is not None) or \
        (requested_page == "edit_member" and st.session_state.get("editing_member_id") is None): #
            
            st.session_state.current_page = requested_page #
            
            if requested_page == "add_member": #
                st.session_state.editing_member_id = None #
                clear_form_session_state() #
            elif requested_page == "edit_member": #
                pass #
            else: #
                st.session_state.editing_member_id = None #
                clear_form_session_state() #
            
            st.rerun() #

if st.session_state.current_page == "home": #
    st.title("🎂 מנהל ימי הולדת משפפתיים") #
    
    st.markdown("---") #
    st.subheader("רוצה לשתף את הכיף? 🔗") #
    app_url = "https://familybirthdaysapp-ri5ajb26fmqubpobtyfczz.streamlit.app" # החלף בכתובת האמיתית שלך #
    add_member_link = f"{app_url}/?page=add_member" #
    st.info(f""" #
    כדי שאחרים יוכלו להזין את הפרטים שלהם (ולשחק בשאלון המצחיק), שלח להם את הקישור הבא: #
    `{add_member_link}` #
    """) #
    st.write("זכור להחליף את הכתובת בקישור האמיתי של האפליקציה שלך.") #
    st.markdown("---") #

    st.subheader("ימי הולדת קרובים (היכונו למסיבות!)") #
    current_date_for_display = datetime.date.today() #
    upcoming = manager.get_upcoming_birthdays(days_in_advance=90, current_date=current_date_for_display) #

    if upcoming: #
        for member in upcoming: #
            days_left = member.get_days_until_next_birthday(current_date_for_display) #
            
            if days_left == 0: #
                display_text = f"**🎉 {member.get_full_name()}** - **יום הולדת היום!** 🥳 הבה נרקוד!" #
            elif days_left == 1: #
                display_text = f"**🎂 {member.get_full_name()}** - **יום הולדת מחר!** תתחילו להתכונן!" #
            else: #
                display_text = f"**🎈 {member.get_full_name()}** - יום הולדת ב- {member.get_next_birthday(current_date_for_display).strftime('%d/%m')} (עוד {days_left} ימים)" #
            
            col_img, col_text = st.columns([0.2, 0.8]) #
            with col_img: #
                if member.profile_picture_base64: #
                    image_data = get_base64_as_image(member.profile_picture_base64) #
                    if image_data: #
                        st.image(image_data, width=70) #
            with col_text: #
                st.write(display_text) #

            if st.button(f"פרטים / ערוך {member.first_name}", key=f"home_edit_{member.id}"): #
                st.session_state.current_page = "edit_member" #
                st.session_state.editing_member_id = member.id #
                clear_form_session_state(editing_id=member.id) #
                st.rerun() #
            st.markdown("---") #

    else: #
        st.info("אין ימי הולדת קרובים ב-90 הימים הבאים. כנראה כולם בחופשה. הוסף בני משפחה כדי שיהיה לנו על מי לחגוג!") #

elif st.session_state.current_page == "add_member" or st.session_state.current_page == "edit_member": #
    add_edit_member_form() #
elif st.session_state.current_page == "list_all": #
    list_all_members_page() #
elif st.session_state.current_page == "calendar": #
    calendar_page() #
elif st.session_state.current_page == "settings": #
    settings_page() #