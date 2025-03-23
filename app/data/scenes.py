MANSION_SCENES = {
    "mansion_entrance": {
        "name": "맨션 입구",
        "description": "스탠리 맨션의 웅장한 입구입니다.",
        "evidence_spots": {
            "doorbell": "초인종 옆에 희미한 지문이 있습니다.",
            "camera": "CCTV 카메라가 설치되어 있습니다."
        },
        "next_scenes": ["living_room", "garden"]
    },
    "garden": {
        "name": "정원",
        "description": "잘 가꾸어진 정원입니다. 벨라돈나 화분이 보입니다.",
        "evidence_spots": {
            "flower_bed": "벨라돈나 화분이 있습니다.",
            "garden_tools": "정원 도구들이 있습니다."
        },
        "next_scenes": ["mansion_entrance"]
    },
    "kitchen": {
        "name": "주방",
        "description": "넓은 주방입니다. 여러 약병들이 보입니다.",
        "evidence_spots": {
            "medicine_cabinet": "약장에 여러 약병들이 있습니다.",
            "sink": "싱크대에 사용한 약병이 있습니다."
        },
        "next_scenes": ["living_room"]
    },
    "bathroom": {
        "name": "화장실",
        "description": "스탠리의 방에 딸린 화장실입니다.",
        "evidence_spots": {
            "cabinet": "약장을 살펴볼 수 있습니다.",
            "trash": "쓰레기통에 약병이 보입니다."
        },
        "next_scenes": ["stanley_room"]
    },
    "living_room": {
        "name": "거실",
        "description": "넓은 거실에는 고가의 가구들이 놓여있습니다.",
        "evidence_spots": {
            "coffee_table": "커피 테이블 위에 약병이 있습니다.",
            "security_panel": "보안 시스템 제어판이 있습니다."
        },
        "next_scenes": ["stanley_room", "kitchen"]
    },
    "stanley_room": {
      
        "name": "스탠리의 방",
        "description": "사건이 발생한 스탠리의 침실입니다.",
        "evidence_spots": {
            "humidifier": "가습기 내부에 이상한 흔적이 있습니다.",
            "medical_records": "책상 위에 의료 기록이 놓여있습니다.",
            "pacemaker": "심장박동기 조절 장치가 보입니다."
        },
        "next_scenes": ["living_room", "bathroom"]
    }
}

EVIDENCE_DETAILS = {
    "벨라돈나_화분": {
        "description": "배송일: 5월 10일의 벨라돈나 화분",
        "stress_keywords": ["벨라돈나", "화분", "독성"],
        "stress_level": 2
    },
    "의료기록": {
        "description": "아트로핀 처방: 정상 투여량 3mg",
        "stress_keywords": ["아트로핀", "처방", "투여"],
        "stress_level": 1
    },
    "심장박동기_로그": {
        "description": "18:30 비정상 작동 기록",
        "stress_keywords": ["심장박동기", "해킹", "오작동"],
        "stress_level": 2
    },
    "약병_증거": {
        "description": "라벨이 조작된 흔적이 있는 약병",
        "stress_keywords": ["약병", "라벨", "조작"],
        "stress_level": 1
    },
    "보안_로그": {
        "description": "18:15-18:40 사이의 보안 시스템 기록",
        "stress_keywords": ["보안", "기록", "시간"],
        "stress_level": 1
    }
} 