import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Search,
  ViewList,
  Apps,
  BookmarkBorder,
  Bookmark,
  ArrowUpward,
  ArrowDownward,
  AutoAwesome,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const ChapterListPage = () => {
  const navigate = useNavigate();
  
  const [chapters, setChapters] = useState([]);
  const [filteredChapters, setFilteredChapters] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');
  const [viewMode, setViewMode] = useState('grid');
  const [bookmarkedChapters, setBookmarkedChapters] = useState(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const chaptersPerPage = 12;

  // 从文件系统加载章节
  useEffect(() => {
    const loadChapters = async () => {
      try {
        setLoading(true);
        const chapterList = [];
        
        // 读取chapters_2000_words目录下的所有章节文件
        // 从001开始，遇到不存在的文件就停止
        let i = 1;
        while (true) {
          const fileNum = String(i).padStart(3, '0');
          
          // 确定文件名（001是特殊的"楔子：白帝城"，其他都是"未知章节"）
          let filename;
          if (i === 1) {
            filename = `${fileNum}_楔子：白帝城.txt`;
          } else {
            filename = `${fileNum}_未知章节.txt`;
          }
          
          try {
            // 尝试读取文件
            const response = await fetch(`/chapters_2000_words/${filename}`);
            if (!response.ok) {
              // 如果文件不存在，停止读取
              console.log(`✅ 共加载了 ${chapterList.length} 个章节（001-${String(i-1).padStart(3, '0')}）`);
              break;
            }
            
            const content = await response.text();
            
            // 检查是否真的是文本文件（而不是返回的index.html）
            if (content.includes('<!DOCTYPE html>') || content.includes('<html')) {
              // 这是HTML页面，不是文本文件，说明文件不存在
              console.log(`✅ 共加载了 ${chapterList.length} 个章节（001-${String(i-1).padStart(3, '0')}）`);
              break;
            }
            
            // 解析章节内容
            const lines = content.split('\n');
            let title = `第${i}章`;
            let wordCount = 0;
            let isAIGenerated = false;
            
            // 提取标题（通常在第6行附近，跳过头部）
            for (let j = 0; j < Math.min(lines.length, 20); j++) {
              const line = lines[j].trim();
              if (line && 
                  !line.includes('《龙族') && 
                  !line.includes('作者：') &&
                  !line.includes('══') &&
                  !line.includes('字数统计') &&
                  !line.includes('文件编号')) {
                // 检查是否是章节标题
                if (line.match(/^第.*章/) || line.includes('：') || line.includes('章')) {
                  title = line;
                  // 限制标题长度，避免过长
                  if (title.length > 30) {
                    title = title.substring(0, 30) + '...';
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
            
            // 判断是否是AI生成的章节（文件编号>=132）
            // 注意：文件编号001-131是原文，132开始是AI生成
            isAIGenerated = i >= 132;
            
            // 提取描述（取正文前100字）
            let description = '';
            let contentStarted = false;
            let descLines = [];
            for (const line of lines) {
              const trimmed = line.trim();
              if (contentStarted) {
                if (trimmed && !trimmed.includes('═') && !trimmed.includes('字数统计')) {
                  descLines.push(trimmed);
                  if (descLines.join('').length >= 100) {
                    break;
                  }
                }
              } else if (trimmed && 
                         !trimmed.includes('《龙族') &&
                         !trimmed.includes('作者：') &&
                         !trimmed.includes('══') &&
                         !trimmed.includes('第') &&
                         !trimmed.includes('章')) {
                contentStarted = true;
                descLines.push(trimmed);
              }
            }
            description = descLines.join('').substring(0, 100) + '...';
            
            chapterList.push({
              id: i,
              title: title,
              wordCount: wordCount || 2000, // 默认2000字
              chapter: i === 1 ? '楔子' : `第${Math.ceil(i/10)}幕`,
              description: description,
              isAIGenerated: isAIGenerated,
              filename: filename
            });
            
            i++; // 继续下一个文件
            
          } catch (error) {
            // 如果读取失败，跳出循环
            console.log(`❌ 读取失败于文件 ${i}: ${error.message}`);
            break;
          }
        }
        
        console.log(`Loaded ${chapterList.length} chapters`);
        setChapters(chapterList);
        setFilteredChapters(chapterList);
      } catch (error) {
        console.error('Failed to load chapters:', error);
        // 如果失败，使用模拟数据
        loadMockData();
      } finally {
        setLoading(false);
      }
    };
    
    // 模拟数据作为后备
    const loadMockData = () => {
      const mockChapters = [];
      for (let i = 1; i <= 131; i++) {
        mockChapters.push({
          id: i,
          title: i === 1 ? '楔子：白帝城' : `第${i}章`,
          wordCount: Math.floor(Math.random() * 400) + 1800,
          chapter: i === 1 ? '楔子' : `第${Math.ceil(i/10)}幕`,
          description: '章节内容加载中...',
          isAIGenerated: false,
          filename: `${String(i).padStart(3, '0')}_未知章节.txt`
        });
      }
      setChapters(mockChapters);
      setFilteredChapters(mockChapters);
    };
    
    loadChapters();
  }, []);

  // 搜索功能
  useEffect(() => {
    const filtered = chapters.filter(chapter =>
      chapter.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      chapter.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    // 排序
    const sorted = [...filtered].sort((a, b) => {
      if (sortOrder === 'asc') {
        return a.id - b.id;
      } else {
        return b.id - a.id;
      }
    });
    
    setFilteredChapters(sorted);
    setCurrentPage(1);
  }, [chapters, searchTerm, sortOrder]);

  // 分页
  const totalPages = Math.ceil(filteredChapters.length / chaptersPerPage);
  const startIndex = (currentPage - 1) * chaptersPerPage;
  const endIndex = startIndex + chaptersPerPage;
  const currentChapters = filteredChapters.slice(startIndex, endIndex);

  const handleChapterClick = (chapterId) => {
    navigate(`/chapter/${chapterId}`);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleBookmark = (chapterId) => {
    setBookmarkedChapters(prev => {
      const newSet = new Set(prev);
      if (newSet.has(chapterId)) {
        newSet.delete(chapterId);
      } else {
        newSet.add(chapterId);
      }
      return newSet;
    });
  };

  const getChapterTypeColor = (chapter) => {
    if (chapter.chapter === '楔子') return 'primary';
    if (chapter.chapter.includes('幕')) return 'secondary';
    return 'default';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 页面标题 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          章节列表
        </Typography>
        <Typography variant="body1" color="text.secondary">
          共 {filteredChapters.length} 个章节，选择您想要阅读的章节
        </Typography>
        <Box sx={{ mt: 1, display: 'flex', gap: 2 }}>
          <Chip 
            icon={<AutoAwesome />} 
            label={`AI生成: ${chapters.filter(c => c.isAIGenerated).length} 章`} 
            color="success" 
            variant="outlined" 
            size="small"
          />
          <Chip 
            label={`原文: ${chapters.filter(c => !c.isAIGenerated).length} 章`} 
            variant="outlined" 
            size="small"
          />
        </Box>
      </Box>

      {/* 搜索和过滤控制 */}
      <Card elevation={2} sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                placeholder="搜索章节..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            
            <Grid item xs={12} sm={3} md={2}>
              <FormControl fullWidth>
                <InputLabel>排序</InputLabel>
                <Select
                  value={sortOrder}
                  label="排序"
                  onChange={(e) => setSortOrder(e.target.value)}
                >
                  <MenuItem value="asc">
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <ArrowUpward sx={{ mr: 1 }} />
                      正序
                    </Box>
                  </MenuItem>
                  <MenuItem value="desc">
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <ArrowDownward sx={{ mr: 1 }} />
                      倒序
                    </Box>
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={3} md={2}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Tooltip title="网格视图">
                  <IconButton
                    onClick={() => setViewMode('grid')}
                    color={viewMode === 'grid' ? 'primary' : 'default'}
                  >
                    <Apps />
                  </IconButton>
                </Tooltip>
                <Tooltip title="列表视图">
                  <IconButton
                    onClick={() => setViewMode('list')}
                    color={viewMode === 'list' ? 'primary' : 'default'}
                  >
                    <ViewList />
                  </IconButton>
                </Tooltip>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* 章节列表 */}
      <Grid container spacing={2}>
        {currentChapters.map((chapter) => (
          <Grid item xs={12} sm={6} md={4} key={chapter.id}>
            <Card
              elevation={2}
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                cursor: 'pointer',
                transition: 'all 0.2s',
                position: 'relative',
                border: chapter.isAIGenerated ? '2px solid' : 'none',
                borderColor: chapter.isAIGenerated ? 'success.main' : 'transparent',
                '&:hover': {
                  elevation: 4,
                  transform: 'translateY(-2px)',
                },
              }}
              onClick={() => handleChapterClick(chapter.id)}
            >
              {chapter.isAIGenerated && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    zIndex: 1,
                  }}
                >
                  <Chip 
                    icon={<AutoAwesome />} 
                    label="AI" 
                    color="success" 
                    size="small"
                  />
                </Box>
              )}
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Chip
                    label={chapter.chapter}
                    size="small"
                    color={getChapterTypeColor(chapter)}
                    variant="outlined"
                  />
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleBookmark(chapter.id);
                    }}
                  >
                    {bookmarkedChapters.has(chapter.id) ? (
                      <Bookmark color="primary" />
                    ) : (
                      <BookmarkBorder />
                    )}
                  </IconButton>
                </Box>
                
                <Typography variant="h6" component="h3" gutterBottom sx={{ 
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                }}>
                  {chapter.title}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" sx={{ 
                  mb: 2,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                }}>
                  {chapter.description}
                </Typography>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" color="text.secondary">
                    {chapter.wordCount} 字
                  </Typography>
                  <Button size="small" variant="outlined">
                    开始阅读
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* 分页 */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={totalPages}
            page={currentPage}
            onChange={(event, page) => setCurrentPage(page)}
            color="primary"
            size="large"
          />
        </Box>
      )}
    </Container>
  );
};

export default ChapterListPage;
