import streamlit as st
import pandas as pd
import json
import time
from Backend.codebase import get_best_sample
import os
from shutil import make_archive
import base64

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
    
def zip_folder(folder_path, output_path):
    # Make sure the folder exists
    
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    # Create a zip archive of the folder and its contents
    make_archive(output_path, 'zip', folder_path)

    print(f"Folder '{folder_path}' has been zipped to '{output_path}.zip'.")


def gen_results():
    get_best_sample()
    zip_folder('tempData','final')

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
            i=0
            for _i, (param, data) in enumerate(params.items()):
                if data["selected"]:
                    col = col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3
                    data["score"] = col.number_input(f"Score for {param.capitalize()}", value=data["score"] ,key=f"{param}_score")
                    i+=1

    save_boolean_variables_to_json(parameters_data)

    
    

    

    

    
    
    st.header(f"CSV File Uploader")
    selected_file_name = st.selectbox("Select File Name", ["INV", "PNRB", "PNRP", "SCH", "Cancelled"])


    # Upload CSV file based on selected file name
    uploaded_file = st.file_uploader(f"Upload CSV file for {selected_file_name}", type=["csv"])

    # Process and save the uploaded file
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            # Save the DataFrame to a specified folder
            save_location = f"Backend/final_data/{selected_file_name}.csv/"
            
            df.to_csv(save_location, index=False)
            st.success(f"{selected_file_name} file successfully uploaded!")
        except:
            st.error("Oops! Something went wrong...")



    st.header("Download the results")
    
    
    if st.sidebar.button("Run"):
        with st.spinner("Running..."):
            # Simulate a long-running function
            gen_results()

        st.success("Function executed successfully!")
        # Provide download link for the ZIP file

    zip_filename = "final.zip"  # Replace with your actual ZIP file name

    if not os.path.exists(zip_filename):

        zip_folder('tempData','final')

    
    
    with open(zip_filename, "rb") as f:
        zip_data = f.read()
        zip_base64 = base64.b64encode(zip_data).decode('utf-8')
        # st.markdown(f"**[Download {zip_filename}](data:application/zip;base64,{zip_base64})**", unsafe_allow_html=True)
        # st.success(f"ZIP file '{zip_filename}' is ready for download!")

    st.download_button(
        label=f"Download {zip_filename}",
        data=zip_data,
        key="download_button zip file",
        file_name=zip_filename,
        mime="application/zip"
    )

    


if __name__ == "__main__":
    main()
