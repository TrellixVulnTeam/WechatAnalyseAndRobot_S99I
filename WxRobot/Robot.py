from wxpy import *
from WxRobot import Load
from WxRobot import Reply
from WxRobot import Commod


def RunRobot(bot,queue):
    # bot = Bot(cache_path=True)
    # 加载配置信息到机器人
    Load.loadConfig(bot)

    """好友功能"""

    @bot.register(msg_types=FRIENDS)
    def auto_accept_friends(msg):
        """自动接受好友请求"""
        Reply.autoAcceptFriends(msg)

    @bot.register(chats=Friend)
    def friend_msg(msg):
        """接收好友消息"""
        if not msg.bot.is_friend_auto_reply:
            return None
        if msg.type == TEXT:
            Reply.autoReply(msg)
            return None
        elif msg.type == RECORDING:
            return '不听不听，王八念经'
        elif msg.type == PICTURE:
            return '这图片很棒，但下一秒就是我的了'
        else:
            pass

    """群功能"""

    @bot.register(chats=Group)
    def group_msg(msg):
        """接收群消息"""
        # 群@转发功能
        if msg.is_at and msg.bot.is_forward_group_at_msg:
            msg.forward(msg.bot.master, prefix='「{0}」在群「{1}」中艾特了你：'.format(msg.member.name, msg.chat.name))

        if msg.type == TEXT:
            # 群回复
            if msg.bot.is_group_reply:
                if msg.bot.is_group_at_reply:
                    # @机器人才回复
                    if msg.is_at:
                        Reply.autoReply(msg)
                else:
                    # 不用@直接回复
                    Reply.autoReply(msg)
        elif msg.type == SHARING and msg.bot.is_listen_sharing and msg.chat in msg.bot.listen_sharing_groups:
            # 群分享转发监控，防止分享广告
            msg.forward(msg.bot.master, prefix='分享监控：「{0}」在「{1}」分享了：'.format(msg.member.name, msg.chat.name))
        else:
            pass
        # 监听好友群聊，如老板讲话
        if msg.bot.is_listen_friend and msg.chat in msg.bot.listen_friend_groups and msg.member.is_friend in msg.bot.listen_friends:
            msg.forward(msg.bot.master, prefix='监听指定好友群消息：「{0}」在「{1}」发了消息：'.format(
                msg.member.is_friend.remark_name or msg.member.nick_name, msg.chat.name))
        return None

    @bot.register(msg_types=NOTE)
    def system_msg(msg):
        """接收系统消息"""
        Reply.handleSystemMsg(msg)

    """管理员功能"""
    @bot.register(chats=bot.master)
    def do_command(msg):
        """执行管理员命令"""
        content = msg.text
        sender = str(msg.sender)
        queuemsg=['管理员',sender+'发送来：\n'+content+'\n\n']
        queue.put(queuemsg)
        queue.join()
        returnstr=Commod.doCommand(msg)

    # 堵塞进程，直到结束消息监听 (例如，机器人被登出时)
    # embed() 互交模式阻塞，电脑休眠或关闭互交窗口则退出程序
    bot.join()


