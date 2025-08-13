# Streamlit landing page per lo spettacolo di danza aerea
# Hosting previsto: Streamlit Community Cloud (collegato a GitHub)
# Invio form: consigliato Formspree (endpoint salvato in st.secrets["FORMSPREE_ENDPOINT"]).
# In alternativa, SMTP con secrets: EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_TO.

import re
import json
import requests
import streamlit as st
from datetime import date

# ---------------------- CONFIGURAZIONE RAPIDA ----------------------
COMPANY_NAME = "Il Nodo del Vento"
CONTACT_EMAIL = "tua@mail.com"   # TODO: metti la tua
CONTACT_PHONE = "+39 333 123 4567"  # TODO: metti il tuo numero
WHATSAPP_PHONE = "393331234567"      # TODO: solo cifre per link wa.me
YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # TODO: tuo video
PHOTOS = [
    "https://images.unsplash.com/photo-1564758986271-0a5a51c6f7f5?q=80&w=1600&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1520975922441-c2a38b4646b3?q=80&w=1600&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1521334726092-b509a19597c6?q=80&w=1600&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1516715094483-75da7dee9758?q=80&w=1600&auto=format&fit=crop",
]
# -------------------------------------------------------------------

st.set_page_config(
    page_title=f"{COMPANY_NAME} – Danza Aerea",
    page_icon="✨",
    layout="wide",
)

# ---- Stili leggeri ----
st.markdown(
    """
    <style>
    .stButton>button {border-radius:14px;padding:10px 16px}
    .card {background: rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.12); padding:18px; border-radius:16px}
    .muted {color: rgba(255,255,255,0.7)}
    .small {font-size: 0.9rem}
    .hidden-field {display:none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Utility di validazione ----
EMAIL_RE = re.compile(r"^[\w\-.]+@([\w-]+\.)+[\w-]{2,}$")
PHONE_RE = re.compile(r"^[0-9 +()\-]{7,}$")

def is_valid_email(s: str) -> bool:
    return bool(EMAIL_RE.match(s or ""))

def is_valid_phone(s: str) -> bool:
    return bool(PHONE_RE.match(s or ""))

# ---- Header/Hero ----
st.title("Spettacolo di Danza Aerea")
st.markdown(f"### {COMPANY_NAME}")
st.write("Due aerialiste, cerchio e tessuti. Adatto a scuole, matrimoni e piazze. Durata massima 35 minuti.")

colA, colB, colC = st.columns([1,1,1])
with colA:
    st.metric("Durata", "≤ 35 min")
with colB:
    st.metric("Format", "Cerchio + Tessuti")
with colC:
    st.metric("Per", "Scuole · Matrimoni · Piazze")

st.divider()

# ---- Galleria ----
st.subheader("Galleria")
cols = st.columns(4)
for i, src in enumerate(PHOTOS[:4]):
    with cols[i % 4]:
        st.image(src, use_container_width=True, caption=f"Foto {i+1}")

st.divider()

# ---- Video ----
st.subheader("Video demo")
st.video(YOUTUBE_URL)

st.divider()

# ---- Contatti ----
left, right = st.columns([1,1])
with left:
    st.subheader("Contatti")
    st.markdown(
        f"""
        **Email:** [{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})  
        **Telefono:** [{CONTACT_PHONE}](tel:{CONTACT_PHONE})  
        **WhatsApp:** [Scrivici](https://wa.me/{WHATSAPP_PHONE})
        """
    )
    st.markdown("- Durata: max 35 minuti\n- Formato: 2 aerialiste (cerchio + tessuti), un punto aereo\n- Spazio: 6×6 m; altezza ideale 6–8 m (ok versione bassa 4–5 m)\n- Sicurezza: rigger qualificato, tappeti antitrauma, check attrezzatura")

# ---- Form prenotazione ----
with right:
    st.subheader("Richiedi disponibilità")
    st.caption("Compila il modulo: ti rispondiamo via mail o telefono.")

    # honeypot (anti-bot)
    hp = st.text_input("Lascia questo campo vuoto", key="hp")
    st.markdown("<div class='hidden-field'>Campo nascosto anti-spam</div>", unsafe_allow_html=True)

    with st.form("booking_form", clear_on_submit=False):
        ev_date = st.date_input("Data evento *", min_value=date.today(), format="DD/MM/YYYY")
        name = st.text_input("Nome e cognome *")
        phone = st.text_input("Telefono *")
        email = st.text_input("Email *")
        location = st.text_input("Luogo (città/venue)")
        message = st.text_area("Messaggio (opzionale)")
        consent = st.checkbox("Acconsento al trattamento dei dati inseriti per essere ricontattato/a in merito alla mia richiesta.")
        submitted = st.form_submit_button("Invia richiesta")

    if submitted:
        errors = []
        if hp.strip():
            errors.append("Rilevato spam.")
        if not name or len(name.strip()) < 2:
            errors.append("Inserisci il tuo nome.")
        if not is_valid_email(email):
            errors.append("Email non valida.")
        if not is_valid_phone(phone):
            errors.append("Numero di telefono non valido.")
        if not ev_date:
            errors.append("Scegli una data.")
        if not consent:
            errors.append("Serve il consenso per poter essere ricontattati.")

        if errors:
            st.error("\n".join(errors))
        else:
            # Preferenza 1: Formspree
            endpoint = st.secrets.get("FORMSPREE_ENDPOINT")
            payload = {
                "evento_data": ev_date.strftime("%Y-%m-%d"),
                "nome": name,
                "telefono": phone,
                "email": email,
                "location": location,
                "messaggio": message,
                "_subject": f"Richiesta preventivo – {COMPANY_NAME}",
            }
            sent = False
            err_msg = None

            if endpoint:
                try:
                    r = requests.post(endpoint, json=payload, timeout=10)
                    if r.ok:
                        sent = True
                    else:
                        err_msg = f"Invio non riuscito (HTTP {r.status_code})."
                except Exception as e:
                    err_msg = f"Errore invio: {e}"

            # Preferenza 2: SMTP (se secrets presenti)
            if not sent and all(k in st.secrets for k in ["EMAIL_HOST", "EMAIL_PORT", "EMAIL_USER", "EMAIL_PASS", "EMAIL_TO"]):
                try:
                    import smtplib
                    from email.mime.text import MIMEText

                    body = (
                        f"Data evento: {payload['evento_data']}\n"
                        f"Nome: {payload['nome']}\n"
                        f"Telefono: {payload['telefono']}\n"
                        f"Email: {payload['email']}\n"
                        f"Luogo: {payload['location']}\n"
                        f"Messaggio: {payload['messaggio']}\n"
                    )
                    msg = MIMEText(body, _charset="utf-8")
                    msg["Subject"] = payload["_subject"]
                    msg["From"] = st.secrets["EMAIL_USER"]
                    msg["To"] = st.secrets["EMAIL_TO"]

                    with smtplib.SMTP_SSL(st.secrets["EMAIL_HOST"], int(st.secrets["EMAIL_PORT"])) as server:
                        server.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
                        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
                    sent = True
                except Exception as e:
                    err_msg = f"Errore SMTP: {e}"

            if sent:
                st.success("Richiesta inviata! Ti risponderemo al più presto.")
                st.balloons()
            else:
                mailto = (
                    f"mailto:{CONTACT_EMAIL}?subject="
                    f"Richiesta%20{COMPANY_NAME.replace(' ', '%20')}"
                    f"&body="
                    + (
                        f"Ciao,%0D%0Avorrei prenotare lo spettacolo {COMPANY_NAME}.%0D%0A"
                        f"Data evento: {payload['evento_data']}%0D%0A"
                        f"Nome: {payload['nome']}%0D%0A"
                        f"Telefono: {payload['telefono']}%0D%0A"
                        f"Email: {payload['email']}%0D%0A"
                        f"Luogo: {payload['location']}%0D%0A"
                        f"Messaggio: {payload['messaggio']}"
                    )
                )
                st.warning(
                    (
                        (err_msg + " ") if err_msg else ""
                    )
                    + f"Non sono riuscito a inviare al server. Puoi scriverci direttamente "
                    f"a [{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL}) oppure "
                    f"[clicca qui per aprire la mail]({mailto})."
                )

st.divider()

# ---- Area test (per sviluppatore) ----
with st.expander("Mostra test di validazione (facoltativo)"):
    tests = [
        ("email valida semplice", is_valid_email("mario.rossi@mail.it")),
        ("email senza dominio", not is_valid_email("mario@")),
        ("email dominio corto", not is_valid_email("mario@mail")),
        ("telefono valido IT", is_valid_phone("+39 333 123 4567")),
        ("telefono troppo corto", not is_valid_phone("123")),
    ]
    passed = sum(1 for _, ok in tests if ok)
    st.write(f"Passati {passed}/{len(tests)}")
    st.table({"test": [t[0] for t in tests], "ok": ["✔" if t[1] else "✘" for t in tests]})

st.caption("© {} {}. Tutti i diritti riservati.".format(date.today().year, COMPANY_NAME))
