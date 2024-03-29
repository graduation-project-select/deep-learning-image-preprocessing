# fashion_pose.py : MPII를 사용한 신체부위 검출
import cv2

# MPII에서 각 파트 번호, 선으로 연결될 POSE_PAIRS
BODY_PARTS = {"Head": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
              "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
              "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "Chest": 14,
              "Background": 15}

POSE_PAIRS = [["Head", "Neck"], ["Neck", "RShoulder"], ["RShoulder", "RElbow"],
              ["RElbow", "RWrist"], ["Neck", "LShoulder"], ["LShoulder", "LElbow"],
              ["LElbow", "LWrist"], ["Neck", "Chest"], ["Chest", "RHip"], ["RHip", "RKnee"],
              ["RKnee", "RAnkle"], ["Chest", "LHip"], ["LHip", "LKnee"], ["LKnee", "LAnkle"]]

# 각 파일 path
protoFile = "./pose_deploy_linevec_faster_4_stages.prototxt"
weightsFile = "./pose_iter_160000.caffemodel"

def findX1(output, W, imageWidth):
    x1 = -1
    # 2,3,4 중 가장 작은
    for i in range(2,5):
        # 해당 신체부위 신뢰도 얻음.
        probMap = output[0, i, :, :]
        # global 최대값 찾기
        minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
        # 원래 이미지에 맞게 점 위치 변경
        x = (imageWidth * point[0]) / W
        if prob > 0.1:
          if x1 == -1 or (x != -1 and x < x1):
              x1 = x
        # else:
        #     print(str(i)+" is 'else'")
    return x1

def findX2(output, W, imageWidth):
    x2 = -1
    # 5,6,7 중 가장 큰 값
    for i in range(5,8):
        # 해당 신체부위 신뢰도 얻음.
        probMap = output[0, i, :, :]
        # global 최대값 찾기
        minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
        # 원래 이미지에 맞게 점 위치 변경
        x = (imageWidth * point[0]) / W
        if prob > 0.1:
          if x2 == -1 or (x != -1 and x > x2):
              x2 = x
        # else:
        #     print(str(i)+" is 'else'")
    return x2

def findY1(output, H, imageHeight):
    y1 = -1
    probMap = output[0, 1, :, :] #목
    # global 최대값 찾기
    minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
    # 원래 이미지에 맞게 점 위치 변경
    y = (imageHeight * point[1]) / H
    # 키포인트 검출한 결과가 0.1보다 크면(검출한곳이 위 BODY_PARTS랑 맞는 부위면) points에 추가, 검출했는데 부위가 없으면 None으로
    # if prob > 0.1:
    y1 = y
    # else:
    #     print("1 is 'else'")
    return y1

def findY2(output, H, imageHeight):
    # 8,11 중 더 큰 값
    y2 = -1
    probMap8 = output[0, 8, :, :]
    minVal8, prob8, minLoc8, point8 = cv2.minMaxLoc(probMap8)
    probMap11 = output[0, 11, :, :]
    minVal11, prob11, minLoc11, point11 = cv2.minMaxLoc(probMap11)
    y8 = (imageHeight * point8[1]) / H
    y11 = (imageHeight * point11[1]) / H
    if y8 < y11 and prob8 > 0.1:
        y2 = y11
    elif y8 >= y11 and prob11 > 0.1:
        y2 = y8
    return y2

def detectUpperbody(image, output, imageWidth, imageHeight):
    H = output.shape[2]
    W = output.shape[3]

    x1 = findX1(output, W, imageWidth)
    x2 = findX2(output, W, imageWidth)
    y1 = findY1(output, H, imageHeight)
    y2 = findY2(output, H, imageHeight)
    print("x1:"+str(x1)+", x2: "+str(x2)+", y1: "+str(y1)+", y2: "+str(y2))

    if x1 != -1 and x2 != -1 and y1 != -1 and y2 != -1:
        alpha = 2
        if int(y1) - alpha > 0:
            y1 = int(y1) - alpha
        if int(x1) - alpha > 0:
            x1 = int(x1) - alpha
        if int(y2) + alpha < imageHeight:
            y2 = int(y2) + alpha
        if int(x2) + alpha < imageWidth:
            x2 = int(x2) + alpha

        cropped_img = image[int(y1): int(y2), int(x1): int(x2)]
        # cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), thickness=1)
        # cv2.imshow("Output-Keypoints", image)
        # cv2.waitKey(0)
        return cropped_img
    else:
        return []

# # 사용법!
# # 위의 path에 있는 network 불러오기
# net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
#
# # 이미지 읽어오기
# filePath = "./poseExample/"
# fileName = "17272.jpg"
# image = cv2.imread(filePath + fileName)
# # frame.shape = 불러온 이미지에서 height, width, color 받아옴
# imageHeight, imageWidth, _ = image.shape
# # network에 넣기위해 전처리
# inpBlob = cv2.dnn.blobFromImage(image, 1.0 / 255, (imageWidth, imageHeight), (0, 0, 0), swapRB=False, crop=False)
# # network에 넣어주기
# net.setInput(inpBlob)
# # 결과 받아오기
# output = net.forward()
# cropped_img = detectUpperbody(image, net)
# if len(cropped_img) != 0:
#     cv2.imshow("cropped_img", cropped_img)
#     cv2.imwrite(filePath + "cropped_ub/" + fileName, cropped_img)
# else:
#     print("Cannot find upper body")
# cv2.waitKey(0)
