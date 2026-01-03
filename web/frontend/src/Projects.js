import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
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
  Box,
  Alert
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

const API_BASE = '';

function Projects() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', site_url: '', description: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [editingField, setEditingField] = useState(null);
  const [editingValue, setEditingValue] = useState('');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/projects`);
      setProjects(response.data);
      setSelectedProjectId(null);
    } catch (err) {
      setError('Ошибка загрузки проектов');
    } finally {
      setLoading(false);
    }
  };

  const openSelectedProject = () => {
    if (!selectedProjectId) return;
    navigate(`/projects/${selectedProjectId}/periods`);
  };

  const deleteSelectedProject = async () => {
    if (!selectedProjectId) return;
    const ok = window.confirm('Удалить проект?\n\n⚠ Будут удалены все периоды, товары и отзывы этого проекта!');
    if (!ok) return;
    try {
      await axios.delete(`${API_BASE}/api/projects/${selectedProjectId}`);
      setSuccess('Проект удалён');
      setTimeout(() => setSuccess(''), 2000);
      await loadProjects();
    } catch (_) {
      setError('Ошибка удаления проекта');
    }
  };

  const createProject = async () => {
    try {
      const response = await axios.post(`${API_BASE}/api/projects`, newProject);
      setProjects([...projects, response.data]);
      setOpen(false);
      setNewProject({ name: '', site_url: '', description: '' });
      setSuccess('Проект создан успешно!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Ошибка создания проекта');
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
      await axios.patch(`${API_BASE}/api/projects/${editingId}`, { [editingField]: editingValue });
      setProjects(projects.map(p => p.id === editingId ? { ...p, [editingField]: editingValue } : p));
      cancelEdit();
      setSuccess('Изменения сохранены');
      setTimeout(() => setSuccess(''), 2000);
    } catch (_) {
      setError('Ошибка сохранения');
    }
  };

  if (loading) return <Typography>Загрузка...</Typography>;

  return (
    <>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Проекты
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpen(true)}
              sx={{
                background: 'linear-gradient(45deg, #00f3ff, #bc13fe)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #00d4e6, #a012d6)',
                }
              }}
            >
              Новый проект
            </Button>
            <Button
              variant="outlined"
              disabled={!selectedProjectId}
              onClick={openSelectedProject}
              sx={{ color: '#00f3ff', borderColor: '#00f3ff' }}
            >
              Открыть
            </Button>
            <Button
              variant="outlined"
              disabled={!selectedProjectId}
              onClick={deleteSelectedProject}
              sx={{ color: '#ff8a65', borderColor: '#ff8a65' }}
            >
              Удалить
            </Button>
          </Box>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

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
                <TableCell sx={{ color: '#888' }}>Название</TableCell>
                <TableCell sx={{ color: '#888' }}>URL сайта</TableCell>
                <TableCell sx={{ color: '#888' }}>Описание</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {projects.map((project, idx) => (
                <TableRow
                  key={project.id}
                  hover
                  selected={project.id === selectedProjectId}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'rgba(0, 243, 255, 0.05)',
                    },
                  }}
                  onClick={() => setSelectedProjectId(project.id)}
                  onDoubleClick={() => navigate(`/projects/${project.id}/periods`)}
                >
                  <TableCell sx={{ color: '#e0e0e0' }}>{idx + 1}</TableCell>
                  <TableCell sx={{ color: '#e0e0e0' }}>{project.id}</TableCell>
                  <TableCell
                    sx={{ color: '#e0e0e0', cursor: 'pointer' }}
                    onDoubleClick={(e) => {
                      e.stopPropagation();
                      startEdit(project.id, 'name', project.name);
                    }}
                  >
                    {editingId === project.id && editingField === 'name' ? (
                      <TextField
                        value={editingValue}
                        onChange={(e) => setEditingValue(e.target.value)}
                        onBlur={saveEdit}
                        onKeyDown={(e) => { if (e.key === 'Enter') saveEdit(); else if (e.key === 'Escape') cancelEdit(); }}
                        size="small"
                        sx={{ minWidth: 200 }}
                        autoFocus
                      />
                    ) : (
                      project.name
                    )}
                  </TableCell>
                  <TableCell
                    sx={{ color: '#aaa', cursor: 'pointer' }}
                    onDoubleClick={(e) => {
                      e.stopPropagation();
                      startEdit(project.id, 'site_url', project.site_url);
                    }}
                  >
                    {editingId === project.id && editingField === 'site_url' ? (
                      <TextField
                        value={editingValue}
                        onChange={(e) => setEditingValue(e.target.value)}
                        onBlur={saveEdit}
                        onKeyDown={(e) => { if (e.key === 'Enter') saveEdit(); else if (e.key === 'Escape') cancelEdit(); }}
                        size="small"
                        sx={{ minWidth: 300 }}
                        autoFocus
                      />
                    ) : (
                      project.site_url
                    )}
                  </TableCell>
                  <TableCell
                    sx={{ color: '#aaa', cursor: 'pointer' }}
                    onDoubleClick={(e) => {
                      e.stopPropagation();
                      startEdit(project.id, 'description', project.description);
                    }}
                  >
                    {editingId === project.id && editingField === 'description' ? (
                      <TextField
                        value={editingValue}
                        onChange={(e) => setEditingValue(e.target.value)}
                        onBlur={saveEdit}
                        onKeyDown={(e) => { if (e.key === 'Enter') saveEdit(); else if (e.key === 'Escape') cancelEdit(); }}
                        size="small"
                        sx={{ minWidth: 300 }}
                        autoFocus
                      />
                    ) : (
                      project.description
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Container>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ color: '#e0e0e0' }}>Новый проект</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Название проекта"
            fullWidth
            variant="outlined"
            value={newProject.name}
            onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />
          <TextField
            margin="dense"
            label="Сайт"
            fullWidth
            variant="outlined"
            value={newProject.site_url}
            onChange={(e) => setNewProject({ ...newProject, site_url: e.target.value })}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />
          <TextField
            margin="dense"
            label="Описание"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newProject.description}
            onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
            sx={{ mt: 2, '& .MuiOutlinedInput-root': { color: '#e0e0e0' } }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} sx={{ color: '#888' }}>
            Отмена
          </Button>
          <Button onClick={createProject} variant="contained" sx={{
            background: 'linear-gradient(45deg, #00f3ff, #bc13fe)',
            '&:hover': {
              background: 'linear-gradient(45deg, #00d4e6, #a012d6)',
            }
          }}>
            Создать
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default Projects;
