// start loading 
function load_property_grid(title,div, params) {
	// params = [{params}, {jqmeta}]
	console.log("load_property_grid : " +  title + " to <DIV>" + div + "</DIV>");

	// ### TO DO: Widget Framework Load the Widget HTML into the DIV first (if exist && !Empty)
	// $(div).find("#"+div).HTML();
	// Link the CSS if exist
	// ### WIDGET FRAMEWORK

	// Create the grid (or parent control)
	$(div).find("#"+div).jqPropertyGrid(params[0],params[1]);
	//$('#'+ div).jqPropertyGrid(params.params,params.jqmeta);

	// ### TO DO - HOOKUP TO LOCALSTORAGE/USER PROFILE -> move to JS file
	$(div).find("#btnSave").click(function() {
	  var first = JSON.stringify($(div).find("#jqContainer").jqPropertyGrid('get'), null, '\t');
	  console.log(first);
	  // store updates to LocalStorage (for now, add RestAPI storage)

	  // hide the DIV again
	  $(div).find("#jqContainer").modal('toggle');
	});

}