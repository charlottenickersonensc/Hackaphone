import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import axios from 'axios';
import { 
  CssBaseline, 
  ThemeProvider, 
  createTheme, 
  Box 
} from '@mui/material';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import VisualizerPage from './pages/VisualizerPage';
import NotFound from './pages/NotFound';
import './App.css';

// Création du thème sombre pour notre application
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
});

function App() {
  // État pour stocker les visualisations disponibles
  const [visualizations, setVisualizations] = useState([]);
  // État pour stocker le statut des visualisations
  const [status, setStatus] = useState({});
  // État pour suivre si les données sont en cours de chargement
  const [loading, setLoading] = useState(true);
  
  // Récupérer la liste des visualisations au chargement de l'application
  useEffect(() => {
    // Fonction pour charger les visualisations depuis l'API
    const fetchVisualizations = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/visualizations');
        setVisualizations(response.data);
        
        // Récupérer également le statut actuel des visualisations
        const statusResponse = await axios.get('/api/status');
        setStatus(statusResponse.data);
      } catch (error) {
        console.error('Erreur lors du chargement des visualisations:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchVisualizations();
    
    // Mettre en place un intervalle pour la mise à jour du statut des visualisations
    const statusInterval = setInterval(async () => {
      try {
        const statusResponse = await axios.get('/api/status');
        setStatus(statusResponse.data);
      } catch (error) {
        console.error('Erreur lors de la mise à jour du statut:', error);
      }
    }, 5000); // Mise à jour toutes les 5 secondes
    
    // Nettoyer l'intervalle lorsque le composant est démonté
    return () => clearInterval(statusInterval);
  }, []);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        <Box sx={{ flexGrow: 1, padding: 3 }}>
          <Routes>
            <Route 
              path="/" 
              element={
                <Dashboard 
                  visualizations={visualizations} 
                  status={status}
                  loading={loading} 
                />
              } 
            />
            <Route 
              path="/visualizer/:id" 
              element={
                <VisualizerPage 
                  visualizations={visualizations} 
                  status={status}
                />
              } 
            />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;