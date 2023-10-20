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
        elif not os.path.exists(os.path.join(config.universe_path, 'gui.exe')):
            logger.error(_("模拟宇宙缺失核心文件，请尝试更新"))
            return False
        # 日常任务需要能够自定义次数的模拟宇宙版本，检测是否存在 nums 参数
        with open(os.path.join(config.universe_path, 'states.py'), 'r', encoding='utf-8') as f:
            if "nums" not in f.read():
                logger.warning(_("模拟宇宙版本过低"))
                Universe.update()
        return True

    @staticmethod
    def check_requirements():
        if not config.universe_requirements:
            logger.info(_("开始安装依赖"))
            from tasks.base.fastest_mirror import FastestMirror
            subprocess.run([config.python_exe_path, "-m", "pip", "install", "-i", FastestMirror.get_pypi_mirror(), "pip", "--upgrade"])
            while not subprocess.run([config.python_exe_path, "-m", "pip", "install", "-i", FastestMirror.get_pypi_mirror(), "-r", "requirements.txt"], check=True, cwd=config.universe_path):
                logger.error(_("依赖安装失败"))
                input(_("按回车键重试. . ."))
            logger.info(_("依赖安装成功"))
            config.set_value("universe_requirements", True)

    @staticmethod
    def before_start():
        check_result = True
        PythonChecker.run()
        check_result &= Universe.check_path()
        Universe.check_requirements()
        return check_result

    @staticmethod
    def start(get_reward=False, nums=None, save=True):
        logger.hr(_("准备模拟宇宙"), 2)
        if Universe.before_start():

            screen.change_to('main')

            logger.info(_("开始校准"))
            if subprocess_with_timeout([config.python_exe_path, "align_angle.py"], 60, config.universe_path, config.env):

                screen.change_to('universe_main')

                logger.info(_("开始模拟宇宙"))
                command = [config.python_exe_path, "states.py"]
                if config.universe_bonus_enable:
                    command.append("--bonus=1")
                if nums:
                    command.append(f"--nums={nums}")
                if subprocess_with_timeout(command, config.universe_timeout * 3600, config.universe_path, config.env):

                    screen.change_to('main')
                    if save:
                        config.save_timestamp("universe_timestamp")
                    if get_reward:
                        Universe.get_reward()
                    else:
                        Base.send_notification_with_screenshot(_("🎉模拟宇宙已完成🎉"))
                    return True

                else:
                    logger.error(_("模拟宇宙失败"))
            else:
                logger.error(_("校准失败"))
        Base.send_notification_with_screenshot(_("⚠️模拟宇宙未完成⚠️"))
        return False

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
            if subprocess.run(["start", "gui.exe"], shell=True, check=True, cwd=config.universe_path, env=config.env):
                return True
        return False
