import socketio
import socketio
import time
import base64
import os
from datetime import datetime
from typing import Dict, Callable, Any, Optional

class ASEngineClient:
    def __init__(self, server_url: str, namespace: str):
        """
        初始化客户端
        :param server_url: 服务器URL，例如 'http://localhost:5000'
        :param namespace: 命名空间，例如 '/socket.io/7100eebf7a909e1ee3f4e06766f512f0358ecb6ac51d5434c17d31dd70890dc1'
        """
        self.server_url = server_url
        self.namespace = namespace
        self.sid = None
        self.connected = False
        
        # 创建SocketIO客户端
        self.sio = socketio.Client()
        
        # 存储路由和对应的回调函数
        self.routes: Dict[str, Dict[str, Callable]] = {}
        
        # 注册基础事件处理函数
        self._register_base_events()
        
    def _register_base_events(self):
        """注册基础事件处理函数"""
        # 连接事件
        @self.sio.on('connect', namespace=self.namespace)
        def on_connect():
            self.connected = True
            self.sid = self.sio.get_sid(namespace=self.namespace)
            print(f"Connected to server. SID: {self.sid}")
            
        # 断开连接事件
        @self.sio.on('disconnect', namespace=self.namespace)
        def on_disconnect():
            self.connected = False
            self.sid = None
            print("Disconnected from server")
            
        @self.sio.on('error', namespace=self.namespace)
        def on_error(data):
            print(f"Received error: {data}")
            self.connected = False
            self.sid = None


        # 响应事件
        @self.sio.on('response', namespace=self.namespace)
        def on_response(data):
            print(f"Received response: {data}")
            
    def register_route(self, route: str, callback: Optional[Callable] = None):
        """
        注册一个路由及其回调函数
        :param route: 路由名称
        :param callback: 回调函数，接收消息数据作为参数
        :return: 是否注册成功
        """
        if not route:
            print("Route cannot be empty")
            return False
        
        # 存储路由和回调
        self.routes[route] = {
            'callback': callback if callback else self._default_callback
        }
        
        # 注册事件处理器
        @self.sio.on(route, namespace=self.namespace)
        def on_route_message(data):
            print(f"Received message on route '{route}': {data}")
            if 'callback' in self.routes[route]:
                try:
                    self.routes[route]['callback'](data)
                except Exception as e:
                    print(f"Error in callback for route '{route}': {e}")
            
        print(f"Route '{route}' registered successfully")
        return True
        
    def _default_callback(self, data: Any):
        """默认回调函数"""
        print(f"Default callback received: {data}")
        
    def connect(self, timeout: int = 5) -> bool:
        """
        连接到服务器
        :param timeout: 超时时间(秒)
        :return: 是否连接成功
        """
        try:
            self.sio.connect(
                self.server_url,
                namespaces=[self.namespace],
                wait_timeout=timeout
            )
            # 等待连接建立
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            return self.connected
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
        
    def disconnect(self):
        """断开与服务器的连接"""
        if self.connected:
            self.sio.disconnect()
            self.connected = False
            self.sid = None
            print("Disconnected from server")
        
    def send_text(self, route: str, text: str) -> bool:
        """
        发送文本消息
        :param route: 目标路由
        :param text: 要发送的文本
        :return: 是否发送成功
        """
        if not self.connected:
            print("Not connected to server")
            return False
        
        if route not in self.routes:
            print(f"Route '{route}' not registered")
            return False
        
        try:
            self.sio.emit(route, {'type': 'text', 'data': text}, namespace=self.namespace)
            print(f"Sent text to route '{route}': {text}")
            return True
        except Exception as e:
            print(f"Failed to send text to route '{route}': {e}")
            return False
        
    def send_voice(self, route: str, voice_data: bytes) -> bool:
        """
        发送语音数据
        :param route: 目标路由
        :param voice_data: 语音数据字节流
        :return: 是否发送成功
        """
        if not self.connected:
            print("Not connected to server")
            return False
        
        try:
            # 编码语音数据为base64
            # voice_data = 'data:image/jpeg;base64,' +base64.b64encode(voice_data).decode('utf-8')
            
            # 发送数据
            self.sio.emit(
                route,
                {
                    'type': 'audio',
                    'data': voice_data,
                    'timestamp': int(time.time() * 1000),
                    'sampleRate': 16000
                },
                namespace=self.namespace
            )
            

            print(f"Sent voice file to route '{route}'")
            return True
        except Exception as e:
            print(f"Failed to send voice to route '{route}': {e}")
            return False
        
    def send_image(self, route: str, file_path: str) -> bool:
        """
        发送图片文件
        :param route: 目标路由
        :param file_path: 图片文件路径
        :return: 是否发送成功
        """
        if not self.connected:
            print("Not connected to server")
            return False
        
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return False
            
            # 读取文件并进行base64编码
            with open(file_path, 'rb') as f:
                image_data = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('utf-8')

            # 获取文件名
            filename = os.path.basename(file_path)
            
            # 发送数据
            self.sio.emit(
                route,
                {
                    'type': 'image',
                    'data': image_data
                },
                namespace=self.namespace
            )
            print(f"Sent image file to route '{route}': {filename}")
            return True
        except Exception as e:
            print(f"Failed to send image to route '{route}': {e}")
            return False
        
    def run_forever(self):
        """
        保持客户端运行"""
        if self.connected:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Client stopped by user")
                self.disconnect()
        else:
            print("Not connected to server")

