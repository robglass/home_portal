App = (function(){
 var app = {};

 app.getTorrents = function(){
  $.ajax({
    url: "torrents",
    success: function(json){
   	console.log(json);
    }	  
  });
 }
 app.getTorrents();
 return app;
}());
