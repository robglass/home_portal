App = (function(){
 var app = {};
 var _initRan;
 app.getTorrents = function(){
  $.ajax({
    url: "torrents",
    success: function(json){
	if ($('#torrentTable').datatable === 'function'){
	          $('#torrentTable').dataTable().fnDestroy();
		  $('#torrentTable').empty();
	};
	var torrents = $.parseJSON(json);
	$('#torrentTable').append('<thead><tr><th>Torrent</th><th>Size</th><th>Date</th><th>Link</th></tr></thead>');
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
 app.fetchTorrents = function(){
  $.ajax({
     url: 'fetch_torrents',
     success: function(json){
      if (json.status !== undefined){
        app.getTorrents();
	app.lastUpdate();	
      }
     },
     error: function(err) {
       console.log('Shits broke son!');
     }
   })
 }
 app.lastUpdate = function(){
  $.ajax({
     url: 'lastUpdate',
     success: function(json){
      if (json.date !== undefined){	
      	$('.date').empty();
      	$('.date').append(json.date)
      }
     },
     error: function(err) {
       console.log('Couldnt get lastUpdate');
     }
   })
 }
 _init= function() {
   app.getTorrents();
   app.lastUpdate();
   $('#updateTorrents').click(function(){
	app.fetchTorrents();
	});
   
 _initRan=true;
}
 _init();
 return app;
}());
