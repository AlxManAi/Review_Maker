import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Box,
  Button,
  Typography,
  Alert,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { FilterList as FilterIcon, CalendarToday as CalendarIcon } from '@mui/icons-material';

const API_BASE = '';

function CalendarTab({ periodId }) {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [selectedReviewIds, setSelectedReviewIds] = useState([]);

  const [filterApproved, setFilterApproved] = useState('all');
  const [filterPublished, setFilterPublished] = useState('all');
  const [filterUsed, setFilterUsed] = useState('all');
  const [filterDateFrom, setFilterDateFrom] = useState('');
  const [filterDateTo, setFilterDateTo] = useState('');
  const [filterProduct, setFilterProduct] = useState('');

  const [openFilters, setOpenFilters] = useState(false);

  const pid = Number(periodId);

  const loadReviews = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_BASE}/api/periods/${pid}/reviews`);
      setReviews(response.data);
      setSelectedReviewIds([]);
    } catch (_) {
      setError('Ошибка загрузки отзывов');
    } finally {
      setLoading(false);
    }
  };

  const toggleApproved = async (reviewId, nextValue) => {
    setError('');
    try {
      await axios.patch(`${API_BASE}/api/reviews/${reviewId}`, { is_approved: nextValue });
      setReviews((prev) => prev.map((r) => (r.id === reviewId ? { ...r, is_approved: nextValue } : r)));
    } catch (_) {
      setError('Ошибка сохранения');
    }
  };

  const togglePublished = async (reviewId, nextValue) => {
    setError('');
    try {
      await axios.patch(`${API_BASE}/api/reviews/${reviewId}`, { is_published: nextValue });
      setReviews((prev) => prev.map((r) => (r.id === reviewId ? { ...r, is_published: nextValue } : r)));
    } catch (_) {
      setError('Ошибка сохранения');
    }
  };

  const toggleUsed = async (reviewId, nextValue) => {
    setError('');
    try {
      await axios.patch(`${API_BASE}/api/reviews/${reviewId}`, { is_used: nextValue });
      setReviews((prev) => prev.map((r) => (r.id === reviewId ? { ...r, is_used: nextValue } : r)));
    } catch (_) {
      setError('Ошибка сохранения');
    }
  };

  const updateTargetDate = async (reviewId, targetDate) => {
    setError('');
    try {
      await axios.patch(`${API_BASE}/api/reviews/${reviewId}`, { target_date: targetDate || null });
      setReviews((prev) => prev.map((r) => (r.id === reviewId ? { ...r, target_date: targetDate || null } : r)));
    } catch (_) {
      setError('Ошибка сохранения');
    }
  };

  const deleteSelectedReviews = async () => {
    if (!selectedReviewIds.length) return;
    const ok = window.confirm(`Удалить выбранные отзывы (${selectedReviewIds.length})?`);
    if (!ok) return;
    try {
      await Promise.all(selectedReviewIds.map((id) => axios.delete(`${API_BASE}/api/reviews/${id}`)));
      setSuccess('Отзывы удалены');
      setTimeout(() => setSuccess(''), 2000);
      await loadReviews();
    } catch (_) {
      setError('Ошибка удаления отзывов');
    }
  };

  const clearFilters = () => {
    setFilterApproved('all');
    setFilterPublished('all');
    setFilterUsed('all');
    setFilterDateFrom('');
    setFilterDateTo('');
    setFilterProduct('');
  };

  const filteredReviews = reviews.filter((r) => {
    if (filterApproved !== 'all' && r.is_approved !== (filterApproved === 'true')) return false;
    if (filterPublished !== 'all' && r.is_published !== (filterPublished === 'true')) return false;
    if (filterUsed !== 'all' && r.is_used !== (filterUsed === 'true')) return false;
    if (filterDateFrom && r.date < filterDateFrom) return false;
    if (filterDateTo && r.date > filterDateTo) return false;
    if (filterProduct && !r.product_name.toLowerCase().includes(filterProduct.toLowerCase())) return false;
    return true;
  });

  useEffect(() => {
    loadReviews();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pid]);

  return (
    <>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" sx={{ color: '#e0e0e0' }}>
          Календарь отзывов
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Button
            variant="outlined"
            onClick={() => setOpenFilters(true)}
            startIcon={<FilterIcon />}
            sx={{ color: '#00f3ff', borderColor: '#00f3ff' }}
          >
            Фильтры
          </Button>
          <Button
            variant="outlined"
            disabled={!selectedReviewIds.length}
            onClick={deleteSelectedReviews}
            sx={{ color: '#ff8a65', borderColor: '#ff8a65' }}
          >
            Удалить
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {loading ? (
        <Typography sx={{ color: '#888' }}>Загрузка...</Typography>
      ) : (
        <TableContainer
          component={Paper}
          sx={{
            background: '#16161a',
            border: '1px solid rgba(255, 255, 255, 0.05)',
          }}
        >
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ color: '#888', width: 60 }}>№</TableCell>
                <TableCell sx={{ color: '#888', width: 70 }}>ID</TableCell>
                <TableCell sx={{ color: '#888', width: 120 }}>Дата</TableCell>
                <TableCell sx={{ color: '#888' }}>Товар</TableCell>
                <TableCell sx={{ color: '#888' }}>Имя</TableCell>
                <TableCell sx={{ color: '#888', width: 80 }}>Рейтинг</TableCell>
                <TableCell sx={{ color: '#888' }}>Содержание</TableCell>
                <TableCell sx={{ color: '#888', width: 90 }}>Принято</TableCell>
                <TableCell sx={{ color: '#888', width: 100 }}>Опубликовано</TableCell>
                <TableCell sx={{ color: '#888', width: 80 }}>Использовано</TableCell>
                <TableCell sx={{ color: '#888', width: 130 }}>Целевая дата</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredReviews.map((r, idx) => (
                <TableRow
                  key={r.id}
                  hover
                  selected={selectedReviewIds.includes(r.id)}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'rgba(0, 243, 255, 0.05)',
                    },
                  }}
                >
                  <TableCell sx={{ color: '#e0e0e0' }}>{idx + 1}</TableCell>
                  <TableCell sx={{ color: '#e0e0e0' }}>{r.id}</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>{(r.date || '').slice(0, 10)}</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>{r.product_name}</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>{r.customer_name}</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>{r.rating}</TableCell>
                  <TableCell sx={{ color: '#aaa', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={r.content}>
                    {r.content}
                  </TableCell>
                  <TableCell>
                    <Checkbox
                      size="small"
                      checked={Boolean(r.is_approved)}
                      onChange={(e) => toggleApproved(r.id, e.target.checked)}
                      sx={{
                        color: '#888',
                        '&.Mui-checked': { color: '#00f3ff' },
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Checkbox
                      size="small"
                      checked={Boolean(r.is_published)}
                      onChange={(e) => togglePublished(r.id, e.target.checked)}
                      sx={{
                        color: '#888',
                        '&.Mui-checked': { color: '#00f3ff' },
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Checkbox
                      size="small"
                      checked={Boolean(r.is_used)}
                      onChange={(e) => toggleUsed(r.id, e.target.checked)}
                      sx={{
                        color: '#888',
                        '&.Mui-checked': { color: '#00f3ff' },
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      type="date"
                      size="small"
                      value={r.target_date ? r.target_date.slice(0, 10) : ''}
                      onChange={(e) => updateTargetDate(r.id, e.target.value)}
                      sx={{
                        minWidth: 120,
                        '& .MuiOutlinedInput-root': {
                          color: '#e0e0e0',
                          '& fieldset': { borderColor: '#444' },
                        },
                      }}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={openFilters} onClose={() => setOpenFilters(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ color: '#e0e0e0' }}>Фильтры</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2, mb: 2 }}>
            <InputLabel sx={{ color: '#888' }}>Принято</InputLabel>
            <Select
              value={filterApproved}
              onChange={(e) => setFilterApproved(e.target.value)}
              sx={{ color: '#e0e0e0', '& .MuiOutlinedInput-notchedOutline': { borderColor: '#444' } }}
            >
              <MenuItem value="all">Все</MenuItem>
              <MenuItem value="true">Принятые</MenuItem>
              <MenuItem value="false">Непринятые</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel sx={{ color: '#888' }}>Опубликовано</InputLabel>
            <Select
              value={filterPublished}
              onChange={(e) => setFilterPublished(e.target.value)}
              sx={{ color: '#e0e0e0', '& .MuiOutlinedInput-notchedOutline': { borderColor: '#444' } }}
            >
              <MenuItem value="all">Все</MenuItem>
              <MenuItem value="true">Опубликовано</MenuItem>
              <MenuItem value="false">Не опубликовано</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel sx={{ color: '#888' }}>Использовано</InputLabel>
            <Select
              value={filterUsed}
              onChange={(e) => setFilterUsed(e.target.value)}
              sx={{ color: '#e0e0e0', '& .MuiOutlinedInput-notchedOutline': { borderColor: '#444' } }}
            >
              <MenuItem value="all">Все</MenuItem>
              <MenuItem value="true">Использовано</MenuItem>
              <MenuItem value="false">Не использовано</MenuItem>
            </Select>
          </FormControl>

          <TextField
            margin="dense"
            label="Дата с"
            type="date"
            fullWidth
            variant="outlined"
            value={filterDateFrom}
            onChange={(e) => setFilterDateFrom(e.target.value)}
            sx={{ '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />

          <TextField
            margin="dense"
            label="Дата по"
            type="date"
            fullWidth
            variant="outlined"
            value={filterDateTo}
            onChange={(e) => setFilterDateTo(e.target.value)}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />

          <TextField
            margin="dense"
            label="Товар"
            fullWidth
            variant="outlined"
            value={filterProduct}
            onChange={(e) => setFilterProduct(e.target.value)}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={clearFilters} sx={{ color: '#888' }}>
            Сбросить
          </Button>
          <Button onClick={() => setOpenFilters(false)} sx={{ color: '#888' }}>
            Закрыть
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default CalendarTab;
