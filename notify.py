import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
import random as rng
import requests
import sqlite3
import time
import schedule
import datetime
import sys

def lineNotify(message):
    payload = {'message':message}
    return _lineNotify(payload)

def notifySticker(stickerID,stickerPackageID):
    payload = {'message':" ",'stickerPackageId':stickerPackageID,'stickerId':stickerID}
    return _lineNotify(payload)

def _lineNotify(payload,file=None):
    url = 'https://notify-api.line.me/api/notify'
    token = '34RqfUorGZvKOStoI349R8OOF2SvQO4vYNVd7G3A3RG'   #EDIT
    headers = {'Authorization':'Bearer '+token}
    return requests.post(url, headers=headers , data = payload, files=file)

def nothing(x):
    pass

def notify_error(weight):
    lineNotify('Underweight: ' + str(weight) + ' grams')