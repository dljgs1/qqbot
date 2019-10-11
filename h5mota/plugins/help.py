
from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand

help_text = "1. 发送【推荐】，获取魔塔推荐\n 2. 发送【详情】+魔塔名，获取魔塔的详细信息（开发中）。\n 3. 发送【帮助】获取命令说明。 \n 4. 发送【教程塔】获取新人专属塔链接！"


@on_natural_language(keywords={'帮助'})
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    return IntentCommand(90.0, '帮助', current_arg='')

@on_command('帮助', aliases=('帮助'))
async def address(session: CommandSession):
    try:
        await session.send("命令说明：\n"+help_text, ignore_failure=False)
    except:
        print("send error!")

@on_command('教程塔', aliases=('教程'))
async def address(session: CommandSession):
    try:
        await session.send("教程塔地址： https://h5mota.com/games/tutorial/", ignore_failure=False)
    except:
        print("send error!")
