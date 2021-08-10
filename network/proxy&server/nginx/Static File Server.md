# 静态文件服务器

Nginx 原生就支持静态文件服务，可用做文件服务器。

但是默认情况下 Nginx 不会提供文件夹索引(AutoIndex)，这项功能需要通过配置文件开启：

```conf
location /images/ {
    # 自动根据文件列表，生成 index
    autoindex on;
}
```

如果你还希望支持文件上传、删除等功能，那显然使用专用的文件共享工具是更好的方案，详见 [/datastore/file-sharing](/datastore/file-sharing/README.md)

