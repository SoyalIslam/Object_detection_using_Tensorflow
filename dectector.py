import cv2,time
import os
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.utils.data_utils import get_file

np.random.seed(40)
class Detector:
    def __init__(self):
        self.model = None
        self.classeslist = []
        self.colorList = []
        self.cacheDir = "./pretrained_model"

    def readClasses(self, classesFilePath):
        with open(classesFilePath, 'r') as f:
            self.classeslist = f.read().splitlines()
        self.colorList = np.random.uniform(low=0, high=255, size=(len(self.classeslist), 3))
        print(len(self.classeslist), len(self.colorList))

    def download(self, modelUrl):
        fileName = os.path.basename(modelUrl)
        self.modelName = fileName[:fileName.index('.')]
        os.makedirs(self.cacheDir, exist_ok=True)
        get_file(fname=fileName, origin=modelUrl, cache_dir=self.cacheDir, cache_subdir="checkpoints", extract=True)

    def loadModel(self):
        print("Loading Model " + self.modelName)
        tf.keras.backend.clear_session()
        self.model = tf.saved_model.load(os.path.join(self.cacheDir, "checkpoints", self.modelName, "saved_model"))
        print('Model ' + self.modelName + " loaded successfully..")

    def createIdentifier(self, image, threshold=0.5):
        inputTensor = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2RGB)
        inputTensor = tf.convert_to_tensor(inputTensor, dtype=tf.uint8)
        inputTensor = inputTensor[tf.newaxis, ...]

        detections = self.model(inputTensor)
        boxes = detections['detection_boxes'][0].numpy()
        classIndexes = detections['detection_classes'][0].numpy().astype(np.int32)
        classScores = detections['detection_scores'][0].numpy()

        imH, imW, inC = image.shape

        boxIdx = tf.image.non_max_suppression(
            boxes,
            classScores,
            max_output_size=70,
            iou_threshold=threshold,
            score_threshold=threshold
        ).numpy() 
        if len(boxes) != 0:
            for i in boxIdx:
                box = tuple(boxes[i].tolist())
                classConfidence = round(100 * classScores[i])
                classIndex = classIndexes[i]

                classLabel = self.classeslist[classIndex].upper()
                classColor = self.colorList[classIndex]
                displayText = '{}:{}'.format(classLabel, classConfidence)

                ymin, xmin, ymax, xmax = box
                xmin, xmax, ymin, ymax = (xmin * imW, xmax * imW, ymin * imH, ymax * imH)
                xmin, xmax, ymin, ymax = int(xmin), int(xmax), int(ymin), int(ymax)

                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color=classColor, thickness=1)
                cv2.putText(image, displayText, (xmin, ymin - 10), cv2.FONT_HERSHEY_PLAIN, 1, classColor, 2)

                lineWidth = min(int((xmax - xmin) * 0.2), int((ymax - ymin) * 0.2))
                # Correct the cv2.line arguments to use tuples of two integers
                cv2.line(image, (xmin, ymin), (xmin + lineWidth, ymin), classColor, thickness=5)
                cv2.line(image, (xmin, ymin), (xmin, ymin + lineWidth), classColor, thickness=5)

                cv2.line(image, (xmax, ymin), (xmax-lineWidth, ymin), classColor, thickness=5)
                cv2.line(image, (xmax, ymin), (xmax, ymin + lineWidth), classColor, thickness=5)
                
                cv2.line(image, (xmin, ymax), (xmin + lineWidth, ymax), classColor, thickness=5)
                cv2.line(image, (xmin, ymax), (xmin, ymax - lineWidth), classColor, thickness=5)
                
                cv2.line(image, (xmax, ymax), (xmax-lineWidth, ymax), classColor, thickness=5)
                cv2.line(image, (xmax, ymax), (xmax, ymax - lineWidth), classColor, thickness=5)        
        return image

    def predictImage(self, imagePath, threshold=0.5):
        image = cv2.imread(imagePath)
        if image is None:
            print(f"Error: Unable to read image at path: {imagePath}")
            return
        boxImage = self.createIdentifier(image, threshold)

        cv2.imwrite(self.modelName + ".jpg", boxImage)
        cv2.imshow("Result", boxImage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    def predectVideo(self,videoPath,threshold=0.5):
        cap=cv2.VideoCapture(videoPath)

        if (cap.isOpened()==False):
            print("Error! File can't open")
            return
        (sucess,image)=cap.read()
        startTime=0  

        while sucess:
          currentTime=time.time()
          fps=1/(currentTime-startTime)
          startTime=currentTime
          boxesImage=self.createIdentifier(image,threshold)
          cv2.putText(boxesImage,"FPS"+str(int(fps)),(20,70),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
          cv2.imshow("Result",boxesImage)
          key=cv2.waitKey(1) & 0xFF
          if key == ord("q"):
              break
          (sucess,image)=cap.read()
        cv2.destroyAllWindows()
