import streamlit as st
from PIL import Image, ImageDraw
import ast
import google.generativeai as genai

# Configure the GenAI service with API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Choose a Gemini model
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

# Function to detect defects in images
@st.cache_data
def detect_defect(files):
    results = []
    for file in files:
        # Upload the file to the GenAI service
        uploaded_file = genai.upload_file(path="static/"+file.name, display_name=file.name)

        # Make API calls to the Gemini model
        response_defect = model.generate_content([uploaded_file, "Diagnose the image to determine if there is a defect in the aircraft engine, outputting ONLY one of these words: scratch or dirty or stain or dot or crease or damage."])
        response_bbox = model.generate_content([uploaded_file, "Return a bounding box for the detected defect in the uploaded image. Your output must be in this form: [ymin, xmin, ymax, xmax]. No side text."])
        
        # Convert bbox coordinates to list of numeric values
        global bbox 
        bbox = ast.literal_eval(response_bbox.text)
        
        # Open the image file
        image = Image.open("static/"+file.name)
        
        # Get the dimensions of the image
        width, height = image.size

        # Convert these coordinates to the dimensions of the original image
        bbox[0] = round((bbox[0]/1000) * height)
        bbox[1] = round((bbox[1]/1000) * width)
        bbox[2] = round((bbox[2]/1000) * height)
        bbox[3] = round((bbox[3]/1000) * width)
        
        # Create an ImageDraw object
        draw = ImageDraw.Draw(image)

        # Draw the bounding box
        draw.rectangle([bbox[1], bbox[0], bbox[3], bbox[2]], outline="red", width=10)

        # Save the image
        output_file_path = "static/img+bbox/"+file.name
        image.save(output_file_path)

        # Append uploaded_file and response to results list
        results.append(("app/"+output_file_path, response_defect.text, bbox))    
    return results
