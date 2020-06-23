# biliDownload

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

Just download the ffmpeg in this project, and put it in the same folder of the code.



## If you failed to work with ffmpeg

Find those two lines in the code then comment or remove them.

```python
os.remove(video_path)
os.remove(audio_path)
```

