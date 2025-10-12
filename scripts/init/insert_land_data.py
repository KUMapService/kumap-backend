import json
import os
import sys
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from app.core.config import BASE_DIR  # noqa: E402
from app.integrations.kakao_api import kakao_get_coord  # noqa: E402
from src.init import DATABASE_NAME, USER_NAME, USER_PW, create_connection  # noqa: E402


def get_centroid(coords: list) -> tuple[float, float]:
    """다각형 좌표 리스트의 중심 좌표(centroid)를 계산."""
    x_sum, y_sum = 0, 0
    n = len(coords)
    for coord in coords:
        x_sum += coord[1]  # lng
        y_sum += coord[0]  # lat
    return y_sum / n, x_sum / n  # (lat, lng)

def insert_region_coordinates(connection):
    """행정구역 코드(PNU) 기준으로 중심좌표 저장"""
    print("# 행정구역 중심 좌표 데이터를 삽입합니다.")
    cursor = connection.cursor()
    query = """
        INSERT INTO region_coordinate
        (pnu, type, region, lat, lng)
        VALUES (%s, %s, %s, %s, %s);
    """

    csv_path = os.path.join(BASE_DIR, "data/PnuCode.csv")
    with open(csv_path, encoding="utf-8") as file:
        lines = file.readlines()

    for idx, line in enumerate(lines, 1):
        print(f"\r#   {idx:5d}/{len(lines):5d}", end="")
        parts = line.strip().split(",")
        if parts[1] == "sido":
            continue  # 시도 타이틀 행은 스킵

        pnu_prefix, region_type, region_name = "", "", ""
        if parts[4] == "":
            if parts[3] == "":
                if parts[2] == "":
                    # 시도 단위
                    pnu_prefix = parts[0][0:2]
                    region_type = "sido"
                    region_name = parts[1]
                else:
                    # 시군구 단위
                    pnu_prefix = parts[0][0:5]
                    region_type = "sigungu"
                    region_name = parts[2]
            else:
                # 읍면동 단위
                pnu_prefix = parts[0][0:8]
                region_type = "eupmyeondong"
                region_name = parts[3]

            query_str = " ".join(filter(None, parts[1:4]))
            lat, lng = kakao_get_coord(query_str)
            cursor.execute(query, (pnu_prefix, region_type, region_name, lat, lng))

    connection.commit()
    print("\n# 행정구역 중심 좌표 삽입 완료.")

def insert_cadastral_data(connection):
    """지적도 좌표 JSON 파일을 DB에 저장"""
    print("# 지적도 좌표 데이터를 삽입합니다.")
    cursor = connection.cursor()
    query = """
        INSERT INTO geometry_data
        (pnu, centroid_lat, centroid_lng, multi_polygon)
        VALUES (%s, %s, %s, %s);
    """

    for scale in ["emd", "sig", "sido"]:
        json_path = Path(BASE_DIR) / "src/dataset/cadastralmap" / f"{scale}.json"
        with open(json_path) as file:
            data = json.load(file)

        polygons = data["features"]

        for count, polygon in enumerate(polygons, 1):
            try:
                coords_list = polygon["geometry"]["coordinates"]
                centroids = []
                total_area = 0

                for poly in coords_list:
                    for coords in poly:
                        centroid = get_centroid(coords)
                        centroids.append(centroid)
                        total_area += 1

                final_centroid = get_centroid(centroids)

                prop_key = {
                    "emd": "EMD_CD",
                    "sig": "SIG_CD",
                    "sido": "CTPRVN_CD"
                }[scale]
                pnu_code = polygon["properties"][prop_key]

                print(f"({count:4d}/{len(polygons):4d}) {pnu_code}")
                cursor.execute(
                    query,
                    (
                        pnu_code,
                        final_centroid[1],  # 중심 좌표 (lng)
                        final_centroid[0],  # 중심 좌표 (lat)
                        json.dumps(coords_list),  # 원본 지오JSON 좌표
                    ),
                )
                connection.commit()
            except Exception as e:
                print(f"에러 발생 [{scale.upper()} {count}] → {e}")


if __name__ == "__main__":
    conn = create_connection("localhost", USER_NAME, USER_PW, DATABASE_NAME)
    # insert_region_coordinates(conn)
    insert_cadastral_data(conn)
    conn.close()
