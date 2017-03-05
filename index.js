var express = require('express')
var app = express()

// Use a python shell so we can run the Casper simulation
var PythonShell = require('python-shell');

app.use(express.static('public'))

app.get('/', function (req, res) {
  res.sendFile(__dirname + '/public/index.html');
})

var casperSimulationResult = null;
var isSimulationRunning = false;

function printRunning() {
  if (isSimulationRunning) {
    process.stdout.write('.');
    setTimeout(printRunning, 1000);
  }
}

function onSimulationEnd(err, data) {
  if (err) {
    console.error(err);
  } else {
    isSimulationRunning = false;
    casperSimulationResult = JSON.parse(data);
    console.log('Simulation complete!')
  }
}

app.get('/results', function (req, res) {
  // We have the result value to serve up
  if (casperSimulationResult) {
    res.send(casperSimulationResult);
    return;
  }
  // We don't have the result, so we need to calculate
  if (!isSimulationRunning) {
    isSimulationRunning = true;
    console.log('Running simulation');
    PythonShell.run('casper-python/casper.py', {pythonOptions: ['-O']}, onSimulationEnd);
    printRunning();
  }
  // Reply to the request, informing the user that a simulation is running
  res.json(JSON.stringify({
    'isSimulationRunning': true
  }));
})

app.get('/simulate', function (req, res) {
  python("print('test')", function(err, data) { 
    if (err) {
      console.error(err);
    } else {
      res.json(data);
    }
  });
})

app.listen(3000, function () {
  console.log('Casper simulator listening on port 3000!')
})

// a callback to handle the response 
var mycallback = function(err, data) {
};
