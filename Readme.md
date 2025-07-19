# Some git command

>最好在git bash 中执行,git bash 与 linix 命令差不多

## 与 linix 相关
`mkdir <files name>` 新建文件夹

`touch <file name.xx>` 新建文件

`cd <files name>` 进入目录 files name

`cd ..` 回到上一级目录

`pwd` 显示当前目录路径

`ls/ll` 列出当前目录下的所有文件，"ll" 会更加详细

`rm <file name>` 删除文件file name

`rm -r <files name>` 删除文件夹 files name

`mv <file 1> <target path>` 移动 file1 至 target path 下的文件夹

`mv <file name 1> <file name 1>` 将文件file name 1 重命名为file name 2

`history` 查看命令历史

`clear` 清屏

`reset` 重新初始化终端

`help` 查看所有命令

`exit` 退出

## 与 git 相关

> 配置

`git config --system --list` 查看系统config

`git config --global  --list` 查看当前用户（global）配置

> 初始化文件

`git init` 为当前目录的文件夹初始化（本地初始化）

`git clone <github url>` 从 github 上克隆文件

> 修改文件
`git status` 查看目前修改上传状态

`git diff` 查看所有修改

`git add <file name>` 将指定文件的更改添加至暂存区

`git add .` 将所有文件的更改添加至暂存区

`git commit -m "信息提示"` 将缓存区里的所有文件添加至本地仓库

> 时光穿梭

`git log` 查看 commit 提交历史，只能查看当前版本之前的历史，可确定要回到哪个版本

`git reset --hard HEAD^` 回到上一个 commit 版本

`git reset --hard HEAD^^` 回到上上个 commit 版本，以此类推

`git reset --hard HEAD~100` 回到向上100个 commit 版本

`git reset --hard <版本号>` 跳转到版本号为<版本号>的版本

`git reflog` 查看所有本地仓库的变更历史 


`git pull `

`git push `