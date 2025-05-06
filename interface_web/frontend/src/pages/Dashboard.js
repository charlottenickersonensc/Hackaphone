import React from 'react';
import { 
  Grid, 
  Typography, 
  Container, 
  CircularProgress, 
  Box 
} from '@mui/material';
import VisualizationCard from '../components/VisualizationCard';

const Dashboard = ({ visualizations, status, loading }) => {
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        Tableau de Bord des Visualisations
      </Typography>
      <Typography variant="body1" paragraph>
        Bienvenue dans l'interface de gestion des visualisations Hackaphone. 
        Sélectionnez une visualisation pour la démarrer, l'arrêter ou voir ses détails.
      </Typography>
      
      {loading ? (
        <Box className="loading-container">
          <CircularProgress />
        </Box>
      ) : visualizations.length > 0 ? (
        <Grid container spacing={3}>
          {visualizations.map((visualization) => (
            <Grid item xs={12} sm={6} md={4} key={visualization.id}>
              <VisualizationCard 
                visualization={visualization} 
                status={status} 
              />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Box 
          sx={{ 
            py: 4, 
            textAlign: 'center' 
          }}
        >
          <Typography variant="h6">
            Aucune visualisation disponible
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Veuillez vérifier la configuration du serveur.
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default Dashboard;