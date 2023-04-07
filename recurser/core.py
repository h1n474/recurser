import pathlib
import itertools
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from rich.progress import track


class Recurser:
    def __init__(self, path='.', recursive=True, resolve=True):
        self.path = path
        self.recursive = recursive
        self.resolve = resolve
        self.items = None

    def __check_items(self):
        if self.items == None:
            raise Exception("💥Not found self.items. 1st, `get_files()` or `get_dirs()`")
        return

    def _all(self):
        if self.resolve:
            p = pathlib.Path(self.path).expanduser().resolve()
        else:
            p = pathlib.Path(self.path).expanduser()
        if self.recursive:
            return  (i for i in p.glob('**/*')
                           if not any(map(lambda x: x.startswith('.'), i.parts)))
        else:
            return  (i for i in p.glob('*')
                           if not any(map(lambda x: x.startswith('.'), i.parts)))

    def get_files(self, *extname: str):
        if extname == ():
            self.items = (i for i in self._all() if i.is_file())
            return self
        else:
            lower = ['.' + i.lower() for i in extname]
            upper = ['.' + i.upper() for i in extname]
            extname = lower + upper
            self.items = (i for i in self._all() if i.is_file() and i.suffix in extname)
            return self

    def get_dirs(self, *dirname: str):
        if dirname == ():
            self.items = (i for i in self._all() if i.is_dir())
            return self
        else:
            self.items = (i for i in self._all() if i.is_dir() and i.stem in dirname)
            return self

    def func(self, path):
        # Recurserに対して再帰的に処理をしたい時クラスをオーバーライド
        # 引数にpathは必須
        pass

    def print(self):
        self.__check_items()
        print(*list(self.items), sep='\n', end='\n')

    def exec(self, *args, **kwargs):
        self.__check_items()
        p, pp = itertools.tee(self.items, 2)
        num = sum(1 for _ in pp)
        result_arr = []
        for i in track(p, description="executing.", total=num):
            result = self.func(i, *args, **kwargs)
            result_arr.append(result)
        return result_arr

    def multi_exec(self, *args, **kwargs):
        self.__check_items()
        p, pp = itertools.tee(self.items, 2)
        num = sum(1 for _ in pp)
        func = partial(self.func, *args, **kwargs)
        with ThreadPoolExecutor() as executor:
            result_map_arr = list(track(executor.map(func, p), description="multi_executing.", total=num))
        return result_map_arr
