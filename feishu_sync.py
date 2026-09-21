import requests
import json
import os

# 从环境变量读取，不要硬编码在代码里
APP_ID = os.environ["FEISHU_APP_ID"]
APP_SECRET = os.environ["FEISHU_APP_SECRET"]
APP_TOKEN = os.environ["FEISHU_APP_TOKEN"]
TABLE_ID = os.environ["FEISHU_TABLE_ID"]

def get_tenant_access_token():
    """获取访问令牌，有效期 2 小时"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    resp = requests.post(url, json=payload)
    return resp.json().get("tenant_access_token")

def fetch_all_records(token):
    """分页拉取多维表格中的所有记录"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    all_items = []
    page_token = None

    while True:
        params = {"page_size": 500}
        if page_token:
            params["page_token"] = page_token
        resp = requests.get(url, headers=headers, params=params)
        data = resp.json().get("data", {})
        items = data.get("items", [])
        all_items.extend(items)
        if not data.get("has_more"):
            break
        page_token = data.get("page_token")

    return all_items

def transform(records):
    """把飞书返回的复杂结构转成前端友好的扁平 JSON"""
    result = []
    for r in records:
        fields = r.get("fields", {})
        result.append({
            "id": r.get("record_id"),
            "title": fields.get("标题", ""),
            "content": fields.get("内容", ""),
            "date": fields.get("日期", "")
        })
    return result

if __name__ == "__main__":
    token = get_tenant_access_token()
    if not token:
        print("获取 token 失败，请检查 App ID / App Secret")
        exit(1)

    records = fetch_all_records(token)
    data = transform(records)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已同步 {len(data)} 条记录到 data.json")
