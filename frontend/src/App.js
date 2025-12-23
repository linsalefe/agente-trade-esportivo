import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, AppBar, Toolbar, Typography, Box, Tabs, Tab, Container } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import DashboardIcon from '@mui/icons-material/Dashboard';
import theme from './theme/theme';
import Chat from './pages/Chat';
import Dashboard from './pages/Dashboard';

function Navigation() {
  const location = useLocation();
  const currentPath = location.pathname;

  return (
    <AppBar position="static" elevation={0}>
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <Typography
            variant="h5"
            sx={{
              flexGrow: 1,
              fontWeight: 700,
              color: 'white',
              textDecoration: 'none',
            }}
          >
            🎯 Value Betting Agent
          </Typography>

          <Tabs
            value={currentPath}
            textColor="inherit"
            TabIndicatorProps={{
              style: { backgroundColor: 'white' },
            }}
          >
            <Tab
              label="Chat"
              icon={<ChatIcon />}
              iconPosition="start"
              value="/"
              component={Link}
              to="/"
              sx={{ color: 'white', minHeight: 64 }}
            />
            <Tab
              label="Dashboard"
              icon={<DashboardIcon />}
              iconPosition="start"
              value="/dashboard"
              component={Link}
              to="/dashboard"
              sx={{ color: 'white', minHeight: 64 }}
            />
          </Tabs>
        </Toolbar>
      </Container>
    </AppBar>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
          <Navigation />
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;