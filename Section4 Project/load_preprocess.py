import pandas as pd
import cv2
import numpy as np
from PIL import Image
import random
from tqdm import tqdm





emotions = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}
# Pixels들을 배열로 변환, 이미지 라벨링
def prepare_data(data):
    faces = np.zeros(shape=(len(data), 48, 48))
    emotions = np.array(list(map(int, data['emotion'])))
    
    for i, row in enumerate(data.index):
        image = np.fromstring(data.loc[row, ' pixels'], dtype=int, sep=' ')
        image = np.reshape(image, (48, 48))
        faces[i] = image
        
    return faces, emotions

# 이미지 Augmentation
def augmentation(data, faces, emotions):
    
    population = list(data[data[' Usage']=='Training'].index)
    cnt = int(data[' Usage'].value_counts()[0]*0.1)
    
    random.seed(100)
    random_list1 = random.sample(population, k=cnt)
    print("증강할 이미지 개수: ",len(random_list1))

    # 이미지 180도 회전
    for i in tqdm(random_list1):
        N = len(faces[i])
        imgArray = [ [0]*N for _ in range(N) ]

        for r in range(N):
            for c in range(N):
                imgArray[N-1-r][N-1-c] = faces[i][r][c]
        
        faces = np.append(faces, [imgArray], axis=0)
        emotions = np.append(emotions, data['emotion'][i])
    
    random.seed(200)
    random_list2 = random.sample(population, k=cnt)
    # 이미지 좌우 반전
    for i in tqdm(random_list2):
        imgArray = np.fliplr(faces[i])
        faces = np.append(faces, [imgArray], axis=0)
        emotions = np.append(emotions, data['emotion'][i])
        
    return faces, emotions