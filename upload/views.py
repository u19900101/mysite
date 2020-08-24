from django.shortcuts import render, render_to_response
import cv2
import dlib
import os
from django.shortcuts import render
from django.http import HttpResponse

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
    # print(type(img))  //type ndarray
    # img = cv2.resize(img,(500,int(img.shape[0]/(img.shape[1])*500)))
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 彩色图像识别效果更强一些
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 人脸分类器
    detector = dlib.get_frontal_face_detector()
    # 获取人脸检测器
    predictor = dlib.shape_predictor("./upload/shape_predictor_68_face_landmarks.dat")

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
    img = cv2.resize(img,(600,int(img.shape[0]/(img.shape[1])*600)))
    # 绘制矩形框  在图片中标注人脸，并显示

    # cv2.imshow("image", img)
    cv2.imwrite('./media/facek/'+filename,img)  # 竟然必须加上一个点，不然找不到路径
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return len(dets)