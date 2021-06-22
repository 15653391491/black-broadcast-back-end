from redis.client import StrictRedis
import json


class BaseOpration:
    def __init__(self):
        self.con = StrictRedis
        self.keys = list()

    # --------------- 工具 -----------------------
    def get_keys(self):
        keys = self.con.keys()
        key_list = list()
        for key in keys:
            key_list.append(key.decode())
        self.keys = key_list
        return self.keys

    def key_is_legal(self, k):
        self.get_keys()
        if k not in self.keys:
            return False
        else:
            return True

    def formatter_info(self, info):
        """
        格式化数据
        :param info:
        :return:
        """
        pass

    def list_get_len(self, key):
        """
        返回某个列表的长度
        :param key:
        :return:
        """
        length = self.con.llen(key)
        return length

    # ----------------------- 存数据 ------------------
    def kv_set(self, k, v):
        self.con.set(k, json.dumps(v))

    def kvSet(self, k, v):
        self.con.set(k, v)

    def list_push(self, k, v):
        self.con.lpush(k, json.dumps(v))

    # ---------------------- 取数据 --------------------
    def kv_get(self, k):
        is_legal = self.key_is_legal(k)
        if is_legal:
            content = self.con.get(k)
        else:
            return None
        return json.loads(content.decode())

    def kvGet(self, k):
        return self.con.get(k)

    def list_get(self, k):
        """
        获取整个列表数据
        :param k:
        :return:
        """
        is_legal = self.key_is_legal(k)
        if is_legal:
            content = self.con.lrange(k, 0, -1)
            content = list(map(lambda con: con.decode(), content))
        else:
            return 0
        return content

    def list_len(self, k):
        """
        获取队列长度
        :param k:
        :return:
        """
        return self.con.llen(k)

    def list_get_head(self, k):
        """
        获取队首数据，从左往右最后一个
        :param k:
        :return:
        """
        is_legal = self.key_is_legal(k)
        if is_legal:
            content = self.con.lrange(k, -1, -1)
            content = list(map(lambda con: con.decode(), content))
            content = list(map(lambda info: json.loads(info), content))
            if len(content) > 0:
                return content[0]
            else:
                return {}
        else:
            return {}

    def list_get_tail(self, k):
        """
        从左往右第一个
        :param k:
        :return:
        """
        is_legal = self.key_is_legal(k)
        if is_legal:
            content = self.con.lrange(k, 0, 0)
            content = list(map(lambda con: con.decode(), content))
            content = list(map(lambda info: json.loads(info), content))
            return content
        else:
            return "no this key"

    # -------------------- 删除数据 --------------------
    def list_pop(self, k):
        content = self.con.rpop(k)
        return content

    def del_key(self, k):
        self.con.delete(k)
        return "ok"

    def flush_db(self):
        self.con.flushdb()
        return "ok"

    # --------------------- 设置过期 ---------------------
    def expire_key(self):
        pass
