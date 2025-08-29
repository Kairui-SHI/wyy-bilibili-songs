# -*- coding: utf-8 -*-
import requests
import csv
import time
from netease_playlist_exporter import export_playlist

# wangyiyun playlist id
PLAYLIST_ID = "123456789" # 网易云歌单 ID

# bilibili user cookies
SESSDATA = "your SESSDATA"
BILI_JCT = "your BILI_JCT"
DEDEUSERID = "your DEDEUSERID"

# bilibili fav folder settings
title = "网易云歌单"  # 收藏夹名
intro = "空空如也"    # 收藏夹简介
privacy = int(1)     # 0公开, 1私密

headers = {
"User-Agent": "Mozilla/5.0",
"Cookie": f"SESSDATA={SESSDATA}; bili_jct={BILI_JCT}; DedeUserID={DEDEUSERID}"
}

def export_playlist(playlist_id):
    """
    Exports a NetEase Music playlist to a CSV file and returns the playlist as a list.

    Args:
        playlist_id: The ID of the playlist to export.
    
    Returns:
        A list of dictionaries, where each dictionary represents a song.
    """
    # 网易云歌单详情 API
    url = f"https://music.163.com/api/playlist/detail?id={playlist_id}"

    # 模拟浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
        "Referer": "https://music.163.com/",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": "os=pc"   # 强制 PC 环境 -- 导出全部歌曲
    }

    # 请求 API
    res = requests.get(url, headers=headers)
    data = res.json()

    # 输出 CSV 文件
    csv_filename = f"playlist_{playlist_id}.csv"
    playlist = []
    with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        
        for track in data['result']['tracks']:
            song_name = track['name']
            artists = ", ".join([ar['name'] for ar in track['artists']])
            writer.writerow([song_name, artists])
            playlist.append({"song_name": song_name, "artists": artists})

    print(f"已导出文件，保存至：{csv_filename}")
    return playlist

def create_fav_folder(sessdata, bili_jct, dedeuserid, title, intro="", privacy=0):
    """
    创建B站收藏夹
    :param sessdata: Cookie SESSDATA
    :param bili_jct: Cookie bili_jct (csrf)
    :param dedeuserid: Cookie DedeUserID
    :param title: 收藏夹名字
    :param intro: 收藏夹简介
    :param privacy: 0公开, 1私密
    """
    cookies = {
        "SESSDATA": sessdata,
        "bili_jct": bili_jct,
        "DedeUserID": dedeuserid
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bilibili.com/"
    }

    url = "https://api.bilibili.com/x/v3/fav/folder/add"
    data = {
        "title": title,
        "intro": intro,
        "privacy": privacy,
        "cover": "",
        "csrf": bili_jct
    }

    res = requests.post(url, headers=headers, cookies=cookies, data=data)
    return res.json()

# 搜索视频（按播放量排序）
def search_bilibili_video(keyword, limit=5):
    url = "https://api.bilibili.com/x/web-interface/search/type"
    params = {
        "search_type": "video",
        "keyword": keyword,
        "order": "click",  # 按播放量排序
        "page": 1
    }
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    if data.get("code") != 0:
        return []
    result = data["data"].get("result", [])
    return [{"bvid": v["bvid"], "title": v["title"], "play": v["play"]} for v in result[:limit]]

# BVID 转 AVID
def bvid_to_avid(bvid):
    url = "https://api.bilibili.com/x/web-interface/view"
    params = {"bvid": bvid}
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    if data.get("code") == 0:
        return data["data"]["aid"]
    return None

# 添加到收藏夹
def add_video_to_favorites(aid, fav_id):
    url = "https://api.bilibili.com/x/v3/fav/resource/deal"
    data = {
        "rid": aid,
        "type": 2,
        "add_media_ids": fav_id,
        "csrf": BILI_JCT
    }
    resp = requests.post(url, headers=headers, data=data)
    return resp.json()

def main():
    playlist = export_playlist(PLAYLIST_ID)
    songs = [f"{song['song_name']} {song['artists']}" for song in playlist]
    print("✅ Get songs successfully!")

    print("=== 创建B站收藏夹 ===")
    result = create_fav_folder(SESSDATA, BILI_JCT, DEDEUSERID, title, intro, privacy)
    if result.get("code") == 0:
        fid = result["data"]["id"]
        print(f"\n✅ 收藏夹创建成功! ID: {fid}")
    else:
        print("\n❌ 创建失败，请检查Cookie是否正确。")

    # 批量搜索 & 选最佳 & 批量收藏
    batch_size = 10
    for i in range(0, len(playlist), batch_size):
        batch = playlist[i:i+batch_size]
        batch_best = []
        for track in batch:
            keyword = f"完整版 {track['song_name']} {track['artists']}"
            videos = search_bilibili_video(keyword)
            filtered_videos = [v for v in videos if track['song_name'].lower() in v['title'].lower()]
            if filtered_videos:
                best = max(filtered_videos, key=lambda x: x["play"])
                aid = bvid_to_avid(best["bvid"])
                batch_best.append({
                    "aid": aid,
                    "title": best["title"],
                    "play": best["play"]
                })
                print(f"✅ {keyword}: 选择 {best['title']} (播放量 {best['play']})")
                time.sleep(0.3)  # 控制搜索频率

        for item in batch_best:
            result = add_video_to_favorites(item["aid"], fid)
            time.sleep(0.3)  # 控制收藏频率
        print(f"✅ 添加到收藏夹成功!")

if __name__ == "__main__":
    main()
