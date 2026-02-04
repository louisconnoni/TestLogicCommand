import streamlit as st

st.set_page_config(page_title="Custom Logic Interpreter")
st.title("Custom Logic Interpreter")

# -------------------------
# Data file parser
# -------------------------
def parse_data(text):
    data = {}
    for line in text.splitlines():
        if "=" in line:
            var, val = line.split("=")
            data[var.strip()] = int(val.strip())
    return data

# -------------------------
# Logic parser
# -------------------------
def parse_logic(lines):
    parsed = []
    stack = []

    for raw_line in lines:
        indent = len(raw_line) - len(raw_line.lstrip())
        line = raw_line.strip()

        if not line:
            continue

        node = {
            "indent": indent,
            "line": line,
            "children": []
        }

        while stack and stack[-1]["indent"] >= indent:
            stack.pop()

        if stack:
            stack[-1]["children"].append(node)
        else:
            parsed.append(node)

        stack.append(node)

    return parsed

# -------------------------
# Logic executor
# -------------------------
def evaluate(nodes, variables):
    for node in nodes:
        line = node["line"]

        if line.startswith("if"):
            _, condition = line.split("if", 1)
            var, val = condition.split("==")
            var = var.strip()
            val = int(val.strip())

            if variables.get(var) == val:
                evaluate(node["children"], variables)
                return

        elif line.startswith("else"):
            _, var = line.split("else", 1)
            var = var.strip()

            evaluate(node["children"], variables)
            return

        elif "=" in line:
            var, val = line.split("=")
            variables[var.strip()] = int(val.strip())

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

        parsed_logic = parse_logic(logic_lines)
        evaluate(parsed_logic, variables)

        st.subheader("Final Variables")
        st.write(variables)

    except Exception as e:
        st.error("Execution error")
        st.code(str(e))

