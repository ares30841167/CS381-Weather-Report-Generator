# CS381 一周天氣預報報表產生器

### 環境
- Windows 20H2 19042.1052
- ActivePerl v5.28.1
- MikTex 21.6
- Python 3.9.5

以上環境需要先被安裝

### 使用方法與需求
- 使用此程式時不能有**中文路徑**存在
- 需先安裝simhei、simkai字體兩個字體
- MiKTeX需要先安裝ctex套件以支援中文，執行時會跳出更多需要安裝的套件，請逐一安裝
- Python需要安裝pylatex、requests兩個套件

執行方法如下
```bash
python s1071546_final.py -c <要產生報表的縣市>
```
### 介紹

此程式主要功能為產生指定縣市的一周天氣預報，可提供其他旅遊應用作為模塊使用或者出差時可以使用此程式預先產生天氣報表

就像機長要飛航班時，也要先取得航路資料天氣一樣，此程式可以產出PDF報表，讓你快速取得一周天氣預報的可攜、可交換的文件，以利指派出差的部門給予資訊

### 實作細節

此程式會先到中央氣象局的API取得指定縣市的一周的天氣預報，並使用pylatex產生latex格式文檔，最後將其文檔轉為PDF輸出

```python=7
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--county", required= True, help="The city you want to generate the weather report.")

args = parser.parse_args()
```
> 此處為參數設定區

```python=12
# 合法縣市清單，用以檢查輸入
legal_input_list = ["宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣", "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市", "基隆市", "新竹縣", "新竹市", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", "屏東縣"]
```
> 合法縣市清單，用以檢查輸入

```python=15
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
```
> 去中央氣象局的API抓取天氣預報資料

```python=35
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
```
> 填寫Latex文件Preamble裡此次要用到的Packages、標題、作者、設定等等

```python=51
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
```
> 將天氣預報資料製成表格放入Latex文件當中

```python=94
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
```
> 主程式區

### 結果

以下為實際程式產生的文檔樣式，空格為API本身就沒有提供資訊
![](https://i.imgur.com/5jRDC0r.png)

![](https://i.imgur.com/PfqjpqL.png)

程式產生的LaTex部分文檔

![](https://i.imgur.com/Qxg8oYH.png)


### 參考
- 中央氣象局API: https://opendata.cwb.gov.tw/dist/opendata-swagger.html
- PyLaTeX: https://jeltef.github.io/PyLaTeX/current/index.html
- Requests: https://docs.python-requests.org/en/master/
- MikTex: https://miktex.org/
- ActivatePerl: https://www.activestate.com/products/perl/downloads/
- Python: https://www.python.org/
- ctex教學: 
    - https://jdhao.github.io/2018/03/29/latex-chinese.zh/#%E4%BD%BF%E7%94%A8-ctex
    - https://www.kancloud.cn/levey/windows/1003052
- simhei、simkai字體:
    - https://www.wfonts.com/font/simhei 
    - https://github.com/Halfish/lstm-ctc-ocr/blob/master/fonts/simkai.ttf