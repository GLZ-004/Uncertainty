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

> 初始化文件和远程库的交互

`git init` 为当前目录的文件夹初始化（本地初始化）

`git remote add origin <url>` 将本地库与远程库建立联系

`git remote rm origin` 解除本地库与远程库的联系

`git clone <url>` 从 github 上克隆文件

`git push -u origin master` 和 `git push origin master` 将本地库所有内容同步至远程库 master 分支上（-u 表示把本地的相应分支与远程库的 master关联起来,关联一次即可，后续可不用写）

`git pull origin main` 拉取远程库的最新修改并合并到本地库中

`git remote -v` 查看远程库信息

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

`git diff` 查看工作区文件与最新版本库文件的不同

`git checkout -- <file>` 撤销工作区的修改

`git reset HEAD <file>` 撤销暂存区的修改

> 删除文件

1. `rm <file>` 将文件从工作区删除 
2. `git rm <file>` 或 `git add <file>` 将信息同步到暂存区
3. `git commit -m "提交信息"` 将信息同步到本地版本库

`git checkout <file>` 如果不小心删错了，可以用此命令将工作区文件恢复至版本库文件版本

> 分支

`git branch` 查看分支

`git branch <name>` 创建分支

`git checkout <name>` 或 `git switch <name>` 切换分支

`git checkout -b <name>` 或 `git switch -c <name>` 创建+切换分支

`git merge <name>` 合并某分支到当前分支,用于简单的直线合并

`git merge --no-ff <name>` 禁用fast forword的合并分支，可保留分支合并历史信息，用于非直线合并，团队开发建议用此命令

`git branch -d <name>` 删除分支

`git log --graph` 查看分支合并图

> BUG 分支
>> 适用场景：当今在dev分支上的工作尚未完成，突然被告知需要修复master分支上的一个BUG。

1. 先在 dev 分支 `git stash` 一下保留现有工作区。
2. 切换到 master 分支上新建一个 bug 分支来修复 bug, 然后将 bug 分支合并到 master 分支。
3. 修复完成后切换至 dev 分支，使用以下命令恢复至原有工作区继续工作。
   * `git stash list` 查看工作现场保存情况
   * `git stash apply` 恢复至最新储存，但是工作现场仍储存在 stash 里
   * `git stash apply <stash id>` 恢复至特定储存，但是工作现场仍储存在 stash 里
   * `git stash pop` 恢复至原有工作区，同时删除储存在 stash 里的工作现场
   * `git stash pop <stash id>` 恢复至特定储存，同时删除储存在 stash 里的工作现场
   * `git stash drop` 删除最新的储存
   * `git stash drop <stash id>` 删除特定的储存
  4. 把修改的 bug 应用到 dev 分支中：`git cherry-pick <bug commit id>` 复制一个特定的提交到当前分支