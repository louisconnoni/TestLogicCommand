import streamlit as st

st.set_page_config(page_title="Logic Executor", layout="centered")

st.title("Logic Executor App")
st.write(
    "Upload a **data file** and a **logic file**. "
    "The logic file can include nested for-loops and will be executed on the data."
)

# File uploaders
data_file = st.file_uploader("Upload data file (.txt)", type="txt")
logic_file = st.file_uploader("Upload logic file (.txt)", type="txt")

if data_file and logic_file:
    try:
        # --- Read and parse data file ---
        data_text = data_file.read().decode("utf-8")
        data = [int(x) for x in data_text.split()]

        st.subheader("Parsed Data")
        st.write(data)

        # --- Read logic file ---
        logic_code = logic_file.read().decode("utf-8")

        st.subheader("Logic Code")
        st.code(logic_code, language="python")

        # --- Execution environment ---
        # Variables the logic file is allowed to access
        local_vars = {
            "data": data
        }

        # Execute logic
        exec(logic_code, {}, local_vars)

        # --- Display output ---
        st.subheader("Result")
        if "output" in local_vars:
            st.success("Logic executed successfully!")
            st.write(local_vars["output"])
        else:
            st.warning(
                "Logic executed, but no variable named 'output' was found.\n\n"
                "Make sure your logic file assigns a value to `output`."
            )

    except Exception as e:
        st.error("An error occurred while executing the logic:")
        st.code(str(e))


