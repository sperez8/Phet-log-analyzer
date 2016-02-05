

// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //


 //          UTILITIES                                                //


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //

colors = ["#C3D0DB","#98B2C3","#5E869F","#2F5D7C"]; //UBC blue greys

grey = "#7e7e7e"


var opacityNormal = 0.7,
    opacityLow = 0.3,
    opacityHigh = 1,
    colorLow = colors[1],
    colorNormal = colors[1],
    colorHigh = colors[2];

//reloads page if the window is resized so the viz is always at optimal size
window.onresize = function(){ location.reload(); }


function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
  
  
Array.prototype.getUnique = function(){
   var u = {}, a = [];
   for(var i = 0, l = this.length; i < l; ++i){
      if(u.hasOwnProperty(this[i])) {
         continue;
      }
      a.push(this[i]);
      u[this[i]] = 1;
   }
   return a;
}

//default behaviour of tool tip
var tooltip = d3.select("body").append("div")   
    .attr("class", "tooltip")               
    .style("opacity", 0);

var tooltipOpacity = 0.83

var remove_tooltip = function (){
    tooltip.style("opacity", 0);
}

var highlightTime = 500 //milliseconds

var highlight_project = function (link, title){
  d3.selectAll(".link")
    .each(function (l){
      if (l.projectTitle == title){
        d3.select(this).call(highlight_link,colorHigh,opacityHigh)
        highlightProjectInList(l.projectTitle)
      } else {
        d3.select(this).call(highlight_link,colorLow,opacityLow)
      }
    })
}

var highlight_link = function (selection, color, opacity) {
    selection            
        .transition()
        .ease("linear")
        .duration(highlightTime)
        .style("stroke-opacity", opacity)
        .style("stroke", color)
    };

var remove_highlight_link = function(){
    d3.selectAll(".link")
      .call(highlight_link,colorNormal,opacityNormal)
}

var remove_highlight_list_item = function(){
    d3.select("#projectList").selectAll(".projectListItem")
    .call(highlight_list_item,colorNormal,"none")
}

var highlight_list_item = function (selection, color, boldness) {
    selection            
        .transition()
        .ease("linear")
        .duration(highlightTime*2)
        .style("fill", color)
        .attr("font-weight",boldness)
    };

var highlightProjectInList = function(project){
  remove_highlight_list_item()
  d3.select("#projectList").selectAll(".projectListItem")
      .each(function (t){
          if (t == project){
            d3.select(this).call(highlight_list_item,colorHigh,"bold")
          }
      })
  }


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //



 //          MAKING THE SANKEY                //


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //




d3.sankey = function() {
  var sankey = {},
      nodeWidth = 24,
      nodePadding = 8,
      size = [1, 1],
      nodes = [],
      links = [];

  sankey.nodeWidth = function(_) {
    if (!arguments.length) return nodeWidth;
    nodeWidth = +_;
    return sankey;
  };

  sankey.nodePadding = function(_) {
    if (!arguments.length) return nodePadding;
    nodePadding = +_;
    return sankey;
  };

  sankey.nodes = function(_) {
    if (!arguments.length) return nodes;
    nodes = _;
    return sankey;
  };

  sankey.links = function(_) {
    if (!arguments.length) return links;
    links = _;
    return sankey;
  };

  sankey.size = function(_) {
    if (!arguments.length) return size;
    size = _;
    return sankey;
  };

  sankey.layout = function(iterations) {
    computeNodeLinks();
    computeNodeValues();
    computeNodeBreadths();
    computeNodeDepths(iterations);
    computeLinkDepths();
    return sankey;
  };

  sankey.relayout = function() {
    computeLinkDepths();
    return sankey;
  };

  sankey.link = function() {
    var curvature = 0.4;

    function link(d) {
      var x0 = d.source.x + d.source.dx,
          x1 = d.target.x,
          xi = d3.interpolateNumber(x0, x1),
          x2 = xi(curvature),
          x3 = xi(1 - curvature),
          y0 = d.source.y + d.sy + d.dy / 2,
          y1 = d.target.y + d.ty + d.dy / 2;
      return "M" + x0 + "," + y0
           + "C" + x2 + "," + y0
           + " " + x3 + "," + y1
           + " " + x1 + "," + y1;
    }

    link.curvature = function(_) {
      if (!arguments.length) return curvature;
      curvature = +_;
      return link;
    };

    return link;
  };

  // Populate the sourceLinks and targetLinks for each node.
  // Also, if the source and target are not objects, assume they are indices.
  function computeNodeLinks() {
    nodes.forEach(function(node) {
      node.sourceLinks = [];
      node.targetLinks = [];
    });
    links.forEach(function(link) {
      var source = link.source,
          target = link.target;
      if (typeof source === "number") source = link.source = nodes[link.source];
      if (typeof target === "number") target = link.target = nodes[link.target];
      source.sourceLinks.push(link);
      target.targetLinks.push(link);
    });
  }

  // Compute the value (size) of each node by summing the associated links.
  function computeNodeValues() {
    nodes.forEach(function(node) {
      node.value = Math.max(
        d3.sum(node.sourceLinks, value),
        d3.sum(node.targetLinks, value)
      );
    });
  }

  // Iteratively assign the breadth (x-position) for each node.
  // Nodes are assigned the maximum breadth of incoming neighbors plus one;
  // nodes with no incoming links are assigned breadth zero, while
  // nodes with no outgoing links are assigned the maximum breadth.
  function computeNodeBreadths() {
    var remainingNodes = nodes,
        nextNodes,
        x = 0;

    while (remainingNodes.length) {
      nextNodes = [];
      remainingNodes.forEach(function(node) {
        node.x = x;
        node.dx = nodeWidth;
        node.sourceLinks.forEach(function(link) {
          if (nextNodes.indexOf(link.target) < 0) {
            nextNodes.push(link.target);
          }
        });
      });
      remainingNodes = nextNodes;
      ++x;
    }

    //
    moveSinksRight(x);
    scaleNodeBreadths((size[0] - nodeWidth) / (x - 1));
  }

  function moveSourcesRight() {
    nodes.forEach(function(node) {
      if (!node.targetLinks.length) {
        node.x = d3.min(node.sourceLinks, function(d) { return d.target.x; }) - 1;
      }
    });
  }

  function moveSinksRight(x) {
    nodes.forEach(function(node) {
      if (!node.sourceLinks.length) {
        node.x = x - 1;
      }
    });
  }

  function scaleNodeBreadths(kx) {
    nodes.forEach(function(node) {
      node.x *= kx;
    });
  }

  function computeNodeDepths(iterations) {
    var nodesByBreadth = d3.nest()
        .key(function(d) { return d.x; })
        .sortKeys(d3.ascending)
        .entries(nodes)
        .map(function(d) { return d.values; });

    //
    initializeNodeDepth();
    resolveCollisions();
    for (var alpha = 1; iterations > 0; --iterations) {
      relaxRightToLeft(alpha *= .99);
      resolveCollisions();
      relaxLeftToRight(alpha);
      resolveCollisions();
    }

    function initializeNodeDepth() {
      var ky = d3.min(nodesByBreadth, function(nodes) {
        return (size[1] - (nodes.length - 1) * nodePadding) / d3.sum(nodes, value);
      });

      nodesByBreadth.forEach(function(nodes) {
        nodes.forEach(function(node, i) {
          node.y = i;
          node.dy = node.value * ky;
        });
      });

      links.forEach(function(link) {
        link.dy = link.value * ky;
      });
    }

    function relaxLeftToRight(alpha) {
      nodesByBreadth.forEach(function(nodes, breadth) {
        nodes.forEach(function(node) {
          if (node.targetLinks.length) {
            var y = d3.sum(node.targetLinks, weightedSource) / d3.sum(node.targetLinks, value);
            node.y += (y - center(node)) * alpha;
          }
        });
      });

      function weightedSource(link) {
        return center(link.source) * link.value;
      }
    }

    function relaxRightToLeft(alpha) {
      nodesByBreadth.slice().reverse().forEach(function(nodes) {
        nodes.forEach(function(node) {
          if (node.sourceLinks.length) {
            var y = d3.sum(node.sourceLinks, weightedTarget) / d3.sum(node.sourceLinks, value);
            node.y += (y - center(node)) * alpha;
          }
        });
      });

      function weightedTarget(link) {
        return center(link.target) * link.value;
      }
    }

    function resolveCollisions() {
      nodesByBreadth.forEach(function(nodes) {
        var node,
            dy,
            y0 = 0,
            n = nodes.length,
            i;

        // Push any overlapping nodes down.
        nodes.sort(ascendingDepth);
        for (i = 0; i < n; ++i) {
          node = nodes[i];
          dy = y0 - node.y;
          if (dy > 0) node.y += dy;
          y0 = node.y + node.dy + nodePadding;
        }

        // If the bottommost node goes outside the bounds, push it back up.
        dy = y0 - nodePadding - size[1];
        if (dy > 0) {
          y0 = node.y -= dy;

          // Push any overlapping nodes back up.
          for (i = n - 2; i >= 0; --i) {
            node = nodes[i];
            dy = node.y + node.dy + nodePadding - y0;
            if (dy > 0) node.y -= dy;
            y0 = node.y;
          }
        }
      });
    }

    function ascendingDepth(a, b) {
      return a.y - b.y;
    }
  }

  function computeLinkDepths() {
    nodes.forEach(function(node) {
      node.sourceLinks.sort(ascendingTargetDepth);
      node.targetLinks.sort(ascendingSourceDepth);
    });
    nodes.forEach(function(node) {
      var sy = 0, ty = 0;
      node.sourceLinks.forEach(function(link) {
        link.sy = sy;
        sy += link.dy;
      });
      node.targetLinks.forEach(function(link) {
        link.ty = ty;
        ty += link.dy;
      });
    });

    function ascendingSourceDepth(a, b) {
      return a.source.y - b.source.y;
    }

    function ascendingTargetDepth(a, b) {
      return a.target.y - b.target.y;
    }
  }

  function center(node) {
    return node.y + node.dy / 2;
  }

  function value(link) {
    return link.value;
  }

  return sankey;
};

//end sanky script   
  

// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //



 //          WINDOW SETUP?                //


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //


  
  
var customData = jQuery( '#data-here' ).text();

var units = "Project Facet";

var margin = {sankey:{top: 20, right: 10, bottom: 10, left: 10},
				 heatmap:{top: 130, right: 0, bottom: 0, left: 130}};
    //width = 1200 - margin.sankey.left - margin.sankey.right,
    //height = 800 - margin.sankey.top - margin.sankey.bottom;
    width = document.getElementById("allCharts").offsetWidth
    height = window.innerHeight*0.75

var formatNumber = d3.format(",.0f"),    // zero decimal places
    format = function(d) { return formatNumber(d) + " " + units; }
    //color = d3.scale.category20();
//console.log(color);

	// Set the sankey diagram properties	
var sankey = d3.sankey()
    .nodeWidth(38)
    .nodePadding(7)
    .size([width-4, height-50]); //offset a bit to make the labels not cut off. 
	
var path = sankey.link();
var currentDraw = 0;




// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //


 //          MAKING THE HEATMAP                //


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //



// load the data
//console.log(customData);
data = d3.tsv.parse(customData);
var heatMapdata =[];
var data1=[];

var filterData = function(){ //Note that the d is different for the heatMapdata and the data1 data. It comes from the parent (calling function). 


data1 = data;
		d3.select("#sankeyChart").selectAll("svg").remove();
		d3.select("#innovationImpactChart").selectAll("svg").remove();
		d3.select("#impactApproachChart").selectAll("svg").remove();
		//d3.select("#project-table").selectAll("tr").remove();


	//all the single option filters are of type ==
	if (faculty != "Any"){
	heatMapdata = heatMapdata.filter( function(d){ return d.Faculty_School == faculty;});
	data1 = data1.filter( function(d){ return d.Faculty_School == faculty;});
	}

	if (projectTitle != "Any") {
	heatMapdata = heatMapdata.filter( function(d) {return d.project_Title==projectTitle;});
	data1 = data1.filter( function(d) {return d.project_Title==projectTitle;});
	}
			
	if (department != "Any") {
	heatMapdata = heatMapdata.filter( function(d) {return d.Department==department;});
	data1 = data1.filter( function(d) {return d.Department==department;});
	}
		
	if (projectType != "Any") {
	heatMapdata = heatMapdata.filter( function(d) {return d.project_Type==projectType;});
	data1 = data1.filter( function(d) {return d["Type of Project"]==projectType;}); //Sankey chart loads the data differently thank heat maps  :S
	}
		
	if (projectStage != "Any") {
	heatMapdata = heatMapdata.filter( function(d) {return d.project_Stage==projectStage;});
	data1 = data1.filter( function(d) {return  d["Project Stage"]==projectStage;});
	}
		
	if (yearAwarded != "Any") {
	heatMapdata = heatMapdata.filter( function(d) {return d.year_awarded==yearAwarded;});
	data1 = data1.filter( function(d) {return d["Year Awarded"]==yearAwarded;});
	}
	
	
	
 //enrolment cap has ( and ) in it and doesn't work for heatmap data... try with search? 
		if (enrolmentCap != "Any") {
		var searchObj = enrolmentCap.replace('\)','\\\)').replace('\(','\\\('); //note the / needs to be escaped too! 
			searchObj = new RegExp(searchObj,'i'); 
	heatMapdata = heatMapdata.filter( function(d) {return (d.enrolment_Cap.search(searchObj))!=-1;});
	data1 = data1.filter( function(d) {return d["Enrolment Cap"]==enrolmentCap;});
	}
		//all the multi-select type options are of the .search() type. 
	if (courseLevel != "Any") {
	heatMapdata = heatMapdata.filter( function(d){return (d.Course_Level.search(courseLevel))!=-1;});
	data1 = data1.filter( function(d){return (d.Course_Level.search(courseLevel))!=-1;})
	}
	
	if (courseFormat != "Any") {
	heatMapdata = heatMapdata.filter( function(d){return (d.course_Format.search(courseFormat))!=-1;});
	data1 = data1.filter( function(d){return (d["Course Format"].search(courseFormat))!=-1;})
	}	
	
	//console.log(courseLocation);
	if (courseLocation != "Any") {
	// The str.search uses regular expressions. The ( and ) are screwing it up in the course location data. I need to 
	// make a regualr expression object and then use that to search.
	// the obj is made by replacing all the ( with /( and all the ) with /)
	
	//console.log(courseLocation);
	var searchObj = courseLocation.replace('\)','\\\)').replace('\(','\\\('); //note the / needs to be escaped too! 
	//console.log(searchObj);
	//searchObj.replace('\(','\\\('); 
	//console.log(searchObj); console.log("type: " +  typeof searchObj);
	searchObj = new RegExp(searchObj,'i');  //i for case IIIInsensitive. 
		//console.log(searchObj); console.log("type: " +  typeof searchObj);
	heatMapdata = heatMapdata.filter( function(d){return (d.course_Location.search(searchObj))!=-1;});
	//data1 = data1.filter( function(d){return (d["Course Location"].search(courseLocation))!=-1;});  //doesn't work. Needs searchObj
	data1 = data1.filter( function(d){return (d["Course Location"].search(searchObj))!=-1;});
	//console.log(heatMapdata);
	//console.log(data1);
	}	
	
	if (courseType != "Any") {
	heatMapdata = heatMapdata.filter( function(d){return (d.Course_Type.search(courseType))!=-1;});
	data1 = data1.filter( function(d){return (d["Course Type"].search(courseType))!=-1;})
	}

	 //tabulate(heatMapdata,tableColumns);
}; //end filterData

	
	//constants for heatmaps
 gridSize = Math.floor(width / 12),  //should make this dynamic
          legendElementWidth = gridSize*1.50,
          buckets = 4;
			






































































var heatmapInnovationImpact = function(n){
  //projectList(1)
	heatMapdata = d3.tsv.parse(customData, function(d) { //type function
         return {
		   matrix: d.matrix,
          // innovation: d["source long name"], // to coerce into a number or not!  + means yes
           innovation: d["source"], // to coerce into a number or not!  + means yes
         //  impact: d["target long name"], // works
           impact: d["target"],// doesn't work ????  FIX THIS!!! 
                 value: +d.value,
		   Course_Level: d.Course_Level,
		   Faculty_School: d.Faculty_School,
		   project_Title: d["project_Title"],
		   department: d.Department,
		   enrolment_Cap: d["Enrolment Cap"],
		   course_Format: d["Course Format"],
		   Course_Type: d["Course Type"],
		   course_Location: d["Course Location"],
		   project_Type: d["Type of Project"],
		   project_Stage: d["Project Stage"],
		   year_awarded: d["Year Awarded"]
          };
		  }
  );
 // console.log("heat map data: " + heatMapdata);
  //
 //Great nest learning tool: http://bl.ocks.org/shancarter/raw/4748131/ 
var heatMapNest = d3.nest()
.key(function(d) { return d.matrix; })
  .key(function(d) { return d.innovation; }) //innovation first for innovation keys
  .key(function(d) { return d.impact; })
  .rollup(function(x) { return d3.sum(x, function(d) {return d.value; }) })
  .map(heatMapdata, d3.map).get("innovationXimpact");
  
areasOfInnovation=heatMapNest.keys().sort(d3.ascending);

areasOfImpact = d3.nest()
.key(function(d) { return d.matrix; })
  .key(function(d) { return d.impact; })  //impact first for impact keys
  .key(function(d) { return d.innovation; })
  .rollup(function(x) { return d3.sum(x, function(d) {return d.value; }) })
  .map(heatMapdata, d3.map).get("innovationXimpact").keys();
  
areasOfImpact.sort(d3.ascending);

 filterData();//get the keys before you filter the data to get the whole original lists. 
 	

// append the svg canvas to the page
d3.select("#innovationImpactChart").append("svg")
    .attr("width", width + margin.heatmap.left + margin.heatmap.right)
    .attr("height", height + margin.heatmap.top + margin.heatmap.bottom)
  .append("g")
    .attr("transform", 
          "translate(" + margin.heatmap.left + "," + margin.heatmap.top + ")");
		  
 var svg = d3.select("#innovationImpactChart").selectAll("g")
          .append("g")
		  .attr("class", "heatmapInnovationImpact" + n)
          ;

	 
	 //title  "Innovation by Area of Impact"
	svg.append("text")
        .attr("x", - margin.heatmap.left)             
        .attr("y", 0 - (margin.heatmap.top) + 40)
        .attr("text-anchor", "start")  
        .attr("class","heading")
        .text("Innovation by Area of Impact");	
	






 heatMapNest = d3.nest()
.key(function(d) { return d.matrix; })
  .key(function(d) { return d.innovation; })
  .key(function(d) { return d.impact; })
  .rollup(function(x) { return d3.sum(x, function(d) {return d.value; }) })
  .map(heatMapdata, d3.map).get("innovationXimpact");
  
 
 
  dataRollUp =  [];

  if (typeof heatMapNest === "undefined") {
    console.log("no projects found!")
    //Filters return no projects
    return []
  }

    heatMapNest.forEach(function (d,v) {
	 v.forEach(function (d2,v2) {
      dataRollUp.push({ innovation: d2, impact: d, value: v2 });
	  //data.push([ d2,d, v2]); //array-works
	// console.log("inn " +d + "  " + "impact " + d2 + "  " + v2);
	  }
	  )
	  }
	  );
   
//console.log(data);
//console.log("area of impact: " + areasOfImpact);
//console.log("area of Innovation: " + areasOfInnovation);
//console.log(areasOfImpact.length);
  
  		var innovationLabel = svg.selectAll("g")
          .data(areasOfInnovation)
          .enter().append("g")
    		.attr("y", function(d, i) { return (i + 1) * ( gridSize); })
            .attr("x", 0)
			.attr("class","innovationLabel")
			//.style("glyph-orientation-vertical", "-90")			
			.style("text-anchor", "start")
			//.style("writing-mode", "tb")
		    //.attr("transform", "translate(" + -0.5*gridSize + ", -6)")
			; 
			
			//y-axis
		innovationLabel
			.append("text")
			.text(function(d) { return d; })
			.text(function(d, i) { return d; })
			.attr("y", function(d, i) { return (((i) * gridSize/2) +gridSize/6); })
            .attr("x", -10)
			.attr("dx",0)
			.attr("dy",0)
			//.attr("transform", "translate(-6," + gridSize/4  + ")")
			.attr("class","innovationLabel")					
			.style("text-anchor", "end")
			.call(wrapx,margin.heatmap.left-30)  
			;
			
			
  
  
  var max = d3.max(dataRollUp, function (d) { return d.value; });
//console.log(max);  
          var colorScale = d3.scale.quantile()
			//.domain([0,5,10,30,40])
              .domain([1, 0.25*max,0.5*max,0.75*max,max])
              .range(colors);
			  
//console.log("area of impact: " + areasOfImpact);			  
		//x-axis
		var impactLabels = svg.selectAll(".impactLabel")
          .data(areasOfImpact)
          .enter().append("text")
            .text(function (d) { return d; })
            .attr("x", function (d, i) { return ((i) * gridSize); })
            //.attr("x", function (d, i) { return gridSize; })
			.attr("y", -10)
			.attr("dy",0)
			.attr("dx",0)
			.attr("class","impactLabel")
            .style("text-anchor", "start")
            //.attr("transform", "translate(6," + -1*gridSize/4  + ")")
			.call(wrapy,gridSize)
			 ; 
			
			
//draw boxes
          var cards = svg.selectAll(".cards")
			  .data(dataRollUp);
			  
			  //console.log(cards);
			  
			  cards.enter()
			  .append("rect")              		  		  
              //.attr("y", function(d) { return ((areasOfInnovation.indexOf( d[1])) * gridSize/2); }) //array-works
			   .attr("y", function(d) { return ((areasOfInnovation.indexOf( d.impact)) * gridSize/2); })
			  //.attr("x", function(d) { return areasOfImpact.indexOf(d[0]) * gridSize; })  //array. works
			  .attr("x", function(d) { return areasOfImpact.indexOf(d.innovation) * gridSize; })  
			  //.attr("y", function(d,i) { return i * gridSize; })  
              .attr("rx", 6)
              .attr("ry", 6)
			   .attr("class", "card")
              .attr("width", gridSize)
              .attr("height", gridSize/2)
              .style("fill", "white")
			  .style("stroke","white")
			  ;
			   
			   cards.append("title");
			  
          cards.transition()
          .ease("linear")
				.duration(500)  //slows it down! 
              .style("fill", function(d) { return colorScale(d.value); })
			  .style("stroke","#ffffff");

			  //displays as tooltip text :) 
          //cards.select("title").text(function(d) { return d[2]; }); //array-works
		  cards.select("title")
		  .text(function(d) { return (d.value); });
		  
		 		
	
		  // console.log(cards.exit());		
         // cards.exit().remove();
		    

	  function wrapx(text, width) {
  text.each(function() {
    var text = d3.select(this),
        words = text.text().split(/\s+/).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        y = text.attr("y"),
		x = text.attr("x"),
        dy = parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", dy + "em");
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > width) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
      }
    }
  });
  }
  
  function wrapy(text, width) {
  text.each(function() {
    var text = d3.select(this),
        words = text.text().split(/\s+/),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        x = text.attr("x"),
		y = text.attr("y"),
        dx = parseFloat(text.attr("dx")),
		dy = parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dx", dx + "em");
    while (word = words.pop()) {
      line.reverse().push(word);
	  line.reverse();
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > width) {
	  line.reverse();
        line.pop();
		line.reverse();
        tspan.text(line.join(" "));
		line = [word];
        //words.push(word); //NOT this. 
        tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", -1*(++lineNumber * lineHeight + dy) + "em").text(word);
	
      }
    }
  });

  } 
  projectdata = []

  heatMapdata.forEach(function (d) {
    projectdata.push(d.project_Title);
  });

  // return only the distinct / unique nodes
  projectdata = projectdata.getUnique()
  console.log(projectdata)

  return projectdata
}; //end heatmapInnovationImpact



















var heatmapImpactApproach= function(n){
	
		heatMapdata = d3.tsv.parse(customData, function(d) { //type function
         return {
		   matrix: d.matrix,
           approach: d.source, // to coerce into a number or not!  + means yes
           impact: d.target,
              value: +d.value,
		   Course_Level: d.Course_Level,
		   Faculty_School: d.Faculty_School,
		   project_Title: d["project_Title"],
		   department: d.Department,
		   enrolment_Cap: d["Enrolment Cap"],
		   course_Format: d["Course Format"],
		   Course_Type: d["Course Type"],
		   course_Location: d["Course Location"],
		   project_Type: d["Type of Project"],
		   project_Stage: d["Project Stage"],
		   year_awarded: d["Year Awarded"]
          };
		  }
  );

 //Great nest learning tool: http://bl.ocks.org/shancarter/raw/4748131/ 
var heatMapNest = d3.nest()
.key(function(d) { return d.matrix; })
  .key(function(d) { return d.approach; }) //innovation first for innovation keys
  .key(function(d) { return d.impact; })
  .rollup(function(x) { return d3.sum(x, function(d) {return d.value; }) })
  .map(heatMapdata, d3.map).get("impactXapproach"); //impactXapproach is in the data under "matrix"
  
var areasOfImpact=heatMapNest.keys().sort(d3.ascending);

evaluationApproach = d3.nest()
.key(function(d) { return d.matrix; })
  .key(function(d) { return d.impact; })  //impact first for impact keys
  .key(function(d) { return d.approach; })
  .rollup(function(x) { return d3.sum(x, function(d) {return d.value; }) })
  .map(heatMapdata, d3.map).get("impactXapproach").keys();//impactXapproach is in the data under "matrix"
  
evaluationApproach.sort(d3.ascending);
//console.log("evaluation approach: " + evaluationApproach);
 filterData();//get the keys before you filter the data to get the whole original lists. 
 
 d3.select("#impactApproachChart").append("svg")
    .attr("width", width + margin.heatmap.left + margin.heatmap.right)
    .attr("height", height + margin.heatmap.top + margin.heatmap.bottom)
  .append("g")
    .attr("transform", 
          "translate(" + margin.heatmap.left + "," + margin.heatmap.top + ")");
		  
 var svg = d3.select("#impactApproachChart").selectAll("g")
          .append("g")
		  .attr("class", "heatmapImpactApproach" + n)
          ;

	 
	 //title  "Area of Impact by Evaluation Approach"
	svg.append("text")
        .attr("x", - margin.heatmap.left)             
        .attr("y", 0 - (margin.heatmap.top) + 40)
        .attr("text-anchor", "start")  
        .attr("class","heading")
        .text("Area of Impact by Evaluation Approach");	
 
 
 heatMapNest = d3.nest()
.key(function(d) { return d.matrix; })
  .key(function(d) { return d.approach; })
  .key(function(d) { return d.impact; })
  .rollup(function(x) { return d3.sum(x, function(d) {return d.value; }) })
  .map(heatMapdata, d3.map).get("impactXapproach");

  dataRollUp =  [];

  if (typeof heatMapNest === "undefined") {
    console.log("no projects found!")
    //Filters return no projects
    return []
  }

    heatMapNest.forEach(function (d,v) {
	 v.forEach(function (d2,v2) {
      dataRollUp.push({ impact: d, approach: d2, value: v2 });
	  }
	  )
	  }
	  );
   
//console.log(dataRollUp[0].approach);
  
  		var impactLabel = svg.selectAll("g")
          .data(areasOfImpact)
          .enter().append("g")
			//.style("glyph-orientation-vertical", "-90")			
			.style("text-anchor", "start")
			//.style("writing-mode", "tb")
			; 
			
			//y-axis
		impactLabel
			.append("text")
			.text(function(d) { return d; })
			.text(function(d, i) { return d; })
			.attr("y", function(d, i) { return (((i) * gridSize/2) +gridSize/6); })
            .attr("x", -10)
			.attr("dx",0)
			.attr("dy",0)
			//.attr("transform", "translate(-6," + gridSize/4  + ")")
			.attr("class","impactLabel")					
			.style("text-anchor", "end")
			.call(wrapx,margin.heatmap.left-30)  
			;
			
			
  
  
  var max = d3.max(dataRollUp, function (d) { return d.value; });
//console.log(max);  
          var colorScale = d3.scale.quantile()
			//.domain([0,5,10,30,40])
              .domain([1, 0.25*max,0.5*max,0.75*max,max])
              .range(colors);
		
		//x-axis
		var approachLabels = svg.selectAll(".approachLabel")
          .data(evaluationApproach)
          .enter().append("text")
            .text(function (d) { return d; })
            .attr("x", function (d, i) { return ((i) * gridSize); })
			.attr("y", -10)
			.attr("dy",0)
			.attr("dx",0)
			.attr("class","approachLabel")
            .style("text-anchor", "start")
            //.attr("transform", "translate(6," + -1*gridSize/4  + ")")
			.call(wrapy,gridSize)
			 ; 
			
			
//draw boxes
          var cards = svg.selectAll(".cards")
			  .data(dataRollUp);
			  
			  //console.log(cards);
			  
			  cards.enter()
			  .append("rect") 
			  .attr("x", function(d) { return evaluationApproach.indexOf(d.approach) * gridSize; })  
			  .attr("y", function(d) { return ((areasOfImpact.indexOf( d.impact)) * gridSize)/2; })
              .attr("rx", 6)
              .attr("ry", 6)
			   .attr("class", "card")
              .attr("width", gridSize)
              .attr("height", gridSize/2)
              .style("fill", "white")
			  .style("stroke","white")
			  ;
			   
			   cards.append("title");
			  
          cards.transition()
          .ease("linear")
				.duration(500)  //slows it down! 
              .style("fill", function(d) { return colorScale(d.value); })
			  .style("stroke","#ffffff");

			  //displays as tooltip text :) 
		  cards.select("title")
		  .text(function(d) { return (d.value); });
		  
		 		
	
		  // console.log(cards.exit());		
         // cards.exit().remove();
		    

	  function wrapx(text, width) {
  text.each(function() {
    var text = d3.select(this),
        words = text.text().split(/\s+/).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        y = text.attr("y"),
		x = text.attr("x"),
        dy = parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", dy + "em");
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > width) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
      }
    }
  });
  }
  
  function wrapy(text, width) {
  text.each(function() {
    var text = d3.select(this),
        words = text.text().split(/\s+/),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        x = text.attr("x"),
		y = text.attr("y"),
        dx = parseFloat(text.attr("dx")),
		dy = parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dx", dx + "em");
    while (word = words.pop()) {
      line.reverse().push(word);
	  line.reverse();
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > width) {
	  line.reverse();
        line.pop();
		line.reverse();
        tspan.text(line.join(" "));
		line = [word];
        //words.push(word); //NOT this. 
        tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", -1*(++lineNumber * lineHeight + dy) + "em").text(word);
	
      }
    }
  });
  }  

  projectdata = []

  heatMapdata.forEach(function (d) {
    projectdata.push(d.project_Title);
   });

   // return only the distinct / unique nodes
   projectdata = projectdata.getUnique()

   return projectdata
	
}; //end heatmapImpactApproach
	

















































// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //



 //          SANKEY MEAT                //


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //


var sankeyChart = function(n){  //this is used to hide the previous chart. Should be replaced with .exit().remove() if possible! 
	heatMapdata = d3.tsv.parse(customData, function(d) { //do this here for the tabular function. it resets the heatmap data
         return {
		   matrix: d.matrix,
          // innovation: d["source long name"], // to coerce into a number or not!  + means yes
           innovation: d["source"], // to coerce into a number or not!  + means yes
         //  impact: d["target long name"], // works
           impact: d["target"],// doesn't work ????  FIX THIS!!! 
                 value: +d.value,
		   Course_Level: d.Course_Level,
		   Faculty_School: d.Faculty_School,
		   project_Title: d["project_Title"],
		   department: d.Department,
		   enrolment_Cap: d["Enrolment Cap"],
		   course_Format: d["Course Format"],
		   Course_Type: d["Course Type"],
		   course_Location: d["Course Location"],
		   project_Type: d["Type of Project"],
		   project_Stage: d["Project Stage"],
		   year_awarded: d["Year Awarded"]
          };
		  }
  );	
  
  
  filterData();
  	
  // append the svg canvas to the page
   d3.select("#sankeyChart").append("svg")
      .attr("width", width + margin.sankey.left + margin.sankey.right)
      .attr("height", height + margin.sankey.top + margin.sankey.bottom)
    .append("g")
      .attr("transform", 
            "translate(" + margin.sankey.left + "," + margin.sankey.top + ")");

  //console.log(n);
  var	svg = d3.select("#sankeyChart").selectAll("g")
  	.append("g")
  	.attr("class", "sankey" + n)
          .attr("transform", "translate(4,42)") //translate so the top label is not half hidden and left side of nodes is good
  		.style("visibility","block")
  	;
  	
  svg.append("text").text("Innovation")
  	.attr("class","heading")
  	.attr("x",0)
  	.attr("y",-10)
  	.attr("text-anchor", "start");
  svg.append("text").text("Area of Impact")
  	.attr("class","heading")
  	.attr("x",width/2)
  	.attr("y",-10)
  	.attr("text-anchor", "middle");	
  svg.append("text").text("Evaluation Approach")
  	.attr("class","heading")
  	.attr("x",width)
  	.attr("y",-10)
  	.attr("text-anchor", "end");
  	




  	
  //set up graph 
  graph = {"nodes" : [], "links" : []};

  data1.forEach(function (d) {
    graph.nodes.push({ "name": d.source });
    graph.nodes.push({ "name": d.target });
    graph.links.push({ "source": d.source,
  					 "target": d.target,
  					 "value": +d.value,
  					 "projectTitle": d.project_Title
  					});
   });

   // return only the distinct / unique nodes
   graph.nodes = d3.keys(d3.nest()
     .key(function (d) { return d.name; })
     .map(graph.nodes));

   // loop through each link replacing the text with its index from node
   graph.links.forEach(function (d, i) {
     graph.links[i].source = graph.nodes.indexOf(graph.links[i].source);
     graph.links[i].target = graph.nodes.indexOf(graph.links[i].target);
   });

   //now loop through each nodes to make nodes an array of objects
   // rather than an array of strings
   graph.nodes.forEach(function (d, i) {
     graph.nodes[i] = { "name": d };
   });

  sankey
    .nodes(graph.nodes)
    .links(graph.links)
    .layout(30);

  //get array of possible values for trait of a node
  function get_trait_values(trait){
      return graph.nodes.map(function (d) {return d[trait]})
  }

  //get array of possible values for a numerical trait of a node
  function get_numerical_trait_values(trait){
      return graph.nodes.map(function (d) {return Number(d[trait])})
  }

  //get name of all nodes in the "middle" of the sankey chart
  middle_nodes = graph.nodes.filter(function (d) {return d.targetLinks.length !=0 && d.sourceLinks.length !=0}).map(function (d) {return d["name"]})

  //given name of a node, check if it has incoming and outgoing links and thus is in the middle
  function check_middle(node){
    middle_nodes = graph.nodes.filter(function (d) {return d.targetLinks.length !=0 && d.sourceLinks.length !=0}).map(function (d) {return d["name"]})
    return ($.inArray(node.name, middle_nodes) != -1)
  }

  nodeNames = get_trait_values("name")
  nodeValues = get_numerical_trait_values("value")

  // using colors from d3.scale.category10
  // colorscheme = d3.scale.ordinal()
  //   .domain(middle_nodes)
  //   .range(["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"])


  // add in the links
  var link = svg.append("g").selectAll(".link")
    .data(graph.links)
  .enter().append("path")
    .attr("class", "link")
    .attr("d", path)
    .style("stroke-opacity", opacityNormal)
    .style("stroke-width", function(d) {return Math.max(1, d.dy); })
    // .style("stroke", function(d,i) {  //color given the middle node it's connected to
    //   if (check_middle(d.source)) {
    //     return colorscheme(d.source.name)
    //   } else if (check_middle(d.target)) {
    //     return colorscheme(d.target.name)
    //   }
    // })
    .style("stroke",colorNormal)
    .sort(function(a, b) { return b.dy - a.dy; })
    .on("mouseover", function (l){
      var cx = d3.event.pageX
      var cy = d3.event.pageY
      tooltip.html("Project: " + l.projectTitle)
        .style("height", "32px")
        .style("left", (cx + 5) + "px")     
        .style("top", (cy - 28) + "px");
      tooltip
          .style("opacity", tooltipOpacity);

      //console.log(l, l.projectTitle, cx, cy, tooltipOpacity)
      d3.select(this)
        .call(highlight_project, l.projectTitle)
    })
    .on("mouseout", function (){
      remove_tooltip()
      remove_highlight_list_item()
      remove_highlight_link()
    });
    // .on("click", function (d){
    //   console.log("clicked", d.name, d.value)
    //   // XXX DO CLICK project HERE
    //   // if (d3.select(this).classed("clicked")){
    //   //     d3.select(this)
    //   //         .classed({"clicked":false})
    //   //     removeReveal()
    //   // } else {
    //   //     d3.select(this)
    //   //         .classed({"clicked":true})
    //   //         .call(reveal(n))
    //   // }
    // });



  // add in the nodes
  var node = svg.append("g").selectAll(".node")
    .data(graph.nodes)
  .enter().append("g")
    .attr("class", "node")
    .attr("transform", function(d) { 
  	  return "translate(" + d.x + "," + d.y + ")"; })
  .call(d3.behavior.drag()
    .origin(function(d) { return d; })
    .on("dragstart", function() { 
  	  this.parentNode.appendChild(this); })
  .on("drag", dragmove));

  // add the rectangles for the nodes
  node.append("rect")
    .attr("height", function(d) { return d.dy; })
    .attr("width", sankey.nodeWidth())
    .style("fill",colorHigh)
    // .style("fill", function(d) { //color nodes if they are in the middle, otherwise grey
    //   if (check_middle(d)) {
    //     return colorscheme(d.name)
    //   } else{
    //     return grey
    //   }
    // })


  // add in the title for the nodes
  node.append("text")
    .attr("x", -6)
    .attr("y", function(d) { return d.dy / 2; })
    .attr("dy", ".35em")
    .attr("text-anchor", "end")
    .attr("transform", null)
    .text(function(d) { return d.name; })
  .filter(function(d) { return d.x < width / 2; })
    .attr("x", 6 + sankey.nodeWidth())
    .attr("text-anchor", "start");

   
    
  // the function for moving the nodes
  function dragmove(d) {
  d3.select(this).attr("transform", 
  	"translate(" + d.x + "," + (
  			d.y = Math.max(0, Math.min(height -50 - d.dy, d3.event.y))
  		) + ")");
  sankey.relayout();
  link.attr("d", path);
  }

  return  graph.links.map(function (d) {return d["projectTitle"]}).getUnique()
}










//end sankey chart
  



















// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //



 //          MAKING THE TABLE                //


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //




  
// function tabulate(tableData, columns) {

// //console.log(data1[0]);

// //var tableData = d3.nest()   //this works to give a unique list of project titles. 
// 	//.key(function(d) {return d.project_Title;})
// 	//.map(data,d3.map).keys().sort(d3.ascending);

// 	//console.log(data[0]);
// 	//console.log(data[0]["project_Title"]);
// 	//console.log(tableData);
	
//     var table = d3.select("#project-table").append("table")
//      //       .attr("style", "margin-left: 150px"),
//         thead = table.append("thead"),
//         tbody = table.append("tbody");

//     // append the header row
//     thead.append("tr")
//         .selectAll("th")
//         .data(columns)
//         .enter()
//         .append("th")
//             .text(function(column) { return capitalizeFirstLetter(column.replace('_',' ')); });

// 			var x = "_XX_"; //nothing should match this ;)
// 			function unique(value){
//   			return_this = (x != value["project_Title"]);
//   			x = value["project_Title"];
//   			return return_this;
// 			}
// 			tableData = tableData.filter(unique);
			
//     // create a row for each object in the data
//     var rows = tbody.selectAll("tr")
//         .data(tableData)
//        // .data(tableData)
//         .enter()
//        .append("tr");
// 	   //console.log(rows[0]);

//     // create a cell in each row for each column
//     var cells = rows.selectAll("td")
//         .data(function(row) {
//             return columns.map(function(column) {
//                 return {column: column, value: row[column]};
		   
// 		// return d;})
//             });
//         })
//         .enter()
//         .append("td")
// 		//.attr("style", "font-family: Courier") // sets the font style
//             .html(function(d) { return d.value; });
    
//     //return table;
// } //end tabulate
  


























// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //



 //          FILTER stuff                //


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //


function rerun(currentChartType){
  projects = ChartType[currentChartType](1)

  //Show the number of projects displayed in Sankey and HeatMap
  var revealNumberOfProjects = function (total, highlightTime){
      var removeReveal = function (){
         d3.select("#NumberOfProjects").selectAll("p")
          .remove();
      };
      removeReveal()
      d3.select("#NumberOfProjects").append("p")
          .html(total + " projects")
          .style("color", grey)
          .style("background-color", "white")
          .transition()
          .ease("linear")
          .duration(highlightTime/2)
  };

  var updateprojectList = function(projectdata){

    var removeReveal = function (){
       d3.select("#projectList").selectAll("svg")
        .remove();
    };

    removeReveal()

    function wrap(text, width, listheight) {
      text.each(function() {
        var text = d3.select(this),
            words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 1.1, // ems
            y = text.attr("y"),
            dy = parseFloat(text.attr("dy")),
            tspan = text.text(null).append("tspan").attr("class","listitem").attr("x", 0).attr("y", y).attr("dy", dy + "em");
        if (y>listheight){
          return
        }
        spans = 0
        while (word = words.pop()) {
          line.push(word);
          tspan.text(line.join(" "));
          if (tspan.node().getComputedTextLength() > width) {
            line.pop();
            if (spans == 1){
              line.pop()
              line.push('...')
              tspan.text(line.join(" "));
              break
            }
            tspan.text(line.join(" "));
            line = [word];
            tspan = text.append("tspan").attr("class","listitem").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
            spans = spans+1
          }
        }
      });
    }

  var margin = {top: 10, right: 10, bottom: 10, left: 10}
      listwidth = document.getElementById("projectList").offsetWidth - margin.left - margin.right,
      listheight = window.innerHeight*0.7


    // append the svg canvas to the page
  var svg = d3.select("#projectList").append("svg")
      .attr("class", "list")
      .attr("width", listwidth)
      .attr("height", listheight)
    .append("g")
      .attr("transform", "translate(" + listwidth/2 + "," + 0 + ")");

    svg.selectAll(".text")
      .data(projectdata)
    .enter().append("text")
      .attr("class", "projectListItem")
      .attr("x", 0)
      .attr("dx", 0)
      .attr("dy", 0)
      .style("fill", colorNormal)
      .attr("y", function(d,i){return 70*i+20})
      .text(function(d,i) {
          return capitalizeFirstLetter(d.toLowerCase())
      })
      .call(wrap,listwidth, listheight)
      .on("mouseover", function (d){
        highlightProjectInList(d)
        d3.select("this").call(highlight_project, d)
      })
      .on("mouseout", function (){
        remove_highlight_list_item()
        remove_highlight_link()
      });
  }

  total = projects.length
  var highlightTime = 200 //milliseconds
  revealNumberOfProjects(total, highlightTime)
  updateprojectList(projects)

}



heatMapdata = d3.tsv.parse(customData);


//dynamically obtain all options for each filter
function get_filterOptions(filterName) {
  options = heatMapdata.map(function (d) {return d[filterName]}).getUnique()
  newoptions = []
  for (var i = options.length - 1; i >= 0; i--) {
      if (options[i]==" " || options[i] == ""){
      newoptions.push("N/A")
    // } else if (options[i].indexOf(',') > -1) {
    //   newoptions.concat(options[i].split(",")) //need to tease it out when survey gives multiple options[i]s
    } else {
      newoptions.push(options[i])
    }
  }
  fixedoptions = ["Any"].concat(newoptions.getUnique().sort())
  return fixedoptions
}

  //choice arrays for filters
var courseLevelList = get_filterOptions("Course_Level")
var facultyList = get_filterOptions("Faculty_School")
var projectTitleList = get_filterOptions("project_Title")
var departmentList = get_filterOptions("Department")
var enrolmentCapList = get_filterOptions("Enrolment Cap")
var courseFormatList = get_filterOptions("Course Format")
var courseTypeList = get_filterOptions("Course Type")
var courseLocationList = get_filterOptions("Course Location")
var projectTypeList = get_filterOptions("Type of Project")
var projectStageList = get_filterOptions("Project Stage")
var yearAwardedList = get_filterOptions("Year Awarded")

//columns to display for table
 var tableColumns =  ["project_Title","Faculty_School","Course_Level","course_Format","Course_Type","course_Location","project_Type","year_awarded"];

//set default start values
faculty  = "Any"; 
courseLevel = "Any";
projectTitle = "Any";
department = "Any";
enrolmentCap = "Any";
courseType = "Any";
courseLocation = "Any";
courseFormat = "Any"; 
projectType = "Any";
projectStage = "Any";
yearAwarded = "Any";
		
  
  //variables for filters and chart type buttons
  var ChartType = {"sankey":sankeyChart,
  "heatmapInnovationImpact":heatmapInnovationImpact,
  "heatmapImpactApproach":heatmapImpactApproach};
  
  
  var currentChartType =  "sankey";//"heatmapInnovationImpact";  //set the default chart type to be sankey
		
	
  var facultyPicker = d3.select("#context-filter-faculty")
		.append("select")
		.on("change",function() { 				
		//update filter variables
		faculty = d3.select(this).property("value");	
		//I put these in the filter() method now
		//d3.select("#sankeyChart").selectAll("svg").remove();//remove old charts
		//d3.select("#innovationImpactChart").selectAll("svg").remove();
		//d3.select("#impactApproachChart").selectAll("svg").remove();
			rerun(currentChartType);//redraw previously selected chart
 
		});

	facultyPicker.selectAll("option")
		.data(facultyList)
	.enter().append("option")
		.attr("value",function(d) {return d;})
			.text(function(d) {return d;});
		
		
	var courseLevelPicker = d3.select("#context-filter-courseLevel").append("select").on("change",function() { courseLevel = d3.select(this).property("value");	

		rerun(currentChartType);//redraw previously selected chart 
  }); //redraw previously selected chart
		
	courseLevelPicker.selectAll("option").data(courseLevelList).enter().append("option").attr("value",function(d) {return d;}).text(function(d) {return d;});
	
	var projectTitlePicker = d3.select("#context-filter-projectTitle").append("select").on("change",function() { projectTitle = d3.select(this).property("value");	

		rerun(currentChartType);//redraw previously selected chart 
  }); //redraw previously selected chart
		
	projectTitlePicker.selectAll("option").data(projectTitleList).enter().append("option").attr("value",function(d) {return d;}).text(function(d) {return d;});
	
	var departmentPicker = d3.select("#context-filter-department").append("select").on("change",function() { department = d3.select(this).property("value");	

		rerun(currentChartType);//redraw previously selected chart 
  }); //redraw previously selected chart
		
	departmentPicker.selectAll("option").data(departmentList).enter().append("option").attr("value",function(d) {return d;}).text(function(d) {return d;});
	
	var enrolmentCapPicker = d3.select("#context-filter-enrolmentCap").append("select").on("change",function() { enrolmentCap = d3.select(this).property("value");	

		rerun(currentChartType);//redraw previously selected chart 
  }); //redraw previously selected chart
		
	enrolmentCapPicker.selectAll("option").data(enrolmentCapList).enter().append("option").attr("value",function(d) {return d;}).text(function(d) {return d;});
	
var courseTypePicker = d3.select("#context-filter-courseType").append("select").on("change",function() { courseType = d3.select(this).property("value");	

		rerun(currentChartType);//redraw previously selected chart 
  }); //redraw previously selected chart
		
	courseTypePicker.selectAll("option").data(courseTypeList).enter().append("option").attr("value",function(d) {return d;}).text(function(d) {return d;});
	
var courseLocationPicker = d3.select("#context-filter-courseLocation")
.append("select")
.on("change",function() { 
	courseLocation = d3.select(this).property("value");	

		rerun(currentChartType);//redraw previously selected chart 
  }); //redraw previously selected chart
		
	courseLocationPicker.selectAll("option").data(courseLocationList).enter().append("option").attr("value",function(d) {return d;}).text(function(d) {return d;});
	
var courseFormatPicker = d3.select("#context-filter-CourseFormat").append("select").on("change",function() { courseFormat = d3.select(this).property("value");	

		rerun(currentChartType);//redraw previously selected chart 
  }); //redraw previously selected chart
		
	courseFormatPicker.selectAll("option").data(courseFormatList).enter().append("option").attr("value",function(d) {return d;}).text(function(d) {return d;});
	
	
		var projectTypePicker = d3.select("#context-filter-projectType").append("select").on("change",function() { projectType = d3.select(this).property("value");	

		rerun(currentChartType);//redraw previously selected chart 
  }); //redraw previously selected chart
		
	projectTypePicker.selectAll("option").data(projectTypeList).enter().append("option").attr("value",function(d) {return d;}).text(function(d) {return d;});
	

	
	var projectStagePicker = d3.select("#context-filter-projectStage").append("select").on("change",function() { projectStage = d3.select(this).property("value");	

		rerun(currentChartType);//redraw previously selected chart 
  }); //redraw previously selected chart
		
	projectStagePicker.selectAll("option").data(projectStageList).enter().append("option").attr("value",function(d) {return d;}).text(function(d) {return d;});



	var yearAwardedPicker = d3.select("#context-filter-yearAwarded").append("select").on("change",function() { yearAwarded = d3.select(this).property("value");	

		rerun(currentChartType);//redraw previously selected chart 
  }); //redraw previously selected chart
		
	yearAwardedPicker.selectAll("option").data(yearAwardedList).enter().append("option").attr("value",function(d) {return d;}).text(function(d) {return d;});
		
	

	
		//chartType buttons:		
	d3.select("#chartTypeButtons") //Sankey
		.append("input")
		.attr("value","Sankey: Flow from Innovation to Impact to Evaluation")
		 .attr("type", "button")
		.attr("class","chartTypeButtons")
		.on("click",function (){		

		currentChartType = "sankey";
		rerun(currentChartType);//redraw previously selected chart 
 		
		});		
		
		
	d3.select("#chartTypeButtons") //heatmapInnovationImpact
		.append("input")
		.attr("value","Heatmap: Innovation by Area of Impact")
		 .attr("type", "button")
		.attr("class","chartTypeButtons")
		.on("click",function (){
		
		currentChartType = "heatmapInnovationImpact";
		rerun(currentChartType);//redraw previously selected chart 
 
		});
		
		
	d3.select("#chartTypeButtons") 
		.append("input")
		.attr("value","Heatmap: Area of Impact by Evaluation Approach")
		 .attr("type", "button")
		.attr("class","chartTypeButtons")
		.on("click",function (){

		currentChartType = "heatmapImpactApproach";
		rerun(currentChartType);//redraw previously selected chart 
 
		});

	rerun(currentChartType);//redraw previously selected chart 
