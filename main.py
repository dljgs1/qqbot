import nonebot
import config
from os import path

nonebot.init(config)
nonebot.load_builtin_plugins()
nonebot.load_plugins(path.join(path.dirname(__file__), 'h5mota', 'plugins'),'h5mota.plugins')

#nonebot.run(host='0.0.0.0', port=1061)
nonebot.run(host='172.18.0.1', port=1061)


