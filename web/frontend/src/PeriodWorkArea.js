import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Container, Box, Button, Typography, Tabs, Tab } from '@mui/material';
import ProductsTab from './ProductsTab';
import CalendarTab from './CalendarTab';

function PeriodWorkArea() {
  const navigate = useNavigate();
  const { projectId, periodId } = useParams();
  const [tabIndex, setTabIndex] = useState(0);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box display="flex" gap={2} alignItems="center">
          <Button
            variant="outlined"
            onClick={() => navigate(`/projects/${projectId}/periods`)}
            sx={{ color: '#00f3ff', borderColor: '#00f3ff' }}
          >
            Назад к периодам
          </Button>
          <Typography variant="h5" sx={{ color: '#e0e0e0' }}>
            Период #{periodId}
          </Typography>
        </Box>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'rgba(255, 255, 255, 0.08)', mb: 2 }}>
        <Tabs
          value={tabIndex}
          onChange={(_, v) => setTabIndex(v)}
          textColor="inherit"
          TabIndicatorProps={{ style: { background: '#00f3ff' } }}
        >
          <Tab label="1. Товары" sx={{ color: '#e0e0e0' }} />
          <Tab label="2. Календарь" sx={{ color: '#e0e0e0' }} />
        </Tabs>
      </Box>

      {tabIndex === 0 && <ProductsTab periodId={periodId} />}
      {tabIndex === 1 && <CalendarTab periodId={periodId} />}
    </Container>
  );
}

export default PeriodWorkArea;
