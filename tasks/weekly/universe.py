from managers.screen_manager import screen
from managers.config_manager import config
from managers.logger_manager import logger
from managers.automation_manager import auto
from managers.translate_manager import _
from tasks.base.base import Base
from tasks.base.pythonchecker import PythonChecker
from tasks.base.runsubprocess import RunSubprocess


class Universe:
    @staticmethod
    def start(get_reward=False):
        logger.hr(_("准备模拟宇宙"), 2)

        if PythonChecker.check():
            screen.change_to('universe_main')
            screen.change_to('main')

            logger.info(_("开始安装依赖"))
            if RunSubprocess.run(f"cd {config.universe_path} && pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt", 3600):
                logger.info(_("开始校准"))
                if RunSubprocess.run(f"cd {config.universe_path} && python align_angle.py", 60):
                    logger.info(_("开始模拟宇宙"))
                    if RunSubprocess.run(f"cd {config.universe_path} && python states.py" + (" --bonus=1" if config.universe_bonus_enable else ""), config.universe_timeout * 3600):
                        config.save_timestamp("universe_timestamp")
                        if get_reward:
                            Universe.get_reward()
                        else:
                            Base.send_notification_with_screenshot(_("🎉模拟宇宙已完成🎉"))
                        return
                    else:
                        logger.info(_("模拟宇宙失败"))
                else:
                    logger.info(_("校准失败"))
            else:
                logger.info(_("依赖安装失败"))
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
