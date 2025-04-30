import time
import google.generativeai as genai

from app.core.config import GOOGLE_API_KEY, LLM_MODEL
from app.generators.land_prompt import generate_land_prompt
from app.generators.land_trade_finder import find_similar_land_trade
from app.modules.land_data_fetcher import fetch_land_basic_data
from app.services.land.predictor import land_price_predictor
from app.utils.convert_code import code2addr
from app.utils.date import get_now

# 제미나이 모델 로딩
genai.configure(api_key=GOOGLE_API_KEY)
llm = genai.GenerativeModel(LLM_MODEL)


def generate_land_report(pnu: str, predicted_price: float) -> str:
    """"""
    total_start = time.time()

    print("=== [Start] Generate Land Report ===", flush=True)

    # 기본 데이터 불러오기
    start = time.time()
    address = code2addr(pnu)
    now = get_now()
    land_data = fetch_land_basic_data(pnu, now.year, now.month)
    print(f"[Fetched land basic data] {time.time() - start:.2f}초", flush=True)

    # 결정트리 text 생성
    start = time.time()
    tree_text = ""
    for i, tree in enumerate(land_price_predictor.model.get_booster().get_dump()):
        tree_text += f"Tree {i}:\n{tree}"
    print(f"[Generated decision tree text] {time.time() - start:.2f}초", flush=True)

    # 주변 비교군 찾기
    start = time.time()
    compare_land = find_similar_land_trade(
        pnu=pnu, 
        target_cls=land_data.feature.land_cls, 
        target_zoning=land_data.feature.land_zoning, 
        start_year=now.year, 
        start_month=now.month
    )
    print(f"[Fetched land trade data] {time.time() - start:.2f}초", flush=True)

    # 프롬프트 생성
    start = time.time()
    prompt = generate_land_prompt(
        target_address=address,
        target_info=land_data.return_to_prompt(),
        tree_text=tree_text,
        compare_info=compare_land if compare_land else "",
        target_price=predicted_price * land_data.feature.land_area,
    )
    print(f"[Created prompt] {time.time() - start:.2f}초", flush=True)

    # 리포트 생성
    start = time.time()
    response = llm.generate_content(prompt)
    print(f"[Generated report from Gemini] {time.time() - start:.2f}초", flush=True)

    print(f"=== [Finished] Total time: {time.time() - total_start:.2f}초 ===", flush=True)
    return response.text
