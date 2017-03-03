var express = require('express')
var app = express()

// Use a python shell so we can run the Casper simulation
var python=require('python').shell;

app.use(express.static('public'))

app.get('/', function (req, res) {
  res.sendFile(__dirname + '/public/index.html');
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
