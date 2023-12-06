# AliYunDDNSForRouterOS
一个自动更新阿里云DNS记录的Python脚本，实现了Docker部署，用于RouterOS环境下的动态域名解析，支持IPv4和IPv6，兼容多线路解析。

## 项目介绍
这个项目提供了一个 Python 脚本，用于更新阿里云的 DNS 记录以实现动态域名解析（DDNS）。该项目适用于 RouterOS 7 环境，并支持多域名解析、IPv4 和 IPv6 地址解析，以及根据不同线路进行域名解析。

## 主要特性
- 兼容 RouterOS 7 环境。
- 支持多域名解析。
- 每个域名可以根据不同线路（如电信、联通等）进行解析。
- 同时支持 IPv4 和 IPv6 地址的解析。

## 配置文件说明
配置文件 `config.json` 控制了脚本的行为和所需的凭据。以下是配置文件的结构和每个字段的解释：

```json
{
    "update_interval": 300,  // 更新间隔（秒）
    "RouterOS": {
        "API_URL": "<RouterOS_API_URL>",  // RouterOS API URL， 例如http://192.168.88.1
        "User_Name": "<RouterOS_Username>",  // RouterOS 用户名
        "Password": "<RouterOS_Password>"  // RouterOS 密码
    },
    "AliYun": {
        "Access_Key_ID": "<Your_Aliyun_Access_Key_ID>",  // 阿里云Access Key ID
        "Access_Key_Secret": "<Your_Aliyun_Access_Key_Secret>",  // 阿里云Access Key Secret
        "region_id": "cn-hangzhou"  // 阿里云区域ID
    },
    "Domains": [  // 要更新的域名列表
        {
            "Domain_Name": "example.com",  // 域名
            "Sub_Domain_Name": "subdomain",  // 子域名
            "Record": [  // DNS记录配置
                {
                    "Type": "A",  // 记录类型，A或AAAA
                    "Line": "default",  // 解析线路
                    "RouterOS_Interface": "PPPOETelecom",  // RouterOS接口名称
                    "TTL": 600  // DNS记录生存时间
                },
                // 可以添加更多记录配置
            ]
        }
        // 可以添加更多域名配置
    ]
}
```

请在实际使用中替换 <RouterOS_API_URL>, <RouterOS_Username>, <RouterOS_Password>, <Your_Aliyun_Access_Key_ID>, <Your_Aliyun_Access_Key_Secret> 等占位符为您的实际配置信息。

## 如何使用
克隆或下载此仓库。
根据您的环境修改 config.json 配置文件。
安装所需依赖：pip install -r requirements.txt。
运行脚本：python aliyunDDNSForRouterOS.py。
## Docker 支持
如果您的环境中安装了 Docker，您可以使用 Dockerfile 来构建和运行 Docker 容器。

## 构建 Docker 镜像
docker build -t aliyunddns .

## 运行 Docker 容器
docker run -d --name aliyunddns_container -v /path/to/your/config:/config aliyunddns

## 许可
此项目在 MIT 许可下发布。

## 请确保替换配置文件中的占位符为您的实际信息，并在实际部署之前进行充分的测试。
