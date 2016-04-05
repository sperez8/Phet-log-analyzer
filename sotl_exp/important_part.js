// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //


//          UTILITIES                                                //


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** udate// ****************************************************************** //

// function scrollToElement(ele) {
//     $(window).scrollTop(ele.offset().top).scrollLeft(ele.offset().left);
// }
// scrollToElement($('#NumberOfProjects'))

//UBCblue = "#002145"

//Change me when updating impact category names
colorscheme = d3.scale.ordinal()
  .domain(["Course specific knowledge", "Lifelong learning skills", "Attitudes and motivation", "Actions and behaviours", "Other area of impact", "Instructional team practices", "Operations"])
  //.range(["#a6d854","#8da0cb","#fc8d62","#b3b3b3","#ffd92f","#66c2a5","#e78ac3"])
  .range(["#686AF5","#FA7140","#80E633","#FAB03B","#e5fa3b","#05CE8E","#B8447C"])

grey = "#b8b8b8"
darkbluetable = '#85aec8'

var opacityNormal = 0.7,
  opacityLow = 0.2,
  opacityHigh = 1,
  widthNormal = "1px",
  widthHigh = "3px";

var highlightTime = 200; //milliseconds


// Project selection tracker

var projectSelectionTracker = new Array();

//reloads page if the window is resized so the viz is always at optimal size
// window.onresize = function(){ location.reload(); }

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}


Array.prototype.getUnique = function() {
  var u = {},
    a = [];
  for (var i = 0, l = this.length; i < l; ++i) {
    if (u.hasOwnProperty(this[i])) {
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

var remove_tooltip = function() {
  tooltip.style("opacity", 0);
}

var category_tooltip = function(info) {
  var cx = d3.event.pageX
  var cy = d3.event.pageY
  tooltip.html(info)
    .style("left", (cx + 5) + "px")
    .style("top", (cy - 28) + "px");
  tooltip
    .style("opacity", tooltipOpacity);
}


var highlightTime = 500 //milliseconds

var reset_projects = function (){
  rerun(get_current_chart())
  unselect_all_projects()
  revealNumberOfProjects(total, 0, highlightTime)
}

var get_selected_projects = function() {
  selected_projects = []
  for (var key in projectSelectionTracker) {
    if (projectSelectionTracker[key] && key != 'getUnique') {
      selected_projects.push(key)
    }
  }
  return selected_projects
}

var unselect_all_projects = function() {
  for(var key in projectSelectionTracker) {
      projectSelectionTracker[key] = false;
  }
  return total
}

var non_zero_intersection = function(a,b) {
  for (var i = a.length - 1; i >= 0; i--) {
    if ($.inArray(a[i], b) != -1) {
      return true
    }
  }
  return false
}

var update_sankey_selection = function() {
  no_project_selected = true
  remove_highlight_link()
  selected_projects = get_selected_projects()
  d3.selectAll(".link")
    .each(function(l) {
      if ($.inArray(l.projectTitle, selected_projects) != -1) {
        no_project_selected = false
        d3.select(this).call(highlight_link, opacityHigh)
      } else {
        d3.select(this).call(highlight_link, opacityLow)
      }
    })
  if (no_project_selected){
    remove_highlight_link()
  } else {
    highlightMultipleProjectInList(selected_projects)
  }
}

var update_heatmap_selection = function() {
  no_project_selected = true
  remove_highlight_card()
  selected_projects = get_selected_projects()
  d3.selectAll(".card")
    .each(function(l) {
      if (non_zero_intersection(selected_projects,l.projects)) {
        no_project_selected = false
        d3.select(this).call(highlight_card, opacityHigh, grey, widthHigh,1)
      } else {
        d3.select(this).call(highlight_card, opacityLow, "white", widthNormal,1)
      }
    })
  if (no_project_selected){
    remove_highlight_card()
  } else {
    highlightMultipleProjectInList(selected_projects)
  }
}

var update_table_selection = function() {
  no_project_selected = true
  //remove_highlight_row()
  selected_projects = get_selected_projects()
  d3.selectAll(".rowShaded")
    .each(function(l) {
      if ($.inArray(l.project_Title, selected_projects) != -1) {
        no_project_selected = false
        d3.select(this).call(highlight_row, darkbluetable)
      } else {
        d3.select(this).call(highlight_row, null)
      }
    })
  if (no_project_selected){
    remove_highlight_row()
  } else {
    highlightMultipleProjectInList(selected_projects)
  }
  d3.selectAll(".rowNotShaded")
    .each(function(l) {
      if ($.inArray(l.project_Title, selected_projects) != -1) {
        no_project_selected = false
        d3.select(this).call(highlight_row, darkbluetable)
      } else {
        d3.select(this).call(highlight_row, null)
      }
    })
  if (no_project_selected){
    remove_highlight_row()
  } else {
    highlightMultipleProjectInList(selected_projects)
  }
}

var highlight_project_sankey = function(link, title) {
  if (get_selected_projects()[0] != "getUnique" && get_selected_projects().length > 0) {return null} //not sure why this happens on first load but it works...
  d3.selectAll(".link")
    .each(function(l) {
      if (l.projectTitle == title) {
        d3.select(this).call(highlight_link, opacityHigh)
        highlightProjectInList(l.projectTitle)
      //} else if (projectSelectionTracker[l.projectTitle]!=true){
      } else {
        d3.select(this).call(highlight_link, opacityLow)
      }
    })
}

var highlight_project_heatmap = function(card, title) {
  if (get_selected_projects()[0] != "getUnique" && get_selected_projects().length > 0) {return null} //not sure why this happens on first load but it works...
  d3.selectAll(".card")
    .each(function(l) {
      if ($.inArray(title, l.projects) != -1) {
        d3.select(this).call(highlight_card, opacityHigh, grey, widthHigh,1)
        highlightProjectInList(title)
      } else {
        d3.select(this).call(highlight_card, opacityLow, null, widthNormal, opacityLow)
      }
    })
}

var highlight_project_table = function(row, title) {
  if (get_selected_projects()[0] != "getUnique" && get_selected_projects().length > 0) {return null} //not sure why this happens on first load but it works...
  d3.selectAll(".rowShaded")
    .each(function(l) {
      if (l.project_Title == title) {
        d3.select(this).call(highlight_row,darkbluetable)
        highlightProjectInList(l.project_Title)
      } else {
        d3.select(this).call(highlight_row,null)
      }
    })
    d3.selectAll(".rowNotShaded")
    .each(function(l) {
      if (l.project_Title == title) {
        d3.select(this).call(highlight_row,darkbluetable)
        highlightProjectInList(l.project_Title)
      } else {
        d3.select(this).call(highlight_row,null)
      }
    })
}

var highlight_link = function(selection, opacity, widthChanger) {
  selection
    .transition()
    .ease("linear")
    .duration(highlightTime)
    .style("stroke-opacity", opacity)
};

var highlight_card = function(selection, opacity, color, width, stroke_opacity) {
  selection
    .transition()
    .ease("linear")
    .duration(highlightTime)
    .style("stroke", color)
    .style("stroke-width", width)
    //.style("fill",color)
    .style("opacity",opacity)
    .style("stroke-opacity",stroke_opacity)
};

var highlight_row = function(selection, color) {
  selection
    // .transition()
    // .ease("linear")
    // .duration(highlightTime)
    .style("background", color)
};

var remove_highlight_card = function() {
  d3.selectAll(".card")
    .call(highlight_card, opacityHigh, "#ffffff", widthNormal, opacityLow)
}

var remove_highlight_link = function() {
  d3.selectAll(".link")
    .call(highlight_link, opacityNormal)
}

var remove_highlight_row = function() {
  d3.selectAll(".rowShaded")
    .call(highlight_row, null)
  d3.selectAll(".rowNotShaded")
    .call(highlight_row, null)
}

var remove_highlight_list_item = function() {
  d3.select("#projectList").selectAll(".projectListItem")
    .call(highlight_list_item, opacityNormal, "none")
}

var highlight_list_item = function(selection, opacity, boldness) {
  selection
    .transition()
    .ease("linear")
    .duration(highlightTime * 2)
    .style("opacity", opacity)
    .attr("font-weight", boldness)
};

var highlightProjectInList = function(project) {
  remove_highlight_list_item()
  d3.select("#projectList").selectAll(".projectListItem")
    .each(function(t) {
      if (t == project) {
        d3.select(this).call(highlight_list_item, opacityHigh, "bold")
      } else {
        d3.select(this).call(highlight_list_item, opacityLow, null)
      }
    })
}


var highlightMultipleProjectInList = function(projects) {
  remove_highlight_list_item()
  d3.select("#projectList").selectAll(".projectListItem")
    .each(function(t) {
      if ($.inArray(t, projects) != -1) {
        d3.select(this).call(highlight_list_item, opacityHigh, "bold")
      } else {
        d3.select(this).call(highlight_list_item, opacityLow, null)
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
    //nodeWidth = 500,
    nodePadding = 800,
    size = [4, 1],
    nodes = [],
    links = [];

  sankey.nodeWidth = function(_) {
    if (!arguments.length) return nodeWidth;
    nodeWidth = +_;
    return sankey;
  };

  sankey.nodePadding = function(_) {
    if (!arguments.length) return nodePadding;
    nodePadding = +_+7;
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
    var curvature = 0.9;

    function link(d) {
      var x0 = d.source.x + d.source.dx,
        x1 = d.target.x,
        xi = d3.interpolateNumber(x0, x1),
        x2 = xi(curvature),
        x3 = xi(1 - curvature),
        y0 = d.source.y + d.sy + d.dy / 2,
        y1 = d.target.y + d.ty + d.dy / 2;
      return "M" + x0 + "," + y0 + "C" + x2 + "," + y0 + " " + x3 + "," + y1 + " " + x1 + "," + y1;
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
    //console.log(node.sourceLinks)
    // source_projects = node.sourceLinks.map(function(d) {return d["projectTitle"]}).getUnique()
    // target_projects = node.targetLinks.map(function(d) {return d["projectTitle"]}).getUnique()
    // node.value = Math.max(source_projects.length, target_projects.length);
    // console.log(node.value, target_projects)
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
        node.x = d3.min(node.sourceLinks, function(d) {
          return d.target.x;
        }) - 1;
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
      .key(function(d) {
        return d.x;
      })
      .sortKeys(d3.ascending)
      .entries(nodes)
      .map(function(d) {
        return d.values;
      });

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
        //console.log(nodes.length, nodePadding, d3.sum(nodes, value))
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
      var sy = 0,
        ty = 0;
      node.sourceLinks.forEach(function(link) {
        link.sy = sy;
        sy += link.dy;
      });
      node.targetLinks.forEach(function(link) {
        link.ty = ty;
        ty += link.dy;
      });
      // node.sourceLinks.forEach(function(link) {
      //   link.sy = Math.max(node.value-5,1)*link.dy/2.0 + sy;
      //   sy += link.dy*Math.min(node.value,5)/node.value;
      // });
      // node.targetLinks.forEach(function(link) {
      //   link.ty = Math.max(node.value-5,1)*link.dy/2.0 + ty;
      //   ty += link.dy*Math.min(node.value,5)/node.value;
      // });
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



var customData = jQuery('#data-here').text();

var units = "Project Facet";

var margin = {
  sankey: {
    top: 20,
    right: 0,
    bottom: 10,
    left: 0
  },
  heatmap: {
    top: 90,
    right: 0,
    bottom: 0,
    left: 150
  }
};

//width = 1200 - margin.sankey.left - margin.sankey.right,
//height = 800 - margin.sankey.top - margin.sankey.bottom;
width = document.getElementById("allCharts").offsetWidth
console.log(document.body.clientWidth,document.getElementById("sidebars").offsetWidth,document.getElementById("viz").offsetWidth)
width = (document.body.clientWidth - document.getElementById("sidebars").offsetWidth)*0.8
height = window.innerHeight - 140

var formatNumber = d3.format(",.0f"), // zero decimal places
  format = function(d) {
    return formatNumber(d) + " " + units;
  }
  //color = d3.scale.category20();

// Set the sankey diagram properties  
var sankey = d3.sankey()
  .nodeWidth(38)
  .nodePadding(7)
  .size([width - 4, height - 50]); //offset a bit to make the labels not cut off. 

var path = sankey.link();
var currentDraw = 0;



// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //


//          FILTER FUNCTION               //


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //



// load the data
data = d3.tsv.parse(customData);
var heatMapdata = [];
var data1 = [];

var filterData = function(n) { //Note that the d is different for the heatMapdata and the data1 data. It comes from the parent (calling function). 
  data1 = data;
  d3.select("#sankeyChart").selectAll("svg").remove();
  d3.select("#innovationImpactChart").selectAll("svg").remove();
  d3.select("#impactApproachChart").selectAll("svg").remove();
  d3.select("#project-table").selectAll("tr").remove();
  d3.select("#project-table").selectAll("svg").remove();
  d3.select("#project-table").selectAll("th").remove();

  //all the single option filters are of type ==
  if (faculty != "Faculty (all)") {
    heatMapdata = heatMapdata.filter(function(d) {
      return d.Faculty_School == faculty;
    });
    data1 = data1.filter(function(d) {
      return d.Faculty_School == faculty;
    });
  }

  
  if (projectType != "Project type (all)") {
    heatMapdata = heatMapdata.filter(function(d) {
      return d.project_Type == projectType; 
    });
    data1 = data1.filter(function(d) {
      return d["Type of Project"] == projectType;
    }); //Sankey chart loads the data differently thank heat maps  :S
  }

  if (projectStage != "Project stage (all)") {
    heatMapdata = heatMapdata.filter(function(d) {
      return d.project_Stage == projectStage;
    });
    data1 = data1.filter(function(d) {
      return d["Project Stage"] == projectStage;
    });
  }

  if (yearAwarded != "Year awarded (all)") {
    heatMapdata = heatMapdata.filter(function(d) {
      return d.year_awarded == yearAwarded;
    });
    data1 = data1.filter(function(d) {
      return d["Year Awarded"] == yearAwarded;
    });
  }

  //all the multi-select type options are of the .search() type. 
  if (courseLevel != "Course level (all)") {
    heatMapdata = heatMapdata.filter(function(d) {
      return (d.Course_Level.search(courseLevel)) != -1;
    });
    data1 = data1.filter(function(d) {
      return (d.Course_Level.search(courseLevel)) != -1;
    })
  }

  if (innovation != "Innovation (all)") {
    heatMapdata = heatMapdata.filter(function(d) {
      return d.innovation == innovation;
    });

    //find all projects with desired "innovation"
    relevant_projects = data1.map(function(d) {
      if (d["source"] == innovation){return d["project_Title"]}
    }).getUnique()

    //find all impacts that it links too
    relevant_impacts = data1.map(function(d) {
      if (d["source"] == innovation){return d["target"]}
    }).getUnique()

    //filter if row matchs project and impact
    data1 = data1.filter(function(d) {
      if ($.inArray(d["project_Title"], relevant_projects) != -1){
        if (d["source"] == innovation || ($.inArray(d["source"], relevant_impacts) != -1)){
          return true
        }
      }
    });
  }

  if (impact != "Impact (all)") {
    heatMapdata = heatMapdata.filter(function(d) {
      return d.impact == impact;
    });
    data1 = data1.filter(function(d) {
      return d["target"] == impact || d["source"] == impact;
    });
  }

  if (evaluation != "Evaluation (all)") {
    heatMapdata = heatMapdata.filter(function(d) {
      return d.approach == evaluation;
    });
    
    //find all projects with desired "evaluation"
    relevant_projects = data1.map(function(d) {
      if (d["target"] == evaluation){return d["project_Title"]}
    }).getUnique()

    //find all impacts that it links too
    relevant_impacts = data1.map(function(d) {
      if (d["target"] == evaluation){return d["source"]}
    }).getUnique()

    //filter if row matchs project and impact
    data1 = data1.filter(function(d) {
      if ($.inArray(d["project_Title"], relevant_projects) != -1){
        if (d["target"] == evaluation || ($.inArray(d["target"], relevant_impacts) != -1)){
          return true
        }
      }
    });
  }

}; //end filterData











// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //


//          MAKING THE HEATMAP                //


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //


//constants for heatmaps
  gridSizeX = Math.floor(width / 9), //should make this dynamic
  gridSizeY = Math.floor(width / 14), //should make this dynamic
  legendElementWidth = gridSizeX * 1.50,
  buckets = 4;



var heatmapInnovationImpact = function(n) {
  //projectList(1)
  heatMapdata = d3.tsv.parse(customData, function(d) { //type function
    return {
      matrix: d["matrix"],
      innovation: d["source"],
      impact: d["target"],
      innovation_longname: d["source long name"],
      impact_longname: d["target long name"],
      value: +d["value"],
      Course_Level: d["Course_Level"],
      Faculty_School: d["Faculty_School"],
      project_Title: d["project_Title"],
      department: d["Department"],
      enrolment_Cap: d["Enrolment Cap"],
      course_Format: d["Course Format"],
      Course_Type: d["Course Type"],
      course_Location: d["Course Location"],
      project_Type: d["Type of Project"],
      project_Stage: d["Project Stage"],
      year_awarded: d["Year Awarded"]
    };
  });

  longnames = {}

  //Great nest learning tool: http://bl.ocks.org/shancarter/raw/4748131/ 
  var heatMapNest = d3.nest()
    .key(function(d) {
      return d.matrix;
    })
    .key(function(d) {
      longnames[d.innovation] = d.innovation_longname
      return d.innovation;
    }) //innovation first for innovation keys
    .key(function(d) {
      longnames[d.impact] = d.impact_longname
      return d.impact;
    })
    .rollup(function(x) {
      return d3.sum(x, function(d) {
        return d.value;
      })
    })
    .map(heatMapdata, d3.map).get("innovationXimpact");

  areasOfInnovation = heatMapNest.keys().sort(d3.ascending);

  areasOfImpact = d3.nest()
    .key(function(d) {
      return d.matrix;
    })
    .key(function(d) {
      return d.impact;
    }) //impact first for impact keys
    .key(function(d) {
      return d.innovation;
    })
    .rollup(function(x) {
      return d3.sum(x, function(d) {
        return d.value;
      })
    })
    .map(heatMapdata, d3.map).get("innovationXimpact").keys();

  areasOfImpact.sort(d3.ascending);

  filterData(); //get the keys before you filter the data to get the whole original lists. 

  // append the svg canvas to the page
  d3.select("#innovationImpactChart").append("svg")
    .attr("width", width + margin.heatmap.left + margin.heatmap.right)
    .attr("height", height + margin.heatmap.top + margin.heatmap.bottom)
    .append("g")
    .attr("transform",
      "translate(" + Math.max(margin.sankey.left + margin.sankey.right,margin.heatmap.left + margin.heatmap.right)*1.25 + "," + margin.heatmap.top + ")");

  var svg = d3.select("#innovationImpactChart").selectAll("g")
    .append("g")
    .attr("class", "heatmapInnovationImpact" + n);

  //title  "Innovation by Area of Impact"
  // svg.append("text")
  //        .attr("x", - margin.heatmap.left)             
  //        .attr("y", 0 - (margin.heatmap.top) + 40)
  //        .attr("text-anchor", "start")  
  //        .attr("class","heading")
  //        .text("Innovation by Area of Impact"); 

  heatMapNest = d3.nest()
    .key(function(d) {
      return d.matrix;
    })
    .key(function(d) {
      return d.innovation;
    })
    .key(function(d) {
      return d.impact;
    })
    .rollup(function(projects) {
      // return d3.sum(projects, function(d) {
      //   return d.value;
      // })
      return projects.map(function(d) {return d["project_Title"]}).getUnique()
    })
    .map(heatMapdata, d3.map).get("innovationXimpact");


  projectdata = []
  heatMapdata.forEach(function(d) {
    projectdata.push(d.project_Title);
  });
  // return only the distinct / unique nodes
  projectdata = projectdata.getUnique()
  totalnumberprojects = projectdata.length

  if (totalnumberprojects == 0) {
    svg.append("text").text("No projects were found given those filters")
      .attr("class", "heading")
      .attr("x", width / 2)
      .attr("y", 30)
      .attr("text-anchor", "middle");
    return totalprojects
  } 

  dataRollUp = [];

  heatMapNest.forEach(function(d, v) {
    v.forEach(function(d2, v2) {
      dataRollUp.push({
        innovation: d2,
        impact: d,
        value: v2.length,
        projects: v2
      });
    })
  });

  //need to calculate this before adding totals
  var max = d3.max(dataRollUp, function(d) {
    return d.value;
  });

  //calculating total columns      
  for (var i = areasOfImpact.length - 1; i >= 0; i--) {
    areasOfImpact[i]
    total = []
    for (var j = dataRollUp.length - 1; j >= 0; j--) {
      if (dataRollUp[j].innovation==areasOfImpact[i]){
        total.push.apply(total,dataRollUp[j].projects)
      }
    }
    dataRollUp.push({
      innovation: areasOfImpact[i],
      impact: "Total",
      value: total.getUnique().length,
      projects: total.getUnique()
    });   
  }

  //calculating total rows      
  for (var i = areasOfInnovation.length - 1; i >= 0; i--) {
    areasOfInnovation[i]
    total = []
    for (var j = dataRollUp.length - 1; j >= 0; j--) {
      if (dataRollUp[j].impact==areasOfInnovation[i]){
        total.push.apply(total,dataRollUp[j].projects)
      }
    }
    dataRollUp.push({
      innovation: "Total",
      impact: areasOfInnovation[i],
      value: total.getUnique().length,
      projects: total.getUnique()
    });   
  }

  areasOfInnovation.push("Total")
  areasOfImpact.push("Total")

  var innovationLabel = svg.selectAll("g")
    .data(areasOfInnovation)
    .enter().append("g")
    .attr("y", function(d, i) {
      return (i + 1) * (gridSizeY);
    })
    .attr("x", 0)
    .attr("class", "innovationLabel")
    //.style("glyph-orientation-vertical", "-90")     
    .style("text-anchor", "start")
    //.style("writing-mode", "tb")
    //.attr("transform", "translate(" + -0.5*gridSizeX + ", -6)")
  ;

  //y-axis
  innovationLabel
    .append("text")
    .text(function(d) {
      return d;
    })
    .text(function(d, i) {
      return d;
    })
    .attr("y", function(d, i) {
      return (((i) * gridSizeY / 2) + gridSizeY / 4);
    })
    .attr("x", -10)
    .attr("dx", 0)
    .attr("dy", 0)
    //.attr("transform", "translate(-6," + gridSizeX/4  + ")")
    .attr("class", "innovationLabel")
    .style("text-anchor", "end")
    .style("vertical-align", "middle")
    .on("mouseover", function(d) {
      category_tooltip(capitalizeFirstLetter(longnames[d].toLowerCase()))
    })
    .on("mouseout", function() {remove_tooltip()})
    .call(wrapx, margin.heatmap.left);

  // var colorScale = d3.scale.quantile()
  //   //.domain([0,5,10,30,40])
  //   .domain([1, 0.25 * max, 0.5 * max, 0.75 * max, max])
  //   .range(colors);

  var opacityScale = d3.scale.quantile()
    .domain([1, max])
    .range([0.3,0.7,1])

  svg.append("text").text("Innovation")
    .attr("class", "heading")
    .attr("x", -10)
    .attr("y", -20)
    .attr("text-anchor", "end");
  svg.append("text").text("Area of impact")
    .attr("class", "heading")
    .attr("x", 0)
    .attr("y", -margin.heatmap.top/2-5)
    .attr("text-anchor", "start");

  //x-axis
  var impactLabels = svg.selectAll(".impactLabel")
    .data(areasOfImpact)
    .enter().append("text")
    .text(function(d) {
      return d;
    })
    .attr("x", function(d, i) {
      return ((i) * gridSizeX);
    })
    .attr("y", -10)
    .attr("dy", 0)
    .attr("dx", 0)
    .attr("class", "impactLabel")
    .style("text-anchor", "start")
    .on("mouseover", function(d) {
      category_tooltip(capitalizeFirstLetter(longnames[d].toLowerCase()))
    })
    .on("mouseout", function() {remove_tooltip()})
    .call(wrapy, gridSizeX);


  //draw boxes
  var cards = svg.selectAll(".cards")
    .data(dataRollUp);

  cards.enter()
    .append("rect")
    .attr("y", function(d) {
      return ((areasOfInnovation.indexOf(d.impact)) * gridSizeY / 2);
    })
    .attr("x", function(d) {
      return areasOfImpact.indexOf(d.innovation) * gridSizeX;
    })
    .attr("rx", 6)
    .attr("ry", 6)
    .attr("class", "card")
    .attr("width", gridSizeX)
    .attr("height", gridSizeY / 2)
    .style("cursor","pointer")
    .style("fill", function(d){
      if (d.innovation != "Total"){
        return colorscheme(d.innovation)
      } else {
      return grey
    }})
    .style("fill-opacity", function(d){
      if (d.impact != "Total" && d.innovation != "Total"){
        return opacityScale(d.value)
      } else {
        return opacityScale(max)
    }})
    .style("stroke", "#ffffff")
    .style("stroke-width", "1px")
    .style("stroke-opacity",opacityLow)
    .on("mouseover", function(l) {
      var cx = d3.event.pageX
      var cy = d3.event.pageY
      if (l.value ==1){
        text = l.value + " project"
      } else {
        text = l.value + " projects"
      }
      tooltip.html(text)
        .style("left", (cx + 5) + "px")
        .style("top", (cy - 28) + "px");
      tooltip
        .style("opacity", tooltipOpacity);
      d3.select(this).call(highlight_card, opacityHigh, grey, widthHigh,1)
      highlightMultipleProjectInList(l.projects)
    })
    .on("mouseout", function() {
      remove_tooltip()
      remove_highlight_list_item()
      remove_highlight_card()
      update_heatmap_selection()
    })
    .on("click", function (l){
      selected_projects = get_selected_projects()
      if (non_zero_intersection(selected_projects,l.projects)) {
        unselect_all_projects()
      } else{
        unselect_all_projects()
        for (var i = l.projects.length - 1; i >= 0; i--) {
          projectSelectionTracker[l.projects[i]] = true
        }
      }
      update_heatmap_selection()
      revealNumberOfProjects(totalnumberprojects, get_number_of_selected_projects(), highlightTime)
    });

  //draw boxes
  var cardtext = svg.selectAll(".cards")
    .data(dataRollUp);

  cardtext.enter()
    .append("text")
    .attr("class","cardtext")
    .text(function(d){
      if (d.impact == "Total" || d.innovation == "Total"){
        return d.value
      }
    })
    .attr("y", function(d) {
      return (((areasOfInnovation.indexOf(d.impact))+ 0.5) * gridSizeY / 2);
    })
    .attr("x", function(d) {
      return (areasOfImpact.indexOf(d.innovation)+ 0.5) * gridSizeX ;
    })


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
          tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", -1 * (++lineNumber * lineHeight + dy) + "em").text(word);

        }
      }
    });

  }
  return projectdata
}; //end heatmapInnovationImpact



var heatmapImpactApproach = function(n) {

  heatMapdata = d3.tsv.parse(customData, function(d) { //type function
    return {
      matrix: d.matrix,
      approach: d.source,
      impact: d.target,
      approach_longname: d["source long name"],
      impact_longname: d["target long name"],
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
  });

  longnames = {}

  //Great nest learning tool: http://bl.ocks.org/shancarter/raw/4748131/ 
  var heatMapNest = d3.nest()
    .key(function(d) {
      return d.matrix;
    })
    .key(function(d) {
      longnames[d.approach] = d.approach_longname
      return d.approach;
    }) //innovation first for innovation keys
    .key(function(d) {
      longnames[d.impact] = d.impact_longname
      return d.impact;
    })
    .rollup(function(x) {
      return d3.sum(x, function(d) {
        return d.value;
      })
    })
    .map(heatMapdata, d3.map).get("impactXapproach"); //impactXapproach is in the data under "matrix"

  var areasOfImpact = heatMapNest.keys().sort(d3.ascending);

  evaluationApproach = d3.nest()
    .key(function(d) {
      return d.matrix;
    })
    .key(function(d) {
      return d.impact;
    }) //impact first for impact keys
    .key(function(d) {
      return d.approach;
    })
    .rollup(function(x) {
      return d3.sum(x, function(d) {
        return d.value;
      })
    })
    .map(heatMapdata, d3.map).get("impactXapproach").keys(); //impactXapproach is in the data under "matrix"

  evaluationApproach.sort(d3.ascending);
  filterData(); //get the keys before you filter the data to get the whole original lists. 

  d3.select("#impactApproachChart").append("svg")
    .attr("width", width + margin.heatmap.left + margin.heatmap.right)
    .attr("height", height + margin.heatmap.top + margin.heatmap.bottom)
    .append("g")
    .attr("transform",
      "translate(" + margin.heatmap.left + "," + margin.heatmap.top + ")");

  var svg = d3.select("#impactApproachChart").selectAll("g")
    .append("g")
    .attr("class", "heatmapImpactApproach" + n);


  //title  "Area of Impact by Evaluation Approach"
  // svg.append("text")
  //        .attr("x", - margin.heatmap.left)             
  //        .attr("y", 0 - (margin.heatmap.top) + 40)
  //        .attr("text-anchor", "start")  
  //        .attr("class","heading")
  //        .text("Area of Impact by Evaluation Approach");  


  heatMapNest = d3.nest()
    .key(function(d) {
      return d.matrix;
    })
    .key(function(d) {
      return d.approach;
    })
    .key(function(d) {
      return d.impact;
    })
    .rollup(function(projects) {
      return projects.map(function(d) {return d["project_Title"]}).getUnique()
    })
    .map(heatMapdata, d3.map).get("impactXapproach");

  dataRollUp = [];

  projectdata = []
  heatMapdata.forEach(function(d) {
    projectdata.push(d.project_Title);
  });
  // return only the distinct / unique nodes
  projectdata = projectdata.getUnique()
  totalnumberprojects = projectdata.length

  if (totalnumberprojects == 0) {
    svg.append("text").text("No projects were found given those filters")
      .attr("class", "heading")
      .attr("x", width / 2)
      .attr("y", 30)
      .attr("text-anchor", "middle");
    return totalprojects
  } 

  heatMapNest.forEach(function(d, v) {
    v.forEach(function(d2, v2) {
      dataRollUp.push({
        impact: d,
        approach: d2,
        value: v2.length,
        projects: v2
      });
    })
  });



  //need to calculate this before adding totals
  var max = d3.max(dataRollUp, function(d) {
    return d.value;
  });

  //calculating total columns      
  for (var i = areasOfImpact.length - 1; i >= 0; i--) {
    areasOfImpact[i]
    total = []
    for (var j = dataRollUp.length - 1; j >= 0; j--) {
      if (dataRollUp[j].impact==areasOfImpact[i]){
        total.push.apply(total,dataRollUp[j].projects)
      }
    }
    dataRollUp.push({
      approach: "Total",
      impact: areasOfImpact[i],
      value: total.getUnique().length,
      projects: total.getUnique()
    });   
  }

  //calculating total rows      
  for (var i = evaluationApproach.length - 1; i >= 0; i--) {
    evaluationApproach[i]
    total = []
    for (var j = dataRollUp.length - 1; j >= 0; j--) {
      if (dataRollUp[j].approach==evaluationApproach[i]){
        total.push.apply(total,dataRollUp[j].projects)
      }
    }
    dataRollUp.push({
      approach: evaluationApproach[i],
      impact: "Total",
      value: total.getUnique().length,
      projects: total.getUnique()
    });   
  }

  evaluationApproach.push("Total")
  areasOfImpact.push("Total")

  svg.append("text").text("Area of impact")
    .attr("class", "heading")
    .attr("x", -10)
    .attr("y", -20)
    .attr("text-anchor", "end");
  svg.append("text").text("Evaluation approach")
    .attr("class", "heading")
    .attr("x", 0)
    .attr("y", -margin.heatmap.top/2-5)
    .attr("text-anchor", "start");

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
    .text(function(d) {
      return d;
    })
    .text(function(d, i) {
      return d;
    })
    .attr("y", function(d, i) {
      return (((i) * gridSizeY / 2) + gridSizeY / 4);
    })
    .attr("x", -10)
    .attr("dx", 0)
    .attr("dy", 0)
    //.attr("transform", "translate(-6," + gridSizeX/4  + ")")
    .attr("class", "impactLabel")
    .style("text-anchor", "end")
    .style("vertical-align", "middle")
    .on("mouseover", function(d) {
      category_tooltip(capitalizeFirstLetter(longnames[d].toLowerCase()))
    })
    .on("mouseout", function() {remove_tooltip()})
    .call(wrapx, margin.heatmap.left - 30);


  var opacityScale = d3.scale.quantile()
    .domain([1, 0.4 * max, max])
    .range([0.3,0.7,1])

  //x-axis
  var approachLabels = svg.selectAll(".approachLabel")
    .data(evaluationApproach)
    .enter().append("text")
    .text(function(d) {
      return d;
    })
    .attr("x", function(d, i) {
      return ((i) * gridSizeX);
    })
    .attr("y", -10)
    .attr("dy", 0)
    .attr("dx", 0)
    .attr("class", "approachLabel")
    .style("text-anchor", "start")
    .on("mouseover", function(d) {
      category_tooltip(capitalizeFirstLetter(longnames[d].toLowerCase()))
    })
    .on("mouseout", function() {remove_tooltip()})
    .call(wrapy, gridSizeY);


  //draw boxes
  var cards = svg.selectAll(".cards")
    .data(dataRollUp);

  cards.enter()
    .append("rect")
    .attr("x", function(d) {
      return evaluationApproach.indexOf(d.approach) * gridSizeX;
    })
    .attr("y", function(d) {
      return ((areasOfImpact.indexOf(d.impact)) * gridSizeY) / 2;
    })
    .attr("rx", 6)
    .attr("ry", 6)
    .attr("class", "card")
    .attr("width", gridSizeX)
    .attr("height", gridSizeY / 2)
    .style("cursor","pointer")
    .style("fill", function(d){
      if (d.impact != "Total"){
        return colorscheme(d.impact)
      } else {
      return grey
      }
    })
    .style("fill-opacity", function(d){
      if (d.impact != "Total" && d.approach != "Total"){
        return opacityScale(d.value)
      } else {
        return opacityScale(max)
      }
    })
    .style("stroke", "#ffffff")
    .style("stroke-width", "1px")
    .on("mouseover", function(l) {
      var cx = d3.event.pageX
      var cy = d3.event.pageY
      if (l.value ==1){
        text = l.value + " project"
      } else {
        text = l.value + " projects"
      }
      tooltip.html(text)
        .style("left", (cx + 5) + "px")
        .style("top", (cy - 28) + "px");
      tooltip
        .style("opacity", tooltipOpacity);
      d3.select(this).call(highlight_card, opacityHigh, grey, widthHigh,1)
      highlightMultipleProjectInList(l.projects)
    })
    .on("mouseout", function() {
      remove_tooltip()
      remove_highlight_list_item()
      remove_highlight_card()
      update_heatmap_selection()
    })
    .on("click", function (l){
      selected_projects = get_selected_projects()
      if (non_zero_intersection(selected_projects,l.projects)) {
        unselect_all_projects()
      } else{
        unselect_all_projects()
        for (var i = l.projects.length - 1; i >= 0; i--) {
          projectSelectionTracker[l.projects[i]] = true
        }
      }
      update_heatmap_selection()
      revealNumberOfProjects(totalnumberprojects, get_number_of_selected_projects(), highlightTime)
    });


  //draw boxes
  var cardtext = svg.selectAll(".cards")
    .data(dataRollUp);

  cardtext.enter()
    .append("text")
    .attr("class","cardtext")
    .text(function(d){
      if (d.impact == "Total" || d.approach == "Total"){
        return d.value
      }
    })
    .attr("y", function(d) {
      return ((areasOfImpact.indexOf(d.impact)+ 0.5) * gridSizeY / 2);
    })
    .attr("x", function(d) {
      return (((evaluationApproach.indexOf(d.approach))+ 0.5) * gridSizeX );
    })


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
          tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", -1 * (++lineNumber * lineHeight + dy) + "em").text(word);

        }
      }
    });
  }

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


var sankeyChart = function(n) { //this is used to hide the previous chart. Should be replaced with .exit().remove() if possible! 

  filterData();
  oldwidth = width
  wdith = width + Math.max(margin.sankey.left + margin.sankey.right,margin.heatmap.left + margin.heatmap.right)
  // append the svg canvas to the page
  d3.select("#sankeyChart").append("svg")
    .attr("width", width + Math.max(margin.sankey.left + margin.sankey.right,margin.heatmap.left + margin.heatmap.right))
    .attr("height", height + margin.sankey.top + margin.sankey.bottom)
    .append("g")
    .attr("transform",
      "translate(" + Math.max(margin.sankey.left + margin.sankey.right,margin.heatmap.left + margin.heatmap.right)/2 + "," + margin.sankey.top + ")");

  var svg = d3.select("#sankeyChart").selectAll("g")
    .append("g")
    .attr("class", "sankey" + n)
    .attr("transform", "translate(4,42)") //translate so the top label is not half hidden and left side of nodes is good
    .style("visibility", "block");

  //set up graph 
  graph = {
    "nodes": [],
    "links": []
  };

  longnames = {}

  data1.forEach(function(d) {
    longnames[d.source] = d["source long name"]
    longnames[d.target] = d["target long name"]
    graph.nodes.push({
      "name": d.source,
    });
    graph.nodes.push({
      "name": d.target
    });
    graph.links.push({
      "source": d.source,
      "target": d.target,
      "value": +d.value,
      "projectTitle": d.project_Title
    });
  });

  // return only the distinct / unique nodes
  graph.nodes = d3.keys(d3.nest()
    .key(function(d) {
      return d.name;
    })
    .map(graph.nodes));

  // loop through each link replacing the text with its index from node
  graph.links.forEach(function(d, i) {
    graph.links[i].source = graph.nodes.indexOf(graph.links[i].source);
    graph.links[i].target = graph.nodes.indexOf(graph.links[i].target);
  });

  //now loop through each nodes to make nodes an array of objects
  // rather than an array of strings
  graph.nodes.forEach(function(d, i) {
    graph.nodes[i] = {
      "name": d
    };
  });

  totalprojects = graph.links.map(function(d) {
      return d["projectTitle"]
    }).getUnique()
  totalnumberprojects = totalprojects.length

  if (totalnumberprojects == 0) {
    svg.append("text").text("No projects were found given those filters")
      .attr("class", "heading")
      .attr("x", width / 2)
      .attr("y", 30)
      .attr("text-anchor", "middle");
    return totalprojects
  } 

  sankey
    .nodes(graph.nodes)
    .links(graph.links)
    .layout(30);

  //get array of possible values for trait of a node
  function get_trait_values(trait) {
    return graph.nodes.map(function(d) {
      return d[trait]
    })
  }

  //get array of possible values for a numerical trait of a node
  function get_numerical_trait_values(trait) {
    return graph.nodes.map(function(d) {
      return Number(d[trait])
    })
  }

  //get name of all nodes in the "middle" of the sankey chart
  middle_nodes = graph.nodes.filter(function(d) {
    return d.targetLinks.length != 0 && d.sourceLinks.length != 0
  }).map(function(d) {
    return d["name"]
  })

  //given name of a node, check if it has incoming and outgoing links and thus is in the middle
  function check_middle(node) {
    middle_nodes = graph.nodes.filter(function(d) {
      return d.targetLinks.length != 0 && d.sourceLinks.length != 0
    }).map(function(d) {
      return d["name"]
    })
    return ($.inArray(node.name, middle_nodes) != -1)
  }

  nodeNames = get_trait_values("name")
  nodeValues = get_numerical_trait_values("value")

  svg.append("text").text("Innovation")
    .attr("class", "heading")
    .attr("x", 0)
    .attr("y", -25)
    .attr("text-anchor", "start");
  svg.append("text").text("Area of impact")
    .attr("class", "heading")
    .attr("x", width / 2)
    .attr("y", -25)
    .attr("text-anchor", "middle");
  svg.append("text").text("Evaluation approach")
    .attr("class", "heading")
    .attr("x", width)
    .attr("y", -25)
    .attr("text-anchor", "end");

  // add in the links
  var link = svg.append("g").selectAll(".link")
    .data(graph.links)
    .enter().append("path")
    .attr("class", "link")
    .attr("d", path)
    .style("cursor","pointer")
    .style("stroke-opacity", opacityNormal)
    .style("stroke-width", function(d) {
      return Math.max(1, d.dy);
    })
    .style("stroke", function(d,i) {  //color given the middle node it's connected to
      if (check_middle(d.source)) {
        return colorscheme(d.source.name)
      } else if (check_middle(d.target)) {
        return colorscheme(d.target.name)
      }
    })
    .sort(function(a, b) {
      return b.dy - a.dy;
    })
    .style("fill","none")
    .on("click", function (l){
      if (projectSelectionTracker[l.projectTitle]){
        unselect_all_projects()
        projectSelectionTracker[l.projectTitle] = false
      } else {
        unselect_all_projects()
        projectSelectionTracker[l.projectTitle] = true
      }
      update_sankey_selection()
      revealNumberOfProjects(totalnumberprojects, get_number_of_selected_projects(), highlightTime)
    })
    .on("mouseover", function(l) {
      d3.select(this)
        .call(highlight_project_sankey, l.projectTitle)
    })
    .on("mouseout", function() {
      remove_highlight_list_item()
      remove_highlight_link()
      update_sankey_selection()
    });


  // add in the nodes
  var node = svg.append("g").selectAll(".node")
    .data(graph.nodes)
    .enter().append("g")
    .attr("class", "node")
    .attr("transform", function(d) {
      return "translate(" + d.x + "," + d.y + ")";
    })
    .on("mouseover", function(d) {
      category_tooltip(capitalizeFirstLetter(longnames[d.name].toLowerCase()))
    })
    .on("mouseout", function() {remove_tooltip()})
    .attr("x", function(d) {
      if (d.x == 0) {return 0}
      if (d.x < width/2) {return sankey.nodeWidth()/2}
      else {return sankey.nodeWidth()}
    })
    // .call(d3.behavior.drag()
    //   .origin(function(d) {
    //     return d;
    //   })
    //   .on("dragstart", function() {
    //     this.parentNode.appendChild(this);
    //   })
    //   .on("drag", dragmove));

  // add the rectangles for the nodes
  node.append("rect")
    .attr("height", function(d) {
      return d.dy;
    })
    .attr("width", sankey.nodeWidth())
    .style("fill", function(d) { //color nodes if they are in the middle, otherwise grey
      if (check_middle(d)) {
        return colorscheme(d.name)
      } else{
        return grey
      }
    })

  // add in the title for the nodes
  node.append("text")
    .attr("y", function(d) {
      return -5;
    })
    .attr("dy", ".35em")
    .attr("vertical-align","top")
    .text(function(d) {
      return d.name;
    })
    .attr("text-anchor", function(d) {
      if (d.x == 0) {return "start"}
      if (d.x < width/2) {return "middle"}
      else {return "end"}
    })
    .on("mouseover", function(d) {
      category_tooltip(capitalizeFirstLetter(longnames[d.name].toLowerCase()))
    })
    .on("mouseout", function() {remove_tooltip()})
    .attr("x", function(d) {
      if (d.x == 0) {return 0}
      if (d.x < width/2) {return sankey.nodeWidth()/2}
      else {return sankey.nodeWidth()}
    });

  return totalprojects
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



var tabulate = function() {


    heatMapdata = d3.tsv.parse(customData, function(d) { //type function
        return {
          matrix: d["matrix"],
          innovation: d["source"],
          impact: d["target"],
          value: +d["value"],
          project_lead: d["Name of PI or project lead(s)"],
          Course_Level: d["Course_Level"],
          Faculty_School: d["Faculty_School"],
          project_Title: d["project_Title"],
          department: d["Department"],
          enrolment_Cap: d["Enrolment Cap"],
          course_Format: d["Course Format"],
          Course_Type: d["Course Type"],
          course_Location: d["Course Location"],
          project_Type: d["Type of Project"],
          project_Stage: d["Project Stage"],
          year_awarded: d["Year Awarded"]
        };
      });
    //var tableData = d3.nest()   //this works to give a unique list of project titles. 
    //.key(function(d) {return d.project_Title;})
    //.map(data,d3.map).keys().sort(d3.ascending);

    filterData()
    tableData = heatMapdata
    columns = tableColumns

    margin_table_left = 15
    margin_table_right = 15
    var table = d3.select("#project-table").append("table")
                  .attr("width", width + margin.heatmap.left + margin.heatmap.right-margin_table_left-margin_table_right)
    thead = table.append("thead"),
      tbody = table.append("tbody");

    var x = "_XX_"; //nothing should match this ;)
    function unique(value) {
      return_this = (x != value["project_Title"]);
      x = value["project_Title"];
      return return_this;
    }
    tableData = tableData.filter(unique);
    totalnumberprojects = tableData.length

    totalprojects = graph.links.map(function(d) {
        return d["projectTitle"]
      }).getUnique()
    totalnumberprojects = totalprojects.length

    if (totalnumberprojects == 0) {
      svg = d3.select("#project-table").append("svg")
              .attr("width", width + margin.heatmap.left + margin.heatmap.right-margin_table_left-margin_table_right)

      svg.append("text").text("No projects were found given those filters")
        .attr("class", "heading")
        .attr("x", width / 2)
        .attr("y", 30)
        .attr("text-anchor", "middle");
      return totalprojects
    } 

    // append the header row
    thead.append("tr")
      .selectAll("th")
      .data(columns)
      .enter()
      .append("th")
      .text(function(column) {
        return capitalizeFirstLetter(column.replace('_', ' '));
      });

    // create a row for each object in the data
    var rows = tbody.selectAll("tr")
      .data(tableData)
      // .data(tableData)
      .enter()
      .append("tr")
      .attr("class", function(d,i) {
        if (i % 2 === 0  ) {return "rowNotShaded"}
        else {return "rowShaded"}
      })
      .on("mouseover", function(l) {
        d3.select(this)
          .call(highlight_project_table, l.project_Title)
      })
      .on("mouseout", function() {
        remove_highlight_list_item()
        update_table_selection()
      })
      .on("click", function (l){
      if (projectSelectionTracker[l.project_Title]) {
        unselect_all_projects()
      } else{
        unselect_all_projects()
        projectSelectionTracker[l.project_Title] = true
      }
      update_table_selection()
      revealNumberOfProjects(totalnumberprojects, get_number_of_selected_projects(), highlightTime)
    });

    // create a cell in each row for each column
    var cells = rows.selectAll("td")
      .data(function(row) {
        return columns.map(function(column) {
          return {  
            column: column,
            value: row[column]
          };

          // return d;})
        });
      })
      .enter()
      .append("td")
      //.attr("style", "font-family: Courier") // sets the font style
      .html(function(d) {
        return d.value;
      });


    projects = tableData.map(function(d) {
      return d["project_Title"]
    })
    return projects;
  } //end tabulate



// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //



//          FILTER stuff                //


// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //
// ****************************************************************** //



var filtersOpen = false;

function toggleFilterSidebar (argument) {
  $('#allFilters').toggle();
  if (filtersOpen)
    $('.sidebarTitle.filters .openclose').text('-');
  else
    $('.sidebarTitle.filters .openclose').text('+');
  filtersOpen = !filtersOpen;
}

var projectsOpen = true;

function toggleProjectSidebar (argument) {
  $('#projectList').toggle();
  if (projectsOpen)
    $('.sidebarTitle.projects .openclose').text('-');
  else
    $('.sidebarTitle.projects .openclose').text('+');
  projectsOpen = !projectsOpen;
}

function get_number_of_selected_projects() {
  if ($.inArray("getUnique", get_selected_projects())) {
    numberselectedprojects = get_selected_projects().length
  } else {
    numberselectedprojects = 0
  }
  return numberselectedprojects
}

//Show the number of projects displayed in Sankey and HeatMap
var revealNumberOfProjects = function(total, numberselected, highlightTime) {
  var removeReveal = function() {
    d3.select("#NumberOfProjects").selectAll("p")
      .remove();
  };
  removeReveal()
  d3.select("#NumberOfProjects").append("p")
    .html(function(){
      if (total==0){return "No projects given filters"}
      else if (total==1){return "Selected " + numberselected + " out of " + total + " project"}
      else {return "Selected " + numberselected + " out of " + total + " projects"}
    })
};


var updateprojectList = function(projectdata) {
  //total = projects.length
  var removeReveal = function() {
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
        tspan = text.text(null).append("tspan").attr("class", "listitem").attr("x", 0).attr("y", y).attr("dy", dy + "em");
      if (y > listheight) {
        return
      }
      spans = 0
      while (word = words.pop()) {
        line.push(word);
        tspan.text(line.join(" "));
        if (tspan.node().getComputedTextLength() > width) {
          line.pop();
          if (spans == 1) {
            line.pop()
            line.push('...')
            tspan.text(line.join(" "));
            break
          }
          tspan.text(line.join(" "));
          line = [word];
          tspan = text.append("tspan").attr("class", "listitem").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
          spans = spans + 1
        }
      }
    });
  }

  var margin = {
    top: 0,
    right: 10,
    bottom: 0,
    left: 10,
  }
  listwidth = document.getElementById("projectList").offsetWidth - margin.left - margin.right,
  listheight = window.innerHeight

  // append the svg canvas to the page
  var svg = d3.select("#projectList").append("svg")
    .attr("class", "list")
    .attr("width", listwidth)
    .attr("height", listheight)
    .append("g")
    .attr("transform", "translate( " +  margin.left + ", -" +  10 + ")");
    //Use line beloe and "text-anchor:middle" for centered text
    //.attr("transform", "translate( " +  listwidth /2 + "," + 0 + ")");

  svg.selectAll(".text")
    .data(projectdata)
    .enter().append("text")
    .attr("class", "projectListItem")
    .attr("x", 0)
    .attr("dx", 0)
    .attr("dy", 0)
    .style("cursor","pointer")
    .attr("y", function(d, i) {
      return 33 * i + 33
    })
    .text(function(d, i) {
      return capitalizeFirstLetter(d.toLowerCase())
    })
    .call(wrap, listwidth-margin.left*2-margin.right*2, listheight)
  .on("click", function (d){
    if (projectSelectionTracker[d]){
      unselect_all_projects()
    } else {
      unselect_all_projects()
      projectSelectionTracker[d] = true
    }
    revealNumberOfProjects(total, get_number_of_selected_projects(), highlightTime)
    update_sankey_selection()
    update_heatmap_selection()
    update_table_selection()
  })
    .on("mouseover", function(d) {
      highlightProjectInList(d)
      d3.select("this").call(highlight_project_sankey, d)
      d3.select("this").call(highlight_project_heatmap, d)
      d3.select("this").call(highlight_project_table, d)
    })
    .on("mouseout", function() {
      remove_highlight_list_item()
      update_sankey_selection()
      update_heatmap_selection()
      update_table_selection()
    });
}

function rerun(currentChartType) {
  projects = ChartType[currentChartType](1)
  total = projects.length
  revealNumberOfProjects(total, get_number_of_selected_projects(), highlightTime)
  updateprojectList(projects)
}


//dynamically obtain all options for each filter
function get_filterOptions(filterName) {
  heatMapdata = d3.tsv.parse(customData);
  options = heatMapdata.map(function(d) {
    return d[filterName]
  }).getUnique()
  newoptions = []
  for (var i = options.length - 1; i >= 0; i--) {
    if (options[i] == " " || options[i] == "") {
      newoptions.push("N/A")
        // } else if (options[i].indexOf(',') > -1) {
        //   newoptions.concat(options[i].split(",")) //need to tease it out when survey gives multiple options[i]s
    } else {
      newoptions.push(options[i])
    }
  }
  fixedoptions = newoptions.getUnique().sort()
  return fixedoptions
}



//choice arrays for filters
var courseLevelList = ["Course level (all)"].concat(get_filterOptions("Course_Level"))
var facultyList = ["Faculty (all)"].concat(get_filterOptions("Faculty_School"))
var projectTypeList = ["Project type (all)"].concat(get_filterOptions("Type of Project"))
var projectStageList = ["Project stage (all)"].concat(get_filterOptions("Project Stage"))
var yearAwardedList = ["Year awarded (all)"].concat(get_filterOptions("Year Awarded"))


function get_filterCategoryOptions(category) {
  heatMapdata = d3.tsv.parse(customData);
  options = heatMapdata.map(function(d) {
    if (category == "Innovation" && d["matrix"]=="innovationXimpact"){
        return d["source"]
      } else if (category == "Impact" && d["matrix"]=="innovationXimpact"){
        return d["target"]
      } else if (category == "Evaluation" && d["matrix"]=="impactXapproach"){
        return d["target"]
      }
    }).getUnique()
  newoptions = []
  for (var i = options.length - 1; i >= 0; i--) {
    if (options[i] != " " && options[i] != "") {
      newoptions.push(options[i])
    }
  }
  fixedoptions = newoptions.getUnique().sort()
  return fixedoptions
}


var innovationList = ["Innovation (all)"].concat(get_filterCategoryOptions("Innovation"))
var impactList = ["Impact (all)"].concat(get_filterCategoryOptions("Impact"))
var evaluationList = ["Evaluation (all)"].concat(get_filterCategoryOptions("Evaluation"))

//columns to display for table
var tableColumns = ["project_Title", "project_lead","department","enrolment_Cap", "Course_Level", "course_Format", "Course_Type", "course_Location", "project_Type", "year_awarded"];

//set default start values
faculty = "Faculty (all)";
courseLevel = "Course level (all)";
projectType = "Project type (all)";
projectStage = "Project stage (all)";
yearAwarded = "Year awarded (all)";
innovation = "Innovation (all)"
impact = "Impact (all)"
evaluation = "Evaluation (all)"

//variables for filters and chart type buttons
var ChartType = {
  "sankeyChart": sankeyChart,
  "innovationImpactChart": heatmapInnovationImpact,
  "impactApproachChart": heatmapImpactApproach,
  "project-table": tabulate
};


var currentChartType = "sankeyChart" //set the default chart type to be sankey

function get_current_chart() {
  currentChart = ''
  divs = ["sankeyChart","innovationImpactChart","impactApproachChart","project-table"]
  for (var i = divs.length - 1; i >= 0; i--) {
    if ( $('#'+divs[i]).is(':empty') ) {
    } else { currentChart = divs[i]}
  }
  return currentChart
}


var facultyPicker = d3.select("#context-filter-faculty").append("select").on("change", function() {
  faculty = d3.select(this).property("value");
  unselect_all_projects()
  rerun(get_current_chart())
  
});

var courseLevelPicker = d3.select("#context-filter-courseLevel").append("select").on("change", function() {
  courseLevel = d3.select(this).property("value");
  unselect_all_projects()
  rerun(get_current_chart())
});


var projectTypePicker = d3.select("#context-filter-projectType").append("select").on("change", function() {
  projectType = d3.select(this).property("value");
  unselect_all_projects()
  rerun(get_current_chart())
});

var projectStagePicker = d3.select("#context-filter-projectStage").append("select").on("change", function() {
  projectStage = d3.select(this).property("value");
  unselect_all_projects()
  rerun(get_current_chart())
});

var yearAwardedPicker = d3.select("#context-filter-yearAwarded").append("select").on("change", function() {
  yearAwarded = d3.select(this).property("value");
  unselect_all_projects()
  rerun(get_current_chart())
});

var innovationPicker = d3.select("#context-filter-innovation").append("select").on("change", function() {
  innovation = d3.select(this).property("value");
  unselect_all_projects()
  rerun(get_current_chart())
});

var impactPicker = d3.select("#context-filter-impact").append("select").on("change", function() {
  impact = d3.select(this).property("value");
  unselect_all_projects()
  rerun(get_current_chart())
});

var evaluationPicker = d3.select("#context-filter-evaluation").append("select").on("change", function() {
  evaluation = d3.select(this).property("value");
  unselect_all_projects()
  rerun(get_current_chart())
});


facultyPicker.selectAll("option").data(facultyList).enter().append("option").attr("value", function(d) {return d}).text(function(d) {return d});
courseLevelPicker.selectAll("option").data(courseLevelList).enter().append("option").attr("value", function(d) {return d}).text(function(d) {return d});
projectTypePicker.selectAll("option").data(projectTypeList).enter().append("option").attr("value", function(d) {return d}).text(function(d) {return d});
projectStagePicker.selectAll("option").data(projectStageList).enter().append("option").attr("value", function(d) {return d}).text(function(d) {return d});
yearAwardedPicker.selectAll("option").data(yearAwardedList).enter().append("option").attr("value", function(d) {return d}).text(function(d) {return d});
innovationPicker.selectAll("option").data(innovationList).enter().append("option").attr("value", function(d) {return d}).text(function(d) {return d});
impactPicker.selectAll("option").data(impactList).enter().append("option").attr("value", function(d) {return d}).text(function(d) {return d});
evaluationPicker.selectAll("option").data(evaluationList).enter().append("option").attr("value", function(d) {return d}).text(function(d) {return d});

allprojects = get_filterOptions("project_Title")

for (var i = allprojects.length - 1; i >= 0; i--) {
  projectSelectionTracker[allprojects[i]] = false
}

function unclick_buttons() {
  d3.selectAll(".big_button")
    .each(function(button) {
      d3.select(this)
        .transition()
        .ease("linear")
        .duration(highlightTime)
        .attr("class", "big_button unclicked")
    })
}

function click_button(button) {
  button
    .transition()
    .ease("linear")
    .duration(highlightTime)
    .attr("class", "big_button clicked")
}

//chartType buttons:
d3.select("#chartTypeButtons") //Sankey
  .append("input")
  .attr("value", "Flow")
  .attr("type", "button")
  .attr("class", function (){
  //.style("background",  function() {
      if (currentChartType == "sankeyChart"){
        return "big_button clicked"
      } else {return "big_button unclicked"}
  })
  .on("click", function() {
    unclick_buttons()
    d3.select(this).call(click_button)
    setChartType = "sankeyChart";
    rerun(setChartType); //redraw previously selected chart 
    update_sankey_selection()
  });


d3.select("#chartTypeButtons") //heatmapInnovationImpact
  .append("input")
  .attr("value", "Innovation x Impact")
  .attr("type", "button")
  .attr("class", function (){
  //.style("background",  function() {
      if (currentChartType == "innovationImpactChart"){
        return "big_button clicked"
      } else {return "big_button unclicked"}
  })
  .on("click", function() {
    unclick_buttons()
    d3.select(this).call(click_button)
    setChartType = "innovationImpactChart";
    rerun(setChartType); //redraw previously selected chart 
    update_heatmap_selection()
  });


d3.select("#chartTypeButtons")
  .append("input")
  .attr("value", "Impact x Evaluation")
  .attr("type", "button")
  .attr("class", function (){
  //.style("background",  function() {
      if (currentChartType == "impactApproachChart"){
        return "big_button clicked"
      } else {return "big_button unclicked"}
  })
  .on("click", function() {
    unclick_buttons()
    d3.select(this).call(click_button)
    setChartType = "impactApproachChart";
    rerun(setChartType); //redraw previously selected chart
    update_heatmap_selection()
  });


d3.select("#chartTypeButtons")
  .append("input")
  .attr("value", "Table")
  .attr("type", "button")
  .attr("class", function (){
  //.style("background",  function() {
      if (currentChartType == "project-table"){
        return "big_button clicked"
      } else {return "big_button unclicked"}
  })
  .on("click", function() {
    unclick_buttons()
    d3.select(this).call(click_button)
    setChartType = "project-table";
    rerun(setChartType); //redraw previously selected chart
    update_table_selection()
  });

function runhelp() {
  d3.select("#help").append("svg")
    .attr("width", width + margin.heatmap.left + margin.heatmap.right)
    .attr("height", height + margin.heatmap.top + margin.heatmap.bottom)
    .append("g")
    .attr("transform",
      "translate(" + Math.max(margin.sankey.left + margin.sankey.right,margin.heatmap.left + margin.heatmap.right)*1.25 + "," + margin.heatmap.top + ")");
  return null
}

d3.select("#chartTypeButtons") //Help - info page
  .append("input")
  .attr("value", "?")
  .attr("type", "button")
  .attr("class", function (){
  //.style("background",  function() {
      if (currentChartType == "help"){
        return "big_button clicked"
      } else {return "big_button unclicked"}
  })
  .on("click", function() {
    unclick_buttons()
    d3.select(this).call(click_button)
    setChartType = "help";
    filterData()
    runhelp()
  });

rerun(currentChartType); 


function reset_filters() {
  //reset filters on page

  //reset to default values
  faculty = "Faculty (all)";
  courseLevel = "Course level (all)";
  projectType = "Project type (all)";
  projectStage = "Project stage (all)";
  yearAwarded = "Year awarded (all)";
  innovation = "Innovation (all)"
  impact = "Impact (all)"
  evaluation = "Evaluation (all)"

  d3.select("#context-filter-faculty").selectAll("select").property({"value":faculty})
  d3.select("#context-filter-courseLevel").selectAll("select").property({"value":courseLevel})
  d3.select("#context-filter-projectType").selectAll("select").property({"value":projectType})
  d3.select("#context-filter-projectStage").selectAll("select").property({"value":projectStage})
  d3.select("#context-filter-yearAwarded").selectAll("select").property({"value":yearAwarded})
  d3.select("#context-filter-innovation").selectAll("select").property({"value":innovation})
  d3.select("#context-filter-impact").selectAll("select").property({"value":impact})
  d3.select("#context-filter-evaluation").selectAll("select").property({"value":evaluation})

  //rerun viz
  unselect_all_projects()
  rerun(get_current_chart())
}