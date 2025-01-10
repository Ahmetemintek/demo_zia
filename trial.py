from io import BytesIO
import json
import os
from PIL import Image
import requests
import time
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


# Page configuration
st.set_page_config(
    page_title="Zia.AI - Image Generation",
    page_icon="🎨",
    layout="wide"
)


# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/Ahmetemintek/demo_zia/master/ziaistudio_logo.jpeg", width=200)
    st.markdown("---")
    feature = st.selectbox(
        "Select Feature",
        ["Text to Image", "Image to Image", "Sketch to Image", "Image to 3D"],
        key="feature_selector"
    )
    st.markdown("---")
    st.markdown('<p class="sidebar-info">Powered by Zia.ai</p>', unsafe_allow_html=True)

if feature == "Text to Image":
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Create your image")
        prompt = st.text_area(
            "Enter your prompt:",
            "A modern style house with 2 storeys and a garden. The house is in the middle of a forest.",
            height=100
        )
        
        negative_prompt = st.text_area(
            "Enter your negative prompt:",
            "No mountains, no water",
            height=50
        )

    with col2:
        st.markdown("### Settings")
        style_preset = st.selectbox(
            "Style Preset",
            ["3d-model", "analog-film", "anime", "cinematic", "comic-book", 
             "digital-art", "enhance", "fantasy-art", "isometric", "line-art", 
             "low-poly", "modeling-compound", "neon-punk", "origami", 
             "photographic", "pixel-art", "tile-texture"]
        )
        
        output_format = st.selectbox("Output Format", ["webp", "png", "jpg"])
        aspect_ratio = st.selectbox(
            "Aspect Ratio",
            ["1:1", "16:9", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"]
        )

    # Center the generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_button = st.button("Generate Image ✨", use_container_width=True)

    if generate_button:
        try:
            with st.spinner('Generating your image...'):
                # Call Stability.ai API to generate image
                stability_api_url = "https://api.stability.ai/v2beta/stable-image/generate/core"
                
                headers = {
                    "authorization": f"Bearer {st.secrets['STABILITY_API_KEY']}",
                    "accept": "image/*"
                }
                
                # Prepare data payload
                data = {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "style_preset": style_preset,
                    "output_format": output_format,
                    "aspect_ratio": aspect_ratio
                }
                
                # Make API request
                response = requests.post(
                    stability_api_url,
                    headers=headers,
                    files={"none": ''},  # Required as per documentation
                    data=data
                )
                
                if response.status_code == 200:
                    # Create columns for centered image display
                    img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                    with img_col2:
                        # Display the image directly from response content
                        image = Image.open(BytesIO(response.content))
                        st.image(image, caption="Generated Image", use_column_width=True)
                        
                        # Add download button
                        st.download_button(
                            label="⬇️ Download Image",
                            data=response.content,
                            file_name=f"generated_image.{output_format}",
                            mime=f"image/{output_format}",
                            use_container_width=True
                        )
                else:
                    error_detail = response.json().get('message', response.text)
                    st.error(f"Error generating image: {error_detail}")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

            

elif feature == "Image to Image":
    st.markdown("### Image to Image Generation")
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Image upload
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
        # Prompt inputs
        prompt = st.text_area(
            "Enter your prompt:",
            "Transform this building into a futuristic architectural masterpiece with sleek glass facades, floating elements, and sustainable features like vertical gardens. Add dramatic lighting and a twilight sky background.",
            height=100
        )
        
        negative_prompt = st.text_area(
            "Enter your negative prompt:",
            "blurry, distorted proportions, unrealistic scale, poor lighting, oversaturated colors, low quality, grainy, deformed architecture, structurally impossible elements",
            height=50
        )

        
    with col2:
        st.markdown("### Settings")
        # Sometimes referred to as denoising
        # A value of 0 would yield an image that is identical to the input. A value of 1 would be as if you passed in no image at all.
        image_strength = st.slider(
            "Image Strength",
            min_value=0.0,
            max_value=1.0,
            value=0.35,
            help="Lower values preserve more of the original image"
        )

        cfg_scale = st.slider(
            "CFG Scale",
            min_value=1.0,
            max_value=10.0,
            value=5.0,
            help="Higher values keep your image closer to your prompt"
        )
        
        output_format = st.selectbox("Output Format", ["png", "jpeg"])

    # Center the generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_button = st.button("Transform Image ✨", use_container_width=True)

    if generate_button:
        if uploaded_file is None:
            st.error("Please upload an image first!")
        else:
            try:
                with st.spinner('Transforming your image...'):
                    # Prepare the image
                    image_data = uploaded_file.getvalue()
                    
                    # Call Stability.ai API for image-to-image
                    stability_api_url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
                    
                    headers = {
                        "authorization": f"Bearer {st.secrets['STABILITY_API_KEY']}",
                        "accept": "image/*"
                    }
                
                    # Prepare multipart form data
                    files = {
                        "image": ("image.png", image_data, "image/png")
                    }
                
                    
                    form_data = {
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "cfg_scale": cfg_scale,
                        "output_format": output_format,
                        "strength": image_strength,
                        "mode": "image-to-image",
                        "model": "sd3.5-large-turbo"
                        # "model": "sd3-medium"
                    }
                    
                    # Make API request
                    response = requests.post(
                        stability_api_url,
                        headers=headers,
                        files=files,
                        data=form_data
                    )
                    
                    if response.status_code == 200:
                        # Create columns for centered image display
                        img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                        with img_col2:
                            # Display the transformed image
                            image = Image.open(BytesIO(response.content))
                            st.image(image, caption="Transformed Image", use_column_width=True)
                            
                            # Add download button
                            st.download_button(
                                label="⬇️ Download Image",
                                data=response.content,
                                file_name=f"transformed_image.{output_format}",
                                mime=f"image/{output_format}",
                                use_container_width=True
                            )
                    else:
                        error_detail = response.json().get('message', response.text)
                        st.error(f"Error transforming image: {error_detail}")
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")


elif feature == "Sketch to Image":
    st.markdown("### Sketch to Image Generation")
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Sketch upload
        uploaded_file = st.file_uploader(
            "Upload your sketch",
            type=["png", "jpg", "jpeg", "webp"],
            help="Upload a black and white sketch or line drawing"
        )
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                width, height = image.size
                
                # Display image info and preview
                st.image(image, caption="Uploaded Sketch", use_column_width=True)
                st.info(f"Image Format: {image.format.lower()}, Dimensions: {width}x{height}px")
                
            except Exception as e:
                st.error(f"Error processing sketch: {str(e)}")
                st.stop()
            
        # Prompt input
        prompt = st.text_area(
            "Enter your prompt:",
            "Transform this sketch into a detailed architectural visualization with modern materials, dramatic lighting, and realistic textures",
            height=100
        )

    with col2:
        st.markdown("### Settings")
        # Control strength slider
        control_strength = st.slider(
            "Control Strength",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            help="Higher values make the output more faithful to the input sketch"
        )
        
        output_format = st.selectbox("Output Format", ["webp", "png", "jpeg"])

    # Center the generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_button = st.button("Generate from Sketch ✨", use_container_width=True)

    if generate_button:
        if uploaded_file is None:
            st.error("Please upload a sketch first!")
        else:
            try:
                with st.spinner('Generating from your sketch...'):
                    # Prepare the sketch
                    sketch_data = uploaded_file.getvalue()
                    
                    # Call Stability.ai API for sketch-to-image
                    stability_api_url = "https://api.stability.ai/v2beta/stable-image/control/sketch"
                    
                    headers = {
                        "authorization": f"Bearer {st.secrets['STABILITY_API_KEY']}",
                        "accept": "image/*"
                    }
                    
                    files = {
                        "image": (uploaded_file.name, sketch_data, f"image/{output_format}")
                    }
                    
                    data = {
                        "prompt": prompt,
                        "control_strength": control_strength,
                        "output_format": output_format
                    }
                    
                    # Make API request
                    response = requests.post(
                        stability_api_url,
                        headers=headers,
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        # Create columns for centered image display
                        img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                        with img_col2:
                            # Display the generated image
                            image = Image.open(BytesIO(response.content))
                            st.image(image, caption="Generated Image", use_column_width=True)
                            
                            # Add download button
                            st.download_button(
                                label="⬇️ Download image",
                                data=response.content,
                                file_name=f"sketch_generated.{output_format}",
                                mime=f"image/{output_format}",
                                use_container_width=True
                            )
                    else:
                        error_detail = response.json().get('message', response.text)
                        st.error(f"Error generating image: {error_detail}")
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

elif feature == "Image to 3D":
    st.markdown("### Image to 3D Generation")
    st.info("Upload an image to convert it into a 3D model (GLB format)")
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Image upload
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp"],
            help="Upload a clear image of the object you want to convert to 3D"
        )
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                width, height = image.size
                
                # Display image info and preview
                st.image(image, caption="Uploaded Image", use_column_width=True)
                st.info(f"Image Format: {image.format.lower()}, Dimensions: {width}x{height}px")
                
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                st.stop()

    # Center the generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_button = st.button("Generate 3D Model ✨", use_container_width=True)

    if generate_button:
        if uploaded_file is None:
            st.error("Please upload an image first!")
        else:
            try:
                with st.spinner('Converting image to 3D model... This may take a while...'):
                    # Prepare the image
                    image_data = uploaded_file.getvalue()
                    
                    # Call Stability.ai API for image-to-3D
                    stability_api_url = "https://api.stability.ai/v2beta/3d/stable-fast-3d"
                    
                    headers = {
                        "authorization": f"Bearer {st.secrets['STABILITY_API_KEY']}"
                    }
                    
                    files = {
                        "image": (uploaded_file.name, image_data, "image/png")
                    }
                    
                    # Make API request
                    response = requests.post(
                        stability_api_url,
                        headers=headers,
                        files=files,
                        data={}
                    )
                    
                    if response.status_code == 200:
                        # Create columns for centered content
                        content_col1, content_col2, content_col3 = st.columns([1, 2, 1])
                        with content_col2:
                            st.success("3D model generated successfully!")
                            
                            # Add download button for GLB file
                            st.download_button(
                                label="⬇️ Download 3D Model (GLB)",
                                data=response.content,
                                file_name="generated_3d_model.glb",
                                mime="model/gltf-binary",
                                use_container_width=True
                            )
                            
                            # Add instructions for using the 3D model
                            st.info("""
                            Instructions:
                            1. Download the GLB file
                            2. View it using a 3D viewer or import into a 3D software
                            3. Popular viewers include:
                               - Online: Sketchfab, Google's Model Viewer
                               - Desktop: Windows 3D Viewer, Blender
                            """)
                    else:
                        error_detail = response.json().get('message', response.text)
                        st.error(f"Error generating 3D model: {error_detail}")
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")