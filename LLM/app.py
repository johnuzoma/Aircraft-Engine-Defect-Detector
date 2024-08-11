import streamlit as st
import pandas as pd
import os
from menu import menu
from functionality import detect_defect, model, genai
#import google.generativeai as genai

# Display menu
menu()

# Insert a file uploader that accepts multiple files at a time
uploaded_files = st.file_uploader("Choose one or more image files", accept_multiple_files=True, type=['png', 'jpg', 'webp'])

if len(uploaded_files) > 0:
    # Image(s) uploaded placeholder
    if len(uploaded_files) > 1:
        st.write(len(uploaded_files), "images uploaded!")
    else: 
        st.write(len(uploaded_files), "image uploaded!")
    
    # Define the path to the images directory named 'static' in the root folder
    images_dir = os.path.join("static")

    # Create the images directory if it doesn't exist
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    # Save the uploaded files to the images directory
    for uploaded_file in uploaded_files:
        file_path = os.path.join(images_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    # Display detect button
    detect_bt = st.button("Detect defect", type="primary")
    
    # Detect defects and generate reports when clicked
    if detect_bt:
        # Detect defects and store in a variable
        results = detect_defect(uploaded_files)

        # Initialize a pandas dataframe
        df = pd.DataFrame(results, columns=["Image", "Defect", "Bounding Box Coordinates"])

        # Reset the index and set it to start from 1
        df.index = df.index + 1
        
        # Configure the dataframe
        st.data_editor(
            df,
            column_config={
                "Image": st.column_config.ImageColumn(
                    "Clickable Image"
                )
            },
            disabled=["Image", "Defect", "Bounding Box Coordinates"],
            hide_index=False,
        )
        
        # Generate a report of the defects
        with st.container(border=True) as c:
            st.header("Aircraft Engine Inspection Report")
            st.divider()
            for i, file in enumerate(uploaded_files):
                st.subheader(file.name)  
                col1, col2, col3 = st.columns(3)
                with col1: 
                    st.image("static/img+bbox/"+file.name, width=100)
                with col2:
                    uploaded_file = genai.upload_file(path="static/img+bbox/"+file.name, display_name=file.name)
                    response_report = model.generate_content([uploaded_file, "Provide a 3-line description of the aero engine defect highlighted by the bounding box."])
                    st.markdown("**Defect Description:** " + response_report.text)
                
                # Output the bounding box coordinates for the corresponding index
                # Use loc with 1-based index
                if i + 1 in df.index:
                    with col3:
                        bbox_coords = df.loc[i + 1, 'Bounding Box Coordinates']
                        st.markdown("**Bounding Box Coordinates:** " + str(bbox_coords))
                st.divider()
    else:
        pass
else:
    pass