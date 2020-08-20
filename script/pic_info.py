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
        self.width = config.get("width","-")
        self.height = config.get("height","-")
