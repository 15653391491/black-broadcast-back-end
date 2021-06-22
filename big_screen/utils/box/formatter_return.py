class formatterReturn:
    def __init__(self):
        pass

    def get_whitelist(self, content):
        """
        # a = {
        #     "data": [
        #         {
        #             "district": 2,
        #             "time": "2020-05-25 00:00:00",
        #             "freq": 88.6,
        #             "type": 2,
        #             "id": 129,
        #             "name": "测试频点二"
        #         }
        #     ],
        #     "msg": "success",
        #     "count": 10,
        #     "code": 0
        # }
        # b = {
        #     "data": {
        #         "list": [{
        #             "freq": 92.7,
        #             "name": "\u9891\u90533"
        #         }],
        #         "count": 6,
        #         "this_page_num": 1,
        #         "num_pages": 1
        #         },
        #     "errmsg": "success",
        #     "errno": 10000
        # }
        :param content:
        :return:
        """
        _content = dict()
        _content["errmsg"] = "success"
        _content["errno"] = 10000
        data = dict()
        data["this_page_num"] = 1
        data["num_pages"] = 1
        data["list"] = list()
        for con in content["data"]:
            info = dict()
            info["freq"] = float( con.get("freq"))
            info["name"] = con.get("name")
            info["type"] = con.get("type")
            info["time"] = con.get("time")
            info["district"] = con.get("district")
            data["list"].append(info)
        data["count"] = len(data["list"])
        _content["data"] = data
        return _content
