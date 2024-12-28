import sys
import time
import pygame
import random
import librosa
import numpy as np
from moviepy import *
 

class OSU:
    def __init__(self, audio_path, video_path, note_interval):
        pygame.init()
        self.width, self.height = 1280, 760
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.alpha = 60
        self.screen.fill((0, 0, 0))
        pygame.display.set_caption("艾尔登法球之千恋万球")
        pygame.display.flip()
        
        self.note_color = (255, 255, 255)  # 音符颜色
        self.note_radius = 5  # 音符半径
        self.min_radius = 5
        self.max_radius = 30
        self.score = 0
        self.noteNum = 0
        self.note_timer = 0
        self.note_visible = False
        self.note_position = (0, 0)
        self.start_time = 0  # 记录游戏开始时间

        self.audio_path = audio_path
        self.video_path = video_path
        
        self.font = pygame.font.Font(None, 36)
        self.note_interval = note_interval  # 音符生成间隔
 
    def spawn_note(self):
        self.note_position = (random.randint(self.width //3, self.width // 3 * 2),
                              random.randint(self.height // 3, self.height // 3 * 2))
        self.note_visible = True
        col1 = random.randint(155, 255)
        col2 = random.randint(155, 255)
        col3 = random.randint(155, 255)
        self.note_color = (col1, col2, col3)
        self.note_timer = time.time()
 
    def draw(self, frame):
        # 将帧绘制到 Pygame 窗口
        self.screen.blit(frame, (0, 0))
        transparent_rect_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(transparent_rect_surface, (0, 0, 0, self.alpha), (0, 0, self.width, self.height))
        self.screen.blit(transparent_rect_surface, (0, 0))
        if self.note_visible:
            pygame.draw.circle(self.screen, self.note_color, self.note_position, self.note_radius)  # 绘制音符
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        pygame.display.flip()
 
    def run(self):
        clock = pygame.time.Clock()
        x, y = self.get_beats()
        i, j = 0, 0
        clip = VideoFileClip(self.video_path)

        # 提前加载所有动画
        frames = []
        total_frames = clip.reader.n_frames  # 获取视频帧总数
        loading_font = pygame.font.Font(None, 36)

        for frame_index, frame in enumerate(clip.iter_frames()):
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.unload() 
                        self.show_final_score()
            frame = np.rot90(frame)
            frame_surface = pygame.surfarray.make_surface(np.flipud(frame))
            frame_surface = pygame.transform.scale(frame_surface, (self.width, self.height))
            frames.append(frame_surface)

            # 计算加载进度
            progress = (frame_index + 1) / total_frames
            progress_percent = int(progress * 100)
            progress_text = f"Loading: {progress_percent}%"

            # 在屏幕上显示加载进度, 循环十次保证加载出画面
            for _ in range(10):
                self.screen.fill((0, 0, 0))  # 清空屏幕
                loading_text = loading_font.render(progress_text, True, (255, 255, 255))
                loading_rect = loading_text.get_rect(center=(self.width // 2, self.height // 2))
                self.screen.blit(loading_text, loading_rect)
                pygame.display.flip()  # 更新显示

        pygame.mixer.music.load(self.audio_path)
        pygame.mixer.music.play()
        self.start_time = time.time()
        start_video = False

        while pygame.mixer.music.get_busy():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    self.show_final_score()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.unload() 
                        self.show_final_score()
                if event.type == pygame.MOUSEBUTTONDOWN and self.note_visible:
                    mouse_pos = pygame.mouse.get_pos()
                    note_rect = pygame.Rect(self.note_position[0] - self.note_radius,
                                             self.note_position[1] - self.note_radius,
                                             self.note_radius * 2, self.note_radius * 2)
                    if note_rect.collidepoint(mouse_pos):
                        self.score += 1
                        self.note_visible = False
            if i < len(x) and time.time() - self.start_time - x[i] >= 0:
                if time.time() - self.start_time - x[i] >= 0.5: 
                    i += 1
                if time.time() - self.note_timer > self.note_interval: 
                    if i < len(y) and y[i] > 0.25:
                        self.spawn_note()
                        self.noteNum += 1
                #调整note半径    
                if time.time() - self.note_timer <= 0.1:
                    self.note_radius = self.min_radius
                else:
                    self.note_radius = pygame.math.lerp(self.min_radius, self.max_radius, min((time.time() - self.note_timer) * 4, 1))
            else:
                if time.time() - self.start_time - x[len(x) - 1] >= 1: self.note_visible = False
            #根据视频进行参数调节, 在此x[0]是9.5, 根据这个数以及视频音频播放的时刻, 将两者对齐
            if time.time() - self.start_time > x[0] - int(x[0]) + 0.6:
                start_video = True
            if start_video:
                self.draw(frames[j])
                j += 1
            clock.tick(clip.fps)
    
    def get_beats(self):
        y_audio, sr = librosa.load(self.audio_path)
        _, beats = librosa.beat.beat_track(y=y_audio, sr=sr)
        x = librosa.frames_to_time(beats, sr=sr)
        y_audio, sr = librosa.load(self.audio_path)

        # 提取相应节拍的振幅作为Y坐标
        amplitude = []
        for i in range(len(beats) - 1):
            start_sample = librosa.frames_to_samples(beats[i])
            end_sample = librosa.frames_to_samples(beats[i + 1])
            segment = y_audio[start_sample:end_sample]
            amplitude.append(np.max(np.abs(segment)))  # 计算振幅

        y = amplitude  # 将振幅作为Y坐标

        # 只保留与x相匹配的y
        if len(y) < len(x): x = x[:len(y)]

        return x, y


    def show_final_score(self):
        print(f"游戏结束！您的得分是: {self.score}")
        pygame.quit()
 
if __name__ == "__main__":
    difficulty = input("请输入游戏难度(Ciallo~(∠・ω< )⌒★):").strip()
 
    # 根据难度设置音符生成的间隔
    difficulty_map = {
        "Ciallo~(∠・ω< )⌒★": 0.5
    }
 
    if difficulty in difficulty_map:
        note_interval = difficulty_map[difficulty]
    else:
        print("需要按照规定输入游戏难度！")
        sys.exit()

    print("\n游戏准备就绪,启动中...")
    game = OSU("D:\A my songs\一等情事.mp3", "C:/Users/ruheng47/Desktop/一等情事.mp4", note_interval)
    game.run()