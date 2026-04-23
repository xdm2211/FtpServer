import csv
import io
import logging
import os
import Settings
import myUtils

logger = logging.getLogger("ftpserver")


PERM_READ_ONLY: str = "elr"
PERM_READ_WRITE: str = "elradfmwMT"


class UserConfig:
    def __init__(self, userName: str, password: str, perm: str, path: str) -> None:
        self.userName = userName
        self.password = password
        self.perm = perm
        self.path = path


def permTranslate(perm: str) -> str:
    if perm == PERM_READ_ONLY:
        return "只读"
    elif perm == PERM_READ_WRITE:
        return "读写"
    else:
        return perm


def permConvert(permInput: str) -> str:
    """
    Link: https://pyftpdlib.readthedocs.io/en/latest/api.html#pyftpdlib.authorizers.DummyAuthorizer.add_user
    读取权限：
    - "e" = 更改目录 (CWD 命令)
    - "l" = 列出文件 (LIST、NLST、STAT、MLSD、MLST、SIZE、MDTM 命令)
    - "r" = 从服务器检索文件 (RETR 命令)

    写入权限：
    - "a" = 将数据附加到现有文件 (APPE 命令)
    - "d" = 删除文件或目录 (DELE、RMD 命令)
    - "f" = 重命名文件或目录 (RNFR、RNTO 命令)
    - "m" = 创建目录 (MKD 命令)
    - "w" = 将文件存储到服务器 (STOR、STOU 命令)
    - "M" = 更改文件模式 (SITE CHMOD 命令)
    - "T" = 更新文件上次修改时间 (MFMT 命令)
    """

    if permInput.lower() == "readonly" or permInput == "只读":
        return PERM_READ_ONLY
    elif permInput.lower() == "readwrite" or permInput == "读写":
        return PERM_READ_WRITE
    else:
        charSet = {c for c in permInput if c in PERM_READ_WRITE}
        if len(charSet) == 0:
            return PERM_READ_ONLY
        else:
            return "".join(c for c in PERM_READ_WRITE if c in charSet)


class UserList:
    def __init__(self) -> None:
        self.appDirectory = myUtils.getAppDirectory()
        self.userListCsvPath = os.path.join(self.appDirectory, "FtpServerUserList.csv")
        self.userList: list[UserConfig] = list[UserConfig]()
        self.userNameSet: set[str] = set[str]()
        self.load()

    def readFileContent(self) -> str:
        for encoding in ['utf-8-sig', 'gbk']:
            try:
                with open(self.userListCsvPath, 'r', encoding=encoding) as file:
                    content = file.read()
                return content
            except (UnicodeDecodeError, ValueError):
                continue
        logger.warning(f"无法使用UTF-8或GBK编码读取文件 {self.userListCsvPath}")
        return ""

    def validateRow(self, row: list[str], lineNum: int, rawLine: str) -> UserConfig | None:
        if len(row) < 4:
            logger.warning(f"第{lineNum}行 解析错误(列数不足) [{rawLine}]")
            return None

        userName = row[0].strip()
        password = row[1].strip()
        permInput = row[2].strip()
        rootPath = row[3].strip()

        if not userName or not password or not rootPath:
            if userName and not password and userName != "anonymous":
                logger.warning(f"第{lineNum}行 该用户名条目 [{userName}] 没有密码"
                      f"(只有匿名用户 anonymous 可以不设密码)，已跳过此内容 [{rawLine}]")
                return None
            if not userName or not rootPath:
                logger.warning(f"第{lineNum}行 解析错误(用户名或路径为空) [{rawLine}]")
                return None

        if userName in self.userNameSet:
            logger.warning(f"第{lineNum}行 发现重复的用户名条目 [{userName}], 已跳过此内容 [{rawLine}]")
            return None

        if not os.path.exists(rootPath):
            logger.warning(f"第{lineNum}行 该用户名条目 [{userName}] 的路径不存在或无访问权限 [{rootPath}] 已跳过此内容 [{rawLine}]")
            return None

        if userName != "anonymous" and not password:
            logger.warning(f"第{lineNum}行 该用户名条目 [{userName}] 没有密码"
                  f"(只有匿名用户 anonymous 可以不设密码)，已跳过此内容 [{rawLine}]")
            return None

        return UserConfig(
            userName,
            Settings.Settings.encry2sha256(password),
            permConvert(permInput),
            rootPath,
        )

    def load(self):
        self.userList.clear()
        self.userNameSet.clear()

        if not os.path.exists(self.userListCsvPath):
            return

        try:
            content = self.readFileContent()
            if not content or len(content.strip()) == 0:
                return

            reader = csv.reader(io.StringIO(content))
            for lineNum, row in enumerate(reader, start=1):
                if not row or all(cell.strip() == "" for cell in row):
                    continue
                rawLine = ",".join(row)
                node = self.validateRow(row, lineNum, rawLine)
                if node is not None:
                    self.userNameSet.add(node.userName)
                    self.userList.append(node)

        except Exception as e:
            logger.error(f"用户列表文件读取异常: {self.userListCsvPath}\n{e}")
            return

    def printUserList(self):
        if len(self.userList) == 0:
            logger.info("用户列表空白")
        else:
            logger.info(f"主页面的用户/密码/权限/根路径将会忽略，现将使用以下{len(self.userList)}条用户配置:")
            for userItem in self.userList:
                logger.info(
                    f"[{userItem.userName}] [******] [{permTranslate(userItem.perm)}] [{userItem.path}]"
                )

    def isEmpty(self) -> bool:
        return len(self.userList) == 0
