# pbxproj_parse

##Requirements
此python脚本用于检查iOS多Target工程缺失勾选的.m或者.xib文件，预防项目运行时因找不到相应文件引发crash的问题

##使用命令
打开shell终端输入命令：python python文件路径 -p 索引文件路径 例如：
 
```
python /Users/shangshangqian/Desktop/2018.8.17-2018.8.20/ios_logs2/data/pbxproj_parse.py -p /Users/shangshangqian/Desktop/Joywok10/joywok/joywok.xcodeproj/project.pbxproj

```

解析完成后会有如下输出

正在解析pbxproj...

解析完成

 ===================================================== 
 
 分析文件路径:/Users/shangshangqian/statistic.json 
 
 ===================================================== 

其中statistic.json文件内容为每个target没有勾选的编译文件