from flask import *
import time
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import PIL.Image
import numpy as np
model = tf.keras.models.load_model('model.h5', custom_objects=None, compile=True, options=None)
img_width = 512
img_height = 512
app=Flask(__name__)

def load(img_file):
    image = tf.io.read_file(img_file)
    image = tf.image.decode_jpeg(image)
    image = tf.cast(image, tf.float32)
    return image

def  resize(img, width, height):
    input_image = tf.image.resize(img, [height, width],
                                method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
    return input_image

def normalize(img):
    input_image = (img / 127.5) - 1
    return input_image 

def load_image_test(image_file):
    input_image = load(image_file)
    input_image = resize(input_image, img_width, img_height)
    input_image = normalize(input_image)
    return input_image

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/imageUpload', methods=['POST'])
def image_upload():
    print(request.files)
    sess = tf.compat.v1.Session()
    f = request.files['image']
    f.save('./image/image.png')
    # test_image = image.load_img('./image/image.png', target_size=(512, 512))
    # test_image = image.img_to_array(test_image)
    test_data = tf.data.Dataset.list_files('./image/image.png')
    test_data = test_data.map(load_image_test)
    test_data = test_data.batch(1)
    print("-----------------")
    print(len(test_data))
    # test_image = np.expand_dims(test_image, axis=0)
    print("-----------------")
    # print(test_image.shape())
    # test_image = test_image.reshape(img_width, img_height,3)
    print("-----------------")
    # print(test_image.shape())
    # test_image = test_data.take(1)
    # print(test_image)
    for test_image in test_data.take(1):
        prediction = model(test_image, training=False)
    # print(prediction)
    prediction = tf.cast(prediction[0], tf.uint8)
    print(tf.shape(prediction))
    prediction = tf.image.encode_png(prediction)
    # print(prediction)
    tf.io.write_file('predicted_depth.png', prediction)
    # sess.run(writer)
    # print(type(prediction[0]))
      
    return 'Image uploaded to server'

@app.route('/get_model/<file>')
def get_model(file):
    print(file)
    filename = './model/'+ file
    return send_file(filename, mimetype='application/*', cache_timeout=0)

@app.route('/modelReady', methods=['GET'])
def model_download():
    time.sleep(2)
    return 'Model is ready'

if __name__ == "__main__":
    app.run(debug=True)