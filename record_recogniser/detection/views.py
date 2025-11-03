#Imports
import torch
import torchvision.transforms as transforms
from django.shortcuts import render
from ultralytics import YOLO
import os
import io
import base64
from PIL import Image
from torchvision import models
import torch.nn.functional as F
import re
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect

collection = []

#Load YOLO model for object detection
yolo_model_path = "/Users/darraghdoherty/Desktop/FrontendProject/RecordModels/object_detection.pt"
yolo_model = YOLO(yolo_model_path)

#Load EfficientNet models for classification
efficientnet_model_path = "/Users/darraghdoherty/Desktop/FrontendProject/RecordModels/final_model-2.pth"
efficientnet_record_model_path = "/Users/darraghdoherty/Desktop/FrontendProject/RecordModels/vinyl_record_model.pth"

#Load EfficientNet for record cover classification
efficientnet_model = models.efficientnet_b0(pretrained=False)
num_classes = 5
num_ftrs = efficientnet_model.classifier[1].in_features

#Classifier definition for record cover classification
efficientnet_model.classifier = torch.nn.Sequential(
    torch.nn.Dropout(0.5),
    torch.nn.Linear(num_ftrs, num_classes)
)

efficientnet_model.load_state_dict(torch.load(efficientnet_model_path, map_location=torch.device('cpu')))
efficientnet_model.eval()

#Loading EfficientNet for vinyl record classification
efficientnet_record_model = models.efficientnet_b0(pretrained=False)
efficientnet_record_model.classifier = torch.nn.Sequential(
    torch.nn.Dropout(0.5),
    torch.nn.Linear(num_ftrs, num_classes)
)

efficientnet_record_model.load_state_dict(torch.load(efficientnet_record_model_path, map_location=torch.device('cpu')))
efficientnet_record_model.eval()

#Defining the class names for the covers and records
CLASS_NAMES = [
    "Midnights - Taylor Swift", 
    "Rumours - Fleetwood Mac", 
    "Taste - Sabrina Carpenter", 
    "Whitney Houston - Whitney Houston", 
    "Wicked (20th Anniversary Edition) - Stephen Schwartz"
]

#Image transformations for EfficientNet to ensure consistency
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

#Detect object view that detects the record or cover and then classifies it and returns the result
def detect_object(request):
    if request.method == "POST":
        image = None

        #If file is uploaded via input
        if request.FILES.get("image"):
            image_file = request.FILES["image"]
            image = Image.open(image_file).convert("RGB")

        #If image is captured from camera
        elif request.POST.get("captured_image"):
            base64_data = request.POST["captured_image"]
            base64_data = re.sub('^data:image/.+;base64,', '', base64_data)
            image = Image.open(io.BytesIO(base64.b64decode(base64_data))).convert("RGB")

        if image is None:
            return render(request, "detect.html", {"result": "No image provided"})

        #Convert image to base64 for display
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode()

        #Run YOLO detection
        yolo_results = yolo_model(image)

        highest_confidence = 0
        detected_class = "No Record Found"

        #Confidence thresholds
        yolo_conf_threshold = 0.75
        record_cover_threshold = 0.75
        classification_conf_threshold = 0.32

        #Looping through YOLO results
        for result in yolo_results:
            for box in result.boxes:
                class_index = int(box.cls[0].item())  #Getting class index
                confidence = box.conf[0].item()  #Getting confidence score

                print(f"YOLO Detection - Class: {class_index}, Confidence: {confidence:.4f}")

                if confidence > highest_confidence:
                    highest_confidence = confidence
                    detected_class = "Record Cover" if class_index == 0 else "Vinyl Record"

        #Using pre-defined thresholds to ensure YOLO detection is reliable
        if highest_confidence < yolo_conf_threshold or (
            detected_class == "Record Cover" and highest_confidence < record_cover_threshold
        ):
            detected_class = "No Record Found"

        #If record cover/vinyl record detected classify with EfficientNet
        record_label = "N/A"
        confidence_scores = []

        if detected_class == "Record Cover" or detected_class == "Vinyl Record":
            transformed_image = transform(image).unsqueeze(0)

            #Run EfficientNet model for classification based on detected class
            model = efficientnet_model if detected_class == "Record Cover" else efficientnet_record_model
            with torch.no_grad():
                output = model(transformed_image)
                probabilities = F.softmax(output[0], dim=0)  #Convert logits to probabilities
                confidence_scores = [round(float(score), 4) for score in probabilities.tolist()]
                predicted_class = torch.argmax(probabilities).item()
                record_label = CLASS_NAMES[predicted_class]

            #Printing classification confience scores for testing purposes
            print(f"EfficientNet Classification - Predicted: {record_label}, Confidence Scores: {confidence_scores}")

            #If no confidence score is above the threshold return "No Record Found"
            if max(confidence_scores) < classification_conf_threshold:
                detected_class = "No Record Found"
                record_label = "N/A"
                confidence_scores = []

        print(f"Final Decision: {detected_class}, Record Label: {record_label}")

        #Split the record_label into album and artist if it's valid
        album, artist = None, None
        if record_label != "N/A" and " - " in record_label:
            album, artist = record_label.split(" - ", 1)

        #Returning the results to the template
        return render(request, "results.html", {
            "result": detected_class,
            "album": album,
            "artist": artist,  
            "image_base64": image_base64,
            "confidence_scores": confidence_scores if detected_class != "No Record Found" else None
        })

    return render(request, "detect.html", {"result": None})

#Add record to collection view that adds the record to the collection
@csrf_exempt
def add_to_collection(request):
    if request.method == "POST":
        #Get album, artist, and image data from the POST request
        album = request.POST.get("album")
        artist = request.POST.get("artist")
        image_base64 = request.POST.get("image_base64")
        
        #If album, artist, and image data are provided, add them to the collection
        if album and artist and image_base64:
            collection.append({
                "album": album,
                "artist": artist,
                "image_base64": image_base64
            })

    return redirect("catalogue")

#Catalogue view that displays the collection
def catalogue(request):
    return render(request, "catalogue.html", {"records": collection})

#Home view that displays the homepage
def home(request):
    return render(request, 'home.html')

#Detect view that displays the detection page
def detect(request):
    return render(request, 'detect.html')
