#!/usr/bin/env python
# coding: utf-8

###### Data Preparation #################

import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from sentence_splitter import SentenceSplitter
import matplotlib.pyplot as plt
import os
import ast
import cv2
from sklearn.metrics import confusion_matrix, classification_report
from tqdm import tqdm
import time

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
from tensorflow import keras
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import SGD
from tensorflow.python.keras import backend as K
from focal_loss import SparseCategoricalFocalLoss

######### Configuring GPU #####################
config = tf.compat.v1.ConfigProto( device_count = {'GPU': 1} )
sess = tf.compat.v1.Session(config=config) 
K.set_session(sess)

device_name = tf.test.gpu_device_name()
if "GPU" not in device_name:
    print("GPU device not found")
print('Found GPU at: {}'.format(device_name))

data = pd.read_csv("ETD_minority_original_aug.csv", encoding = 'utf-8')
data['text'] = data['text'].astype(str)

print("############## Splitting Dataset ####################")
# 25% for validation
train_df, val_df = train_test_split(
    data, test_size=0.25, stratify=data["class"].values, random_state=42
)

print(f"Total training examples: {len(train_df)}")
print(f"Total validation examples: {len(val_df)}")


train_df.to_csv("train_orig_aug_minority.csv", encoding = 'utf-8', index = None)
val_df.to_csv("validation_orig_aug_minority.csv", encoding = 'utf-8', index = None)
#test_df.to_csv("test_original_13k.csv", encoding = 'utf-8', index = None)

print("############## Splitting Completed and Saved !!!!!!! ####################")

train_df = pd.read_csv("train_orig_aug_minority.csv")
train_df['text'] = train_df['text'].astype(str)

val_df = pd.read_csv("validation_orig_aug_minority.csv")
val_df['text'] = val_df['text'].astype(str)

test_df = pd.read_csv("test_original_13k.csv")
test_df = test_df[test_df['class']!= 'Label-Chapters']
test_df['text'] = test_df['text'].astype(str)

label_map = {"Label-Appendices": 0, "Label-ReferenceList": 1, "Label-Other": 2, "Label-TableofContent": 3,  "Label-TitlePage": 4, "Label-Abstract": 5, "Label-ListofFigures": 6, "Label-Acknowledgement": 7, "Label-ListofTables": 8, "Label-CurriculumVitae": 9, "Label-Dedication": 10, "Label-ChapterAbstract": 11}

train_df['label_idx'] = train_df['class'].apply(lambda x: label_map[x])
val_df['label_idx'] = val_df['class'].apply(lambda x: label_map[x])
test_df['label_idx'] = test_df['class'].apply(lambda x: label_map[x])

# Define TF Hub paths to the BERT encoder and its preprocessor
#'https://tfhub.dev/tensorflow/bert_en_uncased_L-24_H-1024_A-16/3'
    
bert_model_path = (
    'https://tfhub.dev/tensorflow/talkheads_ggelu_bert_en_large/2'
)
bert_preprocess_path = "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3"

def make_bert_preprocessing_model(sentence_features, seq_length=512):
    """Returns Model mapping string features to BERT inputs.

  Args:
    sentence_features: A list with the names of string-valued features.
    seq_length: An integer that defines the sequence length of BERT inputs.

  Returns:
    A Keras Model that can be called on a list or dict of string Tensors
    (with the order or names, resp., given by sentence_features) and
    returns a dict of tensors for input to BERT.
  """

    input_segments = [
        tf.keras.layers.Input(shape=(), dtype=tf.string, name=ft)
        for ft in sentence_features
    ]

    # Tokenize the text to word pieces.
    bert_preprocess = hub.load(bert_preprocess_path)
    tokenizer = hub.KerasLayer(bert_preprocess.tokenize, name="tokenizer")
    segments = [tokenizer(s) for s in input_segments]

    # Optional: Trim segments in a smart way to fit seq_length.
    # Simple cases (like this example) can skip this step and let
    # the next step apply a default truncation to approximately equal lengths.
    truncated_segments = segments

    # Pack inputs. The details (start/end token ids, dict of output tensors)
    # are model-dependent, so this gets loaded from the SavedModel.
    packer = hub.KerasLayer(
        bert_preprocess.bert_pack_inputs,
        arguments=dict(seq_length=seq_length),
        name="packer",
    )
    model_inputs = packer(truncated_segments)
    return keras.Model(input_segments, model_inputs)

bert_preprocess_model = make_bert_preprocessing_model(['text'])


idx = np.random.choice(len(train_df))
row = train_df.iloc[idx]
sample_text  = row["text"].lower()

print(f"Text: {sample_text}")

test_text = [np.array([sample_text])]
text_preprocessed = bert_preprocess_model(test_text)

print("############### Running BERT preprocessor on Sample Unit ###########################")

print("Keys           : ", list(text_preprocessed.keys()))
print("Shape Word Ids : ", text_preprocessed["input_word_ids"].shape)
print("Word Ids       : ", text_preprocessed["input_word_ids"][0, :16])
print("Shape Mask     : ", text_preprocessed["input_mask"].shape)
print("Input Mask     : ", text_preprocessed["input_mask"][0, :16])
print("Shape Type Ids : ", text_preprocessed["input_type_ids"].shape)
print("Type Ids       : ", text_preprocessed["input_type_ids"][0, :16])

print("#####################################################################################")

def dataframe_to_dataset(dataframe):
    columns = ["img_path", "text", "label_idx"]
    dataframe = dataframe[columns].copy()
    labels = dataframe.pop("label_idx")
    ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
    ds = ds.shuffle(buffer_size=len(dataframe))
    return ds

resize = (224, 224)
bert_input_features = ["input_word_ids", "input_type_ids", "input_mask"]

from keras.preprocessing.image import ImageDataGenerator

def preprocess_image(image_path):

    img_path = tf.io.read_file(image_path)
    image_decode = tf.image.decode_png(img_path, 3)
    image = tf.image.resize(image_decode, resize)
    return image


def preprocess_text(text):
    text = tf.convert_to_tensor([text])
    output = bert_preprocess_model([text])
    output = {feature: tf.squeeze(output[feature]) for feature in bert_input_features}
    return output


def preprocess_text_and_image(sample):
    image_1 = preprocess_image(sample["img_path"])
    text = preprocess_text(sample["text"])
    return {"image": image_1, "text": text}

# example of progressively loading data
batch_size = 12
auto = tf.data.AUTOTUNE


def prepare_dataset(dataframe, training=True):
    ds = dataframe_to_dataset(dataframe)
    if training:
        ds = ds.shuffle(len(train_df))
    ds = ds.map(lambda x, y: (preprocess_text_and_image(x), y)).cache()
    ds = ds.batch(batch_size).prefetch(auto)
    return ds

train_ds = prepare_dataset(train_df)
validation_ds = prepare_dataset(val_df, False)
test_ds = prepare_dataset(test_df, False)

def separate_labels(ds):
    labels = []
    for _, label in tqdm(ds.unbatch(), desc = 'Progress Bar'):
        labels.append(label)
    labels = np.array(labels)
    return labels

print('####### Separating Test Labels ##############')
test_labels = separate_labels(test_ds)


###################### Projection Utility ##################################
def project_embeddings(
    embeddings, num_projection_layers, projection_dims, dropout_rate
):
    projected_embeddings = keras.layers.Dense(units=projection_dims)(embeddings)
    for _ in range(num_projection_layers):
        x = tf.nn.gelu(projected_embeddings)
        x = keras.layers.Dense(projection_dims)(x)
        x = keras.layers.Dropout(dropout_rate)(x)
        x = keras.layers.Add()([projected_embeddings, x])
        projected_embeddings = keras.layers.LayerNormalization()(x)
    return projected_embeddings

##################### Visual Modality ######################################
def create_vision_encoder(
    num_projection_layers, projection_dims, dropout_rate, trainable=False
):
    # Load the pre-trained ResNet50V2 model to be used as the base encoder.
    resnet_v2 = keras.applications.ResNet50V2(
        include_top=False, weights="imagenet", pooling="avg"
    )
    # Set the trainability of the base encoder.
    for layer in resnet_v2.layers:
        layer.trainable = trainable

    # Receive the images as inputs.
    image_1 = keras.Input(shape=(224, 224, 3), name="image")

    # Preprocess the input image.
    preprocessed_1 = keras.applications.resnet_v2.preprocess_input(image_1)

    # Generate the embeddings for the images using the resnet_v2 model
    embeddings = resnet_v2(preprocessed_1)
    # embeddings = keras.layers.Concatenate()([embeddings_1, embeddings_2])

    # Project the embeddings produced by the model.
    outputs = project_embeddings(
        embeddings, num_projection_layers, projection_dims, dropout_rate
    )
    # Create the vision encoder model.
    return keras.Model([image_1], outputs, name="vision_encoder")


##################### Textual Modality ######################################
def create_text_encoder(
    num_projection_layers, projection_dims, dropout_rate, trainable=False
):
    # Load the pre-trained BERT model to be used as the base encoder.
    bert = hub.KerasLayer(bert_model_path, name="bert",)
    # Set the trainability of the base encoder.
    bert.trainable = trainable

    # Receive the text as inputs.
    bert_input_features = ["input_type_ids", "input_mask", "input_word_ids"]
    inputs = {
        feature: keras.Input(shape=(512,), dtype=tf.int32, name=feature)
        for feature in bert_input_features
    }

    # Generate embeddings for the preprocessed text using the BERT model.
    embeddings = bert(inputs)["pooled_output"]

    # Project the embeddings produced by the model.
    outputs = project_embeddings(
        embeddings, num_projection_layers, projection_dims, dropout_rate
    )
    # Create the text encoder model.
    return keras.Model(inputs, outputs, name="text_encoder")

##################### MultiModality with Cross Attention ######################################
def create_multimodal_model(
    num_projection_layers=1,
    projection_dims=256,
    dropout_rate=0.1,
    vision_trainable=False,
    text_trainable=False,
    attention = True
):
    # Receive the images as inputs.
    image_1 = keras.Input(shape=(224, 224, 3), name="image")

    # Receive the text as inputs.
    bert_input_features = ["input_type_ids", "input_mask", "input_word_ids"]
    text_inputs = {
        feature: keras.Input(shape=(512,), dtype=tf.int32, name=feature)
        for feature in bert_input_features
    }

    # Create the encoders.
    vision_encoder = create_vision_encoder(
        num_projection_layers, projection_dims, dropout_rate, vision_trainable
    )
    text_encoder = create_text_encoder(
        num_projection_layers, projection_dims, dropout_rate, text_trainable
    )

    # Fetch the embedding projections.
    vision_projections = vision_encoder([image_1])
    text_projections = text_encoder(text_inputs)
    
    # Cross attention
    attention_seq = keras.layers.Attention(use_scale=True, dropout=0.8)(
            [vision_projections, text_projections])
    
    # Dropout
    vision_projections = keras.layers.Dropout(0.8)(vision_projections)
    text_projections = keras.layers.Dropout(0.8)(text_projections)

    if attention:
        contextual = keras.layers.Concatenate()([vision_projections, text_projections])
        concatenated = keras.layers.Concatenate()([contextual, attention_seq])
    else:
        # Concatenate the projections and pass through the classification layer.
        concatenated = keras.layers.Concatenate()([vision_projections, text_projections])
    
    outputs = keras.layers.Dense(12, activation="softmax")(concatenated)
    return keras.Model([image_1, text_inputs], outputs)


multimodal_model = create_multimodal_model(attention=True)
multimodal_model.summary()

##################### Fine Tuning Hyperparameter ######################################
EPOCHS = 40
optimizer = tf.keras.optimizers.Adam(
    decay=0.004, epsilon=1e-07, clipvalue=2.0, learning_rate=0.001)

multimodal_model.compile(
    optimizer=optimizer, loss=SparseCategoricalFocalLoss(gamma=2), metrics="accuracy"
)

##################### Model Checkpoint and Early Stopping ######################################
checkpoint = tf.keras.callbacks.ModelCheckpoint('multimodal_resNET50BERT_minority_orig_aug.h5', monitor='val_loss', save_best_only=True, verbose=1)
es = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, mode='min', verbose=1)

##################### Training Model ######################################
start = time.time()
with tf.device('/device:GPU:0'):
    history = multimodal_model.fit(train_ds, validation_data=validation_ds, callbacks=[es, checkpoint], epochs=EPOCHS)
stop = time.time()
print(f'Training on GPU took: {(stop-start)/60} minutes')

########## Uncomment the below line if you want to load the best weights of the model without training from the scratch ##############
#multimodal_model.load_weights('multimodal_resNET50BERT_minority_orig_aug.h5')

class_names = list(label_map.keys())
def detailed_test_eval(model):
    prediction_labels = np.argmax(model.predict(test_ds), 1)
    print(classification_report(test_labels, prediction_labels, target_names=class_names))
    result = pd.DataFrame(confusion_matrix(test_labels, prediction_labels),
                        index=class_names, columns=class_names)
    result.to_csv('ETDSeg_confusion-matrix_minority_orig_aug.csv')
    return result

eval_detail = detailed_test_eval(multimodal_model)
print(eval_detail)
