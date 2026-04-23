import os
import sys
import json
import hashlib
import logging
import myUtils
from typing import Any

logger = logging.getLogger("ftpserver")

class Settings:
    encryPasswordPrefix = "ENCRY"
    defaultUserName = "JARK006"
    defaultUserPassword = "123456"

    def __init__(self) -> None:
        self.appDirectory = myUtils.getAppDirectory()

        self.savePath = os.path.join(self.appDirectory, "ftpServer.json")

        self.directoryList: list[str] = [self.appDirectory]
        self.userName: str = Settings.defaultUserName
        self.userPassword: str = self.encry2sha256(Settings.defaultUserPassword)
        self.IPv4Port: int = 21
        self.IPv6Port: int = 0
        self.isGBK: bool = True
        self.isReadOnly: bool = True
        self.isAutoStartServer: bool = False
        self.load()

    @staticmethod
    def encry2sha256(input_string: str) -> str:
        if len(input_string) == 0:
            return ""

        salt = "JARK006_FTP_SERVER_SALT"
        sha256_hash = hashlib.sha256()
        sha256_hash.update((input_string + salt).encode("utf-8"))
        return Settings.encryPasswordPrefix + sha256_hash.hexdigest().upper()

    def load(self):
        if not os.path.exists(self.savePath):
            return

        try:
            with open(self.savePath, "r", encoding="utf-8") as file:
                variables = json.load(file)

            self.directoryList = variables.get("directoryList", [self.appDirectory])
            self.userName = variables.get("userName", Settings.defaultUserName)
            self.userPassword = variables.get("userPassword", self.encry2sha256(Settings.defaultUserPassword))
            self.IPv4Port = variables.get("IPv4Port", 21)
            self.IPv6Port = variables.get("IPv6Port", 0)
            self.isGBK = variables.get("isGBK", True)
            self.isReadOnly = variables.get("isReadOnly", True)
            self.isAutoStartServer = variables.get("isAutoStartServer", False)

            # 检查变量类型
            if not isinstance(self.directoryList, list):
                self.directoryList = [self.appDirectory]
                logger.warning(f"directoryList 类型错误，已恢复默认：[{self.appDirectory}]")
            else:
                self.directoryList = [d for d in self.directoryList if isinstance(d, str) and d]
                if not self.directoryList:
                    self.directoryList = [self.appDirectory]
                    logger.warning(f"directoryList 无有效条目，已恢复默认：[{self.appDirectory}]")
            if not isinstance(self.userName, str):
                self.userName = Settings.defaultUserName
                logger.warning(f"userName 类型错误，已恢复默认：{self.userName}")
            if not isinstance(self.userPassword, str):
                self.userPassword = self.encry2sha256(Settings.defaultUserPassword)
                logger.warning(f"userPassword 类型错误，已恢复默认：{self.userPassword}")
            if not isinstance(self.IPv4Port, int):
                self.IPv4Port = 21
                logger.warning(f"IPv4Port 类型错误，已恢复默认：{self.IPv4Port}")
            if not isinstance(self.IPv6Port, int):
                self.IPv6Port = 0
                logger.warning(f"IPv6Port 类型错误，已恢复默认：{self.IPv6Port}")
            if not isinstance(self.isGBK, bool):
                self.isGBK = True
                logger.warning(f"isGBK 类型错误，已恢复默认：{self.isGBK}")
            if not isinstance(self.isReadOnly, bool):
                self.isReadOnly = True
                logger.warning(f"isReadOnly 类型错误，已恢复默认：{self.isReadOnly}")
            if not isinstance(self.isAutoStartServer, bool):
                self.isAutoStartServer = False
                logger.warning(f"isAutoStartServer 类型错误，已恢复默认：{self.isAutoStartServer}")

        except Exception as e:
            logger.error(f"设置文件读取异常: {self.savePath}\n{e}")
            return

    def save(self):
        """保存前确保调用 updateSettingVars() 或其他函数进行参数检查"""

        self.directoryList = self.directoryList[:20]

        variables: dict[str, Any] = {
            "directoryList": self.directoryList,
            "userName": self.userName,
            "userPassword": self.userPassword,
            "IPv4Port": self.IPv4Port,
            "IPv6Port": self.IPv6Port,
            "isGBK": self.isGBK,
            "isReadOnly": self.isReadOnly,
            "isAutoStartServer": self.isAutoStartServer,
        }
        try:
            with open(self.savePath, "w", encoding="utf-8") as file:
                json.dump(variables, file, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"设置文件保存异常: {self.savePath}\n{e}")
            return
