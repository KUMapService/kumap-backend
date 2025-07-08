from concurrent.futures import ThreadPoolExecutor

from app.integrations import ecos_api, kakao_api, vworld_api
from app.schemas.land import LandBasicData


def fetch_land_basic_data(pnu: str, year: int, month: int) -> LandBasicData:
    """
    주어진 PNU로 필요한 모든 데이터를 병렬로 받아서 PromptLandData 형태로 반환
    """
	# 1. VWORLD / ECOS 병렬 호출
    with ThreadPoolExecutor() as executor:
        future_lf = executor.submit(vworld_api.get_land_feature, pnu, year)
        future_lup = executor.submit(vworld_api.get_land_use_plan, pnu, return2name=True)
        future_lup_code = executor.submit(vworld_api.get_land_use_plan, pnu)
        future_frbr = executor.submit(vworld_api.get_fluctuation_rate_by_region, ld_code=pnu[:10], year=year, month=month)
        future_frbp = executor.submit(vworld_api.get_fluctuation_rate_by_province, ld_code=pnu[:10], year=year, month=month)
        future_ppi = executor.submit(ecos_api.get_producer_price_index, year=year, month=month)
        future_cpi = executor.submit(ecos_api.get_consumer_price_index, year=year, month=month)

        lf_data = future_lf.result()
        lup_data = future_lup.result()
        lup_code_data = future_lup_code.result()
        frbr_data = future_frbr.result()
        frbp_data = future_frbp.result()
        ppi = future_ppi.result()
        cpi = future_cpi.result()

    # 2. 주소 준비
    addr_str = lf_data.legal_dong + " "
    addr_str += lf_data.land_reg if lf_data.land_reg == "산" else ""
    addr_str += lf_data.land_lot_number

    # 3. Kakao API 병렬 호출
    with ThreadPoolExecutor() as executor:
        future_place_dist = executor.submit(kakao_api.get_nearest_place_distance, addr_str)
        future_place_500 = executor.submit(kakao_api.get_place_count_in_radius, addr_str, radius=500)
        future_place_1000 = executor.submit(kakao_api.get_place_count_in_radius, addr_str, radius=1000)
        future_place_3000 = executor.submit(kakao_api.get_place_count_in_radius, addr_str, radius=3000)

        place_distances = future_place_dist.result()
        place_counts_500 = future_place_500.result()
        place_counts_1000 = future_place_1000.result()
        place_counts_3000 = future_place_3000.result()

    return LandBasicData(
        pnu=pnu,
        feature=lf_data,
        uses_plan=lup_data,
        uses_plan_code=lup_code_data,
        land_fluctuation_rate=frbr_data,
        large_cl_fluctuation_rate=frbp_data,
        ppi=ppi,
        cpi=cpi,
        place_distances=place_distances,
        place_counts_500=place_counts_500,
        place_counts_1000=place_counts_1000,
        place_counts_3000=place_counts_3000,
    )
