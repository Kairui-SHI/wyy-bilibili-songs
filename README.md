### 网易云歌单迁移至b站

##### Installation
只用到了几个标准库和requests，所以下个python再装个requests就好。
```bash
pip install requests
```

##### Usage
1. 网易云歌单ID：点击网易云歌单分享，把链接复制到一个地方，链接后面会有一串数字id
2. bilibili cookies：需要你网页版登录自己的b站号，然后F12查看需要的cookies：`SSDATA`、`BILI_JCT`、`DEDEUSERID`。可百度如何查看cookies
3. 一些b站创建新的收藏夹的设置，如：`title`、`intro`、`privacy`。也可以不管他之后b站上自己慢慢设置

##### Attention
1. 只是一个简单的脚本，没调用LLM，识别搜索不准是正常的，适合歌单曲目特别多，之后浏览一遍把失败的重新自己b站搜索选一个添加收藏夹就好。
2. 可能一些风格的音乐本来b站就不是很多，所以运行前可以看看自己常听的品类b站有没有人上传。
