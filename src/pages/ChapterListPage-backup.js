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
} from '@mui/material';
import {
  Search,
  Sort,
  ViewList,
  GridView,
  BookmarkBorder,
  Bookmark,
  ArrowUpward,
  ArrowDownward,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const ChapterListPage = () => {
  const navigate = useNavigate();
  
  // 模拟章节数据 - 实际应用中应该从API获取
  const [chapters, setChapters] = useState([]);
  const [filteredChapters, setFilteredChapters] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');
  const [viewMode, setViewMode] = useState('grid');
  const [bookmarkedChapters, setBookmarkedChapters] = useState(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const chaptersPerPage = 12;

  // 模拟章节数据
  useEffect(() => {
    const mockChapters = [
      { id: 1, title: '楔子：白帝城', wordCount: 2006, chapter: '楔子', description: '故事的开始，神秘的梦境' },
      { id: 2, title: '1. 路明非', wordCount: 2012, chapter: '第一章', description: '普通高中生的日常生活' },
      { id: 3, title: '2. 梦想', wordCount: 1814, chapter: '第一章', description: '关于未来的思考' },
      { id: 4, title: '3. 见面', wordCount: 1934, chapter: '第一章', description: '命运的相遇' },
      { id: 5, title: '4. 选择', wordCount: 1966, chapter: '第一章', description: '重要的决定' },
      { id: 6, title: '5. 命运', wordCount: 1892, chapter: '第一章', description: '命运的转折点' },
      { id: 7, title: '1. 表白', wordCount: 1830, chapter: '第二章', description: '青春的悸动' },
      { id: 8, title: '2. 天使降临', wordCount: 1980, chapter: '第二章', description: '神秘的出现' },
      { id: 9, title: '3. 芝加哥火车站', wordCount: 1977, chapter: '第二章', description: '新的旅程开始' },
      { id: 10, title: '4. 对话', wordCount: 2012, chapter: '第二章', description: '重要的对话' },
      // 可以继续添加更多章节...
    ];
    
    // 为了演示，我们复制数据来模拟131个章节
    const allChapters = [];
    for (let i = 1; i <= 131; i++) {
      const baseChapter = mockChapters[i % mockChapters.length];
      allChapters.push({
        ...baseChapter,
        id: i,
        title: i === 1 ? '楔子：白帝城' : `第${i}章`,
        wordCount: Math.floor(Math.random() * 400) + 1800, // 1800-2200字
        chapter: i === 1 ? '楔子' : `第${Math.ceil(i/10)}幕`,
      });
    }
    
    setChapters(allChapters);
    setFilteredChapters(allChapters);
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
                    <GridView />
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
                '&:hover': {
                  elevation: 4,
                  transform: 'translateY(-2px)',
                },
              }}
              onClick={() => handleChapterClick(chapter.id)}
            >
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
