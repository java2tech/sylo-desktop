Colors = {
    "TEXT_WHITE": "#ffffff",
}

BodyShape = {
    "FEMALE": {
        "H": "H",
        "A": "A",
        "Y": "Y",
        "O": "O",
        "X": "X",
    },
    "MALE": {
        "H": "H",
        "Y": "Y",
        "O": "O",
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
        "Y": BodyStyleItem(
                desc="하체에 비해 상체가 발달한 체형",
                hashtag="#역동적 #당당한 #스포티한",
                recommend="상의 | 깊은 V넥/U넥, 심플한 상의, 단색\n하의 | 와이드팬츠, 카고팬츠",
                ignore="상의 | 과한 오버핏, 과한 어깨 노출\n하의 | 스키니진, 반바지, 밝은 색상, 세로선",
            ),
        "H": BodyStyleItem(
                desc="허리의 굴곡이 적은 체형",
                hashtag="#직선적 #깔끔한 #심플한",
                recommend="상의 | 레이어링, 미디 기장 이상의 자켓\n하의 | 벨트, 와이드팬츠",
                ignore="상의 | 일자핏 상의, 루즈한 핏\n하의 | 스키니진, 톤온톤 색상 조합",
            ),
    },
    "FEMALE": {
        "O": BodyStyleItem(
                desc="허리와 복부가 발달한 체형",
                hashtag="#부드러운 #포근한 #친근한",
                recommend="상의 | 비대칭, 어깨장식, V넥, A라인원피스\n하의 | 스트레이트 팬츠, 어두운 색",
                ignore="상의 | 크롭한 상의, 허리 라인 노출\n하의 | 스키니진, 큰 패턴",
            ),
        "A": BodyStyleItem(
                desc="상체에 비해 하체가 발달한 체형",
                hashtag="#안정감 # 여성스러운 #우아한",
                recommend="상의 | 퍼프소매, 셔링 블라우스, 오프숄더\n하의 | 일자핏 팬츠, A라인 스커트",
                ignore="상의 | 타이트한 핏\n하의 | 스키니진, 밝은색 하의, H라인스커트",
            ),
        "X": BodyStyleItem(
                desc="어깨, 엉덩이가 균형잡힌 허리가 잘록한 체형",
                hashtag="#균형잡힌 #곡선미 #조화로운",
                recommend="상의 | 랩 원피스, 벨트 원피스, 크롭한 상의\n하의 | 하이웨스트 팬츠 ",
                ignore="상의 | 오버사이즈, 터틀넥, 하이넥, 일자핏\n하의 | 스키니진",
            ),
        "H": BodyStyleItem(
                desc="허리의 굴곡이 적은 체형",
                hashtag="#직선적 #깔끔한 #심플한",
                recommend="상의 | 페플럼탑, 자켓 레이어링, 얇은 가로선\n하의 | 벨트, 플리츠 스커트",  
                ignore="상의 | 일자핏 상의, 남성옷, 박시한 핏\n하의 | H라인 스커트, 과한 슬림핏",
            ),
        "Y": BodyStyleItem(
                desc="하체에 비해 상체가 발달한 체형",
                hashtag="#역동적 #당당한 #스포티한",
                recommend="상의 | 깊은 V넥, 드롭숄더, 슬리브리스\n하의 | 플레어스커트, 와이드팬츠",
                ignore="상의 | 퍼프소매, 숄더 패드 자켓, 오프숄더\n하의 | H라인 스커트, 스키니진",
            ),
    }
}
