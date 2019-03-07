import os
import io
import csv
import tqdm
from PIL import Image
from google.cloud import vision
from google.cloud.vision import types

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcp_secret.json'

phi_step = 1
image_path = "duckorrabbit.png"
output_path = "/Volumes/Extreme 510/Data/optillusion-animation/rotated_images"


def get_rotated_image_labels(client, image, bg, phi):

    # https://stackoverflow.com/a/5253554
    rot = image.rotate(-phi)   # clockwise
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

t = tqdm.tqdm(range(0, 360, phi_step))

with open('image_rot_results.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(['phi', 'label', 'score'])
    for phi in t:
        r = get_rotated_image_labels(client, image, bg, phi)
        for ann in r.label_annotations:
            w.writerow([phi, ann.description, ann.score])
