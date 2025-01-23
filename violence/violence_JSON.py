from transformers import CLIPProcessor, CLIPModel
import os
import json
from PIL import Image
from collections import Counter 

def violence(image_folder_path, output_file, threshold=0.45):
    
    # 모델 및 프로세서 로드
    model_name = "openai/clip-vit-large-patch14"
    model = CLIPModel.from_pretrained(model_name)
    processor = CLIPProcessor.from_pretrained(model_name)

    # 텍스트 후보군 생성
    text_candidates = [
        # 폭력
        "a scene of physical violence",
        "a scene of rape",
        "a scene of a person bleeding",
        "a scene of an animal bleeding",
        "the scene of a corpses",
        "a murderous scene",
        "a scene using knives, guns, bats, etc. to pose a threat",

        # 기타
        "A picture of a person standing",
        "A peaceful scene",
        "A person walking in the street",
        "A lot of people walking in the street",
        "A calm conversation between people",
        "A person smiling and laughing",
        "The scene that people are talking about",
        "a picture of a person sitting",
        "a photo of a drinking",
        "a picture of someone kissing",
        "a picture of someone taking off his clothes",
        "a photo of a smoking",
        "a photo of someone on drugs",
    ]

    # 출력 테스트 타깃 설정
    target_captions = {
        "a scene of physical violence",
        "a scene of rape",
        "a scene of a person bleeding",
        "a scene of an animal bleeding",
        "the scene of a corpses",
        "a murderous scene",
        "a scene using knives, guns, bats, etc. to pose a threat"
    }

    # 결과 저장
    results = []
    caption_counts = Counter() 

    # 폴더 내 모든 이미지 파일 가져오기
    image_files = os.listdir(image_folder_path)
    image_files.sort()

    # 폴더 내 모든 이미지 파일 처리
    for idx, image_name in enumerate(image_files, start=1):
        image_path = os.path.join(image_folder_path, image_name)

        try:
            print(f"처리 중: [{idx}/{len(image_files)}] {image_name}")  # 이미지 처리 상황 출력

            # 이미지 로드
            image = Image.open(image_path).convert("RGB")

            # 입력 데이터 전처리
            inputs = processor(text=text_candidates, images=image, return_tensors="pt", padding=True)

            # 모델 추론
            outputs = model(**inputs)

            # 이미지-텍스트 유사도 계산
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)

            # 가장 높은 유사도를 가진 텍스트와 해당 확률
            best_match_idx = probs.argmax()
            best_caption = text_candidates[best_match_idx]
            highest_prob = probs[0, best_match_idx].item()

            # 조건에 따른 출력
            if highest_prob >= threshold and best_caption in target_captions:
                display_caption = best_caption
                caption_counts[best_caption] += 1  
            else:
                display_caption = "폭력적인 장면이 없습니다."

            # 결과 저장
            results.append({
                "image_name": image_name,
                "best_caption": display_caption,
                "highest_prob": highest_prob
            })

        except Exception as e:
            print(f"Error processing {image_name}: {e}")

    # JSON으로 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    # caption_counts와 results 출력
    print("\n폭력적인 장면 빈도:")
    for caption, count in caption_counts.items():
        print(f"{caption}: {count}")

    print("\n분석 결과:")
    for result in results:
        print(result)

    print(f"\n모든 결과가 {output_file}에 저장되었습니다.")

    # 결과와 각 폭력성 빈도 리턴
    return results, dict(caption_counts)

# 실행
image_path = '이미지 폴더 경로'
output_file = '결과 저장 경로'
violence(image_path, output_file, threshold=0.45)
