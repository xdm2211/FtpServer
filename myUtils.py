import base64
import io
import os
import sys
from PIL import Image, ImageTk

tipsTitle: str = "若用户名空白则默认匿名访问(anonymous)。若中文乱码则需更换编码方式, 再重启服务。若无需开启IPv6只需将其端口留空即可, IPv4同理。请设置完后再开启服务。若需FTPS或多用户配置, 请点击“帮助”按钮查看使用说明。以下为本机所有IP地址(含所有物理网卡/虚拟网卡), 右键可复制。\n"

helpTips: str = r"""以下是 安全加密连接FTPS 和 多用户配置 说明, 普通用户一般不需要。

==== FTPS 配置 ====

本软件默认使用 FTP 明文传输数据，如果数据比较敏感，或者网络环境不安全，则可以按以下步骤启用 FTPS 加密传输数据。

只需生成TLS/SSL证书文件即可启用 "FTPS [TLS/SSL显式加密, TLSv1.3]"，以下两种方式均可:

1. 在 "托盘图标" 右键菜单中选择 "生成 FTPS TLS/SSL 证书"。

2. 在 "Linux" 或 "MinGW64" 终端使用 "openssl" 命令生成TLS/SSL证书文件("ftpServer.key" 和 "ftpServer.crt")，"不要重命名" 文件为其他名称，直接将 "ftpServer.key" 和 "ftpServer.crt" 放到程序所在目录，开启服务时若存在这两个文件，则启用加密传输 。

  openssl req -x509 -newkey rsa:2048 -keyout ftpServer.key -out ftpServer.crt -nodes -days 3653

Windows文件管理器对 "显式FTPS" 支持不佳，推荐使用开源客户端软件 [WinSCP](https://winscp.net/eng/index.php)，对 FTPS 支持比较好。启用 FTPS 加密传输后，会 "影响传输性能"，最大传输速度会降到 "50MiB/s" 左右。若对网络安全没那么高要求，不建议加密。


==== 多用户配置 ====

一般单人使用时，只需在软件主页面设置用户名和密码即可。如果需要开放给多人使用，可以按以下步骤建立多个用户，分配不同的读写权限和根目录。

在主程序所在目录新建文件 "FtpServerUserList.csv" , 使用 "Excel"或文本编辑器(需熟悉csv文件格式)编辑, 一行一个配置: 
第一列: 用户名, 限定英文大小写/数字。
第二列: 密码, 限定英文大小写/数字/符号。
第三列: 权限, 详细配置如下。
第四列: 根目录路径。

例如:
| JARK006   | 123456 | readonly  | D:/Downloads |
| JARK007   | 456789 | readwrite | D:/Data      |
| JARK008   | abc123 | 只读      | D:/FtpRoot   |
| JARK009   | abc456 | elr       | D:/FtpRoot   |
| anonymous |        | elr       | D:/FtpRoot   |
| ...       |        |           |              |
注: anonymous 是匿名用户, 允许不设密码, 其他用户必须设置密码。

权限配置: 
使用 "readonly" 或 "只读" 设置为 "只读权限"。
使用 "readwrite" 或 "读写" 设置为 "读写权限"。
使用 "自定义" 权限设置, 从以下权限挑选自行组合(注意大小写)。

参考链接: https://pyftpdlib.readthedocs.io/en/latest/api.html#pyftpdlib.authorizers.DummyAuthorizer.add_user

读取权限: 
 "e" = 更改目录 (CWD 命令)
 "l" = 列出文件 (LIST、NLST、STAT、MLSD、MLST、SIZE、MDTM 命令)
 "r" = 从服务器检索文件 (RETR 命令)

写入权限: 
 "a" = 将数据附加到现有文件 (APPE 命令)
 "d" = 删除文件或目录 (DELE、RMD 命令)
 "f" = 重命名文件或目录 (RNFR、RNTO 命令)
 "m" = 创建目录 (MKD 命令)
 "w" = 将文件存储到服务器 (STOR、STOU 命令)
 "M" = 更改文件模式 (SITE CHMOD 命令)
 "T" = 更新文件上次修改时间 (MFMT 命令)

其他:
1. 若读取到有效配置, 则自动 "禁用"主页面的用户/密码设置。
2. 密码不要出现英文逗号 "," 字符, 以免和csv文本格式冲突。
3. 若临时不需多用户配置, 可将配置文件 "删除" 或 "重命名" 为其他名称。
4. 配置文件可以是UTF-8或GBK编码。
"""

def getAppDirectory() -> str:
    appDirectory = str(os.path.dirname(os.path.abspath(sys.argv[0]))).replace("\\", "/")
    if (
        len(appDirectory) > 2
        and appDirectory[0].islower()
        and appDirectory[1] == ":"
    ):
        appDirectory = appDirectory[0].upper() + appDirectory[1:]
    return appDirectory


class IconObj():
    """
    import base64
    with open(r"ico64x64.ico", "rb") as f:
        iconBase64Str = base64.b64encode(f.read())
        print(iconBase64Str)
    """
    
    def __init__(self):
        iconBase64Str = b"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"
        iconBytes = base64.b64decode(iconBase64Str)

        self.iconImageTk = ImageTk.PhotoImage(data=iconBytes)
        self.strayIconImage = Image.open(io.BytesIO(iconBytes))
