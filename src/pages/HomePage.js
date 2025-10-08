import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  Paper,
  Chip,
  LinearProgress,
  Alert,
  Divider,
} from '@mui/material';
import {
  PlayArrow,
  BookmarkBorder,
  SentimentVeryDissatisfied,
  Timer,
  EmojiPeople,
  FavoriteBorder,
  Warning,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();
  const [daysSincePublish, setDaysSincePublish] = useState(0);

  useEffect(() => {
    // 计算从2009年10月1日到现在的天数
    const publishDate = new Date('2009-10-01');
    const today = new Date();
    const days = Math.floor((today - publishDate) / (1000 * 60 * 60 * 24));
    setDaysSincePublish(days);
  }, []);

  const handleStartReading = () => {
    navigate('/chapters');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleContinueReading = () => {
    navigate('/chapter/1');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // 搞怪的随机吐槽语录
  const tucaoQuotes = [
    "江南：更新？那是什么？能吃吗？🤔",
    "路明非：S级废柴，吊车尾界的战斗机 ✈️",
    "楚子航：面瘫也是一种生活态度 😐",
    "恺撒：有钱真的可以为所欲为 💰",
    "诺诺学姐：那个衰小子好像还挺有意思的 😏",
    "芬格尔：师兄永远是你师兄，八卦永不停歇 🎮",
    "路鸣泽：哥哥，我可以给你力量哦～ 😈",
    "昂热：130岁还在带孩子，累不累啊 👴",
    "夏弥：我只是个卖拉面的小姑娘 🍜",
    "龙族完结？信你个鬼！😤",
  ];

  const [currentQuote, setCurrentQuote] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentQuote((prev) => (prev + 1) % tucaoQuotes.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 主标题区域 - 吐槽风格 */}
      <Box
        sx={{
          textAlign: 'center',
          mb: 4,
          background: 'linear-gradient(135deg, #434343 0%, #000000 100%)',
          borderRadius: 3,
          p: 4,
          color: 'white',
          border: '3px solid #ff6b6b',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          卡塞尔学院废柴生存指南
        </Typography>
        <Typography variant="h6" component="div" gutterBottom sx={{ opacity: 0.9 }}>
          <span style={{ textDecoration: 'line-through', opacity: 0.6 }}>龙族Ⅰ：火之晨曦</span>
          <span style={{ marginLeft: '10px', opacity: 0.8 }}>→ 江南老贼的拖更传奇</span>
        </Typography>
        <Typography variant="h5" component="h2" gutterBottom sx={{ opacity: 0.9 }}>
          出品：江南老贼 <SentimentVeryDissatisfied sx={{ ml: 1 }} />
          <Typography variant="caption" sx={{ display: 'block', mt: 0.5, fontStyle: 'italic' }}>
            （网文圈著名鸽王 | 15年磨一剑...还没磨完）
          </Typography>
        </Typography>
        <Typography variant="body1" sx={{ mt: 2, opacity: 0.8, fontStyle: 'italic' }}>
          "{tucaoQuotes[currentQuote]}"
        </Typography>
        
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Chip label="废柴逆袭" sx={{ bgcolor: '#ff6b6b', color: 'white' }} />
          <Chip label="拖更神作" sx={{ bgcolor: '#ffa500', color: 'white' }} />
          <Chip label="坑王之王" sx={{ bgcolor: '#4ecdc4', color: 'white' }} />
          <Chip label="还我绘梨衣" sx={{ bgcolor: '#ff1744', color: 'white' }} />
          <Chip label="面瘫传说" sx={{ bgcolor: '#536dfe', color: 'white' }} />
        </Box>
      </Box>

      {/* 催更进度条 */}
      <Alert severity="warning" sx={{ mb: 3, fontSize: '1.1rem' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Timer />
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" gutterBottom>
              距离《龙族Ⅰ》出版已过去 <strong>{daysSincePublish}</strong> 天
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={15} 
              sx={{ 
                height: 8, 
                borderRadius: 5,
                '& .MuiLinearProgress-bar': {
                  backgroundColor: '#ff1744',
                }
              }} 
            />
            <Typography variant="caption" sx={{ mt: 0.5, display: 'block' }}>
              龙族Ⅴ完成度：15% （数据纯属虚构，如有巧合，纯属巧合）
            </Typography>
          </Box>
        </Box>
      </Alert>

      {/* 主要内容区域 */}
      <Grid container spacing={4}>
        {/* 左侧：阅读控制 */}
        <Grid item xs={12} md={8}>
          <Card elevation={3} sx={{ mb: 3, border: '2px solid #ff6b6b' }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <EmojiPeople sx={{ fontSize: 40, color: '#ff6b6b' }} />
                <Typography variant="h4" component="h2">
                  开始你的废柴之旅
                </Typography>
              </Box>
              <Typography variant="body1" color="text.secondary" paragraph>
                路明非：一个S级混血种废柴的逆袭故事。
                <br />
                132个章节（原文131章 + AI续写1章），约26万字的青春热血。
                <br />
                <strong>警告</strong>：阅读本书可能导致以下症状：
              </Typography>
              
              <Box sx={{ pl: 2, mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  • 强烈的催更欲望 😤
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • 对作者的爱恨交织 😭
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • 想要一个绘梨衣 💕
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  • 羡慕楚子航的面瘫脸 😐
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<PlayArrow />}
                  onClick={handleStartReading}
                  sx={{ 
                    minWidth: 150,
                    bgcolor: '#ff6b6b',
                    '&:hover': {
                      bgcolor: '#ff5252',
                    }
                  }}
                >
                  开始入坑
                </Button>
                
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<BookmarkBorder />}
                  onClick={handleContinueReading}
                  sx={{ 
                    minWidth: 150,
                    borderColor: '#ff6b6b',
                    color: '#ff6b6b',
                    '&:hover': {
                      borderColor: '#ff5252',
                      bgcolor: 'rgba(255, 107, 107, 0.1)',
                    }
                  }}
                >
                  继续沦陷
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* 小说"简介" */}
          <Card elevation={3} sx={{ border: '2px solid #4ecdc4' }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" component="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Warning color="warning" />
                温馨提示（重要！）
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="h6" gutterBottom sx={{ color: '#ff6b6b' }}>
                📖 这本书讲了什么？
              </Typography>
              <Typography variant="body1" paragraph>
                路明非，一个普通到不能再普通的<strong>废柴</strong>高中生，
                突然收到了神秘的卡塞尔学院邀请信...
              </Typography>
              <Typography variant="body1" paragraph>
                然后他发现：
                <br />
                • 自己居然是S级混血种（虽然没卵用）
                <br />
                • 身边全是挂B（楚子航、恺撒、诺诺...）
                <br />
                • 世界上真的有龙（而且还得去屠）
                <br />
                • 最重要的是...他遇见了<strong style={{ color: '#ff1744' }}>绘梨衣</strong>
              </Typography>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom sx={{ color: '#ff6b6b' }}>
                🎭 主要角色（吐槽版）
              </Typography>
              <Box sx={{ pl: 2 }}>
                <Typography variant="body2" paragraph>
                  <strong>路明非</strong>：S级废柴，吊车尾，衰仔，却是命运之子（主角光环MAX）
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>楚子航</strong>：狮心会会长，面瘫剑圣，村雨爱好者，永远的高冷学长
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>恺撒</strong>：学生会主席，有钱任性，自恋狂，家里有矿的人生赢家
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>诺诺（陈墨瞳）</strong>：恺撒女友，狮心会副会长，红发御姐，好像对衰小子有点...
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>芬格尔</strong>：万年学长（已留级N年），八卦小天才，隐藏大佬，狗仔队专业户
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>路鸣泽</strong>：小魔鬼，路明非的"弟弟"，可以给你力量哦～😈
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>昂热</strong>：校长，130岁高龄还在当孩子王，屠龙世家的传奇
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>夏弥</strong>：卖拉面的小姑娘，路明非的青梅竹马...吗？🍜
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="body2" sx={{ fontStyle: 'italic', color: 'text.secondary', mt: 2 }}>
                注：本书阅读需谨慎，容易上头，后续更新遥遥无期。
                江南老贼的填坑能力？不存在的。
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* 右侧：吐槽统计 */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 3, mb: 3, border: '2px solid #ffa500' }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#ff6b6b' }}>
              📊 现状统计
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  总章节数
                </Typography>
                <Typography variant="body2" fontWeight="bold" sx={{ color: '#4ecdc4' }}>
                  132章
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  原文章节
                </Typography>
                <Typography variant="body2" fontWeight="bold">
                  131章
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  AI续写
                </Typography>
                <Typography variant="body2" fontWeight="bold" sx={{ color: '#ff6b6b' }}>
                  1章（我们替老贼写了）
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  总字数
                </Typography>
                <Typography variant="body2" fontWeight="bold">
                  约26万字
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  预计阅读时间
                </Typography>
                <Typography variant="body2" fontWeight="bold">
                  10小时（一口气读完）
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  催更天数
                </Typography>
                <Typography variant="body2" fontWeight="bold" sx={{ color: '#ff1744' }}>
                  {daysSincePublish}天
                </Typography>
              </Box>
            </Box>
          </Paper>

          <Paper elevation={3} sx={{ p: 3, mb: 3, border: '2px solid #ff1744' }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#ff1744' }}>
              📊 读者投票榜
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  #1 江南老贼快更新
                </Typography>
                <LinearProgress variant="determinate" value={100} sx={{ mt: 0.5, bgcolor: '#ffebee', '& .MuiLinearProgress-bar': { bgcolor: '#ff1744' } }} />
              </Box>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  #2 路明非别怂了
                </Typography>
                <LinearProgress variant="determinate" value={88} sx={{ mt: 0.5, bgcolor: '#fff3e0', '& .MuiLinearProgress-bar': { bgcolor: '#ffa500' } }} />
              </Box>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  #3 楚子航笑一个
                </Typography>
                <LinearProgress variant="determinate" value={5} sx={{ mt: 0.5, bgcolor: '#e3f2fd', '& .MuiLinearProgress-bar': { bgcolor: '#536dfe' } }} />
              </Box>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  #4 小魔鬼路鸣泽真实身份
                </Typography>
                <LinearProgress variant="determinate" value={92} sx={{ mt: 0.5, bgcolor: '#f3e5f5', '& .MuiLinearProgress-bar': { bgcolor: '#9c27b0' } }} />
              </Box>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  #5 芬格尔的秘密
                </Typography>
                <LinearProgress variant="determinate" value={75} sx={{ mt: 0.5, bgcolor: '#e8f5e9', '& .MuiLinearProgress-bar': { bgcolor: '#4caf50' } }} />
              </Box>
            </Box>
          </Paper>

          <Paper elevation={3} sx={{ p: 3, bgcolor: '#fffde7' }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#f57c00' }}>
              ⚠️ 入坑须知
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Typography variant="body2">
                ✓ 本书有毒，容易上头
              </Typography>
              <Typography variant="body2">
                ✓ 看完会想催更，但没用
              </Typography>
              <Typography variant="body2">
                ✓ 会对废柴产生认同感
              </Typography>
              <Typography variant="body2">
                ✓ 可能会爱上绘梨衣
              </Typography>
              <Typography variant="body2">
                ✓ 后续坑多，慎入
              </Typography>
              <Typography variant="body2" sx={{ mt: 1, fontWeight: 'bold', color: '#d32f2f' }}>
                ⚠️ 最重要的：做好等待龙族Ⅴ的心理准备
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* 底部吐槽区 */}
      <Box sx={{ mt: 4, textAlign: 'center', p: 3, bgcolor: '#fafafa', borderRadius: 2 }}>
        <Typography variant="body2" color="text.secondary">
          本站由龙族真爱粉制作，AI续写纯属娱乐，不代表官方内容
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          江南老贼，求求你了，写完吧！ 😭
        </Typography>
      </Box>
    </Container>
  );
};

export default HomePage;
