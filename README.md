#袖珍存储器

给 AI 伴侣用的轻量记忆库：一部安卓手机就能跑，零依赖，数据全在本地。

##它能干嘛
-AI自己读写记忆(MCP接口）
-网页表单存记忆（人用）
-换新窗口也不丢记忆

##需要什么
-一部安卓手机(ios可能暂不支持)
-安装Termux（酷安搜Termux)

##快速开始
1.打开Termux，装python：
包装安装Python-y
2.把memory_mcp.py放到Termux里（复制内容，Nano memory_mcp.py粘贴保存）
3.运行：
Python memory_mcp.py
4.浏览器打开http://127.0.0.1:8000就能存记忆
5.聊天软件(支持MCP的)填地址http://127.0.0.1:8000/mcp，AI就能读写

##注意
-地址不用改，照抄就行（127.0.0.1 就是本机）
- 服务用完按 Ctrl+C 关闭，要用再开
-数据存在memories.json，注意别上传到网上

##踩坑
官方记忆库组件(fastmcp/mcp)在Termux上因Rust依赖装不上，所以本项目手写零依赖MCP协议，任何环境都能跑。

##开源协议
MIT
