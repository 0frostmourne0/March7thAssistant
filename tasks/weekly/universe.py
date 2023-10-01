from managers.screen_manager import screen
from managers.config_manager import config
from managers.logger_manager import logger
from managers.automation_manager import auto
from managers.translate_manager import _
from tasks.base.base import Base
from tasks.base.pythonchecker import PythonChecker
from tasks.base.command import subprocess_with_timeout
import subprocess
import os


class Universe:

    @staticmethod
    def update():
        config.set_value("universe_requirements", False)
        from module.update.update_handler import UpdateHandler
        from tasks.base.fastest_mirror import FastestMirror
        url = FastestMirror.get_github_mirror("https://github.com/CHNZYX/Auto_Simulated_Universe/archive/main.zip")
        update_handler = UpdateHandler(url, config.universe_path, "Auto_Simulated_Universe-main")
        update_handler.run()

    @staticmethod
    def check_path():
        if not os.path.exists(config.universe_path):
            logger.warning(_("模拟宇宙路径不存在: {path}").format(path=config.universe_path))
            Universe.update()

    @staticmethod
    def check_requirements():
        if not config.universe_requirements:
            logger.info(_("开始安装依赖"))
            from tasks.base.fastest_mirror import FastestMirror
            while not subprocess.run(["pip", "install", "-i", FastestMirror.get_pypi_mirror(), "-r", "requirements.txt"], check=True, cwd=config.universe_path):
                logger.error(_("依赖安装失败"))
                input(_("按任意键重试. . ."))
            logger.info(_("依赖安装成功"))
            config.set_value("universe_requirements", True)

    @staticmethod
    def before_start():
        PythonChecker.run()
        Universe.check_path()
        Universe.check_requirements()
        return True

    @staticmethod
    def start(get_reward=False):
        logger.hr(_("准备模拟宇宙"), 2)

        if Universe.before_start():

            screen.change_to('universe_main')
            screen.change_to('main')

            logger.info(_("开始校准"))
            if subprocess_with_timeout(["python", "align_angle.py"], 60, config.universe_path):
                logger.info(_("开始模拟宇宙"))
                command = ["python", "states.py"]
                if config.universe_bonus_enable:
                    command.append("--bonus=1")
                if subprocess_with_timeout(command, config.universe_timeout * 3600, config.universe_path):
                    config.save_timestamp("universe_timestamp")
                    if get_reward:
                        Universe.get_reward()
                    else:
                        Base.send_notification_with_screenshot(_("🎉模拟宇宙已完成🎉"))
                    return
                else:
                    logger.error(_("模拟宇宙失败"))
            else:
                logger.error(_("校准失败"))
        Base.send_notification_with_screenshot(_("⚠️模拟宇宙未完成⚠️"))

    @staticmethod
    def get_reward():
        logger.info(_("开始领取奖励"))
        screen.change_to('universe_main')
        if auto.click_element("./assets/images/universe/universe_reward.png", "image", 0.9):
            if auto.click_element("./assets/images/universe/one_key_receive.png", "image", 0.9, max_retries=10):
                if auto.find_element("./assets/images/base/click_close.png", "image", 0.9, max_retries=10):
                    Base.send_notification_with_screenshot(_("🎉模拟宇宙奖励已领取🎉"))
                    auto.click_element("./assets/images/base/click_close.png", "image", 0.9, max_retries=10)

    @staticmethod
    def gui():
        if Universe.before_start():
            if subprocess.run(f"cd {config.universe_path} && start gui.exe", shell=True, check=True):
                return True
        return False
