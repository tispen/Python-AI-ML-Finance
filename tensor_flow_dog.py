import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from IPython.display import display
from object_detection.utils import ops as utils_ops 
from object_detection.utils import label_map_util 
from object_detection.utils import visualization_utils as vis_util

def load_model(model_name):
   base_url = 'http://download.tensorflow.org/models/object_detection/'
   model_file = model_name + '.tar.gz'
   model_dir = tf.keras.utils.get_file(
   fname=model_name,
   origin=base_url + model_file,
   untar=True)
   model_dir = pathlib.Path(model_dir)/"saved_model"
   model = tf.saved_model.load(str(model_dir))
   return model

PATH_TO_LABELS = '/content/models/research/object_detection/data/mscoco_label_map.pbtxt'
# models/research/object_detection/data/mscoco_label_map.pbtxt'
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

model_name = 'ssd_mobilenet_v1_coco_2017_11_17'
detection_model = load_model(model_name)

def run_inference_for_single_image(model, image):
 image = np.asarray(image)
 # На входе должен быть тензор,
 # конвертируем image используя `tf.convert_to_tensor`.
 input_tensor = tf.convert_to_tensor(image)
 # модель ожидает пакет изображений,
 # поэтому добавляем ось(измерение)
 # c помощью метода with `tf.newaxis`.
 input_tensor = input_tensor[tf.newaxis,...]
 # запускаем нейросеть для вывода результатов
 model_fn = model.signatures['serving_default']
 output_dict = model_fn(input_tensor)
num_detections = int(output_dict.pop('num_detections'))
 output_dict = {key:value[0, :num_detections].numpy()
 for key,value in output_dict.items()}
 output_dict['num_detections'] = num_detections
 # detection_classes должен быть целочисленным
 output_dict['detection_classes'] = output_dict['detection_classes'].astype
(np.int64)
 # Обработаем модель с помощью масок:
 if 'detection_masks' in output_dict:
 # Изменим формат маски bbox в соответствии
 # с размером изображения. 
 detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
 output_dict['detection_masks'], output_dict['detection_boxes'],
 image.shape[0], image.shape[1]) 
 detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
 tf.uint8)
 output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy
()
 return output_dict
def show_inference(model, image_path):
 # представление изображения на основе массива
 # будет использовано позже для подготовки
 # результирующего изображения с рамками и надписями на них.
 image_np = np.array(Image.open(image_path))
 # Запускаем распознавание
 output_dict = run_inference_for_single_image(model, image_np)
 # Визуализируем результаты распознавания
 vis_util.visualize_boxes_and_labels_on_image_array(
 image_np,
 output_dict['detection_boxes'],
 output_dict['detection_classes'],
 output_dict['detection_scores'],
 category_index,
 instance_masks=output_dict.get('detection_masks_reframed', None),
 use_normalized_coordinates=True,
 line_thickness=8)
 display(Image.fromarray(image_np))
for image_path in TEST_IMAGE_PATHS:
 show_inference(detection_model, image_path)
