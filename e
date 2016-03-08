[1mdiff --git a/sotl_exp/important_part.js b/sotl_exp/important_part.js[m
[1mindex 840cefa..d752491 100644[m
[1m--- a/sotl_exp/important_part.js[m
[1m+++ b/sotl_exp/important_part.js[m
[36m@@ -222,7 +222,7 @@[m [md3.sankey = function() {[m
   };[m
 [m
   sankey.link = function() {[m
[31m-    var curvature = 0.4;[m
[32m+[m[32m    var curvature = 0.7;[m
 [m
     function link(d) {[m
       var x0 = d.source.x + d.source.dx,[m
[36m@@ -912,7 +912,7 @@[m [mvar heatmapInnovationImpact = function(n) {[m
       remove_highlight_card()[m
     });[m
 [m
[31m-  cards.append("title");[m
[32m+[m[32m  //cards.append("title");[m
 [m
   cards.transition()[m
     .ease("linear")[m
[36m@@ -1428,10 +1428,10 @@[m [mvar sankeyChart = function(n) { //this is used to hide the previous chart. Shoul[m
   nodeNames = get_trait_values("name")[m
   nodeValues = get_numerical_trait_values("value")[m
 [m
[31m-  // using colors from d3.scale.category10[m
[31m-  // colorscheme = d3.scale.ordinal()[m
[31m-  //   .domain(middle_nodes)[m
[31m-  //   .range(["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"])[m
[32m+[m[32m  //using colors from d3.scale.category10[m
[32m+[m[32m  colorscheme = d3.scale.ordinal()[m
[32m+[m[32m    .domain(middle_nodes)[m
[32m+[m[32m    .range(["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"])[m
 [m
 [m
   // add in the links[m
[36m@@ -1444,17 +1444,17 @@[m [mvar sankeyChart = function(n) { //this is used to hide the previous chart. Shoul[m
     .style("stroke-width", function(d) {[m
       return Math.max(1, d.dy);[m
     })[m
[31m-    // .style("stroke", function(d,i) {  //color given the middle node it's connected to[m
[31m-    //   if (check_middle(d.source)) {[m
[31m-    //     return colorscheme(d.source.name)[m
[31m-    //   } else if (check_middle(d.target)) {[m
[31m-    //     return colorscheme(d.target.name)[m
[31m-    //   }[m
[31m-    // })[m
[31m-    .style("stroke", colorNormal)[m
[31m-    .sort(function(a, b) {[m
[31m-      return b.dy - a.dy;[m
[32m+[m[32m    .style("stroke", function(d,i) {  //color given the middle node it's connected to[m
[32m+[m[32m      if (check_middle(d.source)) {[m
[32m+[m[32m        return colorscheme(d.source.name)[m
[32m+[m[32m      } else if (check_middle(d.target)) {[m
[32m+[m[32m        return colorscheme(d.target.name)[m
[32m+[m[32m      }[m
     })[m
[32m+[m[32m    // .style("stroke", colorNormal)[m
[32m+[m[32m    // .sort(function(a, b) {[m
[32m+[m[32m    //   return b.dy - a.dy;[m
[32m+[m[32m    // })[m
     .on("mouseover", function(l) {[m
       var cx = d3.event.pageX[m
       var cy = d3.event.pageY[m
