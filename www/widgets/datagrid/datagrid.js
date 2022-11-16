// start loading widget
function load_grid_gi(title, div, par){
    console.log("load_grid_gi : " + title + " to <div>" + div + "</div>");
	//console.log(par)
	var grid = $('#' +div ).grid(par);

	grid.on('rowDataChanged', function (e, id, record) {	
	    $.ajax({ url: 'http://192.168.1.140:5000/api/blog/posts/', data: { record: record }, method: 'POST' })
			.fail(function () {
				alert('Failed to save.');
	   }); 
	});
	
	grid.on('rowRemoving', function (e, $row, id, record) {
		$.ajax({ url: 'http://192.168.1.140:5000/api/blog/posts/', data: { id: id }, method: 'POST' })
			.done(function () {
				grid.reload();
			})
			.fail(function () {
				alert('Failed to delete.');
			});
	});
	
}