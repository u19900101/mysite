from django.shortcuts import render
from django.http import HttpResponse
from pandas import np
import cv2
import dlib
import os
import pandas as pd
import numpy as np

def upload_file(request):
    # 请求方法为POST时，进行处理
    print("进入了upload中")
    if request.method == "POST":
        # 获取上传的文件，如果没有文件，则默认为None
        File = request.FILES.get("avatarSlect", None)
        if File is None:
            return HttpResponse("没有需要上传的文件")
        else:
            # 打开特定的文件进行二进制的写操作
            # 可以保存，但是无法访问到
            name = (File.name).replace(' ', '')
            with open("./media/upload/%s" % name, 'wb+') as f:
                # 分块写入文件
                for chunk in File.chunks():
                    f.write(chunk)

            path = "./media/upload/"+name
            print(path)
            # face_num,face_names=getface_dlib(path,filename)
            pdatapath = './media/imginfo2.csv'
            imgpath,face_paths,face_names,face_num= demo(path, pdatapath,name)
            print("测试facename:",face_names)
            content = {}
            # 供显示使用

            content['face_num'] = face_num
            content['face_paths'] = face_paths
            content['face_names'] = face_names

            content['path'] = "/media/facek/" + name
            res = []

            for i in range(len(face_names)):
                temp = {}
                temp['path'] = face_paths[i]
                temp['name'] =face_names[i]
                res.append(temp)

            content['face_pathsAndnames'] = res

            return render(request, "face.html",content)
    else:
        return render(request, "test.html")


def getface_dlib(imgpath,filename):
    img = cv2.imread(imgpath)
    if img is None:
        print("Sorry, we could not load '{}' as an image".format(imgpath))
        return
        # opencv的颜色空间是BGR，需要转为RGB才能用在dlib中
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # img = cv2.resize(img,(500,int(img.shape[0]/(img.shape[1])*500)))
    # 彩色图像识别效果更强一些
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 人脸分类器
    detector = dlib.get_frontal_face_detector()
    # 获取人脸检测器
    predictor = dlib.shape_predictor("./upload/shape_predictor_68_face_landmarks.dat")
    # 识别人脸特征点，并保存下来
    faces = dlib.full_object_detections()
    dets = detector(gray, 1)
    print(len(dets))
    for face in dets:
        shape = predictor(img, face)  # 寻找人脸的68个标定点
        k = shape.parts()
        # print(k[36,0])
        # 遍历所有点，打印出其坐标，并圈出来
        for pt in shape.parts():
            pt_pos = (pt.x, pt.y)
            cv2.circle(img, pt_pos, 1, (0, 255, 0), 1)
            left = face.left()
            top = face.top()
            right = face.right()
            bottom = face.bottom()
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 1)
        faces.append(predictor(rgb_img, face))
    # img = cv2.resize(img,(600,int(img.shape[0]/(img.shape[1])*600)))
    # 绘制矩形框  在图片中标注人脸，并显示
    # cv2.imshow("image", img)
    cv2.imwrite('./media/facek/'+filename,img)  # 竟然必须加上一个点，不然找不到路径
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # 人脸对齐
    images = dlib.get_face_chips(rgb_img, faces, size=320)
    # 显示计数，按照这个计数创建窗口
    image_cnt = 0
    # 显示对齐结果
    facenames = []
    for image in images:
        image_cnt += 1
        cv_rgb_image = np.array(image).astype(np.uint8)  # 先转换为numpy数组
        cv_bgr_image = cv2.cvtColor(cv_rgb_image, cv2.COLOR_RGB2BGR)  # opencv下颜色空间为bgr，所以从rgb转换为bgr
        # cv2.imshow('%s' % (image_cnt), cv_bgr_image)
        # 给校正后的脸添加序号名称
        # facename = chr(cv2.waitKey(0))
        # print(facename)
        # 获取所有的文件名称
        # dirs = 'img1/M/facedata/' + facename
        # if not os.path.exists(dirs):
        #     os.makedirs(dirs)
        dirs = "./media/facek/facedata/"  #此处路径也要加 .
        faceids = os.listdir(dirs)
        # 得到最大的一个数字 +1 作为新的名称
        if len(faceids) > 0:
            newid = int(faceids[-1].split('.')[0]) + 1
        else:
            newid = 0
        facename = dirs + str(newid).zfill(5) + '.jpg'
        print(facename)
        cv2.imwrite(facename, cv_bgr_image)
        facenames.append("/media/facek/facedata/"+str(newid).zfill(5) + '.jpg')
    return len(dets),facenames

def saveface(rgb_img,faces):
    # 人脸对齐
    images = dlib.get_face_chips(rgb_img, faces, size=320)
    # 显示计数，按照这个计数创建窗口
    image_cnt = 0
    # 显示对齐结果
    facepaths = []
    facenames = []
    for image in images:
        image_cnt += 1
        cv_rgb_image = np.array(image).astype(np.uint8)  # 先转换为numpy数组
        cv_bgr_image = cv2.cvtColor(cv_rgb_image, cv2.COLOR_RGB2BGR)
        dirs = "./media/facek/facedata/"
        faceids = os.listdir(dirs)
        # 得到最大的一个数字 +1 作为新的名称
        if len(faceids) > 0:
            newid = int(faceids[-1].split('.')[0]) + 1
        else:
            newid = 0
        facepath = dirs+ str(newid).zfill(5) + '.jpg'
        print(facepath)
        cv2.imwrite(facepath, cv_bgr_image)
        facenames.append(facereg(cv_bgr_image)[0])
        facepaths.append(facepath.strip('.'))
    return facepaths,facenames

def checked(imgpath,pdatapath):
    df=pd.read_csv(pdatapath,header=None,sep=',')
    if imgpath in df[0].values: #df[0]表示第一列imgpath的所有值
        # 得到对应path的那一行值
        row = df[df[0].isin([imgpath])]
        temp = row.values[0][1] #得到 "['facelib/00054.jpg', 'facelib/00055.jpg']"
        # 对字符串进行处理
        facespath = temp.strip('[]').replace("'", "").split(',')
        temp = row.values[0][2]
        facenames = temp.split(',')
        facenamesN = []
        for name in facenames:
            facenamesN.append(name.replace("'", "").replace(" ", "").strip('[]'))
        return imgpath,facespath,facenamesN,int(row.values[0][3])
    else:
        return [imgpath]

def demo(imgpath, pdatapath,name):
    # 判断图片是否已经检测过，若检测过则直接返回已经检测到的结果
    res = checked(imgpath, pdatapath)
    if len(res) > 1:
        print("alrealy checked...")
        return res[0],res[1],res[2],res[3]
    img = cv2.imread(imgpath)
    # print(type(img))  //type ndarray
    img = cv2.resize(img, (1600, int(img.shape[0] / (img.shape[1]) * 1600)))
    # 彩色图像识别效果更强一些
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # 人脸分类器
    detector = dlib.get_frontal_face_detector()
    # 获取人脸检测器
    predictor = dlib.shape_predictor("./upload/shape_predictor_68_face_landmarks.dat")
    faces = dlib.full_object_detections()
    dets = detector(rgb_img, 1)
    print(len(dets))

    for face in dets:
        shape = predictor(img, face)  # 寻找人脸的68个标定点
        k = shape.parts()
        # print(k[36,0])
        # 遍历所有点，打印出其坐标，并圈出来
        for pt in shape.parts():
            pt_pos = (pt.x, pt.y)
            cv2.circle(img, pt_pos, 3, (0, 255, 0), 1)
            left = face.left()
            top = face.top()
            right = face.right()
            bottom = face.bottom()
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 3)

        faces.append(predictor(rgb_img, face))
        # 绘制矩形框  在图片中标注人脸，并显示

    cv2.imwrite('./media/facek/'+name,img)  # 竟然必须加上一个点，不然找不到路径
    facenames = []
    facepaths = []
    if len(dets) > 0:
        facepaths,facenames = saveface(rgb_img, faces)
        print(facenames)
    # 将检测后的结果写入到csv文件中去
    with open(pdatapath, 'a+', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # 写入多行用writerows
        imgpath = imgpath.replace(' ', '')
        writer.writerow([imgpath, facepaths,facenames, len(dets)])
    imgpath = imgpath.replace(' ', '')
    return imgpath, facepaths,facenames, len(dets)
import csv
# 人脸识别
import face_recognition
def facereg(faceimg):
    # 读取文件
    f = open('./media/known_face_names.txt', 'r')
    known_face_names = eval(str(f.readlines()[0]))
    print(known_face_names[0])
    f.close()
    known_face_encodings = np.loadtxt('./media/known_face_encodings.txt', delimiter=',')
    print(known_face_encodings.shape)

    face_names = []
    # 批量编码
    face_encodings = face_recognition.face_encodings(faceimg)
    for face_encoding in face_encodings:
        # 取出一张脸并与数据库中所有的人脸进行对比，计算得分
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)
        name = "Unknown"
        # 找出距离最近的人脸
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        # 取出这个最近人脸的评分
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        face_names.append(name)
    print("已处理：  有人脸", face_names)
    return face_names


# with open(pdatapath,'a+',newline ='',encoding='utf-8-sig') as f:
#         writer = csv.writer(f)
#         #先写入columns_name
#         writer.writerow(["imgpath","Faceloc","FaceNum"])

def writeinfo(imgpath,pdatapath):
    with open(pdatapath,'a+',newline ='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        #写入多行用writerows
        writer.writerow(demo(imgpath, pdatapath))


# demo('d:/py/My_work/6_27_facebook/mtcnn-keras-master/img1/M/9.jpg', pdatapath)