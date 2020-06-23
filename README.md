# biliDownload

```
My Env Version:
Python 		3.6.3
requests	2.23.0
```





Copy the BV code in bilibili.

And paste it in `bili.run` method.

```python
bili = BiliDownloader()
bili.run('https://www.bilibili.com/video/BV1Xx411m7kn')
```



**Use `ffmpeg` for combining video and audio.**



For MacOS or Linux

Install ffmpeg with brew or yum.

```bash
brew install ffmpeg
```



For Windows

Just download the ffmpeg in this project, and put it in the same folder of the code file.



## If you failed to work with ffmpeg

Find those two lines in the code then comment or remove them.

At least you will get the sperated video file and audio file.

You can combine them with `Pr` or `Final Cut Pro`.

```python
os.remove(video_path)
os.remove(audio_path)
```



Just for learning how to get web stream information, please delete what you download in 24h. 