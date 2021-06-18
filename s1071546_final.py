from pylatex import Document, Section, Command, Package, Tabular
from pylatex.utils import NoEscape
import requests
import argparse

# 參數設定區
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--county", required= True, help="The city you want to generate the weather report.")

args = parser.parse_args()

# 合法縣市清單，用以檢查輸入
legal_input_list = ["宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣", "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市", "基隆市", "新竹縣", "新竹市", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", "屏東縣"]

def get_weather_forecast(county):
    """去中央氣象局的API抓取天氣預報資料

    Args:
        county (String): 要抓取預報資料的縣市名稱

    Returns:
        Dict: API回傳的JSON結果
    """

    # API必要的參數，API Key以及縣市名稱
    query_params = {
            'Authorization': 'CWB-2D5D5351-1CB2-42EB-84E2-8E304A4CFF54',
            'locationName': county
        }

    r = requests.get('https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-091', query_params)

    return r.json()

def fill_doc_preamble(doc, forecast_info):
    """填寫Latex文件Preamble裡此次要用到的Packages、標題、作者、設定等等

    Args:
        doc (Document): pylatex的Document物件，也就是Latex文件本身
        forecast_info (Dict): 指定縣市相關的預報資料
    """
    # Latex中文支援
    doc.packages.append(Package('ctex', 'UTF8'))
    # 版面格式設定
    doc.packages.append(Package('geometry', 'a4paper,margin=1in'))
    doc.preamble.append(Command('title', "未來1週逐12小時天氣預報 - {}".format(forecast_info["records"]["locations"][0]["location"][0]["locationName"])))
    doc.preamble.append(Command('author', "中央氣象局API"))
    doc.preamble.append(Command('date', NoEscape(r'\today')))
    doc.append(NoEscape(r'\maketitle'))

def fill_document(doc, forecast_info):
    """將天氣預報資料製成表格放入Latex文件當中

    Args:
        doc (Document): pylatex的Document物件，也就是Latex文件本身
        forecast_info (Dict): 指定縣市相關的預報資料
    """
    # 開始置中區段
    doc.append(Command("begin", "center"))
    # 將所有不同的預報項目做迴圈
    for item in forecast_info["records"]["locations"][0]["location"][0]["weatherElement"]:
        # 天氣預報綜合描述不納入，因為太長了
        if(item["description"] == "天氣預報綜合描述"):
            continue
        # 將每個預報項目的各時間點資料做迴圈
        with doc.create(Section(item["description"])):
            # 依照資料的多寡製作table的格式設定以及標題行的內容
            header = ['起始時間','結束時間']
            header_format = '|c|c|'
            for elementValue in item["time"][0]['elementValue']:
                '''if("NA" in elementValue["measures"]):
                    continue'''
                header_format += 'c|'
                header.append(elementValue["measures"])
            # 設定table
            table = Tabular(header_format)
            table.add_hline()
            table.add_row(header)
            table.add_hline()
            # 將每個預報項目的各時間點資料底下的觀測值做迴圈並放到表格內
            for timeObj in item["time"]:
                row = [timeObj["startTime"], timeObj["endTime"]]
                for elementValue in timeObj["elementValue"]:
                    '''if("NA" in elementValue["measures"]):
                        continue'''
                    row.append(elementValue["value"])
                table.add_row(row)
                table.add_hline()
            doc.append(table)
    # 結束置中區段
    doc.append(Command("end", "center"))


if __name__ == '__main__':

    # 判斷輸入的縣市是否合法
    if(args.county in legal_input_list):

        print("產生的縣市為: {}".format(args.county))
        
        # 取得縣市資料
        forecast_info = get_weather_forecast(args.county)
        # 創建PyLatex物件
        doc = Document('output')
        # 填入內容
        fill_doc_preamble(doc, forecast_info)
        fill_document(doc, forecast_info)
        #產生PDF
        doc.generate_pdf('output', clean_tex=False)

    else:
        # 若不合法則結束
        print("輸入的縣市名稱不合法")