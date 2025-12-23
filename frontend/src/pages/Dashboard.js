import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  LinearProgress,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import FlagIcon from '@mui/icons-material/Flag';
import { getStatistics, getHistory, getCurrentPhase } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [phase, setPhase] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsData, historyData, phaseData] = await Promise.all([
        getStatistics(),
        getHistory(10),
        getCurrentPhase(),
      ]);
      setStats(statsData);
      setHistory(historyData);
      setPhase(phaseData);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusChip = (status) => {
    const statusConfig = {
      won: { label: 'Vitória', color: 'success', icon: '✅' },
      lost: { label: 'Derrota', color: 'error', icon: '❌' },
      pending: { label: 'Pendente', color: 'warning', icon: '⏳' },
      void: { label: 'Anulada', color: 'default', icon: '⚪' },
    };

    const config = statusConfig[status] || statusConfig.pending;
    return (
      <Chip
        label={`${config.icon} ${config.label}`}
        color={config.color}
        size="small"
      />
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  const profit = stats?.profit || 0;
  const isProfit = profit >= 0;

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, color: 'primary.main', fontWeight: 600 }}>
        📊 Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Banca Atual */}
        <Grid item xs={12} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AccountBalanceWalletIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h6">Banca</Typography>
              </Box>
              <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 600 }}>
                R$ {phase?.bankroll?.toFixed(2) || '0.00'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Balanço */}
        <Grid item xs={12} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                {isProfit ? (
                  <TrendingUpIcon sx={{ color: 'success.main', mr: 1 }} />
                ) : (
                  <TrendingDownIcon sx={{ color: 'error.main', mr: 1 }} />
                )}
                <Typography variant="h6">Balanço</Typography>
              </Box>
              <Typography
                variant="h4"
                sx={{
                  color: isProfit ? 'success.main' : 'error.main',
                  fontWeight: 600,
                }}
              >
                R$ {profit.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ROI: {stats?.roi?.toFixed(2) || '0.00'}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Win Rate */}
        <Grid item xs={12} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>Win Rate</Typography>
              <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 600 }}>
                {stats?.win_rate?.toFixed(1) || '0.0'}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {stats?.wins || 0} / {stats?.total_bets || 0} apostas
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Objetivo */}
        <Grid item xs={12} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <FlagIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h6">Fase {phase?.phase || 1}</Typography>
              </Box>
              <Typography variant="h6" sx={{ mb: 1 }}>
                R$ {phase?.target?.toFixed(2) || '0.00'}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={phase?.progress || 0}
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {phase?.progress?.toFixed(1) || '0.0'}% completo
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Histórico */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>
              📋 Últimas 10 Apostas
            </Typography>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'grey.100' }}>
                    <TableCell><strong>Data</strong></TableCell>
                    <TableCell><strong>Jogo</strong></TableCell>
                    <TableCell><strong>Mercado</strong></TableCell>
                    <TableCell align="right"><strong>Odd</strong></TableCell>
                    <TableCell align="right"><strong>Stake</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                    <TableCell align="right"><strong>Resultado</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {history.length > 0 ? (
                    history.map((bet, index) => (
                      <TableRow key={index} hover>
                        <TableCell>{new Date(bet.timestamp).toLocaleDateString('pt-BR')}</TableCell>
                        <TableCell>{bet.match}</TableCell>
                        <TableCell>{bet.market}</TableCell>
                        <TableCell align="right">{bet.odds?.toFixed(2) || '-'}</TableCell>
                        <TableCell align="right">R$ {bet.stake?.toFixed(2) || '0.00'}</TableCell>
                        <TableCell>{getStatusChip(bet.status)}</TableCell>
                        <TableCell align="right">
                          {bet.result !== null && bet.result !== undefined ? (
                            <Typography
                              sx={{
                                color: bet.result > 0 ? 'success.main' : 'error.main',
                                fontWeight: 600,
                              }}
                            >
                              R$ {Number(bet.result).toFixed(2)}
                            </Typography>
                          ) : (
                            <Typography color="text.secondary">-</Typography>
                          )}
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography color="text.secondary">
                          Nenhuma aposta registrada ainda
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;