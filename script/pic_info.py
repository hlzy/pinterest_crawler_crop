class PicInfo:
    INIT = 0
    DOWNLOAD = 1
    CROP = 2
    UPLOAD = 3
    ERROR = -1

    def __init__(self,**config):
        if "url" not in config or "id" not in config:
            self.status = ERROR
            return
        self.url= config.get("url")
        self.id = config.get("id")
        self.query = config.get("query","unkown")
        self.country = config.get("country","unkown")
        self.status = config.get("status",PicInfo.INIT)
        self.width = config.get("width",0)
        self.height = config.get("height",0)

    def __str__(self):
        return ("""
        pic:{}
        url:{}
        query:{}
        country:{}
        status:{}
        width:{}
        height:{}""".format(self.id,
            self.url,
            self.query,
            self.country,
            self.status,
            self.width,
            self.height))
