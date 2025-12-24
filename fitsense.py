import streamlit as st
import mysql.connector
import bcrypt
import pandas as pd
import plotly.express as px
import time

# ================================
# --- PAGE CONFIG ---
# ================================
st.set_page_config(
    page_title="FitSense – Smart Outfit Recommender",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================================
# --- CONSTANTS ---
# ================================
moods = ["happy", "confident", "anxious", "festive", "relaxed", "tired"]
occasions = ["wedding", "party", "office", "travel", "home", "gym", "festival", "college"]
subtypes = {
    "wedding": ["sangeet", "haldi", "reception", "engagement"],
    "party": ["casual", "clubbing", "cocktail"],
    "office": ["meeting", "presentation", "interview"],
    "travel": ["airport", "backpacking", "vacation"],
    "home": ["lounging", "sleeping"],
    "gym": ["cardio", "yoga", "outdoor sports"],
    "festival": ["Diwali", "Holi", "Eid", "Christmas", "Navratri"],
    "college": ["lecture", "lab", "cultural fest", "exam"]
}
weathers = ["hot", "cold", "rainy", "pleasant"]

# ================================
# --- GLOBAL CSS ---
# ================================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    height: 100vh;
    overflow: hidden;
    background: linear-gradient(160deg, #05010a, #0c0018);
    font-family: 'Poppins', sans-serif;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
}
.container {
    max-width: 500px;
    margin: auto;
    text-align: center;
}
input, select {
    text-align: center !important;
    margin: 5px 0;
}
.stButton>button {
    background: linear-gradient(90deg,#7C3AED,#A855F7);
    color: white;
    border-radius: 30px;
    padding: 12px;
    width: 100%;
    font-weight: 600;
    margin-top: 10px;
}
h1,h2,h3 {
    background: linear-gradient(90deg,#7C3AED,#A855F7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
}
p {
    color: #bcbcbc;
    text-align: center;
}
.glass-box {
    padding: 15px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    margin-top: 15px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ================================
# --- DATABASE CONNECTION ---
# ================================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="dhar2007",
        database="fitsense"
    )

# ================================
# --- AUTH FUNCTIONS ---
# ================================
def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, username))
    user = cur.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return user
    return None

def register_user(username, email, password):
    conn = get_connection()
    cur = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        cur.execute(
            "INSERT INTO users(username,email,password_hash,role) VALUES(%s,%s,%s,'user')",
            (username, email, hashed)
        )
        conn.commit()
        return True
    except mysql.connector.Error:
        return False
    finally:
        conn.close()

# ================================
# --- SESSION STATE ---
# ================================
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "user" not in st.session_state:
    st.session_state.user = None
if "landing_shown" not in st.session_state:
    st.session_state.landing_shown = False  # To run animation only once

# ================================
# --- LANDING PAGE ---
# ================================
def landing_page():
    st.markdown("<div class='container'>", unsafe_allow_html=True)

    if not st.session_state.landing_shown:
        main_heading = "FitSense – Smart Outfit Recommender"
        placeholder_heading = st.empty()
        displayed = ""
        for char in main_heading:
            displayed += char
            placeholder_heading.markdown(f"<h1>{displayed}</h1>", unsafe_allow_html=True)
            time.sleep(0.03)

        subtitle = "Style that understands your mood, occasion, and weather"
        subtitle_placeholder = st.empty()
        for i in range(1, len(subtitle)+1):
            subtitle_placeholder.markdown(f"<h3>{subtitle[:i]}</h3>", unsafe_allow_html=True)
            time.sleep(0.01)

        description = (
            "Discover curated outfits that make you feel confident, comfortable, and stylish every day. "
            "Select your mood, occasion, and weather to get personalized recommendations!"
        )
        desc_placeholder = st.empty()
        for i in range(1, len(description)+1):
            desc_placeholder.markdown(f"<p>{description[:i]}</p>", unsafe_allow_html=True)
            time.sleep(0.005)

        st.session_state.landing_shown = True
    else:
        st.markdown("<h1>FitSense – Smart Outfit Recommender</h1>", unsafe_allow_html=True)
        st.markdown("<h3>Style that understands your mood, occasion, and weather</h3>", unsafe_allow_html=True)
        st.markdown("<p>Discover curated outfits that make you feel confident, comfortable, and stylish every day. "
                    "Select your mood, occasion, and weather to get personalized recommendations!</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Start Getting Outfit Recommendations"):
        st.session_state.page = "login"

    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# --- SIGNUP / LOGIN PAGES ---
# ================================
def login_page():
    st.markdown("<div class='container'>", unsafe_allow_html=True)
    st.title("Login")
    username = st.text_input("Username / Email", key="login_u")
    password = st.text_input("Password", type="password", key="login_p")
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.user = user
            role = user.get("role", "user")
            st.session_state.page = "admin" if role=="admin" else "user_mode"
        else:
            st.error("Invalid login credentials")
    if st.button("Sign Up Instead"):
        st.session_state.page = "signup"
    st.markdown("</div>", unsafe_allow_html=True)

def signup_page():
    st.markdown("<div class='container'>", unsafe_allow_html=True)
    st.title("Create Account")
    su = st.text_input("Username", key="su_u")
    se = st.text_input("Email", key="su_e")
    sp1 = st.text_input("Password", type="password", key="su_p1")
    sp2 = st.text_input("Confirm Password", type="password", key="su_p2")
    if st.button("Sign Up"):
        if sp1 != sp2:
            st.error("Passwords do not match")
        elif register_user(su, se, sp1):
            st.success("Account created successfully. Login now.")
            st.session_state.page = "login"
        else:
            st.error("Sign Up failed. Username or Email may already exist.")
    if st.button("Back to Login"):
        st.session_state.page = "login"
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# --- OUTFIT RECOMMENDATION ---
# ================================
def recommend_outfit(gender, mood, occasion, subtype, weather):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT * FROM outfits 
        WHERE gender=%s AND mood=%s AND occasion=%s AND subtype=%s AND weather=%s 
        ORDER BY RAND() LIMIT 1
    """, (gender, mood, occasion, subtype, weather))
    outfit = cur.fetchone()
    conn.close()
    return outfit

def user_mode():
    st.subheader("🎯 Get Personalized Outfit Recommendation")
    st.markdown("<div class='glass-box'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        gender = st.selectbox("Gender", ["male", "female"], key="gender_select")
    with col2:
        mood = st.selectbox("Mood", moods, key="mood_select")
    with col3:
        occasion = st.selectbox("Occasion", occasions, key="occasion_select")

    subtype = st.selectbox("Subtype", subtypes[occasion], key="subtype_select")
    weather = st.selectbox("Weather", weathers, key="weather_select")

    if st.button("✨ Recommend Outfit", key="recommend_btn"):
        outfit = recommend_outfit(gender, mood, occasion, subtype, weather)
        if outfit:
            st.success(f"Recommended for **{mood} | {occasion} | {weather}** 🌤️")
            st.write(f"👗 Dress: {outfit.get('dress','N/A')}")
            st.write(f"🎨 Palette: {outfit.get('dress_palette','N/A')} | Prints: {outfit.get('dress_print_type','N/A')}")
            st.write(f"👟 Footwear: {outfit.get('footwear','N/A')}")
            st.write(f"🧿 Accessory: {outfit.get('accessory','N/A')}")
            st.markdown(f"[🛒 Buy Now]({outfit.get('link_1','#')})")
        else:
            st.warning("⚠️ No matching outfit found. Try a different combo.")

    if st.button("Logout"):
        st.session_state.page = "landing"
        st.session_state.user = None

    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# --- ADMIN DASHBOARD ---
# ================================
def admin_dashboard():
    st.title("🧠 FitSense Admin Dashboard")
    conn = get_connection()

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT user_id, username, email FROM users")
    users = pd.DataFrame(cur.fetchall())
    cur.close()

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT outfit_id, gender, mood, occasion FROM outfits LIMIT 200")
    outfits = pd.DataFrame(cur.fetchall())
    cur.close()
    conn.close()

    tab1, tab2 = st.tabs(["👥 Users", "📊 Analytics"])
    with tab1:
        st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
        st.dataframe(users, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.subheader("Mood Popularity Overview")
        st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
        mood_count = outfits.groupby("mood").size().reset_index(name="count")
        fig = px.bar(
            mood_count,
            x="mood",
            y="count",
            color="mood",
            title="Mood Distribution",
            template="plotly_white"
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#002b5b", size=14),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state.page = "landing"
        st.session_state.user = None

# ================================
# --- ROUTER ---
# ================================
if st.session_state.page == "landing":
    landing_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "user_mode":
    user_mode()
elif st.session_state.page == "admin":
    admin_dashboard()


 






