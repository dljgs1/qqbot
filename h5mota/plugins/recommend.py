from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand

tower_info = {}


# tower / author / list

def save_load(con='S'):
    global tower_info
    import json
    if con == 'S':
        with open("cache,json", "w") as fp:
            json.dump(tower_info, fp, ensure_ascii=False)
    else:
        try:
            with open("cache,json", "r") as fp:
                tower_info = json.load(fp)
        except:
            pass


save_load('L')

color_dict = {
    "绿": 3,
    "蓝": 2,
    "橙": 1,
    "白": 0,
    "红": 4,
    "紫": 5,
}
color_list = [
    "白",
    "橙",
    "蓝",
    "绿",
    "红",
    "紫"
]
key_words = ['复刻', '悬赏', '新人', '高难', '剧情', '创新', '加点', '转换', '道具', '境界', '技能', '单层', '高层', '平面', '连载', '休闲']

"""
list: all tower info
comment: all comment of one tower

"""
pull_time = 0
import time
import jieba


def update_tower_info(type='list', name=None):
    import requests
    import json
    args = {'type': type}
    if name is None:
        response = requests.post("https://h5mota.com/games/info.php", args)
        tower_info[type] = json.loads(response.text)
    else:
        args['name'] = name
        response = requests.post("https://h5mota.com/games/info.php", args)
        if type not in tower_info:
            tower_info[type] = {}
        tower_info[type][name] = json.loads(response.text)
    save_load()


def update_author_info():
    s = ""
    tower_info["author"] = {}
    for t in tower_info["list"]:
        s += t["author"] + "\n"
        author = t["author"]
        if author not in tower_info["author"]:
            tower_info["author"][author] = []
        tower_info["author"][author].append(t)
        author = t["author2"]
        if author:
            s += t["author2"] + "\n"
            if author not in tower_info["author"]:
                tower_info["author"][author] = []
            tower_info["author"][author].append(t)
    for c in color_dict:
        s += c + "\n"
    for k in key_words:
        s += k + "\n"
    with open("author.txt", 'w') as f:
        f.write(s)
    jieba.load_userdict("author.txt")


#
def get_tower_info():
    global pull_time, tower_info
    stamp = time.time()
    if 'tower' not in tower_info:
        tower_info['tower'] = {}
    if stamp - pull_time > 100:  # 100s间隔 更新一次全塔信息
        pull_time = stamp
        update_tower_info()
        update_author_info()
        # 保存缓存
    return tower_info


# huoqu pingfen
def get_tower_rate(name=None, update=False):
    if name is not None:
        if 'tower' not in tower_info or name not in tower_info['tower']:
            update_tower_info(type='tower', name=name)
        score = '无'
        if 'rate' not in tower_info['tower'][name]:
            print(tower_info['tower'][name])
        else:
            score = tower_info['tower'][name]['rate'] or score
            if str(score) == "0":
                score = '无'
        return score
    else:  # loading..
        info = get_tower_info()
        ret = {}
        for t in tower_info['list']:
            name = t['name']
            if name not in info['tower'] or update:
                update_tower_info('tower', name)
            ret[name] = info['tower'][name]['rate']
        return ret


def format_towers(names: list, max_num=None):
    s = "【塔名】【颜色】【评分】"
    import random
    if max_num is None:
        max_num = len(names)
    random.shuffle(names)
    for name in names[:max_num]:
        if name not in tower_info['tower']:
            update_tower_info('tower', name)
        d = tower_info['tower'][name]
        s += '\n' + d['title'] + " " + color_list[int(d["color"])]
        s += " " + str(get_tower_rate(d['name']))
    return s


# 处理检索信息
def proc_recomend_str(content):
    info = get_tower_info()
    score = False
    colors = None
    news = False
    lst = list(jieba.cut(content))
    print(lst)
    ans = [it['name'] for it in info['list']]
    max_num = 5
    for word in lst:
        if word in info['author']:  # 作者的塔 格式化后直接返回
            ans = [it['name'] for it in info['author'][word]]
            max_num = len(ans)
        elif '高分' in word and not score:  # > 4.0
            score = True
            score_dict = get_tower_rate()
            tlist = list(score_dict.keys())
            tlist = [t for t in tlist if float(score_dict[t]) > 4.0]  # .sort(key=lambda k: score_dict[k], reverse=True)
            if len(ans) > 0:
                ans = list(set(ans) & set(tlist))
            else:
                ans = tlist
        elif '简单' in word and not news:
            news = True
            tlist = list(info['tower'].keys())
            score_dict = get_tower_rate()
            tlist = list(set(tlist) and set(score_dict.keys()))
            #tlist.sort(key=lambda t: float(score_dict[t])+float(int(info['tower'][t]['win']) + 1) / (int(info['tower'][t]['people']) + 1),
            #           reverse=True)
            tlist.sort(key=lambda t: float(score_dict[t]) + int(info['tower'][t]['win']), reverse=True)
            tlist = tlist[:int(len(tlist)/5)]
            if len(ans) > 0:
                ans = list(set(ans) & set(tlist[:len(ans) * 5]))
            else:
                ans = tlist[:int(len(tlist) / 10)]
        elif word in key_words:
            tlist = [it for it in info['tower'] if word in info['tower'][it]['tag']]
            if len(ans) > 0:
                ans = list(set(ans) & set(tlist[:len(ans) * 5]))
            else:
                ans = tlist[:int(len(tlist) / 10)]
        else:
            for c in color_dict:
                if c in word:
                    colors = colors or []
                    colors.append(color_dict[c])
    if colors:  # 颜色筛选
        ans = [t for t in ans if int(tower_info['tower'][t]['color']) in colors]
    ret = ""
    if len(ans) == len(info['list']) and not news:
        import random
        ret += "找不到你要的塔，下面是随机的推荐：\n"
    return ret + format_towers(ans, max_num)


recommend_list = "1. 高分塔 \n 2. 简单塔（高通关率）\n 3. 按作者名检索\n 4. 按塔颜色名检索\n5. 按塔标签检索\n\n【示例】推荐 高分新人绿塔"


@on_command('推荐', aliases=('魔塔推荐'))
async def recommend(session: CommandSession):
    # await session.send("开发中", ignore_failure=False)
    recomend = session.get('recommend', prompt='你想得到哪类推荐？输入建议：\n' + recommend_list)
    print("recomend:", recomend)
    await session.send(proc_recomend_str(recomend), ignore_failure=False)


@recommend.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['recommend'] = stripped_arg
        return
    if not stripped_arg:
        session.pause('不知道你在说什么，请重新输入')

    session.state[session.current_key] = stripped_arg


@on_natural_language(keywords={'推荐'})
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    args = stripped_msg.split('推荐')
    if len(args) <= 1:
        args += [None]
    return IntentCommand(90.0, '推荐', current_arg=args[1])


@on_command('update', aliases=('更新'))
async def address(session: CommandSession):
    uid = session.ctx["user_id"]
    if int(uid) == 906348668:
        get_tower_rate(update=True)
        get_tower_info()
        save_load()
        try:
            await session.send("已更新全部塔信息", ignore_failure=False)
        except:
            print("send error!")
    else:
        try:
            await session.send("只有管理员有此权限！", ignore_failure=False)
        except:
            print("send error!")
