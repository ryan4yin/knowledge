# 只在 Ubuntu 上测试过
PRIVATE_GIT_HOST=gitlab.local
GOLANG_VERSION=1.13.5


APT_SOURCE_HOST="mirrors.aliyun.com"

echo "1. apt 更换国内镜像源"
sudo sed -i "s/archive.ubuntu.com/${APT_SOURCE_HOST}/g" /etc/apt/sources.list

sudo apt-get update --fix-missing
sudo apt-get install -y \
        build-essential \
        automake \
        curl wget git \
        unzip zip gzip xz-utils p7zip


echo "2. 配置 git"
while true; do
    read -p "输入 git 使用的 username: " username
    read -p "输入 git 使用的 email 地址: " email
    echo "您设置的 git username 为: ${username}，email 为: ${email}"
    read -p "是否确认(Y/N): " confirm

    if [ $confirm != Y ] && [ $confirm != y ] && [ $confirm == '' ]; then
        echo "输入不能为空，重新输入"
    else
        break
    fi
done

git config --global user.name username
git config --global user.email email
# 让 git 优先走 ssh 协议，使用 ssh 密钥进行鉴权（拉内网数据需要这么配置）
git config --global url."git@$PRIVATE_GIT_HOST:".insteadOf "https://$PRIVATE_GIT_HOST/"

echo "3. 下载安装 go"
curl -sSL --output go.tar.gz https://dl.google.com/go/go$GOLANG_VERSION.linux-amd64.tar.gz
sudo tar -C /opt/ -xzf go.tar.gz
rm go.tar.gz

echo "export PATH=/opt/go/bin:$PATH" >> ~/.bashrc
source ~/.bashrc

echo "4. 为 go 语言配置国内代理，并开启 mod 模式"
go env -w GOPROXY=https://goproxy.cn,direct
go env -w GOPRIVATE=$PRIVATE_GIT_HOST
go env -w GO111MODULE=on


echo "5. 为 git 生成 ssh 密钥"
cat /dev/zero | ssh-keygen -q -N ""
echo "6. 生成完毕，请将以下公钥内容拷贝到 git 中，使 git 可以通过私钥拉取代码："
cat ~/.ssh/id_rsa.pub
