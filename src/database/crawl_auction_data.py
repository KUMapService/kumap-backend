import requests
import json
from time import sleep
import random

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.land import LandAuction
from app.utils.convert_code import addr2code

SIDO_CODE = [
	"11", "26", "27", "28", "29", "30", "31",
	"36", "41", "43", "44", "46", "47", "48",
	"50", "51", "52",
]

def crawl_auction_data(sido_cd: str, sigungu_cd: str = "", db: Session = None) -> None:
	total_group_count = 1
	current_count = 1
	
	cookies = {
		'pageCnt': '40', 
		'WMONID': '-T1D5L7RsVE',
		'SID': '',
		'cortAuctnLgnMbr': '',
		'wcCookieV2': '121.168.132.119_T_617456_WC',
		'JSESSIONID': 'hPK37norIcRc9otyEJwXqwQpnH0T1_9saaf7xISq_4JeUdOBsXcm!-781610137',
		'lastAccess': '1751137547822',
	}

	headers = {
		'Accept': 'application/json',
		'Accept-Language': 'ko-KR,ko;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6',
		'Connection': 'keep-alive',
		'Content-Type': 'application/json;charset=UTF-8',
		'Origin': 'https://www.courtauction.go.kr',
		'Referer': 'https://www.courtauction.go.kr/pgj/index.on?w2xPath=/pgj/ui/pgj100/PGJ151F00.xml',
		'SC-Userid': 'SYSTEM',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-origin',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
		'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"macOS"',
		'submissionid': 'mf_wfm_mainFrame_sbm_selectGdsDtlSrch',
	}

	while current_count <= total_group_count:
		json_data = {
			'dma_pageInfo': {
				'pageNo': current_count,
				'pageSize': '40',
				'totalYn': 'Y',
			},
			'dma_srchGdsDtlSrchInfo': {
				'bidDvsCd': '000331',
				'mvprpRletDvsCd': '00031R',
				'cortAuctnSrchCondCd': '0004601',
				'rprsAdongSdCd': sido_cd,
				'rprsAdongSggCd': sigungu_cd,
				'rprsAdongEmdCd': '',
				'cortOfcCd': 'B000210',
				'lclDspslGdsLstUsgCd': '10000',
				'notifyLoc': 'on',
				'pgmId': 'PGJ151F01',
				'cortStDvs': '2',
				'statNum': 1,
				'bidBgngYmd': '20250629',
				'bidEndYmd': '20250713',
			},
		}

		response = requests.post(
			'https://www.courtauction.go.kr/pgj/pgjsearch/searchControllerMain.on',
			cookies=cookies,
			headers=headers,
			json=json_data,
		)

		response = json.loads(response.text)
		print(response)
		total_group_count = response["data"]["dma_pageInfo"]["groupTotalCount"]
		print(f"[{response["data"]["dma_pageInfo"]["pageNo"]:5d}/{total_group_count:5d}]")
		current_count += 1

		for r in response["data"]["dlt_srchResult"]:
			if r["lclsUtilCd"] == "10000":
				try:
					auction_data = db.query(LandAuction).filter_by(doc_id=r["docid"]).first()
					if auction_data:
						print(f"[UPDATE] {r["docid"]}, {addr2code(r["printSt"])} already exists, updating...")
						# Field update
						auction_data.doc_id = r["docid"]
						auction_data.pnu = addr2code(r["printSt"])
						auction_data.case_cd = r["srnSaNo"]
						auction_data.obj_cd = int(r["maemulSer"])
						auction_data.obj_type = r["jimokList"]
						auction_data.appraisal_price = r["gamevalAmt"]
						auction_data.min_sale_price = r["notifyMinmaePrice1"]
						auction_data.auction_date = r["maeGiil"]
						auction_data.auction_time = r["maeHh1"]
						auction_data.court_in_charge = r["jiwonNm"]
						auction_data.court_detail = r["jpDeptNm"]
						auction_data.land_detail = r["convAddr"]
					else:
						print(f"[INSERT] {r["docid"]}, {addr2code(r["printSt"])} does not exist, inserting new data...")
						auction_data = LandAuction(
							doc_id=r["docid"],
							pnu=addr2code(r["printSt"]),
							case_cd=r["srnSaNo"],
							obj_cd=int(r["mokmulSer"]),
							obj_type=r["jimokList"],
							appraisal_price=r["gamevalAmt"],
							min_sale_price=r["notifyMinmaePrice1"],
							auction_date=int(r["maeGiil"]),
							auction_time=int(r["maeHh1"]),
							court_in_charge=r["jiwonNm"],
							court_detail=r["jpDeptNm"],
							land_detail=r["convAddr"],
						)
						db.add(auction_data)
					db.commit()
				except Exception as e:
					print("[ERROR]", str(e))
					db.rollback()
		sleep(random.uniform(1.0, 2.0))

def main():
	db = SessionLocal()
	try:
		for sido in SIDO_CODE:
			print(f"[START] {sido} crawling...")
			crawl_auction_data(sido, db=db)
	except:  # noqa: E722
		print("[ERROR] BAD RESPONSE")
	


if __name__ == "__main__":
    main()