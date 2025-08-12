from client import ASEngineClient
import asyncio
import pyaudio
import numpy as np
import time
import json

# 音频配置
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_SIZE = 1024  

# WebSocket 客户端发送音频数据的函数
async def send_audio_data(client, route):
    # 初始化 PyAudio
    p = pyaudio.PyAudio()

    # 打开麦克风流
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)
    audio_chunks = []
    
    while True:
        # 从麦克风读取音频数据
        audio_data = stream.read(CHUNK_SIZE)

        # 这里不需要进行浮动数值转换，直接保留原始 PCM 二进制数据
        audio_chunks.append(audio_data)
        
        if len(audio_chunks) >= 16:  # 当积累到一定数量的块时，发送
            # 合并所有音频块
            merged_data = b''.join(audio_chunks)
            
            client.send_voice(route, merged_data)
            
            # 清空音频块，准备接收下一批数据
            audio_chunks = []

if __name__ == '__main__':
    # 服务器URL和命名空间
    SERVER_URL = 'http://localhost:5000'  # 替换为您的服务器URL
    NAMESPACE = '/socket.io/7100eebf7a909e1ee3f4e06766f512f0358ecb6ac51d5434c17d31dd70890dc1'  # 替换为您的命名空间
    
    # 创建客户端
    client = ASEngineClient(SERVER_URL+NAMESPACE, NAMESPACE)
    
    # 注册路由和回调函数
    def text_message_handler(data):
        print(f"Custom handler received text: {data}")
        
    def voice_message_handler(data):
        print(f"Custom handler received voice: {data}")
        
    client.register_route('test', text_message_handler)
    client.register_route('audiotest', voice_message_handler)
    client.register_route('imagetest')  # 使用默认回调
    
    # 连接服务器
    if client.connect():
        print("Successfully connected to server")
        
        # 发送初始文本消息到test路由
        # client.send_text('test', "Hello, this is a test message!")
        
        print('''请输入指令 
        1. `send_text 路由名 文本`          直接发送文本消息
        2. `send_voice 路由名`             打开麦克风并开始流式发送音频消息
        3. `send_image 路由名 文件路径`     发送图片消息
        4. `exit` 退出):''')
        while True:
            try:
                user_input = input().strip()
                if user_input.lower() == 'exit':
                    print("正在断开连接...")
                    client.disconnect()
                    break
                
                parts = user_input.split(' ')
                command = parts[0]
                if command not in ['send_text', 'send_voice', 'send_image']:
                    print("输入格式错误，请按照格式输入指令")
                    continue

                
                route = parts[1]
                if command != 'send_voice':
                    if len(parts) < 3:
                        print("输入格式错误，请按照格式输入指令")
                        continue
                    content = " ".join(parts[2:])
                else:
                    content = None
                if command == 'send_text':
                    client.send_text(route, content)
                elif command == 'send_voice':
                    asyncio.run(send_audio_data(client, route))

                elif command == 'send_image':
                    client.send_image(route, content)
                else:
                    print("未知指令，请输入有效的指令")
            except KeyboardInterrupt:
                print("\n检测到中断信号，正在断开连接...")
                client.disconnect()
                break
    else:
        print("Failed to connect to server")