import streamlit as st
import operator

# MUST be first Streamlit command
st.set_page_config(page_title="Custom Logic Interpreter", layout="centered")

st.title("Custom Logic Interpreter")

# -------------------------
# File uploaders (ALWAYS visible)
# -------------------------
data_file = st.file_uploader("Upload data file (.txt)", type="txt")
logic_file = st.file_uploader("Upload logic file (.txt)", type="txt")

run_button = st.button("Run Logic")

# -------------------------
# Parse data file
# -------------------------
def parse_data(text):
    variables = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        var, val = line.split("=")
        variables[var.strip()] = int(val.strip())
    return variables

# -------------------------
# Parse logic into tree
# -------------------------
def parse_logic(lines):
    root = []
    stack = []

    for raw_line in lines:
        indent = len(raw_line) - len(raw_line.lstrip())
        line = raw_line.strip()

        if not line:
            continue

        node = {
            "indent": indent,
            "text": line,
            "children": []
        }

        while stack and stack[-1]["indent"] >= indent:
            stack.pop()

        if stack:
            stack[-1]["children"].append(node)
        else:
            root.append(node)

        stack.append(node)

    return root

# -------------------------
# Display logic tree
# -------------------------
def display_logic(nodes, level=0):
    for node in nodes:
        st.text("  " * level + "- " + node["text"])
        if node["children"]:
            display_logic(node["children"], level + 1)

# -------------------------
# Condition evaluation
# -------------------------
OPS = {
    "==": operator.eq,
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
}

def evaluate_condition(condition, variables):
    for symbol, func in OPS.items():
        if symbol in condition:
            left, right = condition.split(symbol)
            left = left.strip()
            right = int(right.strip())
            return func(variables.get(left), right)
    raise ValueError(f"Invalid condition: {condition}")

# -------------------------
# Exec
