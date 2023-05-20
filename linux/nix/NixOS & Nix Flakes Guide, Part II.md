

## Nix Modules System


- [Nix modules: Improving Nix's discoverability and usability ](https://cfp.nixcon.org/nixcon2020/talk/K89WJY/)


## devenv

[numtide/devshell](https://github.com/numtide/devshell) seems to be a personal project, and not documented well.

[cachix/devenv](https://github.com/cachix/devenv) has rich documentation, and the project is very active, so I decided to give it a try.


## disk encryption

Physicial disk may borked, and you need to repair it by send it back to the manufacturer. In this case, you may have some sensitive data on it and you would suffer from data leakage, because the manufacturer may not be trusted, and they can read data directly from the disk.

so the best way to protect your data is to encrypt the disk all the time, you can encrypt the disk with a password to protect your data.

https://gist.github.com/ladinu/bfebdd90a5afd45dec811296016b2a3f

https://www.reddit.com/r/NixOS/comments/xrgszw/nixos_full_disk_encryption_with_tpm_and_secure/