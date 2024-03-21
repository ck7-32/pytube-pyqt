from PyQt6 import QtWidgets, QtGui


from UI import Ui_Dialog

from pytubefix import YouTube
import sys
import urllib.request
import os

def find_resolution_index(resolution):
    index = RES.index(resolution)
    return index+1

def thumbnail(url):
    return YouTube(url).thumbnail_url


class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui =Ui_Dialog()
        self.ui.setupUi(self)
        self.setup_control()
        self.video=None
    def setup_control(self):
        self.clicked_counter = 0
        self.ui.loadvideo.clicked.connect(self.loadvideo)
        self.ui.downloadbutton.setDisabled(True)
        self.ui.downloadbutton.clicked.connect(self.download)
        self.ui.quickmp4.clicked.connect(self.quickmp4)
        self.ui.mp3.clicked.connect(self.downloadmp3)
        self.ui.videotitle.setText("請載入影片")
        self.ui.progressBar.hide()
        self.ui.done.hide()
        self.ui.filesize.hide()
    def loadvideo(self):
        self.video=YouTube( self.ui.lineEdit.text(),on_progress_callback=self.progess)
        self.loadthumbnail()
        self.loadtitle()
        self.getresolution()
        self.ui.downloadbutton.setDisabled(False)
    def loadthumbnail(self):
        imgurl= self.video.thumbnail_url
        print(imgurl)
        img=urllib.request.urlretrieve(imgurl,"test.jpg")     # 加入 QGraphicsScene)      # 設定 QGraphicsScene 位置與大小
        img = QtGui.QPixmap("test.jpg")
        os.remove("test.jpg")
        img = img.scaled(427,320)           # 加入圖片
            # 將圖片加入 scene
        self.ui.thumbnail.setPixmap(img)  


    def loadtitle(self):
            self.ui.videotitle.setText(self.video.title)
    def getresolution(self):
            self.ui.resolution.clear
            res=[]
            for stream in self.video.streams:
        # 如果解析度存在於串流中，添加到集合中
                if stream.resolution:
                    res.append(stream.resolution)
                    print(f"Resolution: {stream.resolution}")
                    print(f"File Format: {stream.mime_type}")
                    print(f"Audio Format: {stream.audio_codec}")
                    print(f"File Size: {stream.filesize / (1024 * 1024):.2f} MB")
                    print("---------------")
            self.ui.resolution.addItems(res)
            self.ui.resolution.setCurrentIndex(len(self.ui.resolution))

    def downloadmp4(self,res="h"):
        yt = self.video
        if res =="h":
            yt.streams.filter().get_highest_resolution().download()
        else:
            yt.streams.filter().get_by_resolution(res).download()

    def bytes_to_megabytes(self,bytes_size):
        megabytes_size = bytes_size / (1024 ** 2)
        return megabytes_size
    def progess(self,stream, chunk, bytes_remaining):
        self.ui.filesize.show()
        self.ui.filesize.setText("檔案大小:"+("{:.2f}".format(self.bytes_to_megabytes(stream.filesize)))+"MB")
        current = stream.filesize - bytes_remaining
        done = int(50 * current / stream.filesize)
        self.ui.progressBar.show()
        self.ui.progressBar.setRange(0,int("{:.0f}".format(self.bytes_to_megabytes(stream.filesize))))
        self.ui.progressBar.setValue(int("{:.0f}".format(self.bytes_to_megabytes(current))))
        if stream.filesize==current:
            self.ui.progressBar.hide()
            self.ui.done.show()
            self.ui.filesize.hide()

    def download(self):
        rs=self.ui.resolution.currentText()
        print(rs)
        self.downloadmp4(rs)
    def quickmp4(self):
        self.loadvideo()
        self.downloadmp4()
    def downloadmp3(self):
        self.loadvideo()
        self.video.streams.filter().get_audio_only().download()
        
        
           
                
            
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    window.show()
    sys.exit(app.exec())