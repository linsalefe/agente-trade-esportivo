import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  CircularProgress,
  useTheme,
  useMediaQuery,
  Fade,
  Alert,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SportsIcon from '@mui/icons-material/Sports';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import { getOpportunities } from '../services/api';

const Opportunities = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [multiples, setMultiples] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    loadOpportunities();
  }, []);

  const loadOpportunities = async () => {
    try {
      setLoading(true);
      const data = await getOpportunities(100);
      setOpportunities(data.opportunities || []);
      setMultiples(data.multiples || []);
    } catch (error) {
      console.error('Erro ao carregar oportunidades:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = () => {
    const hoje = new Date();
    return hoje.toLocaleDateString('pt-BR', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric' 
    });
  };

  if (loading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #F5F7FA 0%, #E8EEF2 100%)',
        }}
      >
        <CircularProgress size={60} sx={{ color: 'primary.main' }} />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #F5F7FA 0%, #E8EEF2 100%)',
        py: { xs: 3, md: 4 },
      }}
    >
      <Container maxWidth="lg">
        {/* Header */}
        <Fade in timeout={600}>
          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
              <SportsIcon
                sx={{
                  color: 'primary.main',
                  fontSize: isMobile ? 32 : 40,
                }}
              />
              <Typography
                variant={isMobile ? 'h4' : 'h3'}
                sx={{
                  fontWeight: 800,
                  background: 'linear-gradient(135deg, #00A859 0%, #00763E 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Oportunidades de Hoje
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <CalendarTodayIcon fontSize="small" color="action" />
              <Typography variant="body1" color="text.secondary">
                {formatDate()}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip
                label={`${opportunities.length} Apostas Simples`}
                sx={{
                  bgcolor: 'primary.main',
                  color: 'white',
                  fontWeight: 600,
                }}
              />
              {multiples.length > 0 && (
                <Chip
                  label={`${multiples.length} Múltiplas`}
                  sx={{
                    bgcolor: 'secondary.main',
                    color: 'white',
                    fontWeight: 600,
                  }}
                />
              )}
            </Box>
          </Box>
        </Fade>

        {/* Sem Oportunidades */}
        {opportunities.length === 0 && (
          <Fade in timeout={800}>
            <Alert
              severity="info"
              sx={{
                borderRadius: 3,
                fontSize: '1rem',
                '& .MuiAlert-icon': {
                  fontSize: 28,
                },
              }}
            >
              <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                Nenhuma oportunidade com bom +EV hoje
              </Typography>
              <Typography variant="body2">
                Não encontramos apostas com valor esperado positivo suficiente. 
                Isso é normal em dias com poucos jogos (como vésperas de feriados).
                Continue acompanhando!
              </Typography>
            </Alert>
          </Fade>
        )}

        {/* Lista de Oportunidades */}
        {opportunities.length > 0 && (
          <Grid container spacing={3}>
            {opportunities.map((opp, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Fade in timeout={600 + index * 100}>
                  <Card
                    elevation={0}
                    sx={{
                      borderRadius: 3,
                      border: '1px solid rgba(0,0,0,0.08)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 24px rgba(0,168,89,0.15)',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 3 }}>
                      {/* Header do Card */}
                      <Box sx={{ mb: 2 }}>
                        <Typography
                          variant="h6"
                          sx={{
                            fontWeight: 700,
                            mb: 0.5,
                            color: 'text.primary',
                          }}
                        >
                          {opp.match}
                        </Typography>
                        <Typography
                          variant="caption"
                          sx={{
                            color: 'text.secondary',
                            textTransform: 'uppercase',
                            letterSpacing: 0.5,
                          }}
                        >
                          {opp.competition}
                        </Typography>
                      </Box>

                      <Divider sx={{ my: 2 }} />

                      {/* Informações da Aposta */}
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                            Mercado
                          </Typography>
                          <Typography variant="body1" fontWeight={600}>
                            {opp.market}
                          </Typography>
                        </Grid>

                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                            Odd
                          </Typography>
                          <Typography variant="body1" fontWeight={600} color="primary.main">
                            {opp.odds.toFixed(2)}
                          </Typography>
                        </Grid>

                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                            EV (Valor Esperado)
                          </Typography>
                          <Chip
                            label={`+${opp.ev.toFixed(1)}%`}
                            size="small"
                            sx={{
                              bgcolor: 'success.main',
                              color: 'white',
                              fontWeight: 700,
                            }}
                          />
                        </Grid>

                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                            Probabilidade
                          </Typography>
                          <Typography variant="body2" fontWeight={600}>
                            {(opp.probability * 100).toFixed(1)}%
                          </Typography>
                        </Grid>

                        <Grid item xs={12}>
                          <Box
                            sx={{
                              mt: 1,
                              p: 2,
                              borderRadius: 2,
                              background: 'linear-gradient(135deg, #00A859 0%, #00C46A 100%)',
                            }}
                          >
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Box>
                                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                                  Stake Sugerido
                                </Typography>
                                <Typography variant="h6" sx={{ color: 'white', fontWeight: 700 }}>
                                  R$ {opp.stake.toFixed(2)}
                                </Typography>
                              </Box>
                              <Box sx={{ textAlign: 'right' }}>
                                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                                  Retorno Potencial
                                </Typography>
                                <Typography variant="h6" sx={{ color: 'white', fontWeight: 700 }}>
                                  R$ {opp.potential_return.toFixed(2)}
                                </Typography>
                              </Box>
                            </Box>
                          </Box>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </Fade>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Múltiplas */}
        {multiples.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 700,
                mb: 3,
                color: 'text.primary',
              }}
            >
              🎯 Múltiplas Estratégicas
            </Typography>
            <Grid container spacing={3}>
              {multiples.map((multiple, index) => (
                <Grid item xs={12} key={index}>
                  <Fade in timeout={800 + index * 100}>
                    <Card
                      elevation={0}
                      sx={{
                        borderRadius: 3,
                        border: '2px solid',
                        borderColor: 'secondary.main',
                        background: 'linear-gradient(135deg, #FFF9F0 0%, #FFFFFF 100%)',
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                          Múltipla #{index + 1} - Odd Combinada: {multiple.combined_odds?.toFixed(2)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {multiple.description || `${multiple.legs?.length || 0} pernas combinadas`}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Fade>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Container>
    </Box>
  );
};

export default Opportunities;