from client import ASEngineClient

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
        
        print("请输入指令 (格式: send_text 路由名 文本 或 send_voice 路由名 文件路径 或 send_image 路由名 文件路径 或 exit 退出):")
        while True:
            try:
                user_input = input().strip()
                if user_input.lower() == 'exit':
                    print("正在断开连接...")
                    client.disconnect()
                    break
                
                parts = user_input.split()
                if len(parts) < 3:
                    print("输入格式错误，请按照格式输入指令")
                    continue
                
                command = parts[0]
                route = parts[1]
                content = " ".join(parts[2:])
                
                if command == 'send_text':
                    client.send_text(route, content)
                elif command == 'send_voice':
                    client.send_voice(route, content)
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