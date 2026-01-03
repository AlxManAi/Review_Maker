import React, { useEffect, useMemo, useState } from 'react';
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import { FileUpload as ImportIcon, FileDownload as ExportIcon, Sync as ParseIcon, AutoAwesome as GenerateIcon, DeleteSweep as DeleteReviewsIcon } from '@mui/icons-material';

const API_BASE = '';

function ProductsTab({ periodId }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [selectedProductIds, setSelectedProductIds] = useState([]);

  const [editing, setEditing] = useState(null); // { productId, field, value }

  const [open, setOpen] = useState(false);
  const [newProduct, setNewProduct] = useState({ product_name: '', review_count: '', product_url: '' });

  const [importOpen, setImportOpen] = useState(false);
  const [importFile, setImportFile] = useState(null);

  const [exportOpen, setExportOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState('csv');

  const pid = useMemo(() => Number(periodId), [periodId]);

  const loadProducts = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_BASE}/api/periods/${pid}/products`);
      setProducts(response.data);
      setSelectedProductIds([]);
    } catch (_) {
      setError('Ошибка загрузки товаров');
    } finally {
      setLoading(false);
    }
  };

  const toggleSelected = (productId) => {
    setSelectedProductIds((prev) => {
      if (prev.includes(productId)) return prev.filter((x) => x !== productId);
      return [...prev, productId];
    });
  };

  const deleteSelectedProducts = async () => {
    if (!selectedProductIds.length) return;
    const ok = window.confirm(`Удалить выбранные товары (${selectedProductIds.length})?`);
    if (!ok) return;
    try {
      await Promise.all(selectedProductIds.map((id) => axios.delete(`${API_BASE}/api/products/${id}`)));
      setSuccess('Товары удалены');
      setTimeout(() => setSuccess(''), 2000);
      await loadProducts();
    } catch (_) {
      setError('Ошибка удаления товаров');
    }
  };

  const startEdit = (productId, field, currentValue) => {
    setEditing({
      productId,
      field,
      value: currentValue ?? '',
    });
  };

  const cancelEdit = () => {
    setEditing(null);
  };

  const commitEdit = async () => {
    if (!editing) return;

    const { productId, field, value } = editing;
    const payload = {};

    if (field === 'review_count') {
      payload[field] = value === '' ? null : Number(value);
      if (value !== '' && Number.isNaN(payload[field])) {
        setError('Количество отзывов должно быть числом');
        return;
      }
    } else {
      payload[field] = value === '' ? null : value;
    }

    try {
      await axios.patch(`${API_BASE}/api/products/${productId}`, payload);
      setProducts((prev) => prev.map((p) => (p.id === productId ? { ...p, ...payload } : p)));
      setSuccess('Сохранено');
      setTimeout(() => setSuccess(''), 1000);
      setEditing(null);
    } catch (_) {
      setError('Ошибка сохранения');
    }
  };

  const toggleUsed = async (productId, nextValue) => {
    setError('');
    try {
      await axios.patch(`${API_BASE}/api/products/${productId}`, { is_used: nextValue });
      setProducts((prev) => prev.map((p) => (p.id === productId ? { ...p, is_used: nextValue } : p)));
    } catch (_) {
      setError('Ошибка сохранения');
    }
  };

  useEffect(() => {
    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pid]);

  const createProduct = async () => {
    setError('');
    setSuccess('');

    if (!newProduct.product_name?.trim()) {
      setError('Название товара обязательно');
      return;
    }

    const payload = {
      period_id: pid,
      product_name: newProduct.product_name.trim(),
      review_count: newProduct.review_count === '' ? null : Number(newProduct.review_count),
      product_url: newProduct.product_url || null,
    };

    try {
      await axios.post(`${API_BASE}/api/periods/${pid}/products`, payload);
      setSuccess('Товар добавлен');
      setOpen(false);
      setNewProduct({ product_name: '', review_count: '', product_url: '' });
      await loadProducts();
    } catch (_) {
      setError('Ошибка добавления товара');
    }
  };

  const importProducts = async () => {
    if (!importFile) {
      setError('Выберите файл для импорта');
      return;
    }
    setError('');
    setSuccess('');
    const formData = new FormData();
    formData.append('file', importFile);
    try {
      await axios.post(`${API_BASE}/api/periods/${pid}/products/import`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setSuccess('Импорт завершён');
      setImportOpen(false);
      setImportFile(null);
      await loadProducts();
    } catch (_) {
      setError('Ошибка импорта');
    }
  };

  const exportProducts = async () => {
    setError('');
    setSuccess('');
    try {
      const response = await axios.get(`${API_BASE}/api/periods/${pid}/products/export?format=${exportFormat}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `products.${exportFormat}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setSuccess('Экспорт завершён');
      setExportOpen(false);
    } catch (_) {
      setError('Ошибка экспорта');
    }
  };

  const parseProducts = async () => {
    if (!selectedProductIds.length) {
      setError('Выберите товары для парсинга');
      return;
    }
    setError('');
    setSuccess('');
    try {
      await axios.post(`${API_BASE}/api/products/parse`, { product_ids: selectedProductIds });
      setSuccess('Парсинг запущен');
      await loadProducts();
    } catch (_) {
      setError('Ошибка запуска парсинга');
    }
  };

  const generateReviews = async () => {
    if (!selectedProductIds.length) {
      setError('Выберите товары для генерации');
      return;
    }
    setError('');
    setSuccess('');
    try {
      await axios.post(`${API_BASE}/api/products/generate`, { product_ids: selectedProductIds });
      setSuccess('Генерация запущена');
      await loadProducts();
    } catch (_) {
      setError('Ошибка запуска генерации');
    }
  };

  const deleteReviews = async () => {
    if (!selectedProductIds.length) {
      setError('Выберите товары для удаления отзывов');
      return;
    }
    const ok = window.confirm('Удалить все отзывы для выбранных товаров?');
    if (!ok) return;
    setError('');
    setSuccess('');
    try {
      await axios.delete(`${API_BASE}/api/products/reviews`, { data: { product_ids: selectedProductIds } });
      setSuccess('Отзывы удалены');
      await loadProducts();
    } catch (_) {
      setError('Ошибка удаления отзывов');
    }
  };

  return (
    <>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" sx={{ color: '#e0e0e0' }}>
          Товары
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            onClick={() => setOpen(true)}
            sx={{
              background: 'linear-gradient(45deg, #00f3ff, #bc13fe)',
              '&:hover': { background: 'linear-gradient(45deg, #00d4e6, #a012d6)' },
            }}
          >
            Добавить товар
          </Button>
          <Button
            variant="outlined"
            disabled={!selectedProductIds.length}
            onClick={deleteSelectedProducts}
            sx={{ color: '#ff8a65', borderColor: '#ff8a65' }}
          >
            Удалить
          </Button>
          <Button
            variant="outlined"
            onClick={() => setImportOpen(true)}
            startIcon={<ImportIcon />}
            sx={{ color: '#00f3ff', borderColor: '#00f3ff' }}
          >
            Импорт
          </Button>
          <Button
            variant="outlined"
            onClick={() => setExportOpen(true)}
            startIcon={<ExportIcon />}
            sx={{ color: '#00f3ff', borderColor: '#00f3ff' }}
          >
            Экспорт
          </Button>
          <Button
            variant="outlined"
            disabled={!selectedProductIds.length}
            onClick={parseProducts}
            startIcon={<ParseIcon />}
            sx={{ color: '#00f3ff', borderColor: '#00f3ff' }}
          >
            Парсинг
          </Button>
          <Button
            variant="outlined"
            disabled={!selectedProductIds.length}
            onClick={generateReviews}
            startIcon={<GenerateIcon />}
            sx={{ color: '#00f3ff', borderColor: '#00f3ff' }}
          >
            Генерация
          </Button>
          <Button
            variant="outlined"
            disabled={!selectedProductIds.length}
            onClick={deleteReviews}
            startIcon={<DeleteReviewsIcon />}
            sx={{ color: '#ff8a65', borderColor: '#ff8a65' }}
          >
            Удалить отзывы
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
                <TableCell sx={{ color: '#888', width: 70 }}>Принято</TableCell>
                <TableCell sx={{ color: '#888' }}>Название</TableCell>
                <TableCell sx={{ color: '#888', width: 110 }}>Отзывов</TableCell>
                <TableCell sx={{ color: '#888' }}>URL</TableCell>
                <TableCell sx={{ color: '#888', width: 140 }}>Статус</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {products.map((p, idx) => (
                <TableRow
                  key={p.id}
                  hover
                  selected={selectedProductIds.includes(p.id)}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'rgba(0, 243, 255, 0.05)',
                    },
                  }}
                >
                  <TableCell sx={{ color: '#e0e0e0' }}>{idx + 1}</TableCell>
                  <TableCell sx={{ color: '#e0e0e0' }}>{p.id}</TableCell>
                  <TableCell>
                    <Checkbox
                      size="small"
                      checked={Boolean(p.is_used)}
                      onChange={(e) => toggleUsed(p.id, e.target.checked)}
                      sx={{
                        color: '#888',
                        '&.Mui-checked': { color: '#00f3ff' },
                      }}
                    />
                  </TableCell>

                  <TableCell
                    sx={{ color: '#e0e0e0', cursor: 'pointer' }}
                    onDoubleClick={(e) => {
                      e.stopPropagation();
                      startEdit(p.id, 'product_name', p.product_name);
                    }}
                  >
                    {editing && editing.productId === p.id && editing.field === 'product_name' ? (
                      <TextField
                        value={editing.value}
                        size="small"
                        autoFocus
                        fullWidth
                        onChange={(e) => setEditing({ ...editing, value: e.target.value })}
                        onBlur={commitEdit}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') commitEdit();
                          if (e.key === 'Escape') cancelEdit();
                        }}
                        sx={{ minWidth: 260, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
                      />
                    ) : (
                      p.product_name
                    )}
                  </TableCell>

                  <TableCell
                    sx={{ color: '#aaa', cursor: 'pointer' }}
                    onDoubleClick={(e) => {
                      e.stopPropagation();
                      startEdit(p.id, 'review_count', p.review_count ?? '');
                    }}
                  >
                    {editing && editing.productId === p.id && editing.field === 'review_count' ? (
                      <TextField
                        value={editing.value}
                        size="small"
                        autoFocus
                        type="number"
                        fullWidth
                        onChange={(e) => setEditing({ ...editing, value: e.target.value })}
                        onBlur={commitEdit}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') commitEdit();
                          if (e.key === 'Escape') cancelEdit();
                        }}
                        sx={{ minWidth: 90, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
                      />
                    ) : (
                      p.review_count ?? ''
                    )}
                  </TableCell>

                  <TableCell
                    sx={{ color: '#aaa', cursor: 'pointer' }}
                    onDoubleClick={(e) => {
                      e.stopPropagation();
                      startEdit(p.id, 'product_url', p.product_url ?? '');
                    }}
                  >
                    {editing && editing.productId === p.id && editing.field === 'product_url' ? (
                      <TextField
                        value={editing.value}
                        size="small"
                        autoFocus
                        fullWidth
                        onChange={(e) => setEditing({ ...editing, value: e.target.value })}
                        onBlur={commitEdit}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') commitEdit();
                          if (e.key === 'Escape') cancelEdit();
                        }}
                        sx={{ minWidth: 260, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
                      />
                    ) : (
                      p.product_url ?? ''
                    )}
                  </TableCell>
                  <TableCell sx={{ color: '#aaa' }}>{p.parse_status}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ color: '#e0e0e0' }}>Новый товар</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Название товара"
            fullWidth
            variant="outlined"
            value={newProduct.product_name}
            onChange={(e) => setNewProduct({ ...newProduct, product_name: e.target.value })}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />
          <TextField
            margin="dense"
            label="Количество отзывов"
            type="number"
            fullWidth
            variant="outlined"
            value={newProduct.review_count}
            onChange={(e) => setNewProduct({ ...newProduct, review_count: e.target.value })}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />
          <TextField
            margin="dense"
            label="URL"
            fullWidth
            variant="outlined"
            value={newProduct.product_url}
            onChange={(e) => setNewProduct({ ...newProduct, product_url: e.target.value })}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} sx={{ color: '#888' }}>
            Отмена
          </Button>
          <Button
            onClick={createProduct}
            variant="contained"
            sx={{
              background: 'linear-gradient(45deg, #00f3ff, #bc13fe)',
              '&:hover': { background: 'linear-gradient(45deg, #00d4e6, #a012d6)' },
            }}
          >
            Создать
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={importOpen} onClose={() => setImportOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ color: '#e0e0e0' }}>Импорт товаров</DialogTitle>
        <DialogContent>
          <TextField
            type="file"
            fullWidth
            variant="outlined"
            inputProps={{ accept: '.csv,.xlsx,.xls' }}
            onChange={(e) => setImportFile(e.target.files?.[0] || null)}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportOpen(false)} sx={{ color: '#888' }}>
            Отмена
          </Button>
          <Button
            onClick={importProducts}
            variant="contained"
            sx={{
              background: 'linear-gradient(45deg, #00f3ff, #bc13fe)',
              '&:hover': { background: 'linear-gradient(45deg, #00d4e6, #a012d6)' },
            }}
          >
            Импорт
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={exportOpen} onClose={() => setExportOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ color: '#e0e0e0' }}>Экспорт товаров</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel sx={{ color: '#888' }}>Формат</InputLabel>
            <Select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value)}
              sx={{ color: '#e0e0e0', '& .MuiOutlinedInput-notchedOutline': { borderColor: '#444' } }}
            >
              <MenuItem value="csv">CSV</MenuItem>
              <MenuItem value="xlsx">Excel</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportOpen(false)} sx={{ color: '#888' }}>
            Отмена
          </Button>
          <Button
            onClick={exportProducts}
            variant="contained"
            sx={{
              background: 'linear-gradient(45deg, #00f3ff, #bc13fe)',
              '&:hover': { background: 'linear-gradient(45deg, #00d4e6, #a012d6)' },
            }}
          >
            Экспорт
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default ProductsTab;
