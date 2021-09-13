import requests

import subprocess
import sys

import re
import os
import json
import time

# PS: if there is no error, but you get no video output,
# comment the os.remove


class BiliDownloader:
    def __init__(self):
        self.start_page = 0
        self.session = requests.session()
        self.title = ''
        self.url = ''
        self.quality = 'h'

    def req_web(self, url, main=False, stream_mode=False):
        if main:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
                'Content-Range': 'bytes 0-xxxxxx',
                'Referer': main
            }
            if stream_mode:
                return self.session.get(url, stream=True, headers=headers)
            else:
                return self.session.get(url, headers=headers)
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
                'Content-Range': 'bytes 0-xxxxxx',
                'Referer': url
            }
            req = self.session.get(url, headers=headers)
            req.encoding = 'utf-8'
            return req.text

    def modify_quality(self,video_dict):
        # Modify quality
        highest_quality = sorted(video_dict.keys(),key=lambda x:int(x[:-1]))[-1]
        if self.quality == 'h':
            print('\n[Msg] We have {} quality for {}.'.format(highest_quality,self.film_title))
            video_url = video_dict[highest_quality]
        else:
            if self.quality in video_dict:
                video_url = video_dict[self.quality]
            else:
                print("This Video Options：")
                for i in video_dict:
                    print(i)
                quality = input("Your choice：")
                if quality in video_dict:
                    self.quality = quality
                    try:
                        video_url = video_dict[quality]
                    except:
                        print('[Error]No this quality! But we have {} one.'.format(highest_quality))
                        video_url = video_dict[highest_quality]
                else:
                    print("wrong")
                    time.sleep(5)
                    self.modify_quality(video_dict)
        return video_url

    def download_video(self,video_url,video_path):
        req_stream = self.req_web(video_url, main=self.down_url, stream_mode=True)
     
        file = open(video_path, "wb")
        length = float(req_stream.headers['content-length'])

        count = 0
        count_tmp = 0
        time1 = time.time()
        for chunk in req_stream.iter_content(chunk_size=512):
            if chunk:
                file.write(chunk)
                count += len(chunk)
                if time.time() - time1 > 1:
                    p = count / length * 100
                    speed = (count - count_tmp) / 1024 / 1
                    count_tmp = count
                    if 0 <= speed < (1024):
                        print("\r" + self.film_title + '   Process: ' + '{:.2f}'.format(p) + '%' + '    Speed: ' + '{:.2f}'.format(
                            speed) + 'KB/S', end="")
                    else:
                        print("\r" + self.film_title + '   Process: ' + '{:.2f}'.format(p) + '%' + '    Speed: ' + '{:.2f}'.format(
                            speed / 1024) + 'MB/S', end="")
                    time1 = time.time()
        file.close()

    def download_audio(self,audio_url,audio_path):
        r = self.req_web(audio_url, main=self.down_url)
        file = open(audio_path, "wb")
        file.write(r.content)
        file.close()

    def mix_final(self,video_path, audio_path, final_path):
        # -------------- mac/linux version --------------
        # you should have ffmpeg in your PC:
        # brew install ffmpeg
        
        cmd = "ffmpeg -i {} -i {} -vcodec copy -acodec copy {}".format(video_path, audio_path, final_path)
        # print('\nAlign Code:\n',cmd)
        subprocess.call(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)
        
        os.remove(video_path)
        os.remove(audio_path)
#         # -------------- windows version --------------
#         # Put the ffmpeg.exe in the same folder of this program.
#         mixer_path = os.path.join(os.getcwd(),'ffmpeg.exe')
#         if os.path.exists(mixer_path):            

#             # align the video and audio
#             cmd = "{} -i {} -i {} -vcodec copy -acodec copy {}".format(mixer_path,video_path,audio_path, final_path)
#             # print('\nAlign Code:\n',cmd)
#             subprocess.call(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#             os.remove(video_path)
#             os.remove(audio_path)
#         else:
#             print("No ffmpeg for mixing, Origin Video and Audio saved.")
        
#         time.sleep(5)
    
    def download(self, down_url, film_title):
        self.film_title = film_title
        
        req_text = self.req_web(down_url)
        json_pat = 'window.__playinfo__=(.*?)</script><script>window.__INITIAL_STATE'
        page_info = re.compile(json_pat).findall(req_text)[0]
        page_json = json.loads(page_info)
        video_process = page_json["data"]["dash"]["video"]
        audio_url = page_json["data"]["dash"]["audio"][0]["baseUrl"]

        video_dict = {str(i["id"]): i["baseUrl"] for i in video_process}
        video_url = self.modify_quality(video_dict)
        

        store_path = os.path.join(os.getcwd()+'/download',self.bv_code+'_'+self.title)
        
        if not os.path.exists(store_path):
            os.mkdir(store_path)
            
        video_path = os.path.join(store_path,"temp_{}.mp4".format(film_title))
        audio_path = os.path.join(store_path,"temp_{}.acc".format(film_title))
        final_path = os.path.join(store_path,"{}.mp4".format(film_title))
        
        self.down_url = down_url
        
        self.download_video(video_url,video_path)
        self.download_audio(audio_url,audio_path)
        self.mix_final(video_path, audio_path, final_path)

    def run(self, bv_code):
        
        if bv_code.startswith('http'):
            self.url_bili = bv_code
            self.bv_code = self.url_bili.split('/')[-1].split('?')[0]
        else:
            self.url_bili = 'https://www.bilibili.com/video/' + bv_code
            self.bv_code = bv_code
        req = self.req_web(self.url_bili)

        page_pat = re.compile('"page":(\d*?),"from".*?"part":"(.*?)",', re.S)
        name_pat = re.compile('name="keywords" content="(.*?),')
        pages = page_pat.findall(req)[self.start_page:]
        
        # remove the character which cannot exit in the name.
        filenameRemover = "[\/\\\:\*\?\"\<\>\|《》？“”’‘「」【】|、，。！@#￥%……&（）——+$ ]"
        title = re.sub(filenameRemover, '_', name_pat.findall(req)[0])
        self.title=title

        if "视频选集" in req:
            choice = input("We have multiple videos, input \n1 for all and \n0 for the first episode.\nDefault 0\n")
            if choice == '1':
                print("Video List：")
                print(*['{}_{}'.format(i[1], title) for i in pages], sep='\n')
                
                for each_page in pages:
                    each_title = re.sub(filenameRemover, '_', each_page[1])
                    page_title = '{}_{}_{}'.format(each_page[0],each_title, title)
                    page_url = '{}?p={}'.format(self.url_bili,each_page[0])
                    self.download(page_url, page_title)

            else:
                self.download(self.url_bili, title)
        else:
            self.download(self.url_bili, title)
            
        input("\nFilm has been saved, please press Enter to quit.")


bili = BiliDownloader()
bili.run('BV1Xx411m7kn')
# linux运维 https://www.bilibili.com/video/BV1r4411A7Qk

# 小程序测试 https://www.bilibili.com/video/BV1PT4y1G7cy
# vue小程序 https://www.bilibili.com/video/BV1Sc41187nZ
# 28节课小程序 https://www.bilibili.com/video/BV1Ct411p7bj
# 小程序五天 https://www.bilibili.com/video/BV1c4411P7US
# 小程序开发 https://www.bilibili.com/video/BV1nE41117BQ
# 党妹视频 https://www.bilibili.com/video/BV16a4y1e7r8
# 汇丰银行吸血史 https://www.bilibili.com/video/BV1BD4y1D7Cj