import streamlit as st
import operator

st.set_page_config(page_title="Custom Logic Interpreter", layout="centered")
st.title("Custom Logic Interpreter (Debug Mode)")

# -------------------------
# Session state
# -------------------------
if "run" not in st.session_state:
    st.session_state.run = False

# -------------------------
# UI
# -------------------------
data_file = st.file_uploader("Upload data file (.txt)", type="txt")
logic_file = st.file_uploader("Upload logic file (.txt)", type="txt")

if st.button("Run Logic"):
    st.session_state.run = True

# -------------------------
# User input variables
# -------------------------
st.subheader("Environmental Inputs")

aext = st.number_input(
    "Outdoor air temperature in deg C",
    value=10.0,
    step=0.5
)

# -------------------------
# Parse data
# -------------------------
def parse_data(text):
    variables = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if "=" not in line:
            raise ValueError(f"Invalid data line: {line}")
        var, val = line.split("=")
        variables[var.strip()] = int(val.strip())
    return variables

# -------------------------
# Parse logic tree
# -------------------------

def remove_comments(lines):
    cleaned = []
    for line in lines:

        # remove inline comments
        if "//" in line:
            line = line.split("//", 1)[0]

        # strip whitespace
        line = line.rstrip()

        # ignore empty lines after comment removal
        if line.strip() == "":
            continue

        cleaned.append(line)

    return cleaned


def parse_logic(lines):
    root = []
    stack = []

    for raw_line in lines:
        indent = len(raw_line) - len(raw_line.lstrip())
        text = raw_line.strip()

        if not text:
            continue

        node = {
            "indent": indent,
            "text": text,
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
# Identify logic type
# -------------------------
OPS = ["==", ">=", "<=", ">", "<"]

def classify_line(text):
    if text.startswith("if "):
        return "IF"
    if text.startswith("else"):
        return "ELSE"
    if "=" in text:
        return "ASSIGN"
    return "UNKNOWN"

# -------------------------
# Display interpreted logic
# -------------------------
def display_interpretation(nodes, level=0):
    for node in nodes:
        kind = classify_line(node["text"])
        st.text("  " * level + f"- [{kind}] {node['text']}")
        if node["children"]:
            display_interpretation(node["children"], level + 1)

# -------------------------
# Evaluate condition
# -------------------------
OP_FUNCS = {
    "==": operator.eq,
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
}

def evaluate_condition(condition, variables):
    for op in OP_FUNCS:
        if op in condition:
            left, right = condition.split(op)

            left = left.strip()
            right = right.strip()

            # get left value
            if left in variables:
                left_val = variables[left]
            else:
                left_val = float(left)

            # get right value
            if right in variables:
                right_val = variables[right]
            else:
                right_val = float(right)

            return OP_FUNCS[op](left_val, right_val)

    raise ValueError(f"Invalid condition: {condition}")

# -------------------------
# Execute logic
# -------------------------
def execute(nodes, variables):
    for node in nodes:
        text = node["text"]

        if text.startswith("if "):
            condition = text[3:].strip()
            if evaluate_condition(condition, variables):
                execute(node["children"], variables)
                return True

        elif text.startswith("else"):
            execute(node["children"], variables)
            return True

        elif "=" in text:
            var, val = text.split("=")
            variables[var.strip()] = int(val.strip())
            return True

    return False

# -------------------------
# Decision output based on i
# -------------------------
def heat_recovery_recommendation(variables):
    if "i" not in variables:
        return "No decision made (i not defined)."

    i_value = variables["i"]

    if i_value == 0:
        return "other heat waste recovery option"
    elif i_value == 1:
        return "use district heating"
    else:
        return f"Unknown option for i = {i_value}"

# -------------------------
# Run
# -------------------------
if st.session_state.run:
    try:
        if not data_file or not logic_file:
            st.warning("Please upload both files.")
        else:
            variables = parse_data(data_file.read().decode("utf-8"))

# Inject user input into interpreter variables
            variables["aext"] = aext
            logic_lines = logic_file.read().decode("utf-8").splitlines()
            logic_tree = parse_logic(logic_lines)

            st.subheader("Parsed Variables")
            st.write(variables)

            st.subheader("Interpreted Logic")
            display_interpretation(logic_tree)

            execute(logic_tree, variables)

            st.subheader("Final Variables After Execution")
            st.success(variables)


    # -------------------------
# Show recommendation
# -------------------------
recommendation = heat_recovery_recommendation(variables)

st.subheader("Recommended Heat Waste Recovery Method")
st.info(recommendation)

    except Exception as e:
        st.error("Error detected")
        st.code(str(e))

    st.session_state.run = False
