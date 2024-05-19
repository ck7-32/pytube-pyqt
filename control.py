from PyQt6 import QtWidgets, QtGui


from UI import Ui_Dialog
import subprocess
from pytubefix import YouTube
import sys
import urllib.request
import os


def get_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key =(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')
output_dir=get_download_path()    
def fixfilename(filename):
    invalid = '<>:"/\|?* '
    for char in invalid:
        filename = filename.replace(char, ' ')
    return(filename)

class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui =Ui_Dialog()
        self.ui.setupUi(self)
        self.setup_control()
        self.video=None
        self.itags=[]
        self.res=[]
        self.title=""
        self.url=""
        self.path=get_download_path()
    def setup_control(self):
        self.clicked_counter = 0
        self.ui.loadvideo.clicked.connect(self.loadvideo)
        self.ui.downloadbutton.setDisabled(True)
        self.ui.downloadbutton.clicked.connect(self.download)
        self.ui.quickmp4.clicked.connect(self.quickmp4)
        self.ui.mp3.clicked.connect(self.downloadmusic)
        self.ui.videotitle.setText("請載入影片")
        self.ui.progressBar.hide()
        self.ui.done.hide()
        self.ui.filesize.hide()
        self.ui.audio.hide()
        if not os.path.exists(str(output_dir)):
            os.makedirs(str(output_dir))
    def loadvideo(self):
        self.url=self.ui.lineEdit.text()
        self.video=YouTube( self.url,on_progress_callback=self.progess)
        self.loadthumbnail()
        self.loadtitle()
        if "music.youtube.com" in self.url:
            self.loadaudio()
        else:
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
        self.title=self.video.title
        self.ui.videotitle.setText(self.title)
    
    def loadaudio(self):
        self.ui.resolution.clear()
        self.res=[]
        self.itags=[]
        for stream in self.video.streams.filter(only_audio=True): 
            codecs=stream.codecs[0].split(".")[0]
        # 如果解析度存在於串流中，添加到集合中
            if stream.type == "audio":
                self.res.append(f"{stream.abr}/{stream.filesize / (1024 * 1024):.0f}mb")
                self.itags.append(stream.itag)
                        
                print(f"Resolution: {stream.resolution}")
                print(f"File Format: {stream.mime_type}")
                print(f"位元率: {stream.abr}")
                print(f"Audio Format: {stream.audio_codec}")
                print(f"codec: {codecs}")
                print(f"File Size: {stream.filesize / (1024 * 1024):.2f} MB")
                print("---------------")                        
            
        self.ui.resolution.addItems(self.res)
        self.ui.resolution.setCurrentIndex(len(self.ui.resolution))
        self.ui.audio.show()
        self.ui.audio.setChecked(True)
            
                
    def getresolution(self):
            self.ui.resolution.clear()
            self.res=[]
            self.itags=[]
            for stream in self.video.streams.filter(adaptive=True,file_extension='mp4'): 
                codecs=stream.codecs[0].split(".")[0]
        # 如果解析度存在於串流中，添加到集合中
                if stream.resolution and stream.mime_type == "video/mp4" and stream.type == "video" :
                    self.res.append(f"{stream.resolution}/{stream.filesize / (1024 * 1024):.0f}mb")
                    self.itags.append(stream.itag)
                    
                    print(f"Resolution: {stream.resolution}")
                    print(f"Fps: {stream.fps}")
                    print(f"File Format: {stream.mime_type}")
                    print(f"Audio Format: {stream.audio_codec}")
                    print(f"codec: {codecs}")
                    print(f"File Size: {stream.filesize / (1024 * 1024):.2f} MB")
                    print("---------------")
                    
            self.ui.resolution.addItems(self.res)
            self.ui.resolution.setCurrentIndex(len(self.ui.resolution))
            self.ui.audio.show()
            self.ui.audio.setChecked(True)

    def downloadmp4(self,res="h"):
        yt = self.video
        if res =="h":
            yt.streams.filter().get_highest_resolution().download(self.path)
        else:
            yt.streams.filter().get_by_itag(self.itags[self.res.index(res)]).download(self.path,filename="pyvideo.mp4")
        self.ui.filesize.hide()
        self.ui.progressBar.hide()
        self.ui.done.setText("下載完成")
        #如果要合成音檔的話:
        if self.ui.audio.isChecked():
            self.ui.done.setText("正在下載音檔")
            print("have to download audio")
            yt.streams.get_audio_only().download(self.path,filename="pyaudio.mp3")
            self.ui.progressBar.hide()
            self.ui.done.setText("正在使用ffmpeg合成")
            # 獲取已下載的影片和音頻檔案路徑
            
            video_file =f"{self.path}\\pyvideo.mp4"  
            audio_file =f"{self.path}\\pyaudio.mp3"
            print(self.path)
            # 使用ffmpeg將影片和音頻檔案合併
            try:
                outputfile=os.path.join(f"{self.path}\\{fixfilename(self.title)} merged.mp4")
                subprocess.run(["ffmpeg", "-i", video_file, "-i", audio_file, "-c", "copy", outputfile])
                os.remove(video_file)
                os.remove(audio_file)
                self.ui.done.setText("完成")
            except:
                self.ui.done.setText("發生錯誤 請檢查ffmpeg")
    def downloadmp3(self,res="h"):
        yt = self.video
        if res =="h":
            yt.streams.get_audio_only().download(self.path)
        else:
            yt.streams.filter().get_by_itag(self.itags[self.res.index(res)]).download(self.path)
        self.ui.filesize.hide()
        self.ui.progressBar.hide()
        self.ui.done.setText("下載完成")
    def bytes_to_megabytes(self,bytes_size):
        megabytes_size = bytes_size / (1024 ** 2)
        return megabytes_size
    def progess(self,stream, chunk, bytes_remaining):
        self.ui.done.hide()
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

    def download(self):
        rs=self.ui.resolution.currentText()
        print(rs)
        if "music.youtube" in self.url:
            self.downloadmp3(rs)
        else:
            self.downloadmp4(rs)
    def quickmp4(self):
        self.loadvideo()
        self.downloadmp4()
    def downloadmusic(self):
        self.loadvideo()
        self.downloadmp3()
        
        
           
                
            
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    window.show()
    sys.exit(app.exec())