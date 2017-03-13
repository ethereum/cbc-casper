var width = window.innerWidth;
var height = window.innerHeight*0.9;

var svg = d3.select("svg")
            .attr("width", width)
            .attr("height", height);

var color = d3.scaleOrdinal(d3.schemeCategory20);
var nodeRadius = 10;

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }))
    .force("charge", d3.forceManyBody())

var plotViewData;
var maxStage;
var currentStage = 0;

d3.json("/results", function(error, graphData) {
  if (error) throw error;

  maxStage = graphData.length-1;
  document.getElementById('stage-slider').setAttribute("max", maxStage+1);
  plotViewData = { 
    links: [], 
    nodes: graphData[0].nodes.map(function (node) {
      return Object.assign({}, node, {
        stage: 0,
      });
    })
  };
  for (var i = 1; i < graphData.length; i++) {
    var linksDiff = _.differenceWith(graphData[i].links, graphData[i-1].links, _.isEqual);
    var nodesDiff = _.differenceWith(graphData[i].nodes, graphData[i-1].nodes, function(node1, node2) {
      if (node1.id === node2.id) {
        return true;
      }
      return false;
    });
    function appendStage(obj) {
      return Object.assign({}, obj, {
        stage: i,
      });
    }
    plotViewData.links = plotViewData.links.concat(linksDiff.map(appendStage))
    plotViewData.nodes = plotViewData.nodes.concat(nodesDiff.map(appendStage));
  }
});


function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.01).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}

function plotGraph() {
  defs = svg.append("defs")

	defs.append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 5)
    .attr("refY", 0)
    .attr("markerWidth", 4)
    .attr("markerHeight", 4)
    .attr("orient", "auto")
    .attr("fill", "#777")
    .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("class","arrowHead");


  /* Define the data for the circles */
  var linksContainer = svg.append("g")
        .attr("class", "links")
      .selectAll("line")
      .data(plotViewData.links)
  var linksEnter = linksContainer.enter();

  var link = linksEnter.append("line")
        .attr("class", function(d) { return 'stage-' + d.stage; })
        .attr("stroke", "#999")
        .attr("stroke-width", "1.5")
        .attr('marker-end', 'url(#arrow)');

  /* Define the data for the circles */
  var nodesContainer = svg.append('g')
        .attr("class", "nodes")
      .selectAll('circle')
      .data(plotViewData.nodes)
  var nodesEnter = nodesContainer.enter()
	    .append("g")
      .attr("class", "nodes")

  estimateColors = ['HotPink', 'LightSkyBlue']

  var node = nodesEnter.append("circle")
      .attr("class", function(d) { return 'stage-' + d.stage; })
      .attr("r", nodeRadius)
      .attr("fill", function(d) { return estimateColors[d.estimate]; })
      .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));

  /* Create the text for each block */
  var text = nodesEnter.append("text")
    .attr("class", function(d) { return 'stage-' + d.stage; })
	  .text(function(d){return d.estimate})

  node.append("title")
      .text(function(d) { return d.id; });

  //Add SVG Text Element Attributes
  simulation
      .nodes(plotViewData.nodes)
      .on("tick", ticked);

  simulation.force("link")
      .links(plotViewData.links);

  var test = true;
  function ticked() {
    if (test) {
      test = false;
      console.log(node);
    }

    node
        .each(gravity(.2 * 2))
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; })

    link
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x + (d.source.x - d.target.x)*0.01; })
        .attr("y2", function(d) { return d.target.y+nodeRadius*1.2; });

    text
        .attr("x", function(d) { return d.x; })
        .attr("y", function(d) { return d.y; })
  }

  // Move nodes toward their natural position
  function gravity(alpha) {
    return function(d) {
      d.y += ((height-((d.stage/maxStage)+0.1)*height*0.8) - d.y) * alpha;
      d.x += ((d.xPos*width) - d.x) * alpha;
    };
  }
}

function sliderInput (err, v) {
  currentStage = document.getElementById('stage-slider').value;
  for (var i = 0; i < currentStage; i++) {
    d3.selectAll('.stage-'+i).style('opacity', '1');
  }
  for (var i = currentStage; i < maxStage+1; i++) {
    d3.selectAll('.stage-'+i).style('opacity', '0');
  }
}
