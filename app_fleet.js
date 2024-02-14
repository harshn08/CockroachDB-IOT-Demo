const express = require('express');
const { Pool } = require('pg');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

const pool = new Pool({
  user: "",
  host: "",
  database: "",
  password: "",
  port: 26257,
  ssl: {
    rejectUnauthorized: false,
  }
});

// Render files from the 'views' directory

app.set('view engine', 'ejs');

app.get('/', (req, res) => {
    res.render('index');
  });

// Route to fetch vehicle data
app.get('/vehicles', async (req, res) => {
  try {
    const result = await pool.query("SELECT v.VehicleID, v.Latitude, v.Longitude, f.FleetName, to_char(ms.NextDue, 'MM/DD/YYYY') AS NextDueDate FROM movr_demo.public.Vehicle v JOIN Fleet f ON v.FleetID = f.FleetID LEFT JOIN MaintenanceSchedule ms ON v.VehicleID = ms.VehicleID;");
    const vehicleData = result.rows;
    res.json(vehicleData);
  } catch (error) {
    console.error('Error fetching vehicle data:', error);
    res.status(500).json({ error: 'Error fetching vehicle data' });
  }
});

// Detailed dashboard route
app.get('/vehicle/:vehicleId/dashboard', async (req, res) => {
    const vehicleId = req.params.vehicleId;
    try {
      // Query database to get detailed dashboard data based on vehicleId
      const result = await pool.query("SELECT * FROM movr_demo.public.Vehicle WHERE VehicleID = '" + vehicleId + "'");
      const vehicleData = result.rows[0];
      // Render the detailed dashboard page with vehicle data
      res.render('dashboard', { vehicleId });
    } catch (error) {
      console.error('Error fetching vehicle data:', error);
      res.status(500).send('Error fetching vehicle data');
    }
  });
  
  // Diagnostic data route
  app.get('/vehicle/:vehicleId/diagnostic', async (req, res) => {
    const vehicleId = req.params.vehicleId;
    try {
      // Query database to get diagnostic data based on vehicleId
      const result = await pool.query("SELECT * FROM movr_demo.public.Diagnostic WHERE VehicleID = '" + vehicleId + "' ORDER BY timestamp ASC");
      const diagnosticData = result.rows;
      // Return the diagnostic data as JSON
      res.json(diagnosticData);
    } catch (error) {
      console.error('Error fetching diagnostic data:', error);
      res.status(500).json({ error: 'Error fetching diagnostic data' });
    }
  });
  
  // Location history route
  app.get('/vehicle/:vehicleId/locationhistory', async (req, res) => {
    const vehicleId = req.params.vehicleId;
    try {
      // Query database to get location history data based on vehicleId
      const result = await pool.query("SELECT * FROM movr_demo.public.LocationHistory WHERE VehicleID = '" + vehicleId + "'");
      const locationHistoryData = result.rows;
      // Return the location history data as JSON
      res.json(locationHistoryData);
    } catch (error) {
      console.error('Error fetching location history data:', error);
      res.status(500).json({ error: 'Error fetching location history data' });
    }
  });

// Start the server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
