import os
import cv2
from PIL import Image
import numpy as np

import tensorflow as tf
from django.shortcuts import render
from django.conf import settings
from django.template.response import TemplateResponse
from django.utils.datastructures import MultiValueDictKeyError
from accounts.models import Services, Itworks
from django.core.files.storage import FileSystemStorage


class CustomFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name

def homepage(request):
    itworks = Itworks.objects.all()
    services = Services.objects.all()

    context = {
        'itworks':itworks,
        'services':services,
    }

    return render(request, 'index.html',context)

def classifier_model(request):
    message = ""
    prediction = ""
    fss = CustomFileSystemStorage()
    try:
        image = request.FILES["image"]
        print("Name", image.file)
        _image = fss.save(image.name, image)
        path = str(settings.MEDIA_ROOT) + "/" + image.name
        # image details
        image_url = fss.url(_image)
        # Read the image
        imag=cv2.imread(path)
        img_from_ar = Image.fromarray(imag, 'RGB')
        resized_image = img_from_ar.resize((180, 180))

        test_image =np.expand_dims(resized_image, axis=0) 

        # load model
        model = tf.keras.models.load_model(os.getcwd() + '/tomato_diseases_classifier.h5')

        result = model.predict(test_image) 
        # ----------------
        # LABELS
        
        # ----------------
        print("Prediction: " + str(np.argmax(result)))

        if (np.argmax(result) == 0):
            prediction = "Tomato__Tomato_YellowLeaf__Curl_Virus"
        elif (np.argmax(result) == 1):
            prediction = "Tomato_Bacterial_spot"
        elif (np.argmax(result) == 2):
            prediction = "Tomato_healthy"
        elif (np.argmax(result) == 3):
            prediction = "Tomato_Late_blight"
        elif (np.argmax(result) == 4):
            prediction = "Tomato_Leaf_Mold"
        elif (np.argmax(result) == 5):
            prediction = "Tomato_Spider_mites_Two_spotted_spider_mite"
        else:
            prediction = "Unknown"
        
        return TemplateResponse(
            request,
            "classifier/classifier_model.html",
            {
                "message": message,
                "image": image,
                "image_url": image_url,
                "prediction": prediction,
            },
        )
    except MultiValueDictKeyError:

        return TemplateResponse(
            request,
            "classifier/classifier_model.html",
            {"message": "No Image Selected"},
        )