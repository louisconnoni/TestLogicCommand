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
        variables[var.strip()] = float(val.strip())
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
    i = 0

    while i < len(nodes):
        node = nodes[i]
        text = node["text"]

        # ---------------- IF ----------------
        if text.startswith("if "):
            condition = text[3:].strip()

            if evaluate_condition(condition, variables):
                execute(node["children"], variables)

                # skip following else block
                if i + 1 < len(nodes) and nodes[i+1]["text"].startswith("else"):
                    i += 1

            else:
                # run else block if it exists
                if i + 1 < len(nodes) and nodes[i+1]["text"].startswith("else"):
                    execute(nodes[i+1]["children"], variables)
                    i += 1

        # ---------------- ELSE ----------------
        elif text.startswith("else"):
            # already handled by IF
            pass

        # ---------------- ASSIGNMENT ----------------
        elif "=" in text:
            var, val = text.split("=")
            var = var.strip()
            val = val.strip()

            # allow assigning variables OR numbers
            if val in variables:
                variables[var] = variables[val]
            else:
                variables[var] = float(val)

        i += 1

# -------------------------
# Decision output based on i
# -------------------------
def heat_recovery_recommendation(variables):
    if "i" not in variables:
        return "No decision made (i not defined)."

    i_value = int(variables["i"])

    if i_value == 0:
        return "other heat waste recovery option"
    elif i_value == 1:
        return "use district heating"
    else:
        return f"Unknown option for i = {i_value}"

# -------------------------
# Run
# -------------------------
# -------------------------
# Run
# -------------------------
if st.session_state.run:
    try:
        if not data_file or not logic_file:
            st.warning("Please upload both files.")
        else:
            # Parse data file
            variables = parse_data(data_file.read().decode("utf-8"))

            # guarantee decision variable exists
            if "i" not in variables:
                variables["i"] = 0

            # Inject environmental input
            variables["aext"] = float(aext)

            # Parse logic file
            logic_lines = logic_file.read().decode("utf-8").splitlines()
            logic_lines = remove_comments(logic_lines)
            logic_tree = parse_logic(logic_lines)

            st.subheader("Parsed Variables")
            st.write(variables)

            st.subheader("Interpreted Logic")
            display_interpretation(logic_tree)

            # Execute interpreter
            execute(logic_tree, variables)

            st.subheader("Final Variables After Execution")
            st.success(variables)

            # -------------------------
            # Recommendation (NOW SAFE)
            # -------------------------
            recommendation = heat_recovery_recommendation(variables)

            st.subheader("Recommended Heat Waste Recovery Method")
            st.info(recommendation)

    except Exception as e:
        st.error("Error detected")
        st.code(str(e))

    st.session_state.run = False

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
