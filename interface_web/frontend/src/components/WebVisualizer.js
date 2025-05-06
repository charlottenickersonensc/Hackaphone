import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';

// Composant qui affichera les visualisations dans le navigateur
const WebVisualizer = ({ visualizationType, isRunning }) => {
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const animationRef = useRef(null);
  
  // Configuration et démarrage de l'analyse audio
  useEffect(() => {
    let audioContext, analyser, microphone, dataArray;
    
    const setupAudio = async () => {
      try {
        // Créer un contexte audio
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        audioContextRef.current = audioContext;
        
        // Demander l'accès au microphone
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
        
        // Créer un nœud d'analyse
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;
        analyserRef.current = analyser;
        
        // Connecter le microphone à l'analyseur
        microphone = audioContext.createMediaStreamSource(stream);
        microphone.connect(analyser);
        
        // Préparer le tableau de données pour l'analyse
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);
        dataArrayRef.current = dataArray;
        
        // Commencer l'animation
        startVisualization();
      } catch (error) {
        console.error("Erreur lors de la configuration de l'audio:", error);
      }
    };
    
    // Nettoyer les ressources audio
    const cleanupAudio = () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
      
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    };
    
    // Démarrer ou arrêter en fonction de l'état
    if (isRunning) {
      setupAudio();
    } else {
      cleanupAudio();
    }
    
    // Nettoyage lors du démontage du composant
    return () => {
      cleanupAudio();
    };
  }, [isRunning]);
  
  // Fonction pour démarrer la visualisation
  const startVisualization = () => {
    if (!canvasRef.current || !analyserRef.current || !dataArrayRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const analyser = analyserRef.current;
    const dataArray = dataArrayRef.current;
    
    // Ajuster la taille du canvas à celle de son conteneur
    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener('resize', resize);
    
    // Fonction d'animation qui sera appelée à chaque frame
    const animate = () => {
      if (!isRunning) return;
      
      animationRef.current = requestAnimationFrame(animate);
      
      // Obtenir les données audio
      analyser.getByteFrequencyData(dataArray);
      
      // Effacer le canvas
      ctx.fillStyle = 'rgb(0, 0, 0)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Dessiner la visualisation en fonction du type sélectionné
      switch(visualizationType) {
        case 'frequency_bands':
          drawFrequencyBands(ctx, dataArray, canvas);
          break;
        case 'waveform':
          drawWaveform(ctx, dataArray, canvas, analyser);
          break;
        case 'spectrum':
          drawSpectrum(ctx, dataArray, canvas);
          break;
        case 'cool_sphere':
          drawCoolSphere(ctx, dataArray, canvas);
          break;
        case 'psychadelic':
          drawPsychedelic(ctx, dataArray, canvas);
          break;
        default:
          drawDefaultVisualization(ctx, dataArray, canvas);
          break;
      }
    };
    
    animate();
  };
  
  return (
    <Box sx={{ width: '100%', height: '60vh', bgcolor: 'black' }}>
      <canvas 
        ref={canvasRef} 
        style={{ width: '100%', height: '100%' }} 
      />
    </Box>
  );
};

// Fonctions pour dessiner différents types de visualisations

// Visualisation des bandes de fréquence
function drawFrequencyBands(ctx, dataArray, canvas) {
  const bufferLength = dataArray.length;
  const barWidth = canvas.width / bufferLength * 2.5;
  let x = 0;
  
  for (let i = 0; i < bufferLength; i++) {
    const barHeight = dataArray[i] * 1.5;
    
    // Couleur basée sur la fréquence
    const r = 50 + dataArray[i] + (i / bufferLength * 100);
    const g = 50 + (i / bufferLength * 200);
    const b = 250;
    
    ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
    ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
    
    x += barWidth + 1;
  }
}

// Visualisation de la forme d'onde
function drawWaveform(ctx, dataArray, canvas, analyser) {
  const bufferLength = analyser.fftSize;
  const waveformData = new Uint8Array(bufferLength);
  analyser.getByteTimeDomainData(waveformData);
  
  ctx.lineWidth = 2;
  ctx.strokeStyle = 'rgb(0, 255, 0)';
  ctx.beginPath();
  
  const sliceWidth = canvas.width / bufferLength;
  let x = 0;
  
  for (let i = 0; i < bufferLength; i++) {
    const v = waveformData[i] / 128.0;
    const y = v * canvas.height / 2;
    
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
    
    x += sliceWidth;
  }
  
  ctx.lineTo(canvas.width, canvas.height / 2);
  ctx.stroke();
}

// Visualisation spectrale
function drawSpectrum(ctx, dataArray, canvas) {
  const bufferLength = dataArray.length;
  const barWidth = canvas.width / bufferLength;
  let x = 0;
  
  for (let i = 0; i < bufferLength; i++) {
    const barHeight = dataArray[i] / 255 * canvas.height;
    
    // Dégradé de couleurs pour le spectre
    const hue = i / bufferLength * 360;
    ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
    ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
    
    x += barWidth;
  }
}

// Visualisation sphère cool
function drawCoolSphere(ctx, dataArray, canvas) {
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  
  // Calculer l'amplitude moyenne
  let sum = 0;
  for (let i = 0; i < dataArray.length; i++) {
    sum += dataArray[i];
  }
  const average = sum / dataArray.length;
  
  // Dessiner plusieurs cercles qui pulsent avec la musique
  const baseRadius = Math.min(canvas.width, canvas.height) / 4;
  const numCircles = 5;
  
  for (let j = 0; j < numCircles; j++) {
    // Rayon basé sur l'amplitude et l'index du cercle
    const radius = baseRadius * (0.5 + (average / 255) * 0.5) * ((numCircles - j) / numCircles);
    
    // Couleur qui change avec la fréquence
    const hue = (j * 30 + Date.now() / 50) % 360;
    ctx.strokeStyle = `hsl(${hue}, 80%, 60%)`;
    ctx.lineWidth = 2 + (average / 255) * 3;
    
    // Dessiner le cercle
    ctx.beginPath();
    ctx.arc(
      centerX, 
      centerY, 
      radius, 
      0, 
      2 * Math.PI
    );
    ctx.stroke();
  }
}

// Visualisation psychédélique
function drawPsychedelic(ctx, dataArray, canvas) {
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const time = Date.now() / 1000;
  
  // Créer un dégradé qui tourne et pulse avec la musique
  const gradient = ctx.createRadialGradient(
    centerX, centerY, 0,
    centerX, centerY, canvas.width / 2
  );
  
  // Ajouter des couleurs au dégradé
  for (let i = 0; i < 6; i++) {
    const pos = i / 5;
    const hue = (time * 20 + i * 60) % 360;
    
    // Utiliser la valeur audio pour la saturation
    const bassIndex = Math.floor(dataArray.length * 0.1);
    const midIndex = Math.floor(dataArray.length * 0.5);
    const trebleIndex = Math.floor(dataArray.length * 0.8);
    
    const bassValue = dataArray[bassIndex] / 255;
    const midValue = dataArray[midIndex] / 255;
    const trebleValue = dataArray[trebleIndex] / 255;
    
    // Saturation basée sur les fréquences médiums
    const saturation = 70 + midValue * 30;
    
    // Luminosité basée sur les basses
    const lightness = 40 + bassValue * 30;
    
    gradient.addColorStop(pos, `hsl(${hue}, ${saturation}%, ${lightness}%)`);
  }
  
  // Appliquer le dégradé
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // Dessiner des formes qui réagissent aux hautes fréquences
  const trebleIndex = Math.floor(dataArray.length * 0.8);
  const trebleValue = dataArray[trebleIndex] / 255;
  
  if (trebleValue > 0.5) {
    const numShapes = 5 + Math.floor(trebleValue * 10);
    
    for (let i = 0; i < numShapes; i++) {
      const x = Math.random() * canvas.width;
      const y = Math.random() * canvas.height;
      const size = 5 + Math.random() * 20 * trebleValue;
      
      ctx.fillStyle = `hsla(${Math.random() * 360}, 100%, 70%, 0.7)`;
      ctx.beginPath();
      ctx.arc(x, y, size, 0, 2 * Math.PI);
      ctx.fill();
    }
  }
}

// Visualisation par défaut
function drawDefaultVisualization(ctx, dataArray, canvas) {
  const bufferLength = dataArray.length;
  const barWidth = canvas.width / bufferLength;
  let x = 0;
  
  for (let i = 0; i < bufferLength; i++) {
    const barHeight = dataArray[i] * 1.5;
    
    // Couleur simple
    ctx.fillStyle = `rgb(50, 100, ${barHeight + 100})`;
    ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
    
    x += barWidth + 1;
  }
}

export default WebVisualizer;