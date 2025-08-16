# curl

```bash
# curl with socks5 proxy (resolve dns remotely, not locally)
curl --max-time 10 --socks5-hostname ip:port http://example.com


# curl - try to send https request to 11.22.33.44:443 with sni example.com
curl -v --resolve 'example.com:443:34.117.167.49' https://example.com:443/xxx
```

# grpc curl

> https://github.com/fullstorydev/grpcurl

TODO


