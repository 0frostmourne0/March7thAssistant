from managers.screen_manager import screen
from managers.automation_manager import auto
from managers.logger_manager import logger
from managers.translate_manager import _
from managers.notify_manager import notify
from managers.config_manager import config
import time


class SRPass:
    @staticmethod
    def get_reward():
        screen.change_to('menu')
        if auto.find_element("./assets/images/menu/pass_reward.png", "image", 0.95):
            # if True:
            logger.hr(_("检测到无名勋礼奖励"), 2)
            screen.change_to('pass1')
            if config.srpass_enable:
                if auto.click_element("./assets/images/pass/one_key_receive.png", "image", 0.9):
                    auto.click_element("./assets/images/base/click_close.png", "image", 0.9, max_retries=10)
            if auto.find_element("./assets/images/pass/50.png", "image", 0.9):
                logger.info("🎉当前版本无名勋礼已满级🎉")
                notify.notify("🎉当前版本无名勋礼已满级🎉")
            if auto.find_element("./assets/images/pass/pass_reward.png", "image", 0.9):
                screen.change_to('pass2')
                auto.click_element("./assets/images/pass/one_key_receive.png", "image", 0.9)
                time.sleep(2)
                # if auto.click_element("./assets/images/pass/one_key_receive.png", "image", 0.9):
                #     auto.click_element("./assets/images/base/click_close.png", "image", 0.9, max_retries=10)
            logger.info(_("领取无名勋礼奖励完成"))
        else:
            logger.info(_("未检测到无名勋礼奖励"))
