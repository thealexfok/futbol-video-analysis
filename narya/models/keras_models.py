from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mxnet as mx

import numpy as np
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense
import tensorflow as tf
import keras
import os
os.environ["SM_FRAMEWORK"] = "tf.keras"
import segmentation_models as sm
from .keras_layers import pyramid_layer
from ..preprocessing.image import _build_homo_preprocessing
from ..preprocessing.image import _build_keypoint_preprocessing


RESNET_ARCHI_TF_KERAS_PATH = (
    "https://storage.googleapis.com/narya-bucket-1/models/deep_homo_model_1.h5"
)
RESNET_ARCHI_TF_KERAS_NAME = "deep_homo_model_1.h5"
RESNET_ARCHI_TF_KERAS_TOTAR = False


# def _build_resnet18():
#     """Builds a resnet18 model in keras from a .h5 file.

#     Arguments:

#     Returns:
#         a tf.keras.models.Model
#     Raises:
#     """
#     resnet18_path_to_file = tf.keras.utils.get_file(
#         RESNET_ARCHI_TF_KERAS_NAME,
#         RESNET_ARCHI_TF_KERAS_PATH,
#         RESNET_ARCHI_TF_KERAS_TOTAR,
#     )

#     print(resnet18_path_to_file)
#     # resnet18_path_to_file=os.path.abspath("new_homo_model.keras")
#     resnet18_path_to_file=os.path.abspath("homo_model.pb")
#     print(resnet18_path_to_file)
#     resnet18 = tf.saved_model.load(resnet18_path_to_file)
#     return resnet18
#     # resnet18.summary()
#     # resnet18.compile()

#     inputs = resnet18.input
#     outputs = resnet18.layers[-2].output

#     return tf.keras.models.Model(inputs=inputs, outputs=outputs, name="custom_resnet18")

def _build_resnet18():
    """Builds a resnet18 model in keras from a .h5 file.

    Returns:
        a tf.keras.models.Model
    """
    resnet18_path_to_file = tf.keras.utils.get_file(
        RESNET_ARCHI_TF_KERAS_NAME,
        RESNET_ARCHI_TF_KERAS_PATH,
        RESNET_ARCHI_TF_KERAS_TOTAR,
    )

    resnet18 = tf.keras.models.load_model(resnet18_path_to_file)
    resnet18.compile()

    inputs = resnet18.input
    outputs = resnet18.layers[-2].output

    return tf.keras.models.Model(inputs=inputs, outputs=outputs, name="custom_resnet18")

def _new_build_resnet18(input_shape=(256, 256)):
    # Load pre-trained ResNet50 model
    resnet50 = ResNet50(weights=None, include_top=False, input_shape=(input_shape[0],input_shape[1],3))
    
    # Remove the fully connected layers at the end
    output = resnet50.layers[-1].output
    output = tf.keras.layers.Flatten()(output)

    # Define new fully connected layers for ResNet18
    output = Dense(512, activation='relu')(output)
    output = Dense(512, activation='relu')(output)
    output = Dense(10, activation='softmax')(output)  # Assuming 10 classes for classification

    # Create the model
    model = Model(inputs=resnet50.input, outputs=output)
    
    return model

class DeepHomoModel:
    """Class for Keras Models to predict the corners displacement from an image. These corners can then get used 
    to compute the homography.

    Arguments:
        pretrained: Boolean, if the model is loaded pretrained on ImageNet or not
        input_shape: Tuple, shape of the model's input 
    Call arguments:
        input_img: a np.array of shape input_shape
    """

    def __init__(self, pretrained=False, input_shape=(256, 256)):

        self.input_shape = input_shape
        self.pretrained = pretrained

        self.resnet_18 = _build_resnet18()
        # self.resnet_18 = _new_build_resnet18(input_shape)
        inputs = tf.keras.layers.Input((self.input_shape[0], self.input_shape[1], 3))
        x = self.resnet_18(inputs)
        outputs = pyramid_layer(x, 2)

        self.model = tf.keras.models.Model(
            inputs=[inputs], outputs=outputs, name="DeepHomoPyramidalFull"
        )

        self.preprocessing = _build_homo_preprocessing(input_shape)

    def __call__(self, input_img):

        # img = self.preprocessing(input_img)
        # corners = self.model.predict(np.array([img]))

        # Ensure input_img is a numpy array
        input_img = np.array(input_img)

        # Preprocess the input image
        img = self.preprocessing(input_img)

        # Convert the input image to a batch with a single sample
        img_batch = np.expand_dims(img, axis=0)

        # Predict corners
        corners = self.model.predict(img_batch)

        return corners

    def load_weights(self, weights_path):
        try:
            self.model.load_weights(weights_path)
            print("Succesfully loaded weights from {}".format(weights_path))
        except:
            orig_weights = "Randomly"
            print(
                "Could not load weights from {}, weights will be loaded {}".format(
                    weights_path, orig_weights
                )
            )


class KeypointDetectorModel:
    """Class for Keras Models to predict the keypoint in an image. These keypoints can then be used to
    compute the homography.

    Arguments:
        backbone: String, the backbone we want to use
        model_choice: The model architecture. ('FPN','Unet','Linknet')
        num_classes: Integer, number of mask to compute (= number of keypoints)
        input_shape: Tuple, shape of the model's input 
    Call arguments:
        input_img: a np.array of shape input_shape
    """

    def __init__(
        self,
        backbone="efficientnetb3",
        model_choice="FPN",
        num_classes=29,
        input_shape=(320, 320),
    ):

        self.input_shape = input_shape
        self.classes = [str(i) for i in range(num_classes)] + ["background"]
        self.backbone = backbone

        n_classes = len(self.classes)
        activation = "softmax"

        if model_choice == "FPN":
            self.model = sm.FPN(
                self.backbone,
                classes=n_classes,
                activation=activation,
                input_shape=(input_shape[0], input_shape[1], 3),
                encoder_weights="imagenet",
            )
        else:
            self.model = None
            print("{} is not used yet".format(model_choice))

        self.preprocessing = _build_keypoint_preprocessing(input_shape, backbone)

    def __call__(self, input_img):

        img = self.preprocessing(input_img)
        pr_mask = self.model.predict(np.array([img]))
        return pr_mask

    def load_weights(self, weights_path):
        try:
            self.model.load_weights(weights_path)
            print("Succesfully loaded weights from {}".format(weights_path))
        except:
            orig_weights = "from Imagenet"
            print(
                "Could not load weights from {}, weights will be loaded {}".format(
                    weights_path, orig_weights
                )
            )
