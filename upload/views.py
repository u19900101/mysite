from django.shortcuts import render, render_to_response
import cv2
import dlib
import os
from django.shortcuts import render
from django.http import HttpResponse
import dlib
from pandas import np


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
            with open("./upload/uploadimg/%s" % File.name, 'wb+') as f:
                # 分块写入文件
                for chunk in File.chunks():
                    f.write(chunk)

            filename = File.name
            print(filename)
            path = "./upload/uploadimg/"+filename
            print(path)
            face_num=getface_dlib(path,filename)
            content = {}
            content['path'] = "/media/facek/"+filename
            content['face_num'] = face_num
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
        print(dirs + str(newid).zfill(5) + '.jpg')
        cv2.imwrite(dirs + str(newid).zfill(5) + '.jpg', cv_bgr_image)
    return len(dets)