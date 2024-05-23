### arucoマーカーを生成して、画像として保存する
import cv2
from cv2 import aruco
import os

### --- parameter --- ###

dir_mark = r'C:\Users\GaYeon\anaconda3\envs\cvenv2\Scripts\ar_markers\bin' # マーカーの保存先

# 生成するマーカー用のパラメータ
num_mark = 2 #個数
size_mark = 500 #マーカーのサイズ

### --- マーカーを生成して保存する --- ###
# マーカー種類を呼び出し
dict_aruco = aruco.Dictionary_get(aruco.DICT_4X4_50)

for count in range(num_mark) :

    id_mark = count #countをidとして流用
    img_mark = aruco.drawMarker(dict_aruco, id_mark, size_mark)

    if count < 10 :
        img_name_mark = 'mark_id_0' + str(count) + '.jpg'
    else :
        img_name_mark = 'mark_id_' + str(count) + '.jpg'
    path_mark = os.path.join(dir_mark, img_name_mark)

    cv2.imwrite(path_mark, img_mark)