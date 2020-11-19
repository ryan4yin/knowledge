# =============== 版本依赖 ========================
terraform {
  required_providers {
    proxmox = {
      source = "Telmate/proxmox"
      version = "2.6.5"
    }
  }
  required_version = ">= 0.13"
}

provider "proxmox" {
    pm_api_url = "https://<server-host>:8006/api2/json"
    pm_user = "root@pam"
    pm_tls_insecure = true
    # 通过环境变量 PAM_PASSWORD 设置密码
}

# =============== 变量定义 ========================

variable "vm_name" {
  type = string
}

variable "vm_ip" {
  type = string
}

variable "vm_gateway" {
  type = string
}


# =============== 虚拟机定义 ========================

resource "proxmox_vm_qemu" "vm" {
  name = var.vm_name
  desc = "a new vm cloned from centos7-template"
  target_node = "xxx"

  clone = "centos7-template"
  full_clone = true

  # 资源池
  pool = "xxx"

  cores = 4
  sockets = 2
  memory = 10240
  onboot = true
  agent = 1

  disk {
    id = 0
    type = "scsi"
    storage = "local-lvm"
    size = "32G"  # 扩容到 32G
  }

  network {
    id = 0
    model = "virtio"
    bridge = "vmbr0"
  }

  os_type = "cloud-init"
  nameserver = "114.114.114.114,119.29.29.29"
  ipconfig0 = "ip=${var.vm_ip}/24,gw=${var.vm_gateway}"
  # 通过 cloud-init 设置初始账号
  ciuser = "root"
  # 为 root 账号设置 ssh 公钥
  sshkeys = file("${path.module}/base-rsa.pub")

  # 在虚拟机启动后，通过一些命令进行 VM 预配置
  connection {
    type = "ssh"
    user = self.ciuser
    private_key = data.local_file.privatekey.content
    host = var.vm_ip
    port = "22"
  }
  provisioner "remote-exec" {
    inline = [
      # 关闭 SSH 的反向 DNS 解析，加快连接速度
      "echo 'UseDNS no' >> /etc/ssh/sshd_config",
    ]
  }
}
