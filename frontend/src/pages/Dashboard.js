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
  useTheme,
  useMediaQuery,
  Fade,
  Zoom,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import FlagIcon from '@mui/icons-material/Flag';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import { getStatistics, getHistory, getCurrentPhase } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [phase, setPhase] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));

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
        label={`${config.icon} ${isMobile ? '' : config.label}`}
        color={config.color}
        size="small"
        sx={{ fontWeight: 600 }}
      />
    );
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          gap: 2,
        }}
      >
        <CircularProgress size={60} thickness={4} />
        <Typography variant="h6" color="text.secondary">
          Carregando dashboard...
        </Typography>
      </Box>
    );
  }

  const profit = stats?.profit || 0;
  const isProfit = profit >= 0;

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #F5F7FA 0%, #E8EEF2 100%)',
        pb: { xs: 4, md: 6 },
      }}
    >
      <Container maxWidth="lg" sx={{ pt: { xs: 2, md: 4 } }}>
        {/* Header */}
        <Fade in timeout={800}>
          <Box sx={{ mb: 4 }}>
            <Typography
              variant={isMobile ? 'h5' : 'h4'}
              sx={{
                fontWeight: 800,
                background: 'linear-gradient(135deg, #00A859 0%, #00763E 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 1,
              }}
            >
              📊 Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Visão geral das suas operações
            </Typography>
          </Box>
        </Fade>

        {/* Cards de Métricas */}
        <Grid container spacing={{ xs: 2, md: 3 }} sx={{ mb: 4 }}>
          {/* Banca */}
          <Grid item xs={6} md={3}>
            <Zoom in timeout={600}>
              <Card
                elevation={0}
                sx={{
                  background: 'linear-gradient(135deg, #00A859 0%, #00C46A 100%)',
                  color: 'white',
                  position: 'relative',
                  overflow: 'hidden',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    right: 0,
                    width: '100px',
                    height: '100px',
                    background: 'rgba(255,255,255,0.1)',
                    borderRadius: '50%',
                    transform: 'translate(30%, -30%)',
                  },
                }}
              >
                <CardContent sx={{ p: { xs: 2, md: 3 } }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AccountBalanceWalletIcon sx={{ mr: 1, fontSize: isMobile ? 20 : 24 }} />
                    <Typography variant={isMobile ? 'body2' : 'h6'} sx={{ fontWeight: 600 }}>
                      Banca
                    </Typography>
                  </Box>
                  <Typography variant={isMobile ? 'h5' : 'h4'} sx={{ fontWeight: 800, letterSpacing: '-0.02em' }}>
                    R$ {phase?.bankroll?.toFixed(2) || '0.00'}
                  </Typography>
                </CardContent>
              </Card>
            </Zoom>
          </Grid>

          {/* Balanço */}
          <Grid item xs={6} md={3}>
            <Zoom in timeout={700}>
              <Card
                elevation={0}
                sx={{
                  background: isProfit
                    ? 'linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%)'
                    : 'linear-gradient(135deg, #F44336 0%, #EF5350 100%)',
                  color: 'white',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                <CardContent sx={{ p: { xs: 2, md: 3 } }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    {isProfit ? (
                      <TrendingUpIcon sx={{ mr: 1, fontSize: isMobile ? 20 : 24 }} />
                    ) : (
                      <TrendingDownIcon sx={{ mr: 1, fontSize: isMobile ? 20 : 24 }} />
                    )}
                    <Typography variant={isMobile ? 'body2' : 'h6'} sx={{ fontWeight: 600 }}>
                      Balanço
                    </Typography>
                  </Box>
                  <Typography variant={isMobile ? 'h5' : 'h4'} sx={{ fontWeight: 800, letterSpacing: '-0.02em' }}>
                    R$ {profit.toFixed(2)}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.9 }}>
                    ROI: {stats?.roi?.toFixed(2) || '0.00'}%
                  </Typography>
                </CardContent>
              </Card>
            </Zoom>
          </Grid>

          {/* Win Rate */}
          <Grid item xs={6} md={3}>
            <Zoom in timeout={800}>
              <Card
                elevation={0}
                sx={{
                  background: 'linear-gradient(135deg, #2196F3 0%, #42A5F5 100%)',
                  color: 'white',
                }}
              >
                <CardContent sx={{ p: { xs: 2, md: 3 } }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <EmojiEventsIcon sx={{ mr: 1, fontSize: isMobile ? 20 : 24 }} />
                    <Typography variant={isMobile ? 'body2' : 'h6'} sx={{ fontWeight: 600 }}>
                      Win Rate
                    </Typography>
                  </Box>
                  <Typography variant={isMobile ? 'h5' : 'h4'} sx={{ fontWeight: 800, letterSpacing: '-0.02em' }}>
                    {stats?.win_rate?.toFixed(1) || '0.0'}%
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.9 }}>
                    {stats?.wins || 0} / {stats?.total_bets || 0} apostas
                  </Typography>
                </CardContent>
              </Card>
            </Zoom>
          </Grid>

          {/* Fase */}
          <Grid item xs={6} md={3}>
            <Zoom in timeout={900}>
              <Card
                elevation={0}
                sx={{
                  background: 'linear-gradient(135deg, #FF9800 0%, #FFB74D 100%)',
                  color: 'white',
                }}
              >
                <CardContent sx={{ p: { xs: 2, md: 3 } }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <FlagIcon sx={{ mr: 1, fontSize: isMobile ? 20 : 24 }} />
                    <Typography variant={isMobile ? 'body2' : 'h6'} sx={{ fontWeight: 600 }}>
                      Fase {phase?.phase || 1}
                    </Typography>
                  </Box>
                  <Typography variant={isMobile ? 'h6' : 'h5'} sx={{ fontWeight: 700, mb: 1 }}>
                    R$ {phase?.target?.toFixed(2) || '0.00'}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={phase?.progress || 0}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'rgba(255,255,255,0.3)',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: 'white',
                        borderRadius: 4,
                      },
                    }}
                  />
                  <Typography variant="caption" sx={{ opacity: 0.9, mt: 0.5, display: 'block' }}>
                    {phase?.progress?.toFixed(1) || '0.0'}% completo
                  </Typography>
                </CardContent>
              </Card>
            </Zoom>
          </Grid>
        </Grid>

        {/* Histórico */}
        <Fade in timeout={1000}>
          <Paper
            elevation={0}
            sx={{
              p: { xs: 2, md: 3 },
              borderRadius: 3,
              background: 'white',
              border: '1px solid rgba(0,0,0,0.05)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <ShowChartIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant={isMobile ? 'h6' : 'h5'} sx={{ fontWeight: 700 }}>
                Últimas {isMobile ? '5' : '10'} Apostas
              </Typography>
            </Box>

            <TableContainer>
              <Table size={isMobile ? 'small' : 'medium'}>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'grey.50' }}>
                    {!isMobile && <TableCell sx={{ fontWeight: 700 }}>Data</TableCell>}
                    <TableCell sx={{ fontWeight: 700 }}>Jogo</TableCell>
                    {!isMobile && <TableCell sx={{ fontWeight: 700 }}>Mercado</TableCell>}
                    {!isTablet && <TableCell align="right" sx={{ fontWeight: 700 }}>Odd</TableCell>}
                    {!isTablet && <TableCell align="right" sx={{ fontWeight: 700 }}>Stake</TableCell>}
                    <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                    {!isMobile && <TableCell align="right" sx={{ fontWeight: 700 }}>Resultado</TableCell>}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {history.length > 0 ? (
                    history.slice(0, isMobile ? 5 : 10).map((bet, index) => (
                      <TableRow
                        key={index}
                        hover
                        sx={{
                          '&:hover': {
                            bgcolor: 'grey.50',
                          },
                        }}
                      >
                        {!isMobile && (
                          <TableCell>
                            {new Date(bet.timestamp).toLocaleDateString('pt-BR', {
                              day: '2-digit',
                              month: '2-digit',
                            })}
                          </TableCell>
                        )}
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 600, maxWidth: isMobile ? 100 : 200 }}>
                            {isMobile ? bet.match.split('x')[0].trim().substring(0, 10) + '...' : bet.match}
                          </Typography>
                          {isMobile && (
                            <Typography variant="caption" color="text.secondary">
                              {bet.market}
                            </Typography>
                          )}
                        </TableCell>
                        {!isMobile && <TableCell>{bet.market}</TableCell>}
                        {!isTablet && <TableCell align="right">{bet.odds?.toFixed(2) || '-'}</TableCell>}
                        {!isTablet && <TableCell align="right">R$ {bet.stake?.toFixed(2) || '0.00'}</TableCell>}
                        <TableCell>{getStatusChip(bet.status)}</TableCell>
                        {!isMobile && (
                          <TableCell align="right">
                            {bet.result !== null && bet.result !== undefined ? (
                              <Typography
                                variant="body2"
                                sx={{
                                  color: bet.result > 0 ? 'success.main' : 'error.main',
                                  fontWeight: 700,
                                }}
                              >
                                R$ {Number(bet.result).toFixed(2)}
                              </Typography>
                            ) : (
                              <Typography variant="body2" color="text.secondary">
                                -
                              </Typography>
                            )}
                          </TableCell>
                        )}
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={isMobile ? 3 : 7} align="center" sx={{ py: 6 }}>
                        <Typography color="text.secondary" variant="body2">
                          📭 Nenhuma aposta registrada ainda
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Fade>
      </Container>
    </Box>
  );
};

export default Dashboard;