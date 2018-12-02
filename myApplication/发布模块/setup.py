from distutils.core import setup

setup(name="hm_message",  # 包名
      version="1.0",  # 版本
      description="Asher's 发送和接收消息模块",  # 描述信息
      long_description="完整的发送和接收消息模块",  # 完整描述信息
      author="Asher",  # 作者
      author_email="ludahai19@163.com",  # 作者邮箱
      url="www.python.org",  # 主页
      license='88888888',  # 秘钥
      platforms='python3.x',  # 使用平台
      py_modules=["hm_message.send_message",
                  "hm_message.receive_message"])
