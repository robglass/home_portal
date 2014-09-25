var express = require('express');
var router = express.Router();
fs = require('fs');

/* GET home page. */
router.get('/', function(req, res) {
  res.render('index', { title: 'Express' });
});

router.get('/torrents', function(req,res){
  fs.readFile('/var/www/home_portal/public/torrent/torrent_list.json', 'utf8', function(err, data){
  	res.json(data);
  })
})
router.get('/fetch_torrents', function(req,res){
  var process = require('child_process');
    process.exec('python /var/www/home_portal/public/torrent/torrents.py', function(error){
  	if (error !== null) {  
		res.send(500, error.code); 
	} else {
   		res.json({ status: "done"} );
	}
    });
})
router.get('/lastUpdate', function(req,res){
  var process = require('child_process');
    process.exec('date -r /var/www/home_portal/public/torrent/torrent_list.json', function(error, out){
		res.json({date: out});
    });
})
router.get('/grocery', function(req,res){
  fs.readFile('/var/www/home_portal/public/grocery/grocery_list.json', 'utf8', function(err, data){
  	res.json(data);
  })
})
module.exports = router;
