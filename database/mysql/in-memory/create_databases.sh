#!/bin/bash
set -e

# 建数据库示例
mysql --user=root --password=$MYSQL_ROOT_PASSWORD \
    -e "create database if not exists XXX default character set utf8mb4 collate utf8mb4_unicode_ci;"
