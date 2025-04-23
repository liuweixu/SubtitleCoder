# SubtitleCoder
## 特别说明：
推荐使用的视频软件：MPV。
一些方法作废，比如从中文字幕对齐分辨率等，这个是只有potplayer出现的问题，而MPV则是不需要。

## 主要介绍
该软件主要分为四个主要功能：

1. 对中日双语视频MKV或ASS字幕文件中提取为相应的中文或日文字幕文件（ass或srt），并且可以自定义字幕轨道、提取后字幕大小等信息。
2. 对一个文件夹内的所有srt字幕文件，根据自己输入style样式或者调整样式参数，从而将srt文件转为ass文件。
3. 参考中文ass字幕，使用alass和ffmpeg对日语srt字幕文件进行对齐。
4. ASS文件处理工具，分为三个小功能：修改ScaledBorderAndShadow的参数、修改ass样式的字体名称和借助输入样式参数修改ass样式。
   
### 名词解释：  
- **字幕轨道：** 视频中的轨道信息指的是mkv、mp4等视频中，往往有多个轨道，分别指的是图像、音频、字幕（主要是mkv）等， 这也是[MKVToolNix](https://mkvtoolnix.download/)和本软件提取字幕的核心根据。查看字幕的轨道信息可以用[MKVToolNix](https://mkvtoolnix.download/)来查看，一般而言，在大部分的中日双语、简繁、简体等动漫上，简体字幕的轨道ID为2，繁体字幕的轨道ID为3，故而本软件在字幕轨道上是默认设置为2，不过也有特殊例子，比如比如悠哉日常大王第二季繁日字幕版本中，繁体字幕轨道就是0，无简体字幕轨道，会导致软件提取字幕失败。所以如果提取字幕失败，建议用[MKVToolNix](https://mkvtoolnix.download/)查看字幕具体的轨道信息，然后在本软件中调整字幕轨道ID即可。

- **ASS字幕样式：** 在一般的ass文件中，均有[Script Info]、[V4+ Styles]和[Events]三大要素：

  1. 在[Script Info]，一般开始就是字体名称的定义，然后就是标题，缩放，分辨率等样式。
  2. 在[V4+ Styles]，就是字体样式定义，主要有样式名字（在后续的Events中用上）、字体名称、字体大小、字体颜色等不少样式。
  3. [Events]，这地方主要放字幕文本，其中有上述的样式名字，就是可以根据样式名字所对应的字体样式不同，从而让相应的文本显示不同的样式。

  **style样式：** mkv视频中ass字幕显示中，这部分样式的设定至关重要。style样式定义有：

  ```css
  Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
  ```

  这部分在[V4+ Styles]中，从中可以看出第一个是样式名字，第二个是字体名称，接下来就是字体大小、字体颜色等等，比较多样。

  然后，一般而言，正常的动漫字幕会根据OP、ED和文本，以及中文简繁体字幕的不同，有设定不同的样式，现在为了方便处理，在第二个和第三个功能界面中，均只设置一行样式，即专门针对日语ass字幕的字体样式。

  接下来针对日语ass字幕的字体样式中，我搜集了几个比较合适的样式，方便大家使用：

  - Style: Dial_JP,FOT-UDKakugo_Large Pr6N B,72,&H00FFFFFF,&H000000FF,&H28131390,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,2,1
  - Style: Dial_JP,FOT-Seurat ProN B,72,&H00FFFFFF,&HFFFFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,2,1
  - Style: Dial_JP,FOT-Seurat ProN B,72,&H006601FD,&H000000FF,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,1,3,0,2,10,10,10,1
  - Style: Dial_JP,FOT-Seurat ProN B,72,&H00FFFFFF,&H000000FF,&H005051E0,&H00000000,0,0,0,0,100,100,0,0,1,3,0,2,10,10,10,1
  - Style: Dial_JP,FOT-Seurat ProN B,65.0,&H0000008A,&H00FFFFFF,&H00EBEBEB,&H00EBEBEB,0,0,0,0,100.0,100.0,3.0,0.0,1,3.0,0.0,2,22,22,22,1
  - Style: Dial_JP,FOT-Seurat ProN DB,60.0,&H00FFFFFF,&H00FFFFFF,&H00E88600,&H00E88600,0,0,0,0,100.0,100.0,0.0,0.0,1,3.0,0.5,2,10,10,15,1
  - Style: Dial_JP,A-OTF Maru Folk Pro B,70,&H00FFFFFF,&H000000FF,&H31B050F4,&H00000000,-1,0,0,0,100,100,1,0,1,3,0,2,10,10,12,128
  - Style: Dial_JP,FOT-Humming ProN,70,&H00FFFFFF,&H000000FF,&H00705E5B,&H00000000,0,0,0,0,100,100,0,0,1,2.2,0,2,15,15,32,1

  本软件中，只需要在界面中ass样式输入位置时（第二个模块），直接把其中一个拷贝进去就行，也可以输入其他的


## 说明：

#### 1. 查找字幕说明

在搜集字幕中，尽量找简繁日内封或外挂的视频，这样处理会十分方便（甚至不需要本软件）。因为网上找的日语字幕大部分是srt，所以就需要尝试用本软件转换为相应的ass字幕，但是这引出一个新的问题：不同字幕组所制作的字幕所针对的视频来源可能不同，有的是BD，有的是WEB，甚至是有的对视频修改的，所以如果日语srt字幕与视频版本信息（或中文字幕）差距过大，有一定概率存在时间轴不对齐的问题，哪怕使用FFmpeg等都没法自动对齐，不过这情况比较少见，因为不少动漫的网上日语字幕来源比较多样，至少会有一种比较合适的，即可以找到不需要调轴就能用，或者调轴后可以正常使用。

调轴（自动对齐）工具：
- [SubRenamer](https://github.com/qwqcode/SubRenamer) ：该工具原理是根据视频中包含的音频，对字幕进行时间轴的调整。
- 本应用的第三个模块：该模块是使用alass和ffmpeg，根据相应中文ass字幕，对日语srt字幕文件进行时间轴的对齐。

查找日语字幕推荐网址：

-  [Jimaku](https://jimaku.cc/)
- [喵萌奶茶屋](https://github.com/Nekomoekissaten-SUB/Nekomoekissaten-Subs)

如果想查找中文字幕：

- [喵萌奶茶屋](https://github.com/Nekomoekissaten-SUB/Nekomoekissaten-Subs)
- [Anime字幕论坛](https://bbs.acgrip.com/)

#### 2. 内封和内嵌特殊说明

一般而言，简繁日内封、简日内封、繁日内封、简繁日外挂、简日外挂、繁日外挂这几种情况都可以直接提取字幕信息，因为是软字幕，在PotPlayer等视频观看时，可以直接复制字幕。

但是如果是MP4这样硬字幕中，就没法提取字幕轨道，而且也没法复制，解决方法只能是网上找字幕或者使用OCR方法提取字幕。而内嵌就是这种情况，有的字幕组发简日内嵌MKV，尽管是MKV视频，但是字幕还是硬字幕。

#### 3. 安装软件说明
- 需要安装MKVToolNix。
- 需要安装alass和ffmpeg。


# 反馈

如果大家使用过程中有反馈，可以通过Issue反馈，或者发邮件给wei_xu_liu@163.com反馈，十分感谢。

# 未来修改计划
待定...

# 致谢

- [MKVToolNix](https://mkvtoolnix.download/) （灵感源泉之一）
- [VideoCaptioner](https://github.com/WEIFENG2333/VideoCaptioner) （灵感源泉之一）
- [【已完结】PySide6百炼成真，带你系统性入门Qt](https://www.bilibili.com/video/BV1c84y1N7iL/?spm_id_from=333.1387.favlist.content.click&vd_source=601da5164f2780fc668c82ddd0d54bcf) （b站上的PySide6学习视频）
- [SubRenamer](https://github.com/qwqcode/SubRenamer)

