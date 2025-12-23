import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  CircularProgress,
  useTheme,
  useMediaQuery,
  Fade,
  Chip,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { sendChatMessage, getOpportunities, getStatistics, getCurrentPhase } from '../services/api';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Olá! 👋 Sou seu assistente de value betting. Como posso ajudar você hoje?',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [context, setContext] = useState(null);
  const messagesEndRef = useRef(null);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    loadContext();
  }, []);

  const loadContext = async () => {
    try {
      const [opportunities, stats, phase] = await Promise.all([
        getOpportunities(100),
        getStatistics(),
        getCurrentPhase(),
      ]);
      
      setContext({
        bankroll: phase.bankroll,
        phase: phase.phase,
        opportunities: opportunities.opportunities?.slice(0, 5) || [],
        multiples: opportunities.multiples?.slice(0, 2) || [],
        stats: stats,
      });
    } catch (error) {
      console.error('Erro ao carregar contexto:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Envia contexto se a pergunta for relevante
      const needsContext = input.toLowerCase().includes('jogo') ||
                          input.toLowerCase().includes('aposta') ||
                          input.toLowerCase().includes('hoje') ||
                          input.toLowerCase().includes('oportunidade') ||
                          input.toLowerCase().includes('múltipla');
      
      const response = await sendChatMessage(input, needsContext ? context : null);
      const assistantMessage = { role: 'assistant', content: response.message };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro. Tente novamente. 😔',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickQuestions = [
    '💡 O que é EV?',
    '📊 Quais os jogos de hoje?',
    '🎯 Como funciona a gestão de banca?',
    '📈 Vale a pena fazer múltiplas?',
  ];

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #F5F7FA 0%, #E8EEF2 100%)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Container
        maxWidth="md"
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          py: { xs: 2, md: 3 },
        }}
      >
        {/* Header */}
        <Fade in timeout={600}>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <AutoAwesomeIcon
                sx={{
                  color: 'primary.main',
                  fontSize: isMobile ? 28 : 32,
                }}
              />
              <Typography
                variant={isMobile ? 'h5' : 'h4'}
                sx={{
                  fontWeight: 800,
                  background: 'linear-gradient(135deg, #00A859 0%, #00763E 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Chat com Agente
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Tire suas dúvidas sobre value betting
            </Typography>
          </Box>
        </Fade>

        {/* Quick Questions */}
        {messages.length === 1 && (
          <Fade in timeout={800}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                Perguntas rápidas:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {quickQuestions.map((question, index) => (
                  <Chip
                    key={index}
                    label={question}
                    onClick={() => setInput(question.substring(2))}
                    sx={{
                      cursor: 'pointer',
                      fontWeight: 500,
                      '&:hover': {
                        bgcolor: 'primary.main',
                        color: 'white',
                      },
                    }}
                  />
                ))}
              </Box>
            </Box>
          </Fade>
        )}

        {/* Chat Container */}
        <Paper
          elevation={0}
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            borderRadius: 3,
            border: '1px solid rgba(0,0,0,0.05)',
            background: 'white',
          }}
        >
          {/* Messages Area */}
          <Box
            sx={{
              flex: 1,
              overflowY: 'auto',
              p: { xs: 2, md: 3 },
              background: 'linear-gradient(180deg, #FAFBFC 0%, #FFFFFF 100%)',
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                background: 'transparent',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#D1D5DB',
                borderRadius: '4px',
              },
            }}
          >
            {messages.map((msg, index) => (
              <Fade in key={index} timeout={400}>
                <Box
                  sx={{
                    display: 'flex',
                    mb: 3,
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    animation: 'slideIn 0.3s ease',
                    '@keyframes slideIn': {
                      from: {
                        opacity: 0,
                        transform: 'translateY(10px)',
                      },
                      to: {
                        opacity: 1,
                        transform: 'translateY(0)',
                      },
                    },
                  }}
                >
                  {msg.role === 'assistant' && (
                    <Avatar
                      sx={{
                        bgcolor: 'primary.main',
                        mr: 1.5,
                        width: isMobile ? 36 : 40,
                        height: isMobile ? 36 : 40,
                        boxShadow: '0 4px 12px rgba(0,168,89,0.3)',
                      }}
                    >
                      <SmartToyIcon fontSize="small" />
                    </Avatar>
                  )}

                  <Paper
                    elevation={0}
                    sx={{
                      p: { xs: 1.5, md: 2 },
                      maxWidth: { xs: '75%', md: '70%' },
                      background:
                        msg.role === 'user'
                          ? 'linear-gradient(135deg, #00A859 0%, #00C46A 100%)'
                          : 'white',
                      color: msg.role === 'user' ? 'white' : 'text.primary',
                      borderRadius: 3,
                      border: msg.role === 'assistant' ? '1px solid rgba(0,0,0,0.08)' : 'none',
                      boxShadow:
                        msg.role === 'user'
                          ? '0 4px 12px rgba(0,168,89,0.3)'
                          : '0 2px 8px rgba(0,0,0,0.08)',
                    }}
                  >
                    <Typography
                      variant="body1"
                      sx={{
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.6,
                        fontSize: isMobile ? '0.9rem' : '1rem',
                      }}
                    >
                      {msg.content}
                    </Typography>
                  </Paper>

                  {msg.role === 'user' && (
                    <Avatar
                      sx={{
                        bgcolor: 'secondary.main',
                        ml: 1.5,
                        width: isMobile ? 36 : 40,
                        height: isMobile ? 36 : 40,
                        boxShadow: '0 4px 12px rgba(33,33,33,0.3)',
                      }}
                    >
                      <PersonIcon fontSize="small" />
                    </Avatar>
                  )}
                </Box>
              </Fade>
            ))}

            {loading && (
              <Fade in>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Avatar
                    sx={{
                      bgcolor: 'primary.main',
                      mr: 1.5,
                      width: isMobile ? 36 : 40,
                      height: isMobile ? 36 : 40,
                    }}
                  >
                    <SmartToyIcon fontSize="small" />
                  </Avatar>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2,
                      borderRadius: 3,
                      border: '1px solid rgba(0,0,0,0.08)',
                    }}
                  >
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      {[0, 0.2, 0.4].map((delay, i) => (
                        <Box
                          key={i}
                          sx={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            bgcolor: 'primary.main',
                            animation: 'pulse 1.4s infinite',
                            animationDelay: `${delay}s`,
                            '@keyframes pulse': {
                              '0%, 80%, 100%': { opacity: 0.4 },
                              '40%': { opacity: 1 },
                            },
                          }}
                        />
                      ))}
                    </Box>
                  </Paper>
                </Box>
              </Fade>
            )}

            <div ref={messagesEndRef} />
          </Box>

          {/* Input Area */}
          <Box
            sx={{
              p: { xs: 2, md: 2.5 },
              bgcolor: 'white',
              borderTop: '1px solid rgba(0,0,0,0.08)',
            }}
          >
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Digite sua mensagem..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading}
                multiline
                maxRows={4}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 3,
                    bgcolor: 'grey.50',
                    '&:hover': {
                      bgcolor: 'grey.100',
                    },
                    '&.Mui-focused': {
                      bgcolor: 'white',
                    },
                  },
                }}
              />
              <IconButton
                onClick={handleSend}
                disabled={!input.trim() || loading}
                sx={{
                  width: { xs: 48, md: 56 },
                  height: { xs: 48, md: 56 },
                  background: 'linear-gradient(135deg, #00A859 0%, #00C46A 100%)',
                  color: 'white',
                  boxShadow: '0 4px 12px rgba(0,168,89,0.3)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #00763E 0%, #00A859 100%)',
                    transform: 'scale(1.05)',
                  },
                  '&:disabled': {
                    bgcolor: 'grey.300',
                    color: 'grey.500',
                  },
                  transition: 'all 0.2s ease',
                }}
              >
                <SendIcon />
              </IconButton>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default Chat;