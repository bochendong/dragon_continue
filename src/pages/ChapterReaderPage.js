import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  IconButton,
  Tooltip,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Fab,
  Backdrop,
  Chip,
} from '@mui/material';
import {
  ArrowBack,
  ArrowForward,
  ArrowUpward,
  ArrowDownward,
  Settings,
  BookmarkBorder,
  Bookmark,
  Share,
  MenuBook,
  Brightness4,
  Brightness7,
  AutoAwesome,
} from '@mui/icons-material';
import { useParams, useNavigate, useLocation } from 'react-router-dom';

const ChapterReaderPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [currentChapter, setCurrentChapter] = useState(null);
  const [chapterContent, setChapterContent] = useState('');
  const [fontSize, setFontSize] = useState(16);
  const [lineHeight, setLineHeight] = useState(1.6);
  const [theme, setTheme] = useState('light');
  const [showSettings, setShowSettings] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [progress, setProgress] = useState(0);
  const [hasNextChapter, setHasNextChapter] = useState(true);
  const [hasPrevChapter, setHasPrevChapter] = useState(true);

  // 加载章节数据
  useEffect(() => {
    const loadChapter = async () => {
      try {
        const chapterId = parseInt(id);
        const fileNum = String(chapterId).padStart(3, '0');
        
        // 确定文件名（001是特殊的"楔子：白帝城"，其他都是"未知章节"）
        let filename;
        if (chapterId === 1) {
          filename = `${fileNum}_楔子：白帝城.txt`;
        } else {
          filename = `${fileNum}_未知章节.txt`;
        }
        
        // URL编码文件名（处理特殊字符如冒号）
        const encodedFilename = encodeURIComponent(filename);
        
        const response = await fetch(`/chapters_2000_words/${encodedFilename}`);
        if (!response.ok) {
          throw new Error('Chapter not found');
        }
        
        const content = await response.text();
        
        // 检查是否返回了HTML（文件不存在）
        if (content.includes('<!DOCTYPE html>') || content.includes('<html')) {
          throw new Error('Chapter not found - got HTML instead');
        }
        
        // 解析章节内容
        const lines = content.split('\n');
        let title = `第${chapterId}章`;
        let wordCount = 0;
        let isAIGenerated = false;
        let chapterContent = '';
        
        // 提取标题
        for (let j = 0; j < Math.min(lines.length, 20); j++) {
          const line = lines[j].trim();
          if (line && 
              !line.includes('《龙族') && 
              !line.includes('作者：') &&
              !line.includes('══') &&
              !line.includes('字数统计') &&
              !line.includes('文件编号')) {
            if (line.match(/^第.*章/) || line.includes('：') || line.includes('章')) {
              title = line;
              // 限制标题长度
              if (title.length > 40) {
                title = title.substring(0, 40) + '...';
              }
              break;
            }
          }
        }
        
        // 提取字数统计
        const wordCountMatch = content.match(/字数统计：(\d+)\s*字/);
        if (wordCountMatch) {
          wordCount = parseInt(wordCountMatch[1]);
        }
        
        // 判断是否是AI生成（文件编号>=132）
        // 注意：文件编号001-131是原文，132开始是AI生成
        isAIGenerated = chapterId >= 132;
        
        // 提取正文内容
        let contentStarted = false;
        let contentLines = [];
        for (const line of lines) {
          const trimmed = line.trim();
          
          // 跳过头部信息
          if (!contentStarted) {
            if (trimmed && 
                !trimmed.includes('《龙族') &&
                !trimmed.includes('作者：') &&
                !trimmed.includes('══') &&
                trimmed !== title) {
              contentStarted = true;
              contentLines.push(line);
            }
          } else {
            // 跳过尾部分隔符和统计信息
            if (trimmed === '═' || trimmed.includes('字数统计') || trimmed.includes('文件编号')) {
              break;
            }
            contentLines.push(line);
          }
        }
        
        chapterContent = contentLines.join('\n').trim();
        
        setCurrentChapter({
          id: chapterId,
          title: title,
          wordCount: wordCount || 2000,
          isAIGenerated: isAIGenerated,
          filename: filename
        });
        setChapterContent(chapterContent);
        
      } catch (error) {
        console.error('Failed to load chapter:', error);
        // 使用模拟数据作为后备
        const mockChapter = {
          id: parseInt(id),
          title: id === '1' ? '楔子：白帝城' : `第${id}章`,
          wordCount: Math.floor(Math.random() * 400) + 1800,
          content: generateMockContent(),
        };
        
        setCurrentChapter(mockChapter);
        setChapterContent(mockChapter.content);
      }
    };
    
    loadChapter();
  }, [id]);

  // 检测上一章和下一章是否存在
  useEffect(() => {
    const checkAdjacentChapters = async () => {
      const chapterId = parseInt(id);
      
      // 检测上一章
      if (chapterId > 1) {
        const prevFileNum = String(chapterId - 1).padStart(3, '0');
        const prevFilename = chapterId === 2 ? '001_楔子：白帝城.txt' : `${prevFileNum}_未知章节.txt`;
        const encodedPrevFilename = encodeURIComponent(prevFilename);
        try {
          const response = await fetch(`/chapters_2000_words/${encodedPrevFilename}`);
          const content = await response.text();
          setHasPrevChapter(response.ok && !content.includes('<!DOCTYPE html>'));
        } catch {
          setHasPrevChapter(false);
        }
      } else {
        setHasPrevChapter(false);
      }
      
      // 检测下一章
      const nextFileNum = String(chapterId + 1).padStart(3, '0');
      const nextFilename = chapterId === 0 ? '001_楔子：白帝城.txt' : `${nextFileNum}_未知章节.txt`;
      const encodedNextFilename = encodeURIComponent(nextFilename);
      try {
        const response = await fetch(`/chapters_2000_words/${encodedNextFilename}`);
        const content = await response.text();
        // 检查是否是真实文件（不是HTML）
        setHasNextChapter(response.ok && !content.includes('<!DOCTYPE html>'));
      } catch {
        setHasNextChapter(false);
      }
    };
    
    checkAdjacentChapters();
  }, [id]);

  // 监听路由变化，自动滚动到顶部
  useEffect(() => {
    // 延迟滚动，确保内容已渲染
    const timer = setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
    
    return () => clearTimeout(timer);
  }, [location.pathname]);

  // 生成模拟内容
  const generateMockContent = () => {
    return `
    "哥哥……"有人在黑暗里轻声地呼喊。
    
    真烦！谁家的小孩跑丢了？
    
    "哥哥。"孩子又喊。
    
    真烦真烦真烦！哥哥？这里没有！
    
    "哥哥……那我走啦……"孩子低声说，声音渐渐远去。
    
    他心里忽然有点不忍心，那个渐渐远去的声音，透着一股孤单，让人想到那个孩子远去的背影，像只被抛弃的小猎犬。
    
    "好啦好啦好啦！你家住哪街哪号哪门？你那个靠不住的哥哥叫什么名字？我送你回家！"他翻身坐了起来。
    
    他在阳光中席地而坐，一袭白衣皎洁如月，所见的是一朵白色的茶花在粗瓷瓶中盛放，隔着那支花，白衣的孩子手持一管墨笔伏案书写，一笔一划。
    
    "喂，你没走啊？你耍我的吧？"他想说，却没有说。
    
    他很自然地做了一件事，桌上有盘青翠欲滴的葡萄，他从里面摘下一小串，隔着桌子递给那个孩子。
    
    孩子抬起头来，眼睛里闪动着惊慌，像是警觉的幼兽，"哥哥，外面有很多人。"
    
    鬼扯吧？这么安静的。他想。
    
    可是自然而然地，他说了另一句话，"也许会死吧？但是，康斯坦丁，不要害怕。"
    
    "不害怕，和哥哥在一起，不害怕……可为什么……不吃掉我呢？吃掉我，什么样的牢笼哥哥都能冲破。"孩子认真地说。
    
    吃掉……你？虽然你长得很白嫩，但是绝不代表你比汉堡好吃啊，我中午才吃了一个汉堡，一点不饿。他想。
    
    "你是很好的食物，可那样就太孤单了，几千年里，只有你和我在一起。"再一次，他说出了言不由衷的话。
    
    "可是死真的让人很难过，像是被封在一个黑盒子里，永远永远，漆黑漆黑……像是在黑夜里摸索，可伸出的手，永远触不到东西……"
    
    "所谓弃族的命运，就是要穿越荒原，再次竖起战旗，返回故乡。死不可怕，只是一场长眠。在我可以吞噬这个世界之前，与其孤独跋涉，不如安然沉睡。我们仍会醒来。"真不敢相信，这么拉风的台词，居然会出于他的嘴里。
    
    "哥哥……竖起战旗，吞噬世界的时候，你会吃掉我么？"孩子看着他，澄澈的瞳子里闪动着……期待。
    
    见鬼！这是什么"我们是相亲相爱的食人族一家"的话剧桥段么？可你们的家庭伦理真的好奇怪！
    
    "会的，那样你就将和我一起，君临世界！"可他轻轻地点头，声音里透着冷硬的威严。
    
    孩子从水壶里倒了一杯水，递给了他，他茫然地喝了下去。
    
    "我要走了，哥哥，再见。"孩子站了起来。
    
    他想说我不是你哥哥你认错人了，但他也只是随口说，"再见，自己小心，人类，是不能相信。"
    
    又是句奇怪的台词，没头没脑的。
    
    孩子出门去了，在背后带上了门。他听着孩子的脚步声越来越远，最后完全消失了。
    
    他忽然有点害怕，他想自己真是昏头了，那么小的一个孩子，放他自己去街上走，给人拐跑了怎么办？不知道他得走多远的路才能找到哥哥。他变得坐立不安，终于忍不住的时候，他起身往门口跑去。
    
    他推开了门，炽烈的光照在他的白衣上，不是阳光，而是火光。燎天的烈焰中，城市在哭嚎，焦黑的人形在火中奔跑，成千上万的箭从天空里坠落，巨大的牌匾燃烧着、翻转着坠落，上面是"白帝"两个字，简直是地狱。
    
    城市的正中央，立着一根高杆，孩子被挂在高杆顶上，闭着眼睛，整个城市的火焰，都在灼烧他。
    
    像是一场盛大的献祭。
    
    心里真痛啊，真像是有把刀在割。什么重要的人就此失去了，因为他犯了错误。
    
    他忽然想起一件事来，确实没错，他就是个孩子的哥哥。
    
    "康斯……坦丁。"他喊出了那个名字。
    
    他猛地坐起，在下午的阳光中睁开眼睛，呼吸急促，全身都是冷汗，外面是高架轻轨经过的噪音。
    
    他忽然觉得这声音那么悦耳，提醒他梦中的一切都是假的，他所在的，只是普普通通的人世。
    `;
  };

  const handlePreviousChapter = () => {
    if (currentChapter && hasPrevChapter) {
      navigate(`/chapter/${currentChapter.id - 1}`);
    }
  };

  const handleNextChapter = () => {
    if (currentChapter && hasNextChapter) {
      navigate(`/chapter/${currentChapter.id + 1}`);
    }
  };

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked);
  };

  const handleShare = () => {
    // 实现分享功能
    if (navigator.share) {
      navigator.share({
        title: currentChapter?.title,
        text: '我正在阅读《龙族Ⅰ火之晨曦》',
        url: window.location.href,
      });
    } else {
      // 复制链接到剪贴板
      navigator.clipboard.writeText(window.location.href);
    }
  };

  const handleScroll = () => {
    const scrollTop = window.pageYOffset;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = (scrollTop / docHeight) * 100;
    setProgress(scrollPercent);
  };

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  if (!currentChapter) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography>加载中...</Typography>
      </Container>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: theme === 'dark' ? '#121212' : '#f5f5f5' }}>
      {/* 顶部导航栏 */}
      <Paper elevation={2} sx={{ position: 'sticky', top: 0, zIndex: 1000 }}>
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate('/chapters')}
          >
            返回章节列表
          </Button>
          
          <Box sx={{ flexGrow: 1, textAlign: 'center', mx: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
            <Typography variant="h6">
              {currentChapter.title}
            </Typography>
            {currentChapter.isAIGenerated && (
              <Tooltip title="AI生成章节">
                <Chip 
                  icon={<AutoAwesome />} 
                  label="AI" 
                  color="success" 
                  size="small"
                />
              </Tooltip>
            )}
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton onClick={handleBookmark}>
              {isBookmarked ? <Bookmark color="primary" /> : <BookmarkBorder />}
            </IconButton>
            <IconButton onClick={handleShare}>
              <Share />
            </IconButton>
            <IconButton onClick={() => setShowSettings(true)}>
              <Settings />
            </IconButton>
          </Box>
        </Box>
        
        {/* 阅读进度条 */}
        <Box sx={{ width: '100%', height: 4, backgroundColor: 'grey.200' }}>
          <Box
            sx={{
              height: '100%',
              backgroundColor: 'primary.main',
              width: `${progress}%`,
              transition: 'width 0.1s ease',
            }}
          />
        </Box>
      </Paper>

      {/* 章节内容 */}
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Card elevation={3}>
          <CardContent sx={{ p: 4 }}>
            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              sx={{ textAlign: 'center', mb: 4 }}
            >
              {currentChapter.title}
            </Typography>
            
            <Typography
              variant="body1"
              component="div"
              sx={{
                fontSize: `${fontSize}px`,
                lineHeight: lineHeight,
                textAlign: 'justify',
                whiteSpace: 'pre-wrap',
                '& p': {
                  mb: 2,
                },
              }}
            >
              {chapterContent}
            </Typography>
          </CardContent>
        </Card>

        {/* 章节导航 */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            variant="outlined"
            startIcon={<ArrowUpward />}
            onClick={handlePreviousChapter}
            disabled={!hasPrevChapter}
          >
            上一章
          </Button>
          
          <Button
            variant="outlined"
            onClick={() => navigate('/chapters')}
            startIcon={<MenuBook />}
          >
            章节列表
          </Button>
          
          <Button
            variant="outlined"
            endIcon={<ArrowDownward />}
            onClick={handleNextChapter}
            disabled={!hasNextChapter}
          >
            下一章
          </Button>
        </Box>
      </Container>

      {/* 设置面板 */}
      <Backdrop open={showSettings} sx={{ zIndex: 1300 }}>
        <Paper sx={{ p: 3, maxWidth: 400, width: '90%' }}>
          <Typography variant="h6" gutterBottom>
            阅读设置
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>字体大小</Typography>
            <Slider
              value={fontSize}
              onChange={(e, value) => setFontSize(value)}
              min={12}
              max={24}
              step={1}
              marks
              valueLabelDisplay="auto"
            />
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>行间距</Typography>
            <Slider
              value={lineHeight}
              onChange={(e, value) => setLineHeight(value)}
              min={1.2}
              max={2.0}
              step={0.1}
              marks
              valueLabelDisplay="auto"
            />
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <FormControl fullWidth>
              <InputLabel>主题</InputLabel>
              <Select
                value={theme}
                label="主题"
                onChange={(e) => setTheme(e.target.value)}
              >
                <MenuItem value="light">
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Brightness7 sx={{ mr: 1 }} />
                    浅色主题
                  </Box>
                </MenuItem>
                <MenuItem value="dark">
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Brightness4 sx={{ mr: 1 }} />
                    深色主题
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>
          </Box>
          
          <Button
            variant="contained"
            fullWidth
            onClick={() => setShowSettings(false)}
          >
            确定
          </Button>
        </Paper>
      </Backdrop>

      {/* 浮动操作按钮 */}
      <Fab
        color="primary"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      >
        <ArrowUpward />
      </Fab>
    </Box>
  );
};

export default ChapterReaderPage;
