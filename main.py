import ast
import streamlit as st
import os 
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from database import create_database, save_analysis
from database import get_analysis_history
load_dotenv()
create_database()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="CodeSense AI | Code Explainer",
    page_icon="💻",
    layout="wide"
)
if not api_key:
    st.warning("Gemini API key not found.check your .env file.")
else:
    client = genai.Client(api_key=api_key)

st.markdown("""
<style>
.stApp {
    background: #ffffff;
    color: #000000;
}
[data-testid="stSidebar"] {
    background: #f5f5f5;
}
.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}
div.stButton > button {
    background: #6366f1;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.65rem 1rem;
    font-weight: 600;
}
div.stButton > button:hover {
    background: #4f46e5;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("💻 CodeSense AI")
st.sidebar.caption("Python Code Intelligence")
st.sidebar.divider()
st.sidebar.markdown("### Features")
st.sidebar.markdown("""
- Code analysis
- Line-by-line explanation
- Syntax error detection
- Python concept detection
- Sample code library
""")
st.sidebar.info(
    "Your code is analyzed without executing it."
)

st.title("💻 CodeSense AI")
st.markdown(
    "### Understand code. Find errors. Learn faster."
)
st.caption(
    "A Python code analysis and learning assistant"
)

sample_code = """def calculate_total(price, quantity):
    total = price * quantity
    if total > 1000:
        return total * 0.90
    return total

print(calculate_total(600, 2))
"""

if "code_input" not in st.session_state:
    st.session_state.code_input = sample_code

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("📝 Python Code Editor")
    uploded_file = st.file_uploader(
        "upload python File",
        type=["py"]
    )
    if uploded_file is not None:
        code = uploded_file.getvalue().decode("utf-8")
        st.session_state.code_input = code
    code = st.text_area(
        "Paste your Python code below",
        key="code_input",
        height=340,
        label_visibility="collapsed"
    )

    analyze = st.button(
        "🔍 Analyze Code",
        use_container_width=True
    )

with right:
    st.subheader("📊 Code Overview")

    lines = [
        line for line in code.splitlines()
        if line.strip()
    ]

    st.metric("Lines of Code", len(lines))

    if code.strip():
        st.metric(
            "Characters",
            len(code)
        )
    else:
        st.metric("Characters", 0)

    st.caption(
        "Analysis checks syntax and identifies "
        "common Python concepts."
    )

if analyze:
    if not code.strip():
        st.warning("Please enter some Python code.")
    else:
        try:
            tree = ast.parse(code)
            st.success("✅ Syntax check passed!")
            save_analysis(code, "success")
            if api_key:
                try:
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                                contents=(
                                    "Explain python code in simple english."
                                    "Describe its purpose and logic.\n\n"
                                    + code
                                )
                    )
                    ai_explanation = response.text
                    st.subheader("AI-powered Explanation")
                    st.write(ai_explanation)

                except Exception as error:
                    st.error(f"Gemini API error: {error}")
            
            functions = [
                node.name for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
            ]

            classes = [
                node.name for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            ]

            imports = [
                node.names[0].name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                and node.names
            ]

            concepts = []

            if functions:
                concepts.append("Functions")
            if classes:
                concepts.append("Classes")
            if any(isinstance(n, ast.If)
                   for n in ast.walk(tree)):
                concepts.append("Conditions")
            if any(isinstance(n, (ast.For, ast.While))
                   for n in ast.walk(tree)):
                concepts.append("Loops")
            if any(isinstance(n, ast.Call)
                   for n in ast.walk(tree)):
                concepts.append("Function calls")
            if imports or any(
                isinstance(n, ast.ImportFrom)
                for n in ast.walk(tree)
            ):
                concepts.append("Imports")

            tab1, tab2, tab3 = st.tabs([
                "📖 Explanation",
                "🔎 Line by Line",
                "🧩 Code Structure"
            ])

            with tab1:
                st.subheader("What does this code do?")
                st.write(
                    "The code is valid Python syntax. "
                    "Review the statements below to "
                    "understand its logic."
                )

                if functions:
                    st.write(
                        "**Functions defined:** "
                        + ", ".join(functions)
                    )

                if classes:
                    st.write(
                        "**Classes defined:** "
                        + ", ".join(classes)
                    )

                if concepts:
                    st.write(
                        "**Concepts detected:** "
                        + ", ".join(concepts)
                    )

                if not concepts:
                    st.write(
                        "This code uses basic Python "
                        "statements or expressions."
                    )

            with tab2:
                st.subheader("Line-by-line explanation")

                for number, line in enumerate(
                    code.splitlines(), start=1
                ):
                    text = line.strip()

                    if not text:
                        continue
                    elif text.startswith("#"):
                        explanation = "Comment: a note for readers."
                    elif text.startswith("def "):
                        explanation = (
                            "Defines a function that can be called later."
                        )
                    elif text.startswith("class "):
                        explanation = (
                            "Defines a class for creating objects."
                        )
                    elif text.startswith("import "):
                        explanation = (
                            "Imports a module into this program."
                        )
                    elif text.startswith("from "):
                        explanation = (
                            "Imports selected items from a module."
                        )
                    elif text.startswith("if "):
                        explanation = (
                            "Checks a condition; the indented block "
                            "runs when it is true."
                        )
                    elif text.startswith("elif "):
                        explanation = (
                            "Checks another condition if earlier "
                            "conditions were false."
                        )
                    elif text == "else:":
                        explanation = (
                            "Runs when the preceding conditions are false."
                        )
                    elif text.startswith("for "):
                        explanation = (
                            "Repeats a block for each item in a sequence."
                        )
                    elif text.startswith("while "):
                        explanation = (
                            "Repeats a block while a condition is true."
                        )
                    elif text.startswith("return"):
                        explanation = (
                            "Sends a value back from a function."
                        )
                    elif text.startswith("print("):
                        explanation = (
                            "Displays information in the output."
                        )
                    elif "=" in text and "==" not in text:
                        explanation = (
                            "Assigns a value to a variable."
                        )
                    else:
                        explanation = (
                            "Executes an expression or statement; "
                            "its exact effect depends on the code."
                        )

                    with st.expander(
                        f"Line {number}: {text[:65]}"
                    ):
                        st.code(text, language="python")
                        st.write(explanation)

            with tab3:
                st.subheader("Code structure")
                st.write("**Functions:**", functions or "None")
                st.write("**Classes:**", classes or "None")
                st.write("**Imported modules:**", imports or "None")
                st.write("**Concepts:**", concepts or "Basic Python")

                st.code(
                    ast.dump(tree, indent=2),
                    language="text"
                )

            st.info(
                "This tool checks syntax and common code "
                "patterns. It does not execute your code "
                "or guarantee that the program's logic is correct."
            )

        except SyntaxError as error:
            st.error("❌ Python syntax error detected.")
            save_analysis(code,"Synatx Error")
            st.write(f"**Message:** {error.msg}")
            st.write(f"**Line:** {error.lineno}")
            st.write(
                "Check the indicated line for missing "
                "colons, brackets, quotes or indentation."
            )
        except Exception as error:
            st.error(f"Analysis error: {error}")
            st.divider()
st.subheader("📚 Analysis History")

if st.button("View Analysis History"):
    history = get_analysis_history()

    if history:
        for record in history:
            st.write("ID:", record[0])
            st.code(record[1], language="python")
            st.write("Syntax Status:", record[2])
            st.write("Created At:", record[3])
            st.divider()
    else:
        st.info("No analysis history found.")