# thing id: 8e71cb55-bdc4-4590-806c-e5a69696d584  - KEGs Displayer
# float keg1FilledPercent
# client ID: AtWDgu3GE74V2kmHDHCqRqII3bMp4GOj
# client Secret: qfb1hf1v3fBU74vHzvKYjR9H5YGxZCuOo5pFAxRZ6hlV9VLSzDQI27WTMkJbmt80
# or
# thing id: de9ab778-368a-4130-9de5-ddb7b6a06805  - Keg1
# float filledPercent

import sys
import os
import time
import requests
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd2in7_V2
from PIL import Image,ImageDraw,ImageFont,ImageEnhance

isClearScreen = True
client_id = "AtWDgu3GE74V2kmHDHCqRqII3bMp4GOj"
client_secret = "qfb1hf1v3fBU74vHzvKYjR9H5YGxZCuOo5pFAxRZ6hlV9VLSzDQI27WTMkJbmt80"
Keg1Overridepercent = -1
Keg2Overridepercent = -1
Keg3Overridepercent = -1
Keg4Overridepercent = -1

# Function to get OAuth token
def get_oauth_token():
    token_url = "https://api2.arduino.cc/iot/v1/clients/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": "https://api2.arduino.cc/iot"
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        token_info = response.json()
        return token_info["access_token"]
    else:
        print("Failed to obtain token:", response.status_code, response.text)
        return None

# Arduino Cloud settings
api_url = "https://api2.arduino.cc/iot/v2/things/8e71cb55-bdc4-4590-806c-e5a69696d584/properties"

# Setup paths
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
fontdir = picdir  # Since the font is in the same directory as picdir

# Initialize e-paper display
epd = epd2in7_V2.EPD()

# Load the original JPEG image using the simplified path method
image_jpg = Image.open(os.path.join(picdir, 'kegGscale.jpg')).convert('L')

# Optionally enhance the contrast if needed
enhancer = ImageEnhance.Contrast(image_jpg)
image_jpg = enhancer.enhance(1.5)  # Increase contrast slightly

# Load a font for displaying text (adjust the font size as needed)
font = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 18)

# Function to get keg percentages from Arduino Cloud
def get_keg_percentages(auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }
    
    # Replace 'keg1', 'keg2', etc., with the actual property IDs in your Arduino Cloud
    keg_property_ids = ["15d89138-4fcf-43b8-a790-1bc5e52fc782", "51f1861a-3ad4-46ef-8979-671f0341e524", "be4f4752-2107-44c3-9b02-a00bf3a32408", "ed29ffe6-b20c-4a8d-9ced-7a188c80f5cc"]
    
    percentages = []
    
    for property_id in keg_property_ids:
        response = requests.get(f"{api_url}/{property_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["last_value"] == "N/A":
                percentages.append(0)
            elif data["last_value"] < 0:
                percentages.append(0)
            elif data["last_value"] > 100:
                percentages.append(100) 
            else:
                percentages.append(data["last_value"])
        else:
            percentages.append(0)  # Default to 0 if there's an issue
    
    return percentages

# Function to draw the filled keg and gallons text
def draw_filled_keg(image, percentage):
    width, height = image.size
    
    # Use your adjusted top and bottom boundaries
    top_line_y = int(0.20 * height)   # Top boundary
    bottom_line_y = int(0.85 * height)  # Bottom boundary

    # Calculate the height of the filled portion
    fillable_height = bottom_line_y - top_line_y
    filled_height = int((percentage / 100) * fillable_height)
    
    # Create a copy of the image to modify
    filled_image = image.copy()
    draw = ImageDraw.Draw(filled_image)
    
    # Use your adjusted width to fit within the keg's boundaries
    adjusted_width = int(width * 0.80)
    x_offset = int((width - adjusted_width) / 2)
    
    # Draw the solid light gray filled rectangle within the lines
    draw.rectangle([x_offset, bottom_line_y - filled_height, x_offset + adjusted_width, bottom_line_y], fill=epd.GRAY2)
    
    return filled_image

# Function to add text displaying gallons remaining above each keg
def add_gallons_text(draw, x_position, y_position, percentage):
    gallons = (percentage / 100) * 5  # Calculate gallons (assuming 100% is 5 gallons)
    text = f"[{gallons:.2f}]"  # Format the text to two decimal places
    
    # Calculate text bounding box instead of using deprecated textsize
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = x_position + (keg_width - text_width) // 2  # Center the text above the keg
    draw.text((text_x, y_position - text_height - 5), text, font=font, fill=0)  # Adjust y-position for spacing

if isClearScreen:
    epd.init()
    epd.Clear()
    epd.sleep()
    exit()
else:
    # Get the OAuth token
    auth_token = get_oauth_token()

    if auth_token:
        # Fetch keg percentages from Arduino Cloud
        percentages = get_keg_percentages(auth_token)
        if Keg1Overridepercent >= 0:
            percentages[0] = Keg1Overridepercent
        if Keg2Overridepercent >= 0:
            percentages[1] = Keg2Overridepercent
        if Keg3Overridepercent >= 0:
            percentages[2] = Keg3Overridepercent
        if Keg4Overridepercent >= 0:
            percentages[3] = Keg4Overridepercent
            
        # Create a new blank image in landscape mode
        final_image = Image.new('L', (epd.height, epd.width), 255)  # White background, note the swap in dimensions

        # Create a drawing context for the final image
        draw_final = ImageDraw.Draw(final_image)

        # Calculate the width and height of each keg image
        keg_width, keg_height = image_jpg.size

        # Calculate the spacing between kegs to distribute them evenly
        spacing = (epd.height - 4 * keg_width) // 5  # 5 gaps: before the first keg, between kegs, after the last keg

        # Calculate the vertical position to align the kegs at the bottom
        y_position = epd.width - keg_height  # Align at the bottom

        # Paste the keg images with their respective fill levels and add the gallons text
        for i in range(4):
            x_position = spacing + i * (keg_width + spacing)
            filled_keg = draw_filled_keg(image_jpg, percentages[i])
            final_image.paste(filled_keg, (x_position, y_position))
            
            # Add gallons text above the keg
            add_gallons_text(draw_final, x_position, y_position, percentages[i])

        # Save the processed image for verification (optional)
        final_image.save(os.path.join(picdir, 'final_kegs_with_gallons_display.jpg'))

        # Convert the final image to e-paper buffer
        buffer_final = epd.getbuffer_4Gray(final_image)

        # Initialize e-paper in 4-gray mode
        epd.Init_4Gray()

        # Display the processed final image on the e-paper display
        epd.display_4Gray(buffer_final)
        time.sleep(2)

        # Ensure display is updated and put it to sleep
        epd.sleep()