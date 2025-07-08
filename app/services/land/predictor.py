import pandas as pd
import xgboost as xgb

from app.core.config import MODEL_PATH
from app.modules.land_data_fetcher import fetch_land_basic_data
from app.schemas.land import PredictedPriceData
from app.utils.date import get_now


class LandPricePredictor:
    def __init__(self):
        self.model = xgb.XGBRegressor()
        self.model.load_model(MODEL_PATH)

    def prepare_input(self, pnu: str, year: int, month: int) -> dict:
        """
        PNU 기반으로 예측 모델 Input 데이터 준비
        """
        data = fetch_land_basic_data(pnu=pnu, year=year, month=month)

        # 4. 최종 Input 데이터 구성
        input_data = {
            "PNU": pnu,
            "Year": year,
            "Month": month,

            # 토지 특성
            "PblntfPclnd": data.feature.official_price,
            "RegstrSe": "Re" + data.feature.land_reg_code,
            "Lndcgr": "Lc" + data.feature.land_cls_code,
            "LndpclAr": data.feature.land_area,
            "PrposArea1": "A1" + data.feature.land_zoning_code,
            "PrposArea2": "A2" + data.feature.land_zoning2_code,
            "LadUseSittn": "Us" + data.feature.land_usage_code,
            "TpgrphHg": "Hg" + data.feature.land_height_code,
            "TpgrphFrm": "Fm" + data.feature.land_form_code,
            "RoadSide": "Rs" + data.feature.road_side_code,

            # 변동률
            "PclndIndex": data.land_fluctuation_rate.index,
            "PclndChgRt": data.land_fluctuation_rate.change_rt,
            "AcmtlPclndChgRt": data.land_fluctuation_rate.accumulate_change_rt,

            "LargeClPclndIndex": data.large_cl_fluctuation_rate.index,
            "LargeClPclndChgRt": data.large_cl_fluctuation_rate.change_rt,
            "LargeClAcmtlPclndChgRt": data.large_cl_fluctuation_rate.accumulate_change_rt,

            # 물가지수
            "PPI": data.ppi,
            "CPI": data.cpi,

            # 장소 거리 + 카운트
            **data.place_distances,
            **{f"{k}_500m": v for k, v in data.place_counts_500.items()},
            **{f"{k}_1000m": v for k, v in data.place_counts_1000.items()},
            **{f"{k}_3000m": v for k, v in data.place_counts_3000.items()},

            # 토지 이용계획 (Optional)
            "LandUsePlans": data.uses_plan_code,
        }

        return input_data
    def predict(self, pnu: str, year: int, month: int) -> PredictedPriceData:
        """
        예측 수행
        """
        input_data = self.prepare_input(pnu=pnu, year=year, month=month)
        input_features = {}
        for feature in self.model.feature_names_in_:
            if feature not in input_data.keys():
                if feature.split("_")[0] == "Sido":
                    input_features[feature] = (
                        feature.split("_")[1] == input_data["PNU"][0:2]
                    )
                elif feature.split("_")[0] == "LandUsePlans":
                    input_features[feature] = feature.split("_")[1] in input_data["LandUsePlans"].split("/")
                else:
                    input_features[feature] = (
                        feature.split("_")[1] in input_data[feature.split("_")[0]]
                    )
            else:
                input_features[feature] = input_data[feature]

        target_x = pd.DataFrame.from_dict(
            data=[input_features], orient="columns", dtype=float
        )
        target_predict = self.model.predict(target_x)
        predicted_price = abs(int(f"{target_predict[0]:.0f}")) / 1000 * 1000
        last_predicted_date = get_now()
        return PredictedPriceData(predicted_price=predicted_price, last_predicted_date=last_predicted_date)


land_price_predictor = LandPricePredictor()
