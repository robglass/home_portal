App = (function(){
 var app = {};

 app.getTorrents = function(){
  $.ajax({
    url: "torrents",
    success: function(json){
	var torrents = $.parseJSON(json);
        for (var key in torrents) {
         $('#torrentTable').append('<tr><td>'+torrents[key].name+'</td><td data-order="'+torrents[key].sizemb+'">'+torrents[key].size+'</td><td>'+torrents[key].date+'</td><td><a href="'+torrents[key].url+'"><button type="button" class="btn btn-primary">Download</button></a></td></tr>');

        }
	$('#torrentTable').DataTable({
		stateSave: true,
		"order": [[ 2, "desc" ]]
	});
    }	  
  });
 }
 app.getTorrents();
 return app;
}());
