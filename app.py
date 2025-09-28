import os, json, time
import streamlit as st
from openai import OpenAI

# -------------------- CONFIG --------------------
st.set_page_config(page_title="SymptomsChecker.io", page_icon="🩺", layout="wide")
client = OpenAI()  # uses OPENAI_API_KEY from your environment
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# -------------------- SYSTEM PROMPT --------------------
SYSTEM_PROMPT = """
You are a clinical symptom-checker and triage assistant (not a doctor).
Goal: provide educational guidance, a short differential, and clear next steps
(home care vs. clinic vs. ER) using the current message, chat history, and an
optional patient profile (age, sex, pregnancy status, conditions, meds, allergies, vitals).

Process:
1) Ask only minimal critical follow-ups if info is missing (onset/timing, location, severity 0–10,
   triggers, associated symptoms, pregnancy, meds, major conditions).
2) Make a short differential (2–5 likely causes) with brief rationale.
3) Choose exactly one triage level: home_care | see_primary_care_1-3_days | urgent_care_today | emergency_now.
4) Give clear, actionable next steps; list red flags; what to watch for.
Safety: If life-threatening red flags appear, set triage to emergency_now and tell user to call emergency services.
Always include: “This is general information for educational purposes and not a medical diagnosis.”
"""

# -------------------- STRUCTURED OUTPUT SCHEMA --------------------
TRIAGE_SCHEMA = {
    "name": "TriageOutput",
    "schema": {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "differential": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "condition": {"type": "string"},
                        "likelihood": {"type": "string", "enum": ["low","medium","high"]},
                        "rationale": {"type": "string"}
                    },
                    "required": ["condition","likelihood","rationale"],
                    "additionalProperties": False
                },
                "minItems": 1, "maxItems": 5
            },
            "triage_level": {
                "type": "string",
                "enum": ["home_care","see_primary_care_1-3_days","urgent_care_today","emergency_now"]
            },
            "next_steps": {"type": "array", "items": {"type": "string"}},
            "self_care": {"type": "array", "items": {"type": "string"}},
            "red_flags_triggered": {"type": "array", "items": {"type": "string"}},
            "what_to_watch": {"type": "array", "items": {"type": "string"}},
            "follow_up_questions": {"type": "array", "items": {"type": "string"}},
            "sources": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["summary","differential","triage_level","next_steps","what_to_watch"],
        "additionalProperties": False
    }
}

# -------------------- DEMO PROFILE --------------------
PROFILE = {
    "name": "Jane Doe",
    "age": 25,
    "sex": "female",         # demo twist to show fields change cleanly
    "pregnant": True,
    "conditions": ["asthma"],
    "medications": ["albuterol inhaler (PRN)"],
    "allergies": ["penicillin"],
    "recent_vitals": {"temp_f": 98.6}
}

# -------------------- STYLE (GLOBAL, OUTSIDE WRAPPER) --------------------
st.markdown("""
<style>
/* Reduce default paddings for a mobile feel */
.block-container {padding-top: 0.75rem; padding-bottom: 2rem;}

/* Phone canvas: center and cap width to phone-like viewport */
.phone {
  max-width: 430px;  /* good for iPhone Pro Max in portrait */
  margin: 0 auto;
  padding: 12px 12px 24px;
}

/* Cards and small UI polish */
.card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 14px 16px;
}
.kv {display:flex; gap:8px; margin:6px 0;}
.key {opacity:0.7; min-width:120px;}
.value {font-weight:600;}
.small {font-size:13px; opacity:0.8;}

.navbar { display:flex; align-items:center; justify-content:space-between; margin-bottom: 6px; }
.brand { display:flex; align-items:center; gap:10px; }
.brand h1 { margin:0; font-size:22px; }
.icon { font-size:20px; }
.badge {display:inline-block; padding:2px 8px; border-radius:999px;
        background: rgba(46,204,113,0.15); border:1px solid rgba(46,204,113,0.35);
        font-size:12px;}
/* Bigger tap targets */
.stButton>button { padding: 12px 16px; border-radius: 12px; font-weight: 600; }
[data-baseweb="tab"] { padding: 12px 14px; }
</style>
""", unsafe_allow_html=True)

# -------------------- HELPERS --------------------
SEVERITY_MAP = {
    "home_care": 15,
    "see_primary_care_1-3_days": 40,
    "urgent_care_today": 70,
    "emergency_now": 92
}

def severity_bar(sev: int):
    sev = max(0, min(100, int(sev)))
    st.markdown(f"""
    <div style="width:100%; margin: 6px 0 8px 0;">
      <div style="position:relative; height:18px; border-radius:8px;
                  background: linear-gradient(90deg, #2ecc71, #f1c40f, #e67e22, #e74c3c);
                  box-shadow: inset 0 0 0 1px rgba(0,0,0,0.08);">
        <div title="{sev}"
             style="position:absolute; top:-4px; left:calc({sev}% - 8px);
                    width:0; height:0; border-left:8px solid transparent;
                    border-right:8px solid transparent; border-bottom:12px solid rgba(0,0,0,0.85);">
        </div>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:12px; opacity:0.7;">
        <span>Low</span><span>High</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_profile_card(p: dict):
    pregnant = "Yes" if p.get("pregnant") else "No"
    conditions = ", ".join(p.get("conditions", [])) or "None"
    meds = ", ".join(p.get("medications", [])) or "None"
    allergies = ", ".join(p.get("allergies", [])) or "None"
    temp = p.get("recent_vitals", {}).get("temp_f", "—")
    st.markdown(f"""
    <div class="card">
      <div style="display:flex; align-items:center; gap:14px; margin-bottom:8px;">
        <div style="width:48px; height:48px; border-radius:999px; background:rgba(255,255,255,0.10);
                    display:flex; align-items:center; justify-content:center; font-size:22px;">👤</div>
        <div>
          <div style="font-size:18px; font-weight:700;">{p.get('name','')}</div>
          <div class="small">{p.get('age','?')} • {p.get('sex','?').title()} • <span class="badge">Pregnant: {pregnant}</span></div>
        </div>
      </div>
      <div class="kv"><div class="key">Conditions</div><div class="value">{conditions}</div></div>
      <div class="kv"><div class="key">Medications</div><div class="value">{meds}</div></div>
      <div class="kv"><div class="key">Allergies</div><div class="value">{allergies}</div></div>
      <div class="kv"><div class="key">Recent Temp</div><div class="value">{temp} °F</div></div>
    </div>
    """, unsafe_allow_html=True)

# fallback coercer (used only if we must fall back to json_object mode)
def _coerce_triage_shape(d: dict) -> dict:
    def arr(x): return x if isinstance(x, list) else []
    def txt(x): return x if isinstance(x, str) else ""
    out = {
        "summary": txt(d.get("summary")),
        "differential": arr(d.get("differential")),
        "triage_level": d.get("triage_level") if d.get("triage_level") in {
            "home_care","see_primary_care_1-3_days","urgent_care_today","emergency_now"
        } else "home_care",
        "next_steps": arr(d.get("next_steps")),
        "self_care": arr(d.get("self_care")),
        "red_flags_triggered": arr(d.get("red_flags_triggered")),
        "what_to_watch": arr(d.get("what_to_watch")),
        "follow_up_questions": arr(d.get("follow_up_questions")),
        "sources": arr(d.get("sources")),
    }
    norm = []
    for it in out["differential"]:
        if isinstance(it, dict):
            norm.append({
                "condition": it.get("condition",""),
                "likelihood": it.get("likelihood","medium"),
                "rationale": it.get("rationale","")
            })
    out["differential"] = norm[:5]
    return out

def call_openai(symptom_text: str, profile: dict, chat_history: list) -> dict:
    payload = {"symptom_report": symptom_text, "patient_profile": profile}
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *[m for m in chat_history if m["role"] in ("user","assistant")],
        {"role": "user", "content": json.dumps(payload)}
    ]
    try:
        # Preferred: JSON Schema (clean, validated)
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            response_format={"type": "json_schema", "json_schema": TRIAGE_SCHEMA}
        )
        return json.loads(resp.choices[0].message.content)
    except TypeError:
        # Older SDKs: fall back to JSON mode and coerce
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": SYSTEM_PROMPT + "\nReturn ONLY valid JSON."}] +
                     [m for m in chat_history if m["role"] in ("user","assistant")] +
                     [{"role": "user", "content": json.dumps(payload)}],
            response_format={"type": "json_object"}
        )
        raw = resp.choices[0].message.content
        try:
            return _coerce_triage_shape(json.loads(raw))
        except Exception:
            return _coerce_triage_shape({"summary": raw})

# -------------------- STATE --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
if "past_results" not in st.session_state:
    st.session_state.past_results = []

# =========================================================
#                PHONE WRAPPER START
# =========================================================
st.markdown('<div class="phone">', unsafe_allow_html=True)

# -------------------- NAVBAR W/ PROFILE POPOVER --------------------
left, right = st.columns([0.75, 0.25])
with left:
    st.markdown("""
    <div class="navbar">
      <div class="brand">
        <span class="icon">🩺</span>
        <h1>Symptom Checker Ai</h1>
      </div>
    </div>
    """, unsafe_allow_html=True)
with right:
    pop = st.popover("👤 Profile", help="View patient profile")
    with pop:
        render_profile_card(PROFILE)

st.caption("Medical Answers • Next Steps")

# -------------------- TABS (MULTI-PAGE FEEL) --------------------
tab_check, tab_history, tab_about = st.tabs(["Check Symptoms", "History", "About"])

# ----- TAB: CHECK SYMPTOMS -----
with tab_check:
    st.subheader("Describe your symptoms")
    with st.form("symptom_form", clear_on_submit=False):
        symptom_text = st.text_area(
            "What's going on?",
            placeholder="e.g., 'Headache behind my eyes since this morning, 6/10, worse with light.'",
            height=140
        )
        submit_col, _ = st.columns([1, 1])
        with submit_col:
            submitted = st.form_submit_button("Analyze", use_container_width=True)

    if submitted and symptom_text.strip():
        with st.spinner("Analyzing..."):
            result = call_openai(symptom_text.strip(), PROFILE, st.session_state.chat_history)
            time.sleep(0.15)

        # keep conversation context + history
        st.session_state.chat_history.append({"role": "user", "content": symptom_text.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": result.get("summary","")})
        st.session_state.past_results.insert(0, {"input": symptom_text.strip(), "result": result})

        # ----- RESULT -----
        st.markdown("### Triage Recommendation")
        triage = result.get("triage_level", "home_care")
        severity_bar(SEVERITY_MAP.get(triage, 15))
        st.markdown(f"**Level:** `{triage}`")

        with st.container(border=True):
            st.markdown("##### Summary")
            st.write(result.get("summary", ""))

            if result.get("follow_up_questions"):
                st.markdown("##### Follow-up Questions")
                for q in result["follow_up_questions"]:
                    st.write(f"- {q}")

            st.markdown("##### Likely Causes (Short Differential)")
            for item in result.get("differential", []):
                st.write(f"- **{item['condition']}** ({item['likelihood']}): {item['rationale']}")

            st.markdown("##### Next Steps")
            for step in result.get("next_steps", []):
                st.write(f"- {step}")

            if result.get("self_care"):
                st.markdown("##### Self-care")
                for s in result["self_care"]:
                    st.write(f"- {s}")

            if result.get("what_to_watch"):
                st.markdown("##### What to Watch For")
                for s in result["what_to_watch"]:
                    st.write(f"- {s}")

            if result.get("red_flags_triggered"):
                st.markdown("##### Red Flags Triggered")
                for rf in result["red_flags_triggered"]:
                    st.error(rf)

            if result.get("sources"):
                st.markdown("##### Sources")
                for s in result["sources"]:
                    st.caption(f"- {s}")

# ----- TAB: HISTORY -----
with tab_history:
    st.subheader("Your recent checks")
    if not st.session_state.past_results:
        st.info("No symptom checks yet.")
    else:
        for item in st.session_state.past_results:
            res = item["result"]
            triage = res.get("triage_level", "home_care")
            with st.container(border=True):
                st.markdown(f"**Input:** {item['input']}")
                st.markdown(f"**Triage:** `{triage}`")
                st.markdown("**Summary:** " + res.get("summary",""))

# ----- TAB: ABOUT -----
with tab_about:
    st.subheader("About this demo")
    st.write("""
    This is a hackathon demo of a **symptom checker + triage assistant**.
    It provides educational guidance, not medical care. In an emergency, call local emergency services.
    """)

# =========================================================
#                PHONE WRAPPER END
# =========================================================
st.markdown('</div>', unsafe_allow_html=True)
