import datetime
from django.utils import timezone
from django.db import models
from tensorflow import keras
from keras.models import load_model
from PIL import Image
import numpy as np
import tensorflow as tf
import io
import base64


#graph = tf.get_default_graph()
graph = tf.compat.v1.get_default_graph()  # こっち使えって


class Photo(models.Model):
    image = models.ImageField(upload_to='photos')
    IMAGE_SIZE = 224  # 画像サイズ
    MODEL_FILE_PATH = 'predictions/ml_models/vgg16_transfer.h5'  # モデルファイル
    classes = ['car', 'motorbike']
    num_classes = len(classes)

    def predict(self):
        model = None
        global graph
        with graph.as_default():
            model = load_model(self.MODEL_FILE_PATH)

            img_data = self.image.read()
            img_bin = io.BytesIO(img_data)  # バイナリーデータに変換

            image = Image.open(img_bin)  # 変換後渡す＝標準入力と同じ動作
            image = image.convert('RGB').resize(
                (self.IMAGE_SIZE, self.IMAGE_SIZE))
            data = np.asarray(image) / 255.0  # 浮動小数点で正規化
            X = []
            X.append(data)
            X = np.array(X)

            result = model.predict([X])[0]
            predicted = result.argmax()
            percentage = int(result[predicted] * 100)

            return self.classes[predicted], percentage

    def image_src(self):
        with self.image.open() as img:
            base64_img = base64.b64encode(img.read()).decode()

            return 'data:' + img.file.content_type + ';base64,' + base64_img


class Schedule(models.Model):
    """スケジュール"""
    summary = models.CharField('概要', max_length=50)
    description = models.TextField('詳細な説明', blank=True)
    start_time = models.TimeField('開始時間', default=datetime.time(7, 0, 0))
    end_time = models.TimeField('終了時間', default=datetime.time(7, 0, 0))
    date = models.DateField('日付')
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return self.summary
