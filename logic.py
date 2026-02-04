import streamlit as st

st.set_page_config(page_title="Logic Debugger")
st.title("Custom Logic Debugger")

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
# Pretty-print logic tree
# -------------------------
def display_logic(nodes, level=0):
    for node in nodes:
        st.text("  " * level + "- " + node["text"])
        if node["children"]:
            display_logic(node["children"], level + 1)

# -------------------------
# Streamlit UI
# -------------------------
data_file = st.file_uploader("Upload data file (.txt)", type="txt")
logic_file = st.file_uploader("Upload logic file (.txt)", type="txt")

if data_file and logic_file:
    try:
        data_text = data_file.read().decode("utf-8")
        logic_text = logic_file.read().decode("utf-8")

        variables = parse_data(data_text)
        logic_lines = logic_text.splitlines()
        logic_tree = parse_logic(logic_lines)

        st.subheader("Parsed Variables")
        st.write(variables)

        st.subheader("Parsed Logic Tree")
        display_logic(logic_tree)

    except Exception as e:
        st.error("Parsing error")
        st.code(str(e))
