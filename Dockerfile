# 二开推荐阅读[如何提高项目构建效率](https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/scene/build/speed.html)
# 选择构建用基础镜像（选择原则：在包含所有用到的依赖前提下尽可能体积小）。如需更换，请到[dockerhub官方仓库](https://hub.docker.com/_/python?tab=tags)自行选择后替换。
# 已知alpine镜像与pytorch有兼容性问题会导致构建失败，如需使用pytorch请务必按需更换基础镜像。
FROM python:3.10-slim

# 容器默认时区为UTC，如需使用上海时间请启用以下时区设置命令
# RUN apt-get update && apt-get install -y tzdata && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo Asia/Shanghai > /etc/timezone && rm -rf /var/lib/apt/lists/*

# 使用 HTTPS 协议访问容器云调用证书安装
# 备份并替换为 Debian 镜像源（使用阿里云）
# 替换 debian.sources 中的 deb.debian.org
RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's@http://deb.debian.org@https://mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's@https://deb.debian.org@https://mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's@http://security.debian.org@https://mirrors.tuna.tsinghua.edu.cn/debian-security@g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's@https://security.debian.org@https://mirrors.tuna.tsinghua.edu.cn/debian-security@g' /etc/apt/sources.list.d/debian.sources; \
    fi && \
    # 同时处理传统的 sources.list
    sed -i 's@deb.debian.org@mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list 2>/dev/null || true && \
    sed -i 's@security.debian.org@mirrors.tuna.tsinghua.edu.cn/debian-security@g' /etc/apt/sources.list 2>/dev/null || true && \
    apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*


# 拷贝当前项目到/app目录下(.dockerignore中文件除外)
COPY . /app

# 设定当前的工作目录
WORKDIR /app

# 安装依赖到指定的/install文件夹
# 选用国内镜像源以提高下载速度
RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple \
&& pip config set global.trusted-host mirrors.cloud.tencent.com \
&& pip install --upgrade pip \
&& pip install -r requirements.txt

# 暴露端口
# 此处端口必须与「服务设置」-「流水线」以及「手动上传代码包」部署时填写的端口一致，否则会部署失败。
EXPOSE 80

# 执行启动命令
# 写多行独立的CMD命令是错误写法！只有最后一行CMD命令会被执行，之前的都会被忽略，导致业务报错。
# 请参考[Docker官方文档之CMD命令](https://docs.docker.com/engine/reference/builder/#cmd)
CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"]
