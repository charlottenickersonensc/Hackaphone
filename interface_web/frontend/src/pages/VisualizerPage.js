import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Container,
  Grid,
  Alert,
  Card,
  CardContent,
  Switch,
  FormControlLabel
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import HomeIcon from '@mui/icons-material/Home';
import WebVisualizer from '../components/WebVisualizer';

const VisualizerPage = ({ visualizations, status }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [visualization, setVisualization] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [useWebVisualizer, setUseWebVisualizer] = useState(true);
  
  // Trouver la visualisation correspondant à l'ID
  useEffect(() => {
    const viz = visualizations.find(v => v.id === id);
    if (viz) {
      setVisualization(viz);
      setIsRunning(status[id] === 'running');
    } else {
      setError("Visualisation non trouvée");
    }
    setLoading(false);
  }, [id, visualizations, status]);

  // Fonction pour démarrer la visualisation
  const handleStart = async () => {
    try {
      setLoading(true);
      
      if (useWebVisualizer) {
        // Si on utilise le visualiseur web, on met juste à jour l'état local
        setIsRunning(true);
      } else {
        // Sinon, on lance le processus Python via l'API
        const response = await axios.post(`/api/start/${id}`);
        if (response.data.status === 'started') {
          setIsRunning(true);
        }
      }
    } catch (error) {
      setError(`Erreur lors du démarrage: ${error.response?.data?.message || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Fonction pour arrêter la visualisation
  const handleStop = async () => {
    try {
      setLoading(true);
      
      if (useWebVisualizer) {
        // Si on utilise le visualiseur web, on met juste à jour l'état local
        setIsRunning(false);
      } else {
        // Sinon, on arrête le processus Python via l'API
        const response = await axios.post(`/api/stop/${id}`);
        if (response.data.status === 'stopped') {
          setIsRunning(false);
        }
      }
    } catch (error) {
      setError(`Erreur lors de l'arrêt: ${error.response?.data?.message || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Fonction pour basculer entre le visualiseur web et le visualiseur Python
  const handleVisualizerToggle = (event) => {
    // Si une visualisation est en cours, on l'arrête d'abord
    if (isRunning) {
      handleStop();
    }
    setUseWebVisualizer(event.target.checked);
  };

  if (loading && !visualization) {
    return (
      <Box className="loading-container">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>
        <Button 
          variant="contained" 
          startIcon={<HomeIcon />} 
          onClick={() => navigate('/')}
          sx={{ mt: 2 }}
        >
          Retour à l'accueil
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      {visualization && (
        <>
          <Typography variant="h4" component="h1" gutterBottom>
            {visualization.name}
          </Typography>
          
          <Paper className="visualizer-control-panel" elevation={3}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={6}>
                <Typography variant="body1">
                  {visualization.description}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={useWebVisualizer}
                      onChange={handleVisualizerToggle}
                      color="primary"
                    />
                  }
                  label="Visualiser dans le navigateur"
                />
              </Grid>
              <Grid item xs={12} md={3} sx={{ textAlign: 'right' }}>
                {!isRunning ? (
                  <Button 
                    variant="contained" 
                    color="primary" 
                    startIcon={<PlayArrowIcon />}
                    onClick={handleStart}
                    disabled={loading}
                    fullWidth
                  >
                    Démarrer
                  </Button>
                ) : (
                  <Button 
                    variant="contained" 
                    color="error" 
                    startIcon={<StopIcon />}
                    onClick={handleStop}
                    disabled={loading}
                    fullWidth
                  >
                    Arrêter
                  </Button>
                )}
              </Grid>
            </Grid>
          </Paper>
          
          {useWebVisualizer ? (
            // Afficher le visualiseur web si cette option est choisie
            isRunning ? (
              <WebVisualizer 
                visualizationType={id}
                isRunning={isRunning} 
              />
            ) : (
              <Card sx={{ bgcolor: '#1a1a1a', mb: 4 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Visualiseur Web
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Cliquez sur "Démarrer" pour lancer la visualisation dans votre navigateur.
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Cette fonction utilise le microphone de votre appareil pour capter le son et créer une visualisation en temps réel.
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Note: Le navigateur vous demandera l'autorisation d'accéder à votre microphone.
                  </Typography>
                </CardContent>
              </Card>
            )
          ) : (
            // Afficher des instructions pour le visualiseur Python
            isRunning ? (
              <Paper sx={{ p: 0, height: '60vh', bgcolor: 'black', position: 'relative' }}>
                <Box sx={{ 
                  position: 'absolute', 
                  top: '50%', 
                  left: '50%', 
                  transform: 'translate(-50%, -50%)',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <Typography variant="body1" paragraph>
                    La visualisation "{visualization.name}" est en cours d'exécution.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Veuillez vérifier la fenêtre de visualisation qui s'est ouverte sur votre ordinateur.
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 2 }}>
                    Pour afficher la visualisation dans le navigateur, activez l'option "Visualiser dans le navigateur".
                  </Typography>
                </Box>
              </Paper>
            ) : (
              <Card sx={{ bgcolor: '#1a1a1a', mb: 4 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Instructions:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    1. Cliquez sur "Démarrer" pour lancer cette visualisation.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    2. Une nouvelle fenêtre s'ouvrira pour afficher la visualisation.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    3. Pour arrêter, cliquez sur "Arrêter" ou fermez la fenêtre de visualisation.
                  </Typography>
                </CardContent>
              </Card>
            )
          )}
          
          <Button 
            variant="outlined" 
            startIcon={<HomeIcon />} 
            onClick={() => navigate('/')}
            sx={{ mt: 2 }}
          >
            Retour au tableau de bord
          </Button>
        </>
      )}
    </Container>
  );
};

export default VisualizerPage;