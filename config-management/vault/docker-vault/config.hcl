ui = true

// 使用文件做数据存储（单节点）
storage "file" {
  path    = "/vault/file"
}

listener "tcp" {
  address = "[::]:8200"

  tls_disable = false
  tls_cert_file = "/certs/server.crt"
  tls_key_file  = "/certs/server.key"
}
