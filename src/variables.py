Colors = {
    "TEXT_WHITE": "#ffffff",
}

BodyShape = {
    "FEMALE": {
        "H": "H",
        "A": "A",
        "Y": "Y"
    }
}

StorageKeys = {
    "USERNAME": "USERNAME",
    "GENDER": "GENDER",
    "BODY-SHAPE": "BODY-SHAPE",
    "FITTING-TYPE": "FITTING-TYPE",
}

Gender = {
    "MALE": "MALE",
    "FEMALE": "FEMALE",
}

class BodyStyleItem:
    def __init__(self, desc: str, hashtag: str, recommend: str, ignore: str):
        self.desc = desc
        self.hashtag = hashtag
        self.recommend = recommend
        self.ignore = ignore
        
    def get(self):
        return {
            "desc": self.desc,
            "hashtag": self.hashtag,
            "recommend": self.recommend,
            "ignore": self.ignore,
        }

BodyStyles = {
    "MALE": {
        "O": BodyStyleItem(
                desc="허리와 복부가 발달한 체형",
                hashtag="#부드러운 #포근한 #친근한",
                recommend="상의 | V넥 상의, 세로 스트라이프\n하의 | 스트레이트 팬츠, 어두운 색",
                ignore="상의 | 타이트 핏, 크롭한 상의, 박시한 핏\n하의 | 와이드팬츠, 큰 패턴",
            ),
    },
    "FEMALE": {
        "O": BodyStyleItem(
                desc="허리와 복부가 발달한 체형",
                hashtag="#부드러운 #포근한 #친근한",
                recommend="상의 | 비대칭, 어깨장식, V넥, A라인원피스\n하의 | 스트레이트 팬츠, 어두운 색",
                ignore="상의 | 크롭한 상의, 허리 라인 노출\n하의 | 스키니진, 큰 패턴",
            ),
    }
}
