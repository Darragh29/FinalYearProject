import torch
from django.shortcuts import render
from django.core.files.storage import default_storage
from ultralytics import YOLO
import os
from PIL import Image

#Load the YOLO model
model_path = os.path.join(os.path.dirname(__file__), "/Users/darraghdoherty/Library/CloudStorage/OneDrive-AtlanticTU/FrontendProject/RecordModels/object_detection.pt")  # Ensure your model file is here
model = YOLO(model_path)

# Define class labels
CLASS_NAMES = ["Record Cover","Vinyl Record"]

def detect_object(request):
    if request.method == "POST" and request.FILES.get("image"):
        #Save uploaded image
        image_file = request.FILES["image"]
        image_path = default_storage.save("uploads/" + image_file.name, image_file)

        #Run YOLO detection
        image_full_path = os.path.join(default_storage.location, image_path)
        results = model(image_full_path)

        #Get the highest confidence detection
        highest_confidence = 0
        detected_class = "No Record Detected"  # Default if nothing is detected

        for result in results:
            for box in result.boxes:
                class_index = int(box.cls[0].item())  #Get class index
                confidence = box.conf[0].item()       #Get confidence score

                if confidence > highest_confidence:  # Track highest confidence detection
                    highest_confidence = confidence
                    detected_class = CLASS_NAMES[class_index]

        # Set threshold for "No Record Detected"
        if highest_confidence < 0.7:
            detected_class = "No Record Detected"

        return render(request, "detect.html", {"result": detected_class})

    return render(request, "detect.html", {"result": None})


def home(request):
    return render(request, 'home.html')

def detect(request):
    return render(request, 'detect.html')
