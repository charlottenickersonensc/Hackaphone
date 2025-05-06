import React from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Card, 
  CardContent, 
  CardMedia, 
  Typography, 
  CardActionArea, 
  CardActions, 
  Button, 
  Chip 
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';

const VisualizationCard = ({ visualization, status }) => {
  const navigate = useNavigate();
  const isRunning = status[visualization.id] === 'running';
  
  // Fonction pour démarrer une visualisation
  const handleStart = async (e) => {
    e.stopPropagation(); // Éviter la navigation lors du clic sur le bouton
    
    try {
      await axios.post(`/api/start/${visualization.id}`);
      // La mise à jour du statut se fera via le polling dans App.js
    } catch (error) {
      console.error(`Erreur lors du démarrage de la visualisation ${visualization.id}:`, error);
      alert(`Erreur lors du démarrage de la visualisation: ${error.response?.data?.message || error.message}`);
    }
  };
  
  // Fonction pour arrêter une visualisation
  const handleStop = async (e) => {
    e.stopPropagation(); // Éviter la navigation lors du clic sur le bouton
    
    try {
      await axios.post(`/api/stop/${visualization.id}`);
      // La mise à jour du statut se fera via le polling dans App.js
    } catch (error) {
      console.error(`Erreur lors de l'arrêt de la visualisation ${visualization.id}:`, error);
      alert(`Erreur lors de l'arrêt de la visualisation: ${error.response?.data?.message || error.message}`);
    }
  };
  
  // Génère une image de prévisualisation basée sur l'ID (pour démonstration)
  // Dans un environnement réel, vous pourriez stocker des images réelles pour chaque visualisation
  const getImageUrl = (id) => {
    return `https://picsum.photos/seed/${id}/400/300`;
  };
  
  return (
    <Card className="visualization-card">
      <CardActionArea onClick={() => navigate(`/visualizer/${visualization.id}`)}>
        <CardMedia
          component="div"
          sx={{
            height: 200,
            backgroundImage: `url(${getImageUrl(visualization.id)})`,
            backgroundColor: '#303030',
            position: 'relative',
          }}
        >
          <div 
            className={`status-indicator ${isRunning ? 'status-running' : 'status-stopped'}`}
          />
        </CardMedia>
        <CardContent className="visualization-card-content">
          <Typography gutterBottom variant="h5" component="div">
            {visualization.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {visualization.description || "Aucune description disponible."}
          </Typography>
          <Chip 
            label={isRunning ? "En cours d'exécution" : "Arrêté"} 
            color={isRunning ? "success" : "error"} 
            size="small" 
            sx={{ mt: 2 }} 
          />
        </CardContent>
      </CardActionArea>
      <CardActions>
        {!isRunning ? (
          <Button 
            size="small" 
            color="primary" 
            startIcon={<PlayArrowIcon />} 
            onClick={handleStart}
          >
            Démarrer
          </Button>
        ) : (
          <Button 
            size="small" 
            color="error" 
            startIcon={<StopIcon />} 
            onClick={handleStop}
          >
            Arrêter
          </Button>
        )}
        <Button size="small" onClick={() => navigate(`/visualizer/${visualization.id}`)}>
          Détails
        </Button>
      </CardActions>
    </Card>
  );
};

export default VisualizationCard;