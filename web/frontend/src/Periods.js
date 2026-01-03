import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import {
  Container,
  Typography,
  Button,
  Box,
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
  Alert,
} from '@mui/material';

const API_BASE = '';

function Periods() {
  const navigate = useNavigate();
  const { projectId } = useParams();

  const [periods, setPeriods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [projectName, setProjectName] = useState('');
  const [selectedPeriodId, setSelectedPeriodId] = useState(null);

  const [open, setOpen] = useState(false);
  const [newPeriod, setNewPeriod] = useState({
    start_date: '',
    end_date: '',
    total_reviews_count: 100,
  });

  const [editingId, setEditingId] = useState(null);
  const [editingField, setEditingField] = useState(null);
  const [editingValue, setEditingValue] = useState('');

  const loadPeriods = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_BASE}/api/projects/${projectId}/periods`);
      setPeriods(response.data);
      setSelectedPeriodId(null);
    } catch (err) {
      setError('Ошибка загрузки периодов');
    } finally {
      setLoading(false);
    }
  };

  const loadProject = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/projects/${projectId}`);
      setProjectName(response.data?.name || '');
    } catch (_) {
      setProjectName('');
    }
  };

  useEffect(() => {
    loadProject();
    loadPeriods();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  const openSelectedPeriod = () => {
    if (!selectedPeriodId) return;
    navigate(`/projects/${projectId}/periods/${selectedPeriodId}`);
  };

  const deleteSelectedPeriod = async () => {
    if (!selectedPeriodId) return;
    const ok = window.confirm('Удалить период?\n\n⚠ Будут удалены все товары и отзывы этого периода!');
    if (!ok) return;
    try {
      await axios.delete(`${API_BASE}/api/periods/${selectedPeriodId}`);
      setSuccess('Период удалён');
      setTimeout(() => setSuccess(''), 2000);
      await loadPeriods();
    } catch (_) {
      setError('Ошибка удаления периода');
    }
  };

  const createPeriod = async () => {
    setError('');
    setSuccess('');
    try {
      const payload = {
        project_id: Number(projectId),
        start_date: newPeriod.start_date,
        end_date: newPeriod.end_date,
        total_reviews_count: Number(newPeriod.total_reviews_count) || 0,
      };

      await axios.post(`${API_BASE}/api/projects/${projectId}/periods`, payload);
      setSuccess('Период создан');
      setOpen(false);
      setNewPeriod({ start_date: '', end_date: '', total_reviews_count: 100 });
      await loadPeriods();
    } catch (err) {
      setError('Ошибка создания периода');
    }
  };

  const startEdit = (id, field, currentValue) => {
    setEditingId(id);
    setEditingField(field);
    setEditingValue(currentValue || '');
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditingField(null);
    setEditingValue('');
  };

  const saveEdit = async () => {
    if (!editingId || !editingField) return;
    try {
      await axios.patch(`${API_BASE}/api/periods/${editingId}`, { [editingField]: editingValue });
      setPeriods(periods.map(p => p.id === editingId ? { ...p, [editingField]: editingValue } : p));
      cancelEdit();
      setSuccess('Изменения сохранены');
      setTimeout(() => setSuccess(''), 2000);
    } catch (_) {
      setError('Ошибка сохранения');
    }
  };

  return (
    <>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Box display="flex" gap={2} alignItems="center">
            <Button variant="outlined" onClick={() => navigate('/projects')} sx={{ color: '#00f3ff', borderColor: '#00f3ff' }}>
              Назад
            </Button>
            <Typography variant="h4" component="h1" sx={{ color: '#e0e0e0' }}>
              Периоды: {projectName ? projectName : `Проект #${projectId}`}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="contained"
              onClick={() => setOpen(true)}
              sx={{
                background: 'linear-gradient(45deg, #00f3ff, #bc13fe)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #00d4e6, #a012d6)',
                },
              }}
            >
              Добавить период
            </Button>
            <Button
              variant="outlined"
              disabled={!selectedPeriodId}
              onClick={openSelectedPeriod}
              sx={{ color: '#00f3ff', borderColor: '#00f3ff' }}
            >
              Открыть
            </Button>
            <Button
              variant="outlined"
              disabled={!selectedPeriodId}
              onClick={deleteSelectedPeriod}
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
                  <TableCell sx={{ color: '#888' }}>Начало</TableCell>
                  <TableCell sx={{ color: '#888' }}>Окончание</TableCell>
                  <TableCell sx={{ color: '#888', width: 110 }}>Отзывов</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {periods.map((p, idx) => (
                  <TableRow
                    key={p.id}
                    hover
                    selected={p.id === selectedPeriodId}
                    sx={{
                      '&:hover': {
                        backgroundColor: 'rgba(0, 243, 255, 0.05)',
                      },
                    }}
                    onClick={() => setSelectedPeriodId(p.id)}
                    onDoubleClick={() => navigate(`/projects/${projectId}/periods/${p.id}`)}
                  >
                    <TableCell sx={{ color: '#e0e0e0' }}>{idx + 1}</TableCell>
                    <TableCell sx={{ color: '#e0e0e0' }}>{p.id}</TableCell>
                    <TableCell
                      sx={{ color: '#aaa', cursor: 'pointer' }}
                      onDoubleClick={(e) => {
                        e.stopPropagation();
                        startEdit(p.id, 'start_date', (p.start_date || '').slice(0, 10));
                      }}
                    >
                      {editingId === p.id && editingField === 'start_date' ? (
                        <TextField
                          type="date"
                          value={editingValue}
                          onChange={(e) => setEditingValue(e.target.value)}
                          onBlur={saveEdit}
                          onKeyDown={(e) => { if (e.key === 'Enter') saveEdit(); else if (e.key === 'Escape') cancelEdit(); }}
                          size="small"
                          sx={{ minWidth: 140 }}
                          autoFocus
                        />
                      ) : (
                        (p.start_date || '').slice(0, 10)
                      )}
                    </TableCell>
                    <TableCell
                      sx={{ color: '#aaa', cursor: 'pointer' }}
                      onDoubleClick={(e) => {
                        e.stopPropagation();
                        startEdit(p.id, 'end_date', (p.end_date || '').slice(0, 10));
                      }}
                    >
                      {editingId === p.id && editingField === 'end_date' ? (
                        <TextField
                          type="date"
                          value={editingValue}
                          onChange={(e) => setEditingValue(e.target.value)}
                          onBlur={saveEdit}
                          onKeyDown={(e) => { if (e.key === 'Enter') saveEdit(); else if (e.key === 'Escape') cancelEdit(); }}
                          size="small"
                          sx={{ minWidth: 140 }}
                          autoFocus
                        />
                      ) : (
                        (p.end_date || '').slice(0, 10)
                      )}
                    </TableCell>
                    <TableCell
                      sx={{ color: '#aaa', cursor: 'pointer' }}
                      onDoubleClick={(e) => {
                        e.stopPropagation();
                        startEdit(p.id, 'total_reviews_count', p.total_reviews_count);
                      }}
                    >
                      {editingId === p.id && editingField === 'total_reviews_count' ? (
                        <TextField
                          type="number"
                          value={editingValue}
                          onChange={(e) => setEditingValue(e.target.value)}
                          onBlur={saveEdit}
                          onKeyDown={(e) => { if (e.key === 'Enter') saveEdit(); else if (e.key === 'Escape') cancelEdit(); }}
                          size="small"
                          sx={{ minWidth: 100 }}
                          autoFocus
                        />
                      ) : (
                        p.total_reviews_count ?? ''
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Container>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ color: '#e0e0e0' }}>Новый период</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="Дата начала"
            type="date"
            fullWidth
            variant="outlined"
            value={newPeriod.start_date}
            onChange={(e) => setNewPeriod({ ...newPeriod, start_date: e.target.value })}
            InputLabelProps={{ shrink: true }}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />
          <TextField
            margin="dense"
            label="Дата окончания"
            type="date"
            fullWidth
            variant="outlined"
            value={newPeriod.end_date}
            onChange={(e) => setNewPeriod({ ...newPeriod, end_date: e.target.value })}
            InputLabelProps={{ shrink: true }}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />
          <TextField
            margin="dense"
            label="Общее количество отзывов"
            type="number"
            fullWidth
            variant="outlined"
            value={newPeriod.total_reviews_count}
            onChange={(e) => setNewPeriod({ ...newPeriod, total_reviews_count: e.target.value })}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} sx={{ color: '#888' }}>
            Отмена
          </Button>
          <Button
            onClick={createPeriod}
            variant="contained"
            sx={{
              background: 'linear-gradient(45deg, #00f3ff, #bc13fe)',
              '&:hover': {
                background: 'linear-gradient(45deg, #00d4e6, #a012d6)',
              },
            }}
          >
            Создать
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default Periods;
