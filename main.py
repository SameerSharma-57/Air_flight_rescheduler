import streamlit as st
import pandas as pd
import json
import time
from Backend.codebase import get_best_sample

def save_boolean_variables_to_json(boolean_variables, filename="Backend/parameter_values.json"):
    with open(filename, "w") as json_file:
        json.dump(boolean_variables, json_file)

def load_boolean_variables_from_json(filename="Backend/parameter_values.json"):
    default = True
    try:
        with open(filename, "r") as json_file:
            boolean_variables = json.load(json_file)
        
        return boolean_variables
    except FileNotFoundError:
        with open("default_schema.json","r") as json_file:
            boolean_variables = json.load(json_file)
        return boolean_variables
    
def simulate_long_running_function():
    time.sleep(5)

def main():
    st.title("Mphasis Air flight scheduler")
    default = True

    # Load boolean variables from JSON file or use default values
    parameters_data = load_boolean_variables_from_json()

    # Create boolean variables using switches in the sidebar

    for heading, dict in parameters_data.items():
        with st.sidebar.expander(f"{heading} parameters"):
            for param, data in parameters_data[heading].items():
                data["selected"] = st.checkbox(param.capitalize(), value=data["selected"])

    # Display score inputs in the main section
    st.write("Enter Scores:")
    for category, params in parameters_data.items():
        with st.expander(f"{category} parameters for ranking:"):
            # Divide the number_inputs into three columns
            col1, col2, col3 = st.columns(3)
            for i, (param, data) in enumerate(params.items()):
                
                col = col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3
                data["score"] = col.number_input(f"Score for {param.capitalize()}", value=data["score"] ,key=f"{param}_score")

    save_boolean_variables_to_json(parameters_data)

    # # Display the selected boolean variables and scores
    # st.write("Selected Boolean Variables and Scores:")
    # for category, params in parameters_data.items():
    #     for param, data in params.items():
    #         if data['selected']:
    #             st.write(f"{category} - {param}: Score - {data['score']}")

    # with st.expander("Additional Parameters"):
    #     filter_by_value = st.checkbox("Filter by Value (Integer)")
    #     if filter_by_value:
    #         value_to_filter = st.number_input("Enter Integer Value to Filter", value=0)

    # Upload CSV file
    st.header("CSV File Uploader")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if st.sidebar.button("Run"):
        with st.spinner("Running..."):
            # Simulate a long-running function
            get_best_sample()

        st.success("Function executed successfully!")

    # If a file is uploaded, read and display its contents
    if uploaded_file is not None:
        st.write("Uploaded CSV file:")
        df = pd.read_csv(uploaded_file)
        st.write(df)

    df=pd.read_csv('Backend/final_output.csv')
    st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False).encode(),
            file_name="download.csv",
            key="download_button"
        )

if __name__ == "__main__":
    main()
