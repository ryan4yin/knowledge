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

resource "proxmox_vm_qemu" "vm" {
  name = "<vm-name>"
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
  nameserver = "xxx.xxx.xxx.xxx"
  ipconfig0 = "ip=xxx.xxx.xxx.xxx/24,gw=xxx.xxx.xxx.xxx"
  # 通过 cloud-init 设置初始账号
  ciuser = "root"
  # 为 root 账号设置 ssh 公钥
  sshkeys = file("${path.module}/base-rsa.pub")
}
