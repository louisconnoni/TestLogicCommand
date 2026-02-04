import streamlit as st
import operator

st.set_page_config(page_title="Custom Logic Interpreter")
st.title("Custom Logic Interpreter")

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
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
}

def evaluate_condition(text, variables):
    for op_symbol, op_func in OPS.items():
        if op_symbol in text:
            left, right = text.spl
