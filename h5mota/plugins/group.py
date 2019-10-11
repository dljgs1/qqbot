from nonebot import on_request, RequestSession

# 539113091
groups_info = {
    "539113091": {
        "new": [
            {
                "type": "text",
                "data": {"text": "欢迎新群友"}
            },
            {
                "type": "at",
                "data": {"qq": 0}
            },
            {
                "type": "text",
                "data": {
                    "text": " ，我是H5魔塔小助手ver0.2，向我发送【帮助】获取更多命令。如果是新手，建议先玩教程塔熟悉规则；如果有一定经验，可以到蓝绿区潇洒游玩；如果是大佬，来红橙区拆爆吧！记住我们的网址 h5mota.com  到上面搜索塔名就可以找到想找的塔啦！"}
            }
        ],
        "out": [
            {
                "type": "text",
                "data": {"text": ""}
            },
            {
                "type": "text",
                "data": {"text": "跑路了！"}
            }
        ],
    }
}

uid_buff = {

}
groups_member_info = []
import json

try:
    with open('group_info.txt', "r") as f:
        groups_member_info = json.load(f)
except:
    pass
lock = False


def send_check(uid):
    global lock
    while lock:
        pass
    lock = True
    uid = str(uid)
    print(uid, uid_buff)
    if uid not in uid_buff:
        uid_buff[uid] = time.time()
    elif time.time() - uid_buff[uid] < 20:
        lock = False
        return False
    uid_buff[uid] = time.time()
    lock = False
    return True


import time
from nonebot import on_notice, NoticeSession, on_request, RequestSession


@on_notice('group_increase')
async def _(session: NoticeSession):
    # 发送欢迎消息
    global groups_member_info
    print("test", session.ctx)
    gid = str(session.ctx['group_id'])
    if gid not in groups_info:
        return
    msg = groups_info[gid]["new"]
    uid = session.ctx["user_id"]
    groups_member_info = await session.bot.get_group_member_list(
        group_id="539113091"
    )
    if send_check(uid):
        msg[1]["data"]["qq"] = int(uid)
        await session.send(msg)
        print("send success")
        return
    print("error check")


import nonebot


@on_notice('group_decrease')
async def _(session: NoticeSession):
    # 跑路
    print("test", session.ctx)
    gid = str(session.ctx['group_id'])
    if gid not in groups_info:
        return
    msg = groups_info[gid]["out"]
    uid = session.ctx["user_id"]
    name = ''
    bot = nonebot.get_bot()
    try:
        info = [it for it in groups_member_info if str(it["user_id"]) == str(uid)][0]
        name = info['card'] or info['nickname']
    except:
        print("get member info error")
    if send_check(uid):
        msg[0]["data"]["text"] = str(name) + '(' + str(uid) + ')'
        await session.send(msg)
        print("send success")
        return
    print("error check")


from nonebot import on_command, CommandSession


@on_command('网址', aliases=('网址'))
async def address(session: CommandSession):
    uid = session.ctx["user_id"]
    if send_check(uid):
        # city = session.get('city', prompt='你想查询哪个城市的天气呢？')
        # session.pause('mota.pw')
        # weather_report = await get_weather_of_city(city)
        try:
            await session.send("h5mota.com", ignore_failure=False)
        except:
            print("send error!")
    print("error check")


@on_command('管理员', aliases=('管理员'))
async def address(session: CommandSession):
    global groups_member_info
    uid = session.ctx["user_id"]
    if int(uid) == 906348668:
        groups_member_info = await session.bot.get_group_member_list(
            group_id="539113091"
        )
        import json
        with open('group_info.txt', "w") as f:
            f.write(json.dumps(groups_member_info))
        try:
            await session.send("更新成员信息成功！", ignore_failure=False)
        except:
            print("send error!")
    print("error check")


@on_command('group', aliases=('group'))
async def address(session: CommandSession):
    qq = session.get('recommend', prompt='input qq number\n')
    for info in groups_member_info:
        if str(info['user_id']) == str(qq):
            await session.send((info['card'] or info['nickname'])+" "+str(info), ignore_failure=True)
