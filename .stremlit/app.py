# ============================================
# CYBERTWIN AI DASHBOARD
# ULTIMATE FINAL MERGED VERSION
# ADVANCED UI + EMAIL ANALYZER + FILTER FIX
# ============================================

import streamlit as st
import numpy as np
import pandas as pd
import random
import plotly.graph_objects as go
import networkx as nx
import re

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
    AdaBoostClassifier
)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

# EMAIL IMPORTS
import imaplib
import email
from email.header import decode_header

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="CyberTwin AI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(
        135deg,
        #0f172a,
        #111827,
        #1e293b
    );
    color: white;
}

.main-title {
    font-size: 52px;
    font-weight: 800;
    text-align: center;
    color: #38bdf8;
    margin-bottom: 10px;
}

.subtitle {
    text-align: center;
    font-size: 20px;
    color: #cbd5e1;
    margin-bottom: 30px;
}

.glass {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.15);
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}

.section-title {
    font-size: 28px;
    font-weight: 700;
    color: #7dd3fc;
    margin-bottom: 15px;
}

.metric-box {
    background: linear-gradient(
        145deg,
        #1e293b,
        #0f172a
    );
    padding: 20px;
    border-radius: 18px;
    text-align: center;
    border: 1px solid #334155;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.25);
}

.stTextInput input {
    background-color: #111827;
    color: white;
    border-radius: 12px;
    border: 1px solid #334155;
    padding: 10px;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: #111827;
    border-radius: 12px;
}

.stButton > button {
    width: 100%;
    border-radius: 14px;
    background: linear-gradient(
        90deg,
        #06b6d4,
        #3b82f6
    );
    color: white;
    border: none;
    padding: 12px;
    font-size: 16px;
    font-weight: bold;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.03);
}

section[data-testid="stSidebar"] {
    background: #0f172a;
}

[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE
# ============================================

if "connected" not in st.session_state:
    st.session_state.connected = False

if "platform_data" not in st.session_state:
    st.session_state.platform_data = {}

# EMAIL STORAGE FIX
if "emails_df" not in st.session_state:
    st.session_state.emails_df = pd.DataFrame()

# ============================================
# VALIDATION FUNCTIONS
# ============================================

def validate_email(email_text):

    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email_text)

def validate_username(username):

    pattern = r'^[a-zA-Z0-9._]{3,30}$'
    return re.match(pattern, username)

# ============================================
# PASSWORD SECURITY
# ============================================

def check_personal_info(password, personal_inputs):

    password = password.lower()

    for item in personal_inputs:

        if item and item.lower() in password:
            return True

    return False

def generate_strong_password():

    special = random.choice(
        ["@", "#", "$", "&", "!"]
    )

    number = random.randint(100, 999)

    words = [
        "Cyber",
        "Secure",
        "Titan",
        "Quantum",
        "Shield",
        "Guardian",
        "Matrix",
        "Nova"
    ]

    return (
        random.choice(words)
        + special
        + str(number)
        + random.choice(["X", "Z", "Q"])
    )

# ============================================
# SYNTHETIC DATA
# ============================================

@st.cache_data
def generate_data(n=5000):

    data = []

    for _ in range(n):

        accounts = random.randint(1, 25)
        reuse = random.randint(0, 100)
        twofa = random.choice([0, 1])
        exposure = random.randint(0, 3)
        phishing = random.choice([0, 1])
        suspicious_logins = random.randint(0, 10)
        weak_passwords = random.randint(0, 5)

        risk = (
            reuse * 0.25 +
            (1 - twofa) * 20 +
            exposure * 15 +
            phishing * 20 +
            suspicious_logins * 3 +
            weak_passwords * 5 +
            accounts * 1.5
        )

        risk = min(100, int(risk))

        label = 1 if risk > 50 else 0

        data.append([

            accounts,
            reuse,
            twofa,
            exposure,
            phishing,
            suspicious_logins,
            weak_passwords,
            label
        ])

    return pd.DataFrame(data, columns=[

        "accounts",
        "reuse",
        "twofa",
        "exposure",
        "phishing",
        "suspicious_logins",
        "weak_passwords",
        "risk"
    ])

# ============================================
# TRAIN MODELS
# ============================================

@st.cache_resource
def train_models():

    df = generate_data()

    X = df.drop("risk", axis=1)
    y = df["risk"]

    models = {

        "Logistic Regression":
            LogisticRegression(),

        "Random Forest":
            RandomForestClassifier(
                n_estimators=120
            ),

        "Decision Tree":
            DecisionTreeClassifier(),

        "Gradient Boosting":
            GradientBoostingClassifier(),

        "SVM":
            SVC(probability=True),

        "KNN":
            KNeighborsClassifier(),

        "Extra Trees":
            ExtraTreesClassifier(),

        "AdaBoost":
            AdaBoostClassifier(),

        "Naive Bayes":
            GaussianNB()
    }

    for model in models.values():
        model.fit(X, y)

    return models

models = train_models()

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
        width=120
    )

    st.markdown("## 🛡️ CyberTwin")

    st.markdown("""
    ### Features
    - AI Threat Detection
    - Password Analyzer
    - Phishing Simulator
    - Email Spam Detection
    - Attack Graph Visualization
    - Multi-Platform Risk Analysis
    """)

    st.info("🚀 Powered by AI + Machine Learning")

# ============================================
# HEADER
# ============================================

st.markdown(
    '<div class="main-title">🛡️ CyberTwin AI Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Advanced Cybersecurity Simulation Platform</div>',
    unsafe_allow_html=True
)

# ============================================
# CONNECT PLATFORM
# ============================================

st.markdown(
    '<div class="section-title">🔌 Connect Platforms</div>',
    unsafe_allow_html=True
)

platforms = [
    "Email",
    "Facebook",
    "Instagram",
    "Twitter",
    "LinkedIn"
]

col1, col2 = st.columns(2)

with col1:

    selected_platform = st.selectbox(
        "Choose Platform",
        platforms
    )

with col2:

    user_input = st.text_input(
        "Enter Email / Username"
    )

if st.button("🚀 Connect Platform"):

    valid = False

    if selected_platform == "Email":

        if validate_email(user_input):
            valid = True
        else:
            st.error("❌ Invalid Email Format")

    else:

        if validate_username(user_input):
            valid = True
        else:
            st.error("❌ Invalid Username")

    if valid:

        st.session_state.platform_data[selected_platform] = {

            "accounts": random.randint(1, 20),
            "reuse": random.randint(0, 100),
            "twofa": random.choice([0, 1]),
            "exposure": random.randint(0, 3),
            "phishing": random.choice([0, 1]),
            "suspicious_logins": random.randint(0, 10),
            "weak_passwords": random.randint(0, 5)
        }

        st.session_state.connected = True

        st.success(
            f"✅ {selected_platform} Connected Successfully"
        )

# ============================================
# DASHBOARD
# ============================================

if st.session_state.connected:

    st.markdown(
        '<div class="section-title">📊 Platform Risk Overview</div>',
        unsafe_allow_html=True
    )

    results = {}

    cols = st.columns(
        len(st.session_state.platform_data)
    )

    for i, (platform, data) in enumerate(
            st.session_state.platform_data.items()):

        risk = (
            data["reuse"] * 0.25 +
            (1 - data["twofa"]) * 20 +
            data["exposure"] * 15 +
            data["phishing"] * 20 +
            data["suspicious_logins"] * 3 +
            data["weak_passwords"] * 5
        )

        risk = min(100, int(risk))
        results[platform] = risk

        cols[i].markdown(f"""
        <div class="metric-box">
            <h3>{platform}</h3>
            <h1>{risk}%</h1>
            <p>Risk Score</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# PASSWORD CHECKER
# ============================================

st.markdown(
    '<div class="section-title">🔑 Password Security Checker</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    full_name = st.text_input(
        "Enter Your Name"
    )

    birth_year = st.text_input(
        "Enter Birth Year"
    )

with col2:

    phone_number = st.text_input(
        "Enter Phone Number"
    )

    password = st.text_input(
        "Enter Password",
        type="password"
    )

if password:

    score = 0

    if len(password) >= 10:
        score += 1

    if any(c.isdigit() for c in password):
        score += 1

    if any(c.isupper() for c in password):
        score += 1

    if any(c in "!@#$%^&*" for c in password):
        score += 1

    if any(c.islower() for c in password):
        score += 1

    personal_info = [
        full_name,
        birth_year,
        phone_number
    ]

    contains_personal = check_personal_info(
        password,
        personal_info
    )

    if contains_personal:
        st.error("❌ Password contains personal info")

    if score <= 2:
        st.error("🔴 Weak Password")

    elif score == 3:
        st.warning("🟠 Moderate Password")

    else:
        st.success("🟢 Strong Password")

    st.code(generate_strong_password())

# ============================================
# EMAIL FETCH FUNCTION
# ============================================

def fetch_emails(
        username,
        app_password,
        folder="Inbox",
        num_emails=100):

    emails_data = []

    try:

        mail = imaplib.IMAP4_SSL(
            "imap.gmail.com"
        )

        mail.login(
            username,
            app_password
        )

        folder_map = {

            "Inbox":
                "INBOX",

            "Sent":
                '"[Gmail]/Sent Mail"',

            "Spam":
                '"[Gmail]/Spam"',

            "Drafts":
                '"[Gmail]/Drafts"',

            "All Mail":
                '"[Gmail]/All Mail"'
        }

        selected_folder = folder_map.get(
            folder,
            "INBOX"
        )

        mail.select(selected_folder)

        status, messages = mail.search(
            None,
            "ALL"
        )

        mail_ids = messages[0].split()

        latest_ids = mail_ids[-num_emails:]

        for i in reversed(latest_ids):

            res, msg = mail.fetch(
                i,
                "(RFC822)"
            )

            for response in msg:

                if isinstance(response, tuple):

                    msg = email.message_from_bytes(
                        response[1]
                    )

                    subject, encoding = decode_header(
                        msg["Subject"]
                    )[0]

                    if isinstance(subject, bytes):

                        try:

                            subject = subject.decode(
                                encoding if encoding else "utf-8"
                            )

                        except:

                            subject = "No Subject"

                    from_ = msg.get("From")
                    date_ = msg.get("Date")

                    body = ""

                    try:

                        if msg.is_multipart():

                            for part in msg.walk():

                                content_type = (
                                    part.get_content_type()
                                )

                                if content_type == "text/plain":

                                    body = part.get_payload(
                                        decode=True
                                    ).decode(
                                        errors="ignore"
                                    )

                                    break

                        else:

                            body = msg.get_payload(
                                decode=True
                            ).decode(
                                errors="ignore"
                            )

                    except:

                        body = ""

                    emails_data.append({

                        "Subject": subject,
                        "From": from_,
                        "Date": date_,
                        "Folder": folder,
                        "Preview": body[:250]
                    })

        mail.logout()

    except Exception as e:

        st.error(f"❌ Error: {e}")

    return pd.DataFrame(emails_data)

# ============================================
# SPAM DETECTOR
# ============================================

def detect_spam(text):

    spam_keywords = [

        "free",
        "win",
        "urgent",
        "click",
        "offer",
        "money",
        "prize",
        "lottery",
        "gift",
        "bitcoin",
        "crypto",
        "reward",
        "bonus",
        "cash",
        "investment",
        "claim"
    ]

    text = str(text).lower()

    score = sum(
        word in text
        for word in spam_keywords
    )

    return "Spam" if score >= 2 else "Safe"

# ============================================
# EMAIL ANALYZER
# ============================================

st.markdown(
    '<div class="section-title">📩 Email Spam Analyzer</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    email_user = st.text_input(
        "📧 Enter Gmail ID"
    )

with col2:

    email_pass = st.text_input(
        "🔑 Enter App Password",
        type="password"
    )

folder_option = st.selectbox(

    "📂 Select Folder",

    [
        "Inbox",
        "Sent",
        "Spam",
        "Drafts",
        "All Mail"
    ]
)

num_emails = st.slider(

    "📥 Number of Emails",

    10,
    500,
    100
)

# ============================================
# FETCH EMAILS BUTTON
# ============================================

if st.button("📥 Fetch Emails"):

    if not validate_email(email_user):

        st.error(
            "❌ Invalid Email Address"
        )

    else:

        with st.spinner(
            "Fetching Emails..."
        ):

            df_emails = fetch_emails(

                email_user,
                email_pass,
                folder_option,
                num_emails
            )

        if not df_emails.empty:

            df_emails["Spam_Status"] = (

                df_emails["Subject"]
                .apply(detect_spam)
            )

            # SAVE DATA
            st.session_state.emails_df = df_emails

        else:

            st.warning(
                "⚠️ No emails found in this folder"
            )

# ============================================
# SHOW EMAIL DATA
# ============================================

if not st.session_state.emails_df.empty:

    df_emails = st.session_state.emails_df

    # FILTER
    filter_option = st.radio(

        "🔍 Filter Emails",

        [
            "All",
            "Spam",
            "Safe"
        ],

        horizontal=True
    )

    # APPLY FILTER
    if filter_option == "Spam":

        filtered_df = df_emails[
            df_emails["Spam_Status"] == "Spam"
        ]

    elif filter_option == "Safe":

        filtered_df = df_emails[
            df_emails["Spam_Status"] == "Safe"
        ]

    else:

        filtered_df = df_emails

    # EMAIL TABLE
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=500
    )

    # DOWNLOAD CSV
    csv = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        label="⬇️ Download CSV",

        data=csv,

        file_name=f"{folder_option}_emails.csv",

        mime="text/csv"
    )

    # METRICS
    spam_count = (
        filtered_df["Spam_Status"] == "Spam"
    ).sum()

    safe_count = (
        filtered_df["Spam_Status"] == "Safe"
    ).sum()

    total_count = len(filtered_df)

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "📨 Total Emails",
        total_count
    )

    c2.metric(
        "🚨 Spam Emails",
        spam_count
    )

    c3.metric(
        "✅ Safe Emails",
        safe_count
    )

    # PIE CHART
    fig = go.Figure(

        data=[go.Pie(

            labels=[
                "Spam",
                "Safe"
            ],

            values=[
                spam_count,
                safe_count
            ],

            hole=.4
        )]
    )

    fig.update_layout(

        template="plotly_dark",

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ============================================
# FOOTER
# ============================================

st.markdown("""
<hr style="border:1px solid #334155">

<center>
<h4 style="color:#94a3b8;">
🛡️ CyberTwin AI Dashboard • Advanced Cybersecurity Simulation Platform
</h4>
</center>
""", unsafe_allow_html=True)
