import os
import io
import json
import tqdm
from PIL import Image
from collections import OrderedDict
from google.cloud import vision
from google.cloud.vision import types

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcp_secret.json'

phi_step = 120
image_path = "duckorrabbit.png"
output_path = "/Volumes/Extreme 510/Data/optillusion-animation/rotated_images"


def labels_to_dict(label_annotations):
    label_scores = {}
    for ann in label_annotations:
        label_scores[ann.description] = ann.score
    return label_scores


def get_rotated_image_labels(client, image, bg, phi):

    # https://stackoverflow.com/a/5253554
    rot = image.rotate(phi)
    bg = Image.new('RGBA', rot.size, (255,) * 4)
    image_tf = Image.composite(rot, bg, rot)

    filename = str(phi) + '.png'
    image_tf.convert('RGB').save(os.path.join(output_path, filename))

    # https://stackoverflow.com/a/33117447
    imgByteArr = io.BytesIO()
    image_tf.save(imgByteArr, format='PNG')
    imgByteArr = imgByteArr.getvalue() 

    image = types.Image(content=imgByteArr)
    response = client.label_detection(image=image)
    return response

image = Image.open(image_path).convert('RGBA')
bg = Image.new('RGBA', image.size, (255,) * 4)
client = vision.ImageAnnotatorClient()

results = OrderedDict()
t = tqdm.tqdm(range(0, 360, phi_step))

for phi in t:
    r = get_rotated_image_labels(client, image, bg, phi)
    labels = labels_to_dict(r.label_annotations)
    results[phi] = labels

with open('image_rot_results.json', 'w') as f:
    json.dump(results, f)
