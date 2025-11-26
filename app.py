
import os
import streamlit as st
from groq import Groq

# ---- Page setup ----
st.set_page_config(
    page_title="Advanced Smart Calculator",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧮 Advanced Smart Calculator")
st.markdown("A modern calculator with AI explanations powered by **Groq LLM**")

# ---- Session state ----
if "history" not in st.session_state:
    st.session_state["history"] = []

def create_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None, "GROQ_API_KEY missing!"
    try:
        return Groq(api_key=api_key), None
    except Exception as e:
        return None, f"Error: {e}"

def calculate(a, b, op_label):
    if op_label == "Add (+)": return a + b, "+"
    if op_label == "Subtract (-)": return a - b, "-"
    if op_label == "Multiply (×)": return a * b, "×"
    if op_label == "Divide (÷)":
        if b == 0: raise ZeroDivisionError("Cannot divide by zero.")
        return a / b, "÷"
    if op_label == "Power (a^b)": return a ** b, "^"
    if op_label == "Percentage (a% of b)": return (a / 100) * b, "% of"
    raise ValueError("Unknown operation.")

def add_to_history(expression, result):
    st.session_state["history"].insert(0, {"expression": expression, "result": result})
    st.session_state["history"] = st.session_state["history"][:10]

# ---- Sidebar: history ----
with st.sidebar:
    st.header("📜 History")
    if st.session_state["history"]:
        for item in st.session_state["history"]:
            st.write(f"{item['expression']} = **{item['result']}**")
        if st.button("🧹 Clear history"):
            st.session_state["history"] = []
            st.experimental_rerun()
    else:
        st.info("No calculations yet.")

# ---- Tabs for sections ----
tab1, tab2, tab3 = st.tabs(["Basic Calculator", "AI Explanation", "Natural Language AI"])

# ================== TAB 1: BASIC CALCULATOR ==================
with tab1:
    st.header("1️⃣ Basic Calculator")
    col1, col2 = st.columns(2)
    with col1: num1 = st.number_input("First number", value=0.0)
    with col2: num2 = st.number_input("Second number", value=0.0)

    operation = st.selectbox("Choose operation", [
        "Add (+)", "Subtract (-)", "Multiply (×)", "Divide (÷)", "Power (a^b)", "Percentage (a% of b)"
    ])

    if st.button("✅ Calculate"):
        try:
            result, symbol = calculate(num1, num2, operation)
            expression = f"{num1} {symbol} {num2}" if symbol != "% of" else f"{num1}% of {num2}"
            st.success(f"Result: {expression} = {result}")
            st.info(f"Stored in history ✅")
            add_to_history(expression, result)
            st.session_state["last_calc"] = {"expression": expression, "result": result}
        except Exception as e:
            st.error(f"⚠️ {e}")

# ================== TAB 2: AI EXPLANATION ==================
with tab2:
    st.header("2️⃣ Ask Groq to Explain")
    if "last_calc" not in st.session_state or st.session_state["last_calc"] is None:
        st.info("Perform a calculation first.")
    else:
        lc = st.session_state["last_calc"]
        default_prompt = f"Explain step by step how to compute {lc['expression']} to get {lc['result']} for a beginner."
        user_prompt = st.text_area("Customize your question:", value=default_prompt, height=120)
        if st.button("🤖 Explain with AI"):
            client, err = create_groq_client()
            if err: st.error(f"❌ {err}")
            else:
                with st.spinner("Asking Groq..."):
                    try:
                        completion = client.chat.completions.create(
                            messages=[{"role":"user","content":user_prompt}],
                            model="llama-3.3-70b-versatile"
                        )
                        explanation = completion.choices[0].message.content
                        st.subheader("AI Explanation")
                        st.write(explanation)
                    except Exception as e:
                        st.error(f"Error: {e}")

# ================== TAB 3: NATURAL LANGUAGE AI ==================
with tab3:
    st.header("3️⃣ Natural Language Calculator (AI)")
    question = st.text_input("Type a math question in plain English", value="What is 12 divided by 3 plus 4?")
    if st.button("🧠 Ask AI"):
        if not question.strip():
            st.warning("Please type a question.")
        else:
            client, err = create_groq_client()
            if err: st.error(f"❌ {err}")
            else:
                with st.spinner("AI calculating..."):
                    try:
                        prompt = (
                            "You are a careful math tutor. Solve the following math question, "
                            "give the numeric answer and explain step by step in simple language.\n\n"
                            f"Question: {question}"
                        )
                        completion = client.chat.completions.create(
                            messages=[{"role":"user","content":prompt}],
                            model="llama-3.3-70b-versatile"
                        )
                        answer = completion.choices[0].message.content
                        st.subheader("AI Answer")
                        st.write(answer)
                    except Exception as e:
                        st.error(f"Error: {e}")
